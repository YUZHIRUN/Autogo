#include <stdio.h>
#include <unistd.h>
#include <string.h>

#include <malloc.h>

#include "cmsis_os2.h"
#include <hi_types_base.h>

//GPIO
#include "wifiiot_gpio.h"
#include "wifiiot_errno.h"
#include "wifiiot_gpio_ex.h"

#include "display_screen.h"
#include "spi.h"
#include "list.h"
#include "rc522.h"
#include "uart.h"
#include "wifi_config.h"
#include "mqtt_config.h"

#include "nv.h"
// #include "kvstore_common.h"
// #include "ohos_errno.h"



//宏定义
#define RC522_NSS_SetValue(value) GpioSetOutputVal(WIFI_IOT_GPIO_IDX_9,value)
#define RC522_RST_SetValue(value) GpioSetOutputVal(WIFI_IOT_GPIO_IDX_10,value)


/************************************************* 底层函数 *************************************************/

//功    能：写RC632寄存器
//参数说明：Address[IN]:寄存器地址
//          value[IN]:写入的值
void WriteRawRC(unsigned char Address, unsigned char value)
{  
	unsigned char ucAddr;

	RC522_NSS_SetValue(0);
	ucAddr = ((Address<<1)&0x7E);
	SPI0_ReadWriteByte(ucAddr);
	SPI0_ReadWriteByte(value);
	RC522_NSS_SetValue(1);
}

/////////////////////////////////////////////////////////////////////
//功    能：读RC522寄存器
//参数说明：Address[IN]:寄存器地址
//返    回：读出的值
/////////////////////////////////////////////////////////////////////
unsigned char ReadRawRC(unsigned char Address)
{
    unsigned char ucAddr;
    unsigned char ucResult=0;

    RC522_NSS_SetValue(0);   
    ucAddr = ((Address<<1)&0x7E)|0x80;
    SPI0_ReadWriteByte(ucAddr);
    ucResult = SPI0_ReadWriteByte(0xff);
    RC522_NSS_SetValue(1);

    return ucResult;
}

//功    能：清RC522寄存器位
//参数说明：reg[IN]:寄存器地址
//          mask[IN]:清位值
void ClearBitMask(unsigned char reg,unsigned char mask)  
{
	char tmp = 0x0;
	tmp = ReadRawRC(reg);
	WriteRawRC(reg, tmp & ~mask);  // clear bit mask
}

//功    能：置RC522寄存器位
//参数说明：reg[IN]:寄存器地址
//          mask[IN]:置位值
void SetBitMask(unsigned char reg,unsigned char mask)  
{
	char tmp = 0x0;
	tmp = ReadRawRC(reg);
	WriteRawRC(reg,tmp | mask);  // set bit mask
}

/////////////////////////////////////////////////////////////////////
//功    能：复位RC522
//返    回: 成功返回MI_OK
/////////////////////////////////////////////////////////////////////
char PcdReset(void)
{
	RC522_RST_SetValue(1);
	usleep(10);
	RC522_RST_SetValue(0);
	usleep(10);
	RC522_RST_SetValue(1);
	usleep(10);

	WriteRawRC(CommandReg, PCD_RESETPHASE);
	usleep(10);
	WriteRawRC(ModeReg, 0x3D);            //和Mifare卡通讯，CRC初始值0x6363
	WriteRawRC(TReloadRegL, 30);           
	WriteRawRC(TReloadRegH, 0);
	WriteRawRC(TModeReg, 0x8D);
	WriteRawRC(TPrescalerReg, 0x3E);
	WriteRawRC(TxAutoReg, 0x40);
	
	return MI_OK;
}

//功    能：通过RC522和ISO14443卡通讯
//参数说明：Command[IN]:RC522命令字
//          pInData[IN]:通过RC522发送到卡片的数据
//          InLenByte[IN]:发送数据的字节长度
//          pOutData[OUT]:接收到的卡片返回数据
//          *pOutLenBit[OUT]:返回数据的位长度
char PcdComMF522(unsigned char Command,
                 unsigned char *pInData,
                 unsigned char InLenByte,
                 unsigned char *pOutData,
                 unsigned int  *pOutLenBit)
{
	char status = MI_ERR;
	unsigned char irqEn   = 0x00;
	unsigned char waitFor = 0x00;
	unsigned char lastBits;
	unsigned char n;
	unsigned int i;
	switch (Command)
	{
		case PCD_AUTHENT:
				irqEn   = 0x12;
				waitFor = 0x10;
				break;
		case PCD_TRANSCEIVE:
				irqEn   = 0x77;
				waitFor = 0x30;
				break;
		default:
				break;
	}

	WriteRawRC(ComIEnReg,irqEn|0x80);
	ClearBitMask(ComIrqReg,0x80);
	WriteRawRC(CommandReg,PCD_IDLE);
	SetBitMask(FIFOLevelReg,0x80);

	for (i=0; i<InLenByte; i++)
	{
		WriteRawRC(FIFODataReg, pInData[i]);
	}
	WriteRawRC(CommandReg, Command);

	if (Command == PCD_TRANSCEIVE)
	{
		SetBitMask(BitFramingReg,0x80);
	}

	i = 600;//根据时钟频率调整，操作M1卡最大等待时间25ms
	do
	{
		n = ReadRawRC(ComIrqReg);
		i--;
	}
	while ((i!=0) && !(n&0x01) && !(n&waitFor));
	ClearBitMask(BitFramingReg,0x80);

	if (i!=0)
	{   
		if(!(ReadRawRC(ErrorReg)&0x1B))
		{
			status = MI_OK;
			if (n & irqEn & 0x01)
			{
				status = MI_NOTAGERR;
			}
			if (Command == PCD_TRANSCEIVE)
			{
				n = ReadRawRC(FIFOLevelReg);
				lastBits = ReadRawRC(ControlReg) & 0x07;
				if (lastBits)
				{
					*pOutLenBit = (n-1)*8 + lastBits;
				}
				else
				{
					*pOutLenBit = n*8;
				}
				if (n == 0)
				{
					n = 1;
				}
				if (n > MAXRLEN)
				{
					n = MAXRLEN;
				}
				for (i=0; i<n; i++)
				{
					pOutData[i] = ReadRawRC(FIFODataReg);
				}
			}
		}
		else
		{   
			status = MI_ERR;
		}
	}
	SetBitMask(ControlReg,0x80);           // stop timer now
	WriteRawRC(CommandReg,PCD_IDLE);
	
	return status;
}

//关闭天线
void PcdAntennaOff()
{
    ClearBitMask(TxControlReg, 0x03);
}

//开启天线  
//每次启动或关闭天险发射之间应至少有1ms的间隔
void PcdAntennaOn()
{
	unsigned char i;
	
	i = ReadRawRC(TxControlReg);
	if (!(i & 0x03))
	{
		SetBitMask(TxControlReg, 0x03);
	}
}

/////////////////////////////////////////////////////////////////////
//功    能：寻卡
//参数说明: req_code[IN]:寻卡方式
//                0x52 = 寻感应区内所有符合14443A标准的卡
//                0x26 = 寻未进入休眠状态的卡
//          pTagType[OUT]：卡片类型代码
//                0x4400 = Mifare_UltraLight
//                0x0400 = Mifare_One(S50)
//                0x0200 = Mifare_One(S70)
//                0x0800 = Mifare_Pro(X)
//                0x4403 = Mifare_DESFire
//返    回: 成功返回MI_OK
/////////////////////////////////////////////////////////////////////
char PcdRequest(unsigned char req_code,unsigned char *pTagType)
{
	char status;  
	unsigned int  unLen;
	unsigned char ucComMF522Buf[MAXRLEN]; 

	ClearBitMask(Status2Reg,0x08);
	WriteRawRC(BitFramingReg,0x07);
	SetBitMask(TxControlReg,0x03);

	ucComMF522Buf[0] = req_code;

	status = PcdComMF522(PCD_TRANSCEIVE,ucComMF522Buf,1,ucComMF522Buf,&unLen);

	if ((status == MI_OK) && (unLen == 0x10))
	{    
		*pTagType     = ucComMF522Buf[0];
		*(pTagType+1) = ucComMF522Buf[1];
	}
	else
	{   
		status = MI_ERR;
	}

	return status;
}

/////////////////////////////////////////////////////////////////////
//功    能：防冲撞
//参数说明: pSnr[OUT]:卡片序列号，4字节
//返    回: 成功返回MI_OK
/////////////////////////////////////////////////////////////////////  
char PcdAnticoll(unsigned char *pSnr)
{
	char status;
	unsigned char i,snr_check=0;
	unsigned int  unLen;
	unsigned char ucComMF522Buf[MAXRLEN];

	ClearBitMask(Status2Reg,0x08);
	WriteRawRC(BitFramingReg,0x00);
	ClearBitMask(CollReg,0x80);

	ucComMF522Buf[0] = PICC_ANTICOLL1;
	ucComMF522Buf[1] = 0x20;

	status = PcdComMF522(PCD_TRANSCEIVE,ucComMF522Buf,2,ucComMF522Buf,&unLen);

	if (status == MI_OK)
	{
		for (i=0; i<4; i++)
		{
			*(pSnr+i)  = ucComMF522Buf[i];
			snr_check ^= ucComMF522Buf[i];
		}
		if (snr_check != ucComMF522Buf[i])
		{
			status = MI_ERR;
		}
	}

	SetBitMask(CollReg,0x80);
	return status;
}



/************************************************* 顶层函数 *************************************************/

//RC522 GPIO 相关初始化，包括 GPIO 和 SPI 复用的初始化
void RC522_GPIO_Init(void)
{
    // GPIO 初始化
	//在系统初始化时已经调用过了，这里要么就不调用，要再次调用就要在所有GPIO操作之前调用，否则会出现其他异常。
	//比如SPI0在函数SPI0_ReadWriteByte中会出现{hi_spi_host_writeread failed}。
    GpioInit();

	IoSetFunc(WIFI_IOT_IO_NAME_GPIO_6, WIFI_IOT_IO_FUNC_GPIO_6_SPI0_CK); //RC522_SCK
    // GpioSetDir(WIFI_IOT_GPIO_IDX_6, WIFI_IOT_GPIO_DIR_OUT);
    IOSetDriverStrength(WIFI_IOT_IO_NAME_GPIO_6, WIFI_IOT_IO_DRIVER_STRENGTH_2);

    IoSetFunc(WIFI_IOT_IO_NAME_GPIO_7, WIFI_IOT_IO_FUNC_GPIO_7_SPI0_RXD); //RC522_MISO
    // GpioSetDir(WIFI_IOT_GPIO_IDX_7, WIFI_IOT_GPIO_DIR_IN);

    IoSetFunc(WIFI_IOT_IO_NAME_GPIO_8, WIFI_IOT_IO_FUNC_GPIO_8_SPI0_TXD); //RC522_MOSI
    // GpioSetDir(WIFI_IOT_GPIO_IDX_8, WIFI_IOT_GPIO_DIR_OUT);
    IOSetDriverStrength(WIFI_IOT_IO_NAME_GPIO_8, WIFI_IOT_IO_DRIVER_STRENGTH_0);

    IoSetFunc(WIFI_IOT_IO_NAME_GPIO_9, WIFI_IOT_IO_FUNC_GPIO_9_GPIO); //RC522_NSS
    GpioSetDir(WIFI_IOT_IO_NAME_GPIO_9, WIFI_IOT_GPIO_DIR_OUT);

    IoSetFunc(WIFI_IOT_IO_NAME_GPIO_10, WIFI_IOT_IO_FUNC_GPIO_10_GPIO); //RC522_RST
    GpioSetDir(WIFI_IOT_IO_NAME_GPIO_10, WIFI_IOT_GPIO_DIR_OUT);

	SPI0_Init();	
}

//RC522 的硬件配置
void RC522_HW_Config(void)
{
    PcdReset();
	PcdAntennaOff();
    usleep(5000);
	PcdAntennaOn();
}

//RC522 的初始化
void RC522_Init(void)
{
    RC522_GPIO_Init();

    RC522_HW_Config();
}

//RC522 test 测试程序
void RC522_Test(void)
{
    unsigned char i;
	unsigned char status;
	unsigned char g_ucTempbuf[4];
	unsigned char UID[4];

	status = PcdRequest(PICC_REQALL, g_ucTempbuf); //寻卡
	if (status != MI_OK)
	{
		printf("PcdRequest failed\r\n");
		return;
	}

    printf("PcdRequest success\r\n");

	status = PcdAnticoll(UID); //防冲撞
	if (status != MI_OK)
	{
		printf("PcdAnticoll failed\r\n");
		return;
	}

    printf("PcdAnticoll success\r\n");
	PcdReset(); //寻卡、防冲撞操作执行完成后复位卡片一次，防止下一次寻卡失败，造成一次成功一次失败。


    printf("RC522-ID:");
    for(i=0;i<4;i++)
        printf("[%2X]",UID[i]);
    printf("\r\n");
}

/**
 * @brief  扫描卡
 * @par  扫描附近的卡，判断有无卡
 * @param  card_ID  [IN] type #unsigned int 如果扫描到有卡，返回出卡号ID。
 * @retval  #BRUSH_FIND  有卡
 * @retval  #BRUSH_NONE  无卡
*/
BrushCardStatus RC522_FindCard(unsigned int *card_ID)
{
	unsigned char i;
	unsigned char status;
	unsigned char g_ucTempbuf[4];
	// unsigned char UID[4];

	status = PcdRequest(PICC_REQALL, g_ucTempbuf); //寻卡
	if (status != MI_OK)
	{
		*card_ID = 0;
		printf("PcdRequest failed\r\n");
		// RC522_HW_Config();
		return BRUSH_NONE;
	}
    printf("PcdRequest success\r\n");

	status = PcdAnticoll(g_ucTempbuf); //防冲撞
	if (status != MI_OK)
	{
		*card_ID = 0;
		printf("PcdAnticoll failed\r\n");
		// RC522_HW_Config();
		return BRUSH_NONE;
	}
    printf("PcdAnticoll success\r\n");
	PcdReset(); //寻卡、防冲撞操作执行完成后复位卡片一次，防止下一次寻卡失败，造成一次成功一次失败。

	//刷卡验证成功，成功获取卡号
	for(i=0;i<4;i++)
	{
		printf("user ID[%d] = %X\r\n", i, g_ucTempbuf[i]);
	}

	//32bit机上 unsigned int 占用4个字节，测试： printf("%d",sizeof(unsigned int));
	//所以可以用 unsigned int 类型来存储占用4个字节的唯一识别号
	//后续操作：初始化将用户数据从数据库中读取后，
	//          方案一：可以用数组存储用户ID信息，要定义一个足够大的数组
	//          方案二：链表ADT
	*card_ID = ((unsigned int)g_ucTempbuf[0]<<24) | ((unsigned int)g_ucTempbuf[1]<<16) | ((unsigned int)g_ucTempbuf[2]<<8) | ((unsigned int)g_ucTempbuf[3]);

	return BRUSH_FIND;
}

extern LinkList RC522_Database;
extern unsigned char g_user_num;
extern struct sys_time Sys_Time;
extern struct scancard_time ScanCard_Time;
extern struct sys_record_info ScanRecord_Info[50];
extern unsigned char record_num; //记录的考勤信息，初始化为0，表示此时拥有0条信息，下一次的有效信息是下标为0的信息
extern bool sys_Running_First;

#include <hi_types_base.h>
#include <hi_stdlib.h>
#include <hi_early_debug.h>
#include <hi_nv.h>
#include <hi_flash.h>
#include <hi_partition_table.h>
#define  HI_FACTORY_NV_DEMO_ID  0x1F
typedef struct {
    hi_s32 nv_factory_demo_test_num0;
    hi_s32 nv_factory_demo_test_num1;
    hi_s32 nv_factory_demo_test_num2;
} hi_factory_nv_demo_tset_cfg;
hi_void factory_nv_demo(hi_void)
{
    hi_u32 ret;
    hi_u32 err_info = 0;
    hi_factory_nv_demo_tset_cfg cfg, cfg1;
    (hi_void)memset_s(&cfg, sizeof(cfg), 0, sizeof(cfg));
    (hi_void)memset_s(&cfg1, sizeof(cfg1), 0, sizeof(cfg1));

    cfg.nv_factory_demo_test_num0 = 0x1;

    hi_flash_deinit();
    ret = hi_flash_init();
    if (ret != HI_ERR_SUCCESS) {
        err_info |= 1 << 0x6;
        printf("flash init status:0x%x\n", err_info);
        return;
    }

    ret = hi_factory_nv_init(HI_FNV_DEFAULT_ADDR, HI_NV_DEFAULT_TOTAL_SIZE, HI_NV_DEFAULT_BLOCK_SIZE);
    if (ret != HI_ERR_SUCCESS) {
        printf("factory nv init fail\r\n");
        return;
    }

    /* read factory nv data(which nv id is 0x1) from board */
    ret = hi_factory_nv_read(HI_FACTORY_NV_DEMO_ID, &cfg, sizeof(cfg), 0);
    if (ret != HI_ERR_SUCCESS) {
        printf("factory nv read fail\r\n");
        return;
    }
    printf("factory nv read success, cfg.nv_demo_test_num0:%d\r\n", cfg.nv_factory_demo_test_num0);

	if(cfg.nv_factory_demo_test_num0 == 0) // 下完程序第一次上电，运行完就不是第一次了，所以清零
	{
		sys_Running_First = 1;

		cfg1.nv_factory_demo_test_num0 = 0x3;

		/* write factory nv data(which nv id is 0x1) to board */
		ret = hi_factory_nv_write(HI_FACTORY_NV_DEMO_ID, &cfg1, sizeof(cfg1), 0);
		if (ret != HI_ERR_SUCCESS) {
			printf("factory nv write fail\r\n");
			return;
		}
		printf("factory nv write success\r\n");
		ret = hi_factory_nv_read(HI_FACTORY_NV_DEMO_ID, &cfg, sizeof(cfg), 0);
		if (ret != HI_ERR_SUCCESS) {
			printf("factory nv read fail\r\n");
			return;
		}
		printf("factory nv read success, cfg.nv_demo_test_num0:%d\r\n", cfg.nv_factory_demo_test_num0);
	}
	else
	{
		sys_Running_First = 0;
	}
}

#define DATABASE_INIT
#ifdef DATABASE_INIT
//成功
/* 不带掉电保存时的数据库初始化 */
void Database_Init(void)
{
    RC522_Database = CreateListHead(); //初始化 RC522 数据库

/* 钥匙卡 */
    UserInfo user1 = {
		//ID
        .userid = 1240396216, 			// 49 EE F1 B8
		.name = "root",

		//权限
        .permission = AUTHORITY_ROOT, 			//超级用户
        .permission_last = AUTHORITY_RESERVE, 	//保留
		.permission_time_is_forever = YES_YES,	//权限永久生效
        .permission_time_hours = 255,
        .permission_time_minutes = 255,
        .permission_time_seconds = 255,

		//刷卡(打卡)时间
        .scancard_time_is_same = YES_YES, 		//与系统相同
        .morning_time_hours = 255,
        .morning_time_minutes = 255,
        .morning_time_seconds = 255,
        .afternoon_time_hours = 255,
        .afternoon_time_minutes = 255,
        .afternoon_time_seconds = 255,

    };
    // Insert(&user1, RC522_Database);

    UserInfo user2 = {
		//ID
        .userid = 1246919551,			// 4A 52 7B 7F
		.name = "admin",

		//权限
        .permission = AUTHORITY_ADMIN, 	//管理员
		.permission_last = AUTHORITY_RESERVE, 	//保留
		.permission_time_is_forever = YES_YES,	//权限永久生效
        .permission_time_hours = 255,
        .permission_time_minutes = 255,
        .permission_time_seconds = 255,

		//刷卡(打卡)时间
        .scancard_time_is_same = YES_YES, 		//与系统相同
        .morning_time_hours = 255,
        .morning_time_minutes = 255,
        .morning_time_seconds = 255,
        .afternoon_time_hours = 255,
        .afternoon_time_minutes = 255,
        .afternoon_time_seconds = 255,
    };
    // Insert(&user2, RC522_Database);

	UserInfo user3 = {
		//ID
        .userid = 3388891059, 			// C9 FE 5F B3
		.name = "user_test",

        .permission = AUTHORITY_USER, 	//普通用户
		.permission_last = AUTHORITY_RESERVE, 	//保留
		.permission_time_is_forever = YES_YES,	//权限永久生效
        .permission_time_hours = 255,
        .permission_time_minutes = 255,
        .permission_time_seconds = 255,

		//刷卡(打卡)时间
        .scancard_time_is_same = YES_YES, 		//与系统相同
        .morning_time_hours = 255,
        .morning_time_minutes = 255,
        .morning_time_seconds = 255,
        .afternoon_time_hours = 255,
        .afternoon_time_minutes = 255,
        .afternoon_time_seconds = 255,
    };
    // Insert(&user3, RC522_Database);

/* 白卡 */
	// UserInfo user4 = {
	// 	.userid = 3346651283, // C7 79 D8 93
	// 	.permission = AUTHORITY_USER,
	// 	.time_is_forever = FOREVER_YES, //永久期限
    // };
    // Insert(&user4, RC522_Database);

	

	factory_nv_demo(); //判断是不是烧录完程序第一次上电，是的话 sys_Running_First = 1, 否则 sys_Running_First = 0

	if(sys_Running_First)
	{
		Insert(&user1, RC522_Database);
		Insert(&user2, RC522_Database);
		Insert(&user3, RC522_Database);

		//数据库用户数
		g_user_num = 3;

		/* 保存进Flash */
		hi_flash_erase(FLASH_USERINFO_OFFSET, 4096);
		Flash_Write(FLASH_USERINFO_OFFSET, RC522_Database, g_user_num, HI_FALSE);

		return;
	}
	
	// Flash_Test();
	Flash_Read(FLASH_USERINFO_OFFSET, RC522_Database, &g_user_num);
}
#else
//失败
/* 支持掉电保存的数据库初始化 */
void Database_Init(void)
{
    RC522_Database = CreateListHead(); //初始化 RC522 数据库（其实是创建一个无用的头结点）

	g_user_num = 3;

	// Flash_Write_Name(RC522_Database);
	Flash_Read_Name(RC522_Database);

	// Flash_Write_Others(RC522_Database);
	Flash_Read_Others(RC522_Database);
}
#endif

/**
 * @brief  判断卡是否在数据库中
 * @par  对传入的卡id进行遍历数据库，判断该卡是否在数据库中，并返回相应的权限
 * @param  card_ID  [IN] type #unsigned int 传入的卡id
 * @retval  #AUTHORITY_NO    没有权限（不在数据库中)
 * @retval  #AUTHORITY_USER  普通用户
 * @retval  #AUTHORITY_ADMIN 管理员
 * @retval  #AUTHORITY_ROOT  超级用户
*/
AuthorityStatus Card_Is_Database(unsigned int card)
{
	UserInfo user;
	char ret;

	user.userid = card;

	ret = Find_Permission(&user, RC522_Database);
	if(ret != 0) //没有找到此用户
	{
		printf("not find user : [%u]\r\n", card);
		return AUTHORITY_NONE;			 //卡不在数据库中
	}

	//找到该用户
	switch(user.permission)
	{
		case AUTHORITY_NO:
			return AUTHORITY_NO; 		//卡无权限
			break;
		case AUTHORITY_USER:
			return AUTHORITY_USER; 		//卡是普通用户
			break;
		case AUTHORITY_ADMIN:
			return AUTHORITY_ADMIN; 	//卡是管理员
			break;
		case AUTHORITY_ROOT:
			return AUTHORITY_ROOT; 		//卡是 ROOT
			break;
		default:
			return AUTHORITY_RESERVE; 	//保留，一般不会到这里
			break;
	}
}


extern osMessageQueueId_t mid_MsgQueue;
//刷卡(打卡)考勤
void Scan_Card(void)
{
	BrushCardStatus brushCard_Statu;
	unsigned int user_id;
	LinkList P;
	UserInfo find_user;
	unsigned char str[100] = {0};
	unsigned char i;
	app_msg_t *app_msg;


	brushCard_Statu = RC522_FindCard(&user_id);
	if(brushCard_Statu == BRUSH_NONE) //没有发现卡
	{
		printf(RC522_DEBUG "BRUSH_NONE\r\n");

		return;
	}
	else //发现卡
	{
		//串口屏 切换到 white_board 界面
		Display_Screen_Write((hi_u8 *)"page white_board");
		//等待一小会，等串口屏刷新完页面
		usleep(500000);
		// Display_Screen_Write((hi_u8 *)"t0.txt=\"\""); //清空内容
		Display_Screen_Write((hi_u8 *)"vis b0,0");

		find_user.userid = user_id;
		
		P = Find(&find_user, RC522_Database);
		if(P == NULL) //没有查找到该结点，即该用户不在数据库中
		{
			Display_Screen_Write((hi_u8 *)"t0.txt=\"刷卡情况：刷卡失败\r\n\"");
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"ID：无\r\n\"");
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"您的身份是：无\r\n\"");
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"打卡情况：无\r\n\"");
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"打卡时间：无\r\n\"");
		}
		
		else //查找到该结点，并返回结点地址，即该用户已录入数据库中
		{
			/* 刷卡情况 */
			Display_Screen_Write((hi_u8 *)"t0.txt=\"刷卡情况：刷卡成功\r\n\"");
			/* ID */
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"ID：\"");
			Display_Screen_Write_Custom(&P->data.name[0]);
			/* 身份 */
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n您的身份是：\"");
			if(P->data.permission == AUTHORITY_USER) //普通用户
			{
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"普通用户\"");
			}
			else if(P->data.permission == AUTHORITY_ADMIN) //管理员
			{
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员\"");
			}
			else if(P->data.permission == AUTHORITY_ROOT) //超级用户
			{
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"超级用户\"");
			}
			else if(P->data.permission == AUTHORITY_NO) //无权限
			{
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"无权限\"");

				/* 打卡情况 */
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡情况：打卡失败\"");
				/* 打卡时间 */
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡时间：无\"");

				//等待一小会，显示打卡页面情况
				usleep(2000000);

				//串口屏 返回 main 界面
				Display_Screen_Write((hi_u8 *)"page main");

				return;
			}
			else
			{
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"Other\"");
			}

			if( ( \
					(Sys_Time.sys_time_hours < ScanCard_Time.morning_time_hours) || \
					((Sys_Time.sys_time_hours == ScanCard_Time.morning_time_hours) && (Sys_Time.sys_time_minutes < ScanCard_Time.morning_time_minutes)) || \
					((Sys_Time.sys_time_hours == ScanCard_Time.morning_time_hours) && (Sys_Time.sys_time_minutes == ScanCard_Time.morning_time_minutes) && (Sys_Time.sys_time_seconds <= ScanCard_Time.morning_time_seconds)) \
				) || \
				( \
					(Sys_Time.sys_time_hours > ScanCard_Time.afternoon_time_hours) || \
					((Sys_Time.sys_time_hours == ScanCard_Time.afternoon_time_hours) && (Sys_Time.sys_time_minutes > ScanCard_Time.afternoon_time_minutes)) || \
					((Sys_Time.sys_time_hours == ScanCard_Time.afternoon_time_hours) && (Sys_Time.sys_time_minutes == ScanCard_Time.afternoon_time_minutes) && (Sys_Time.sys_time_seconds >= ScanCard_Time.afternoon_time_seconds)) \
				) \
			  )
			{
				/* 打卡情况 */
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡情况：打卡成功\"");
				/* 打卡时间 */
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡时间：\"");
				sprintf((char *)str, "%d/%d/%d,%d:%d:%d", Sys_Time.sys_time_years, Sys_Time.sys_time_months, Sys_Time.sys_time_days,
														Sys_Time.sys_time_hours, Sys_Time.sys_time_minutes, Sys_Time.sys_time_seconds);
				Display_Screen_Write_Custom(str);

				//保留(记录)考勤信息
				ScanRecord_Info[record_num].record_time_years   = Sys_Time.sys_time_years;
				ScanRecord_Info[record_num].record_time_months  = Sys_Time.sys_time_months;
				ScanRecord_Info[record_num].record_time_days    = Sys_Time.sys_time_days;
				ScanRecord_Info[record_num].record_time_hours   = Sys_Time.sys_time_hours;
				ScanRecord_Info[record_num].record_time_minutes = Sys_Time.sys_time_minutes;
				ScanRecord_Info[record_num].record_time_seconds = Sys_Time.sys_time_seconds;
				for(i=0;i<NAME_BYTE_LEN;i++)
				{
					ScanRecord_Info[record_num].name[i] = P->data.name[i];
				}
				ScanRecord_Info[record_num].authority = P->data.permission;
				ScanRecord_Info[record_num].id = P->data.userid;

				/* MQTT 消息队列发布消息到 MQTT 线程 */
				sprintf((char *)str, "ID:%s,Identity:%d,Time:%d/%d/%d %d:%d:%d", &P->data.name[0], P->data.permission,
														Sys_Time.sys_time_years, Sys_Time.sys_time_months, Sys_Time.sys_time_days,
														Sys_Time.sys_time_hours, Sys_Time.sys_time_minutes, Sys_Time.sys_time_seconds);
				app_msg = malloc(sizeof(app_msg_t));
				if(app_msg != NULL)
				{
					app_msg->msg_type = en_msg_report; //消息类型: 报告
					// app_msg->msg.report.scanRecord = &str[0];
					sprintf((char *)app_msg->msg.report.scanRecord, "%s", str);

					if (0 != osMessageQueuePut(mid_MsgQueue, &app_msg, 0U, 0U))
					{
						free(app_msg);
					}
					printf("MQTT MessageQueue Put success.\r\n");
				}
				else
				{
					printf("MQTT MessageQueue Put fail.\r\n");
				}

				record_num = record_num + 1; //记录record自增1

				if(record_num >= 50) //最多50条记录，下标：0-49
				{
					record_num = 0;
				}
			}
			else
			{
				/* 打卡超时: 打卡失败 */
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡情况：打卡失败\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡超时 或 未到打卡时间\"");
			}
		}

		//等待一小会，显示打卡页面情况
		usleep(2000000);

		//串口屏 返回 main 界面
		Display_Screen_Write((hi_u8 *)"page main");
	}
}

//每页显示的信息数量，每页可显示5条信息
#define RECORD_ONE_PAGE_MAX 5
// 打印刷卡记录
// record_start_index : 要打印的起始位置+1，索引前要减去1，因为数组下标是0开始
// num : 打印的数量
void printf_ScanRecord(unsigned char record_start_index,unsigned char num)
{
	unsigned char i;
	unsigned char str[50] = {0};
	unsigned char index;

	// 先清空 t0.txt 的内容，再继续打印刷卡记录
	Display_Screen_Write((hi_u8 *)"t0.txt=\"\"");

	for(i=0;i<num;i++)
	{
		index = i+record_start_index;

		sprintf((char *)str, "%d.", index+1);
		Display_Screen_Write_Custom(str);

		sprintf((char *)str, "time=%d年%d月%d日%d时%d分%d秒,\r\n", ScanRecord_Info[index].record_time_years, ScanRecord_Info[index].record_time_months,  ScanRecord_Info[index].record_time_days,
															  ScanRecord_Info[index].record_time_hours, ScanRecord_Info[index].record_time_minutes, ScanRecord_Info[index].record_time_seconds);
		Display_Screen_Write_Custom(str);

		sprintf((char *)str, "name=%s\r\n",ScanRecord_Info[index].name);
		Display_Screen_Write_Custom(str);
		
		if(ScanRecord_Info[index].authority == AUTHORITY_USER) //普通用户
		{
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限=普通用户,\"");
		}
		else if(ScanRecord_Info[index].authority == AUTHORITY_ADMIN) //管理员
		{
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限=管理员,\"");
		}
		else if(ScanRecord_Info[index].authority == AUTHORITY_ROOT) //超级用户
		{
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限=超级用户,\"");
		}
		else if(ScanRecord_Info[index].authority == AUTHORITY_NO) //无权限
		{
			Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限=无权限,\"");
		}
		else
		{}

		sprintf((char *)str, "id=%u\r\n",ScanRecord_Info[index].id); //%d:按int格式输入或输出10进制数据   %u:按unsigned int格式输入或输出10进制数据
		Display_Screen_Write_Custom(str);
	}
}

#define MIN(a,b) ((a)<(b)?(a):(b))

// 刷卡记录
#ifdef DISPLAY_SCREEN_SCANRECORD
void Scan_Record(void)
{
	unsigned char Rxdata[50] = {0};
	unsigned int Rxdata_len;
	char ret;
	unsigned char str[50] = {0};
	unsigned char i;
	unsigned char page_num = (record_num + RECORD_ONE_PAGE_MAX - 1)/RECORD_ONE_PAGE_MAX; //页数
	unsigned char page_index; // 此时页编号(索引)
	unsigned char record_num_tmp;

	printf("Scan_Record\r\n");
	//切换到 record 界面  考勤记录
	Display_Screen_Write((hi_u8 *)"page record");

	//等待一小会，等串口屏刷新完页面
	usleep(500000);

	/* 打印第一页的考勤记录到串口屏 --- start */
	if(record_num > 0) //至少一条记录
	{
		//第一页
		page_index = 1;

		// 打印第一页的内容
		// 如果 0 < record_num < 5, 打印 record_num 条记录
		// 如果     record_num >= 5,打印 RECORD_ONE_PAGE_MAX = 5 条记录
		printf_ScanRecord(0, MIN(record_num, RECORD_ONE_PAGE_MAX));
	}
	else //一条记录都没有
	{
		Display_Screen_Write((hi_u8 *)"t0.txt+=\"无\"");
	}
	/* 打印第一页的考勤记录到串口屏 --- end */

	while(1)
	{
		//接收串口屏指令消息
		ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
		if(ret == 0)
		{
			//返回主界面
			if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
			{
				printf(DISPLAY_SCREEN_DEBUG "return\r\n");
				//切换到 main 界面
				Display_Screen_Write((hi_u8 *)"page main");

				break;
			}
			//下一页
			else if(strncmp((const char *)Rxdata, (const char *)"next_page", Rxdata_len) == 0) //接收字符串 "return"
			{
				printf(DISPLAY_SCREEN_DEBUG "next_page\r\n");

				if(page_num > 1) //不止一页的记录，大于等于6条以上的记录
				{
					// 第 2--page_num 页
					page_index++; //页编号加1
					if(page_index >= page_num)
					{
						page_index = page_num; //最后一页
						// 隐藏“下一页”的按钮
						Display_Screen_Write((hi_u8 *)"vis b2,0");
					}

					record_num_tmp = (page_index - 1)*RECORD_ONE_PAGE_MAX; //如果是第二页6条记录，就是 1页*5条 = 5 条记录，为第二页的起始位置(index = 5)
					printf_ScanRecord(record_num_tmp, MIN(record_num - record_num_tmp, RECORD_ONE_PAGE_MAX));

					// 显示“上一页”的按钮
					Display_Screen_Write((hi_u8 *)"vis b1,1");
				}
				else //只有一页，5条以内的记录
				{}
			}
			//上一页
			else if(strncmp((const char *)Rxdata, (const char *)"previous_page", Rxdata_len) == 0) //接收字符串 "return"
			{
				printf(DISPLAY_SCREEN_DEBUG "previous_page\r\n");

				page_index--; //页编号减1
				if(page_index <= 1) //第一页
				{
					page_index = 1; //第一页
					// 隐藏“上一页”的按钮
					Display_Screen_Write((hi_u8 *)"vis b1,0");
				}
				else
				{}
				record_num_tmp = (page_index - 1)*RECORD_ONE_PAGE_MAX; //如果是第二页6条记录，就是 1页*5条=5条记录，为第二页的起始位置(index = 5)
				printf_ScanRecord(record_num_tmp, RECORD_ONE_PAGE_MAX); //有上一页，表明前一页一定占满有 RECORD_ONE_PAGE_MAX=5 条记录

				// 显示“下一页”的按钮
				Display_Screen_Write((hi_u8 *)"vis b2,1");
			}
			else
			{}
		}

		printf("wait......\r\n");
		usleep(1000000);
	}
}
#endif

//添加用户
#ifdef DISPLAY_SCREEN_ADDUSER
extern hi_u8 g_tf_pdata[TEST_SIZE];
extern hi_u8 g_tf_pdata_back[TEST_SIZE];
void Add_Card(void)
{
	BrushCardStatus brushCard_Statu;
    unsigned int user_id;
	// 加大接收长度30->60：来自串口屏的数据，才不会导致系统接收完okforever...name...(太长)之后溢出复位。
	/* Rxdata[60] = {0}; */ //初始化为0，后面串口接收完成也要清空Rxdata，这样才不会后面的部分数据是乱的。
	unsigned char Rxdata[60] = {0};
	unsigned int Rxdata_len;
	char ret;
	unsigned char i;
	char *ptr = NULL;
	AuthorityStatus authority_Statu;
	UserInfo add_user;

	printf("Add_Card\r\n");

	//用户数已满
	if(g_user_num >= USER_NUM_MAX)
	{
		Display_Screen_Write((hi_u8 *)"page white_board");
		//等待一小会，等串口屏刷新完页面
		usleep(500000);
		Display_Screen_Write((hi_u8 *)"vis b0,0");

		//串口屏 "数据库已满，请扩容。"
		// Display_Screen_Write((hi_u8 *)"t0.txt=\"The database is full, please enlarge it.\"");
		Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
		Display_Screen_Write((hi_u8 *)"t0.txt+=\"数据库已满，请扩容。\r\n\"");
		Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

		usleep(DISPLAY_TIME);

		//串口屏 返回 main 界面
		Display_Screen_Write((hi_u8 *)"page main");

		return;
	}

	//切换到 adduser 界面  添加用户
	Display_Screen_Write((hi_u8 *)"page adduser");

	//等待一小会，等串口屏刷新完页面
	usleep(500000);

	//管理员 和 超级用户 都允许
	//串口屏 "添加用户前需管理员通过，请使用管理员卡。"
	// Display_Screen_Write((hi_u8 *)"t0.txt=\"Administrator is required before adding user. Please use admin card.\"");
	Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
	Display_Screen_Write((hi_u8 *)"t0.txt+=\"添加用户前需管理员通过，请使用管理员卡。\r\n\"");

	// 隐藏控件
	Display_Screen_Write((hi_u8 *)"vis t2,0");
	Display_Screen_Write((hi_u8 *)"vis t1,0");
	Display_Screen_Write((hi_u8 *)"vis r0,0");
	Display_Screen_Write((hi_u8 *)"vis r1,0");
	Display_Screen_Write((hi_u8 *)"vis t7,0");
	Display_Screen_Write((hi_u8 *)"vis t8,0");
	Display_Screen_Write((hi_u8 *)"vis n0,0");
	Display_Screen_Write((hi_u8 *)"vis n1,0");
	Display_Screen_Write((hi_u8 *)"vis n2,0");
	Display_Screen_Write((hi_u8 *)"vis t4,0");
	Display_Screen_Write((hi_u8 *)"vis t5,0");
	Display_Screen_Write((hi_u8 *)"vis t6,0");
	Display_Screen_Write((hi_u8 *)"r0.val=1");
	Display_Screen_Write((hi_u8 *)"r1.val=0");
	Display_Screen_Write((hi_u8 *)"vis b0,0");

	while(1)
	{
		brushCard_Statu = RC522_FindCard(&user_id); //管理员 超级用户的 ID
        if(brushCard_Statu == BRUSH_FIND)
        {
			printf(RC522_DEBUG "BRUSH_FIND\r\n");
            printf("user_id = [%u]\r\n", user_id);

			authority_Statu = Card_Is_Database(user_id);
			if((authority_Statu != AUTHORITY_ADMIN) && (authority_Statu != AUTHORITY_ROOT)) //刷卡的不是管理员，也不是超级用户
			{
				// 此卡不是管理员，正在退出。
				printf(DISPLAY_SCREEN_DEBUG "This card is not an administrator and is exiting.\r\n");
				printf(DISPLAY_SCREEN_DEBUG "Exiting......\r\n\r\n");

				//串口屏 "此卡不是管理员，正在退出。"
				// Display_Screen_Write((hi_u8 *)"t0.txt=\"This card is not an administrator and is exiting.\"");
				Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡不是管理员，正在退出。\r\n\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

				usleep(DISPLAY_TIME);

				//串口屏 返回 main 界面
				Display_Screen_Write((hi_u8 *)"page main");

				break;
			}
			else //管理员或者超级用户
			{
				//串口屏 "管理员刷卡成功。"
				// Display_Screen_Write((hi_u8 *)"t0.txt=\"Administrator brush card successfully.\"");
				Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员/超级用户刷卡成功。\r\n\"");
				//串口屏 "请刷一张新卡。"
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"请刷一张新卡。\r\n\"");

				usleep(DISPLAY_TIME);

				while(1)
				{
					brushCard_Statu = RC522_FindCard(&user_id); //新用户的 ID
					if(brushCard_Statu == BRUSH_FIND)
					{
						authority_Statu = Card_Is_Database(user_id);
						if(authority_Statu != AUTHORITY_NONE) //不是新用户，已在数据库中
						{
							//串口屏 "已在数据库中，添加失败。"
							// Display_Screen_Write((hi_u8 *)"t0.txt=\"It is already in the database, please brush the card again.\"");
							Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"已在数据库中，添加失败。\r\n\"");
							
							usleep(DISPLAY_TIME);

							Display_Screen_Write((hi_u8 *)"page main");

							return;
						}
						else //AUTHORITY_NONE 未添加的新用户，添加到数据库链表尾
						{
							//串口屏 "添加成功。"
							// Display_Screen_Write((hi_u8 *)"t0.txt=\"Brush successful.\"");
							Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"刷卡成功。\r\n\"");
							// Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\nPlease enter time limit.\"");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"请输入参数。\r\n\"");

							// 显示控件
							Display_Screen_Write((hi_u8 *)"vis t2,1");
							Display_Screen_Write((hi_u8 *)"vis t1,1");
							Display_Screen_Write((hi_u8 *)"vis r0,1");
							Display_Screen_Write((hi_u8 *)"vis r1,1");
							Display_Screen_Write((hi_u8 *)"vis t7,1");
							Display_Screen_Write((hi_u8 *)"vis t8,1");
							Display_Screen_Write((hi_u8 *)"vis b0,1");

							usleep(DISPLAY_TIME);

							while(1)
							{
								//接收串口屏 返回
								ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 100);
								if(ret == 0)
								{
									if(strstr((const char *)Rxdata, (const char *)"return") != NULL) //成功接收字符串 "return"
									{
										printf(DISPLAY_SCREEN_DEBUG "return\r\n");
										Display_Screen_Write((hi_u8 *)"page main");

										return;
									}
									else if(strstr((const char *)Rxdata, (const char *)"ok") != NULL) //成功接收字符串 "ok"
									{
										//ID
										add_user.userid = user_id;
										//name
										for(i=0;i<NAME_BYTE_LEN;i++)
										{
											add_user.name[i] = '\0';
										}
										
										//permission
										add_user.permission = AUTHORITY_USER; //新用户默认权限为：普通用户
										add_user.permission_last = AUTHORITY_NO; //在数据库中，但是没有权限。如果是永久则用不到；如果不是永久，等期限过了就会变为无权限。

										add_user.permission_time_is_forever = YES_YES; //权限默认永久生效
										add_user.permission_time_hours = 255;
										add_user.permission_time_minutes = 255;
										add_user.permission_time_seconds = 255;

										//刷卡(打卡)时间
										add_user.scancard_time_is_same = YES_YES, //与系统相同
										add_user.morning_time_hours = 255;
										add_user.morning_time_minutes = 255;
										add_user.morning_time_seconds = 255;
										add_user.afternoon_time_hours = 255;
										add_user.afternoon_time_minutes = 255;
										add_user.afternoon_time_seconds = 255;

										//name
										if((ptr = strstr((const char *)Rxdata, (const char *)"forever=1")) != NULL) //永久期限
										{
											add_user.permission_time_is_forever = YES_YES;
											sprintf((char *)&add_user.name[0], "%s", &ptr[14]);

											ptr = NULL;

											printf("add_user.permission_time_is_forever=%d\r\n", YES_YES);
											printf("add_user.name=%s\r\n", add_user.name);
										}
										else if((ptr = strstr((const char *)Rxdata, (const char *)"forever=0")) != NULL) //设置期限
										{
											add_user.permission_time_is_forever = NO_NO;
											add_user.permission_time_hours = *(ptr+11);
											add_user.permission_time_minutes = *(ptr+17);
											add_user.permission_time_seconds = *(ptr+23);
											sprintf((char *)&add_user.name[0], "%s", &ptr[32]);

											ptr = NULL;

											printf("add_user.permission_time_is_forever=%d\r\n", NO_NO);
											printf("add_user.permission_time_hours=%d\r\n", add_user.permission_time_hours);
											printf("add_user.permission_time_minutes=%d\r\n", add_user.permission_time_minutes);
											printf("add_user.permission_time_seconds=%d\r\n", add_user.permission_time_seconds);
											printf("add_user.name=%s\r\n", add_user.name);
										}

										Insert(&add_user, RC522_Database); //将新用户添加到数据库中
										g_user_num++;

										/* 保存进Flash */
										// 每次重新写入相同的地址需要提前擦除
										hi_flash_erase(FLASH_USERINFO_OFFSET, 4096); //擦除保存用户信息的区域
										hi_flash_erase(FLASH_USERINFO_USER_NUM, 4096); //擦除保存用户数量的区域

										Flash_Write(FLASH_USERINFO_OFFSET, RC522_Database, g_user_num, HI_TRUE); //HI_TRUE: 需要擦除重写

										printf("Add successful.\r\n");
										printf("Exiting......\r\n");

										// usleep(500000);

										//串口屏 "添加成功。"
										// Display_Screen_Write((hi_u8 *)"t0.txt=\"Add successful.\"");
										Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
										Display_Screen_Write((hi_u8 *)"t0.txt+=\"添加成功。\r\n\"");
										Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

										usleep(DISPLAY_TIME);

										//串口屏 返回 main 界面
										Display_Screen_Write((hi_u8 *)"page main");
										Display_Screen_Write((hi_u8 *)"adduser.r0.val=1");
										Display_Screen_Write((hi_u8 *)"adduser.r1.val=0");
										Display_Screen_Write((hi_u8 *)"adduser.t1.txt=\"\""); // 清空name区域

										// usleep(500000);

										return;
									}
									else
									{
										;
									}
									memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
								}

								printf("wait......\r\n");
								usleep(1000000);
							}
						}
					}
					else
					{
						printf(RC522_DEBUG "BRUSH_NONE\r\n");
					}

					//接收串口屏 返回
					ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
					if(ret == 0)
					{
						if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
						{
							printf(DISPLAY_SCREEN_DEBUG "return\r\n");
							Display_Screen_Write((hi_u8 *)"page main");

							return;
						}
						memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
					}

					printf("wait......\r\n");
					usleep(1000000);
				}
			}
		}
		else
		{
			printf(RC522_DEBUG "BRUSH_NONE\r\n");
		}

		//接收串口屏 返回
		ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50); //50ms
		if(ret == 0)
		{
			if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
			{
				printf(DISPLAY_SCREEN_DEBUG "return\r\n");
				Display_Screen_Write((hi_u8 *)"page main");

				break;
			}
			memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
		}

		printf("wait......\r\n");
		usleep(1000000);
	}
}
#endif

//删除用户
#ifdef DISPLAY_SCREEN_DELUSER
void Del_Card(void)
{
	BrushCardStatus brushCard_Statu;
    unsigned int user_id;
	unsigned char Rxdata[50] = {0};
	unsigned int Rxdata_len;
	char ret;
	AuthorityStatus authority_Statu;
	UserInfo del_user;   //待删除的用户信息
	UserInfo admin_user; //管理者

	printf("Del_Card\r\n");

	//用户数为1：超级用户不可删除
	if(g_user_num <= 1)
	{
		Display_Screen_Write((hi_u8 *)"page white_board");
		//等待一小会，等串口屏刷新完页面
		usleep(500000);
		Display_Screen_Write((hi_u8 *)"vis b0,0");

		//串口屏 "数据库已空，不可删除。"
		// Display_Screen_Write((hi_u8 *)"t0.txt=\"The database is empty and cannot be deleted.\"");
		Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
		Display_Screen_Write((hi_u8 *)"t0.txt+=\"数据库已空，不可删除。\r\n\"");
		Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

		usleep(DISPLAY_TIME);

		//串口屏 返回 main 界面
		Display_Screen_Write((hi_u8 *)"page main");

		return;
	}

	//切换到 adduser 界面  删除用户
	Display_Screen_Write((hi_u8 *)"page deluser");

	//等待一小会，等串口屏刷新完页面
	usleep(500000);
	//串口屏 "删除用户前需管理员通过，请使用管理员卡。"
	Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
	// Display_Screen_Write((hi_u8 *)"t0.txt+=\"Administrator is required before deleting user. Please use admin card.\"");
	Display_Screen_Write((hi_u8 *)"t0.txt+=\"删除用户前需管理员/超级用户通过，请使用管理员/超级用户卡。\r\n\"");

	while (1)
	{
		brushCard_Statu = RC522_FindCard(&user_id);
        if(brushCard_Statu == BRUSH_FIND)
        {
			printf(RC522_DEBUG "BRUSH_FIND\r\n");
            printf("user_id = [%u]\r\n", user_id);

			authority_Statu = Card_Is_Database(user_id);
			if((authority_Statu != AUTHORITY_ADMIN) && (authority_Statu != AUTHORITY_ROOT)) //刷卡的不是管理员，也不是超级用户
			{
				// 此卡不是管理员，正在退出。
				printf(DISPLAY_SCREEN_DEBUG "This card is not an administrator and is exiting.\r\n");
				printf(DISPLAY_SCREEN_DEBUG "Exiting......\r\n\r\n");

				//串口屏 "此卡不是管理员，正在退出。"
				Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
				// Display_Screen_Write((hi_u8 *)"t0.txt=\"This card is not an administrator and is exiting.\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡不是管理员/超级用户，正在退出。\r\n\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

				usleep(DISPLAY_TIME);

				//串口屏 返回 main 界面
				Display_Screen_Write((hi_u8 *)"page main");

				break;
			}
			else //管理员或者超级用户
			{
				admin_user.permission = authority_Statu; //管理者的权限可能是：管理员 或者 超级用户

				//串口屏 "管理员刷卡成功。"
				Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
				// Display_Screen_Write((hi_u8 *)"t0.txt=\"Administrator brush card successfully.\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员/超级用户刷卡成功。\r\n\"");
				//串口屏 "请刷需要删除的卡。"
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"请刷需要删除的卡。\r\n\"");

				usleep(DISPLAY_TIME);

				while(1)
				{
					brushCard_Statu = RC522_FindCard(&user_id);
					if(brushCard_Statu == BRUSH_FIND)
					{
						authority_Statu = Card_Is_Database(user_id);
						if(authority_Statu == AUTHORITY_NONE) //新用户，不在数据库中，无法删除，请重新刷卡
						{
							//串口屏 刷新 deluser 界面
							Display_Screen_Write((hi_u8 *)"t0.txt=\"\"");
							Display_Screen_Write((hi_u8 *)"page deluser");

							//串口屏 "不在数据库中，无法删除，请重新刷卡。"
							Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
							// Display_Screen_Write((hi_u8 *)"t0.txt+=\"It is not in database, cannot be deleted, please brush the card again.\"");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡不在数据库中，无法删除，请重新刷卡。\r\n\"");

							usleep(500000);
						}
						else if(authority_Statu == AUTHORITY_ROOT) //超级用户，无法删除，请重新刷卡
						{
							//串口屏 刷新 deluser 界面
							Display_Screen_Write((hi_u8 *)"t0.txt=\"\"");
							Display_Screen_Write((hi_u8 *)"page deluser");

							//串口屏 "超级用户，无法删除，请重新刷卡。"
							Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
							// Display_Screen_Write((hi_u8 *)"t0.txt=\"This user is <root>, cannot be deleted, please brush the card again.\"");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡是超级用户，无法删除，请重新刷卡。\r\n\"");
						}
						else //删除的是：没有权限的卡 或者 普通用户 或者 管理员
						{
							del_user.userid = user_id;
							del_user.permission = authority_Statu; //待删除的用户可能是：普通用户 或者 管理员

							if(admin_user.permission > del_user.permission) //管理者的权限 大于 待删除的用户
							{
								Delete(&del_user, RC522_Database);
								g_user_num--;

								/* 保存进Flash */
								// 每次重新写入相同的地址需要提前擦除
								hi_flash_erase(FLASH_USERINFO_OFFSET, 4096); //擦除保存用户信息的区域
								hi_flash_erase(FLASH_USERINFO_USER_NUM, 4096); //擦除保存用户数量的区域

								Flash_Write(FLASH_USERINFO_OFFSET, RC522_Database, g_user_num, HI_TRUE); //HI_TRUE: 需要擦除重写

								//串口屏 "删除成功。"
								Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
								Display_Screen_Write((hi_u8 *)"t0.txt+=\"删除成功。\r\n\"");
								Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

								usleep(DISPLAY_TIME);

								//串口屏 返回 main 界面
								Display_Screen_Write((hi_u8 *)"page main");

								return;
							}
							else //管理者的权限 不大于 待删除的用户，不允许删除，删除失败
							{
								//串口屏 "删除失败。"
								Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
								Display_Screen_Write((hi_u8 *)"t0.txt+=\"删除失败。\r\n\"");
								Display_Screen_Write((hi_u8 *)"t0.txt+=\"此用户的权限需小于验证用户\r\n\"");
								Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

								usleep(DISPLAY_TIME);

								//串口屏 返回 main 界面
								Display_Screen_Write((hi_u8 *)"page main");

								return;
							}
						}
					}
					else
					{
						printf(RC522_DEBUG "BRUSH_NONE\r\n");
					}

					//接收串口屏 返回
					ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
					if(ret == 0)
					{
						if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
						{
							printf(DISPLAY_SCREEN_DEBUG "return\r\n");
							Display_Screen_Write((hi_u8 *)"page main");

							return;
						}
					}

					printf("wait......\r\n");
					usleep(1000000);
				}
			}
		}
		else
		{
			printf(RC522_DEBUG "BRUSH_NONE\r\n");
		}

		//接收串口屏 返回
		ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
		if(ret == 0)
		{
			if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
			{
				printf(DISPLAY_SCREEN_DEBUG "return\r\n");
				Display_Screen_Write((hi_u8 *)"page main");

				break;
			}
		}

		printf("wait......\r\n");
		usleep(1000000);
	}
}
#endif

//登录时长
#ifdef DISPLAY_SCREEN_LOGIN
void Login_Card(void)
{
	BrushCardStatus brushCard_Statu;
    unsigned int user_id;
	unsigned char Rxdata[50] = {0};
	unsigned int Rxdata_len;
	char ret;
	char *ptr = NULL;
	AuthorityStatus authority_Statu;
	UserInfo login_time_user;
	UserInfo admin_user;
	LinkList P;

	printf("Login_Card\r\n");

	//等待一小会，等串口屏刷新完页面
	usleep(500000);
	//管理员 和 超级用户 都允许
	//串口屏 "设置用户登录时间限制前需管理员通过，请使用管理员卡。"
	Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
	Display_Screen_Write((hi_u8 *)"t0.txt+=\"设置用户登录时间限制前需管理员通过，请使用管理员卡。\"");

	while(1)
	{
		brushCard_Statu = RC522_FindCard(&user_id);
        if(brushCard_Statu == BRUSH_FIND)
        {
			printf(RC522_DEBUG "BRUSH_FIND\r\n");
            printf("user_id = [%u]\r\n", user_id);

			authority_Statu = Card_Is_Database(user_id);
			if((authority_Statu == AUTHORITY_NO) || (authority_Statu == AUTHORITY_USER)) //刷卡的是：不在数据库中的 和 普通用户
			{
				// 此卡不是管理员，正在退出。
				printf(DISPLAY_SCREEN_DEBUG "This card is not an administrator and is exiting.\r\n");
				printf(DISPLAY_SCREEN_DEBUG "Exiting......\r\n\r\n");

				//串口屏 "此卡不是管理员，正在退出。"
				Display_Screen_Write((hi_u8 *)"t0.txt=\"Login time limit setting:\"\r\n");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"This card is not an administrator and is exiting.\"\r\n");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\"");

				usleep(DISPLAY_TIME);

				//串口屏 返回 main 界面
				Display_Screen_Write((hi_u8 *)"page main");

				break;
			}
			else //管理员或者超级用户
			{
				//串口屏 "管理员刷卡成功。"
				Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员刷卡成功。\"\r\n");
				//串口屏 "请选择要设置时间限制的用户卡。"
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"请选择要设置时间限制的用户卡。\"");

				usleep(DISPLAY_TIME);

				admin_user.permission = authority_Statu; //管理员 或者 超级用户 的权限

				while(1)
				{
					brushCard_Statu = RC522_FindCard(&user_id);
					if(brushCard_Statu == BRUSH_FIND)
					{
						authority_Statu = Card_Is_Database(user_id);

						login_time_user.userid = user_id;  //待操作的数据库中存在的用户 可普通用户 或者 管理员
						login_time_user.permission = authority_Statu; //待操作用户的权限

						if(login_time_user.permission == AUTHORITY_NO) //新用户，不在数据库中，请重新刷卡
						{
							//串口屏 刷新 login 界面
							Display_Screen_Write((hi_u8 *)"t0.txt=\"\"");
							Display_Screen_Write((hi_u8 *)"page login");

							//串口屏 "不在数据库中，请重新刷卡。"
							Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"不在数据库中，请重新刷卡。\"");
						}
						else if(login_time_user.permission < admin_user.permission) //待操作的用户(普通用户 管理员)权限 小于 管理员(管理员 超级用户)
						{
							//串口屏 "刷卡成功。"
							Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"刷卡成功。\"\r\n");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"请输入限制登录时间：\"");

							usleep(DISPLAY_TIME);

							while(1)
							{
								//接收串口屏 返回
								ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
								if(ret == 0)
								{
									if(strstr((const char *)Rxdata, (const char *)"return") != NULL) //成功接收字符串 "return"
									{
										printf(DISPLAY_SCREEN_DEBUG "return\r\n");

										return;
									}
									else if(strstr((const char *)Rxdata, (const char *)"ok") != NULL) //成功接收字符串 "ok"
									{
										if(strstr((const char *)Rxdata, (const char *)"forever=1") != NULL) //永久期限
										{
											login_time_user.time_is_forever = FOREVER_YES;

											printf("login_time_user.time_is_forever=%d\r\n", FOREVER_YES);

											if(login_time_user.permission == AUTHORITY_ADMIN) //待操作的用户为管理员，不允许被永久提升为超级用户，只能有时间限制的升级
											{
												printf("Failed to promote permission\r\n");
												printf("Exiting......\r\n");

												//串口屏 "提升权限失败。"
												Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
												Display_Screen_Write((hi_u8 *)"t0.txt+=\"提升权限失败。\"\r\n");
												Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\"");

												usleep(DISPLAY_TIME);

												//串口屏 返回 main 界面
												Display_Screen_Write((hi_u8 *)"page main");
												Display_Screen_Write((hi_u8 *)"login.r0.val=0"); //默认不永久生效
												Display_Screen_Write((hi_u8 *)"login.r1.val=1");

												return;
											}
										}
										else if((ptr = strstr((const char *)Rxdata, (const char *)"forever=0")) != NULL) //设置期限
										{
											login_time_user.time_is_forever = FOREVER_NO;
											login_time_user.time_hours = *(ptr+11);
											login_time_user.time_minutes = *(ptr+17);
											login_time_user.time_seconds = *(ptr+23);

											ptr = NULL;

											printf("login_time_user.time_is_forever=%d\r\n", FOREVER_NO);
											printf("login_time_user.time_hours=%d\r\n", login_time_user.time_hours);
											printf("login_time_user.time_minutes=%d\r\n", login_time_user.time_minutes);
											printf("login_time_user.time_seconds=%d\r\n", login_time_user.time_seconds);
										}

										P = Find(&login_time_user, RC522_Database);
										if(P != NULL)
										{
											P->data.permission = login_time_user.permission + 1; //升级权限
										}

										printf("Login time limit setting successful.\r\n");
										printf("Exiting......\r\n");

										//串口屏 "操作成功。"
										Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
										Display_Screen_Write((hi_u8 *)"t0.txt+=\"操作成功。\"\r\n");
										Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\"");

										usleep(DISPLAY_TIME);

										//串口屏 返回 main 界面
										Display_Screen_Write((hi_u8 *)"page main");
										Display_Screen_Write((hi_u8 *)"login.r0.val=0"); //默认不永久生效
										Display_Screen_Write((hi_u8 *)"login.r1.val=1");

										return;
									}
								}

								printf("wait......\r\n");
								usleep(1000000);
							}
						}
					}
					else
					{
						printf(RC522_DEBUG "BRUSH_NONE\r\n");
					}

					//接收串口屏 返回
					ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
					if(ret == 0)
					{
						if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
						{
							printf(DISPLAY_SCREEN_DEBUG "return\r\n");

							return;
						}
					}

					printf("wait......\r\n");
					usleep(1000000);
				}
			}
		}
		else
		{
			printf(RC522_DEBUG "BRUSH_NONE\r\n");
		}

		//接收串口屏 返回
		ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50); //50ms
		if(ret == 0)
		{
			if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
			{
				printf(DISPLAY_SCREEN_DEBUG "return\r\n");
				break;
			}
		}

		printf("wait......\r\n");
		usleep(1000000);
	}
}
#endif

//权限管理
#ifdef DISPLAY_SCREEN_PERMISSION
void Permission_Card(void)
{
	BrushCardStatus brushCard_Statu;
    unsigned int user_id;
	unsigned char Rxdata[50] = {0};
	unsigned int Rxdata_len;
	char ret;
	char *ptr = NULL;
	AuthorityStatus authority_Statu;
	UserInfo admin_user;  //管理者（管理员 或者 超级用户）
	UserInfo operate_user;   //待操作权限的用户信息
	LinkList P;

	printf("Permission_Card\r\n");

	//切换到 permission 界面  权限管理
	Display_Screen_Write((hi_u8 *)"page permission");

	//等待一小会，等串口屏刷新完页面
	usleep(500000);
	//串口屏 "删除用户前需管理员通过，请使用管理员卡。"
	Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
	// Display_Screen_Write((hi_u8 *)"t0.txt+=\"Administrator is required before deleting user. Please use admin card.\"");
	Display_Screen_Write((hi_u8 *)"t0.txt+=\"请使用管理员/超级用户卡。\r\n\"");

	// 隐藏控件
	Display_Screen_Write((hi_u8 *)"vis r0,0");
	Display_Screen_Write((hi_u8 *)"vis r1,0");
	Display_Screen_Write((hi_u8 *)"vis r2,0");
	Display_Screen_Write((hi_u8 *)"vis r3,0");
	Display_Screen_Write((hi_u8 *)"vis r4,0");
	Display_Screen_Write((hi_u8 *)"vis t7,0");
	Display_Screen_Write((hi_u8 *)"vis t8,0");
	Display_Screen_Write((hi_u8 *)"vis t2,0");
	Display_Screen_Write((hi_u8 *)"vis t3,0");
	Display_Screen_Write((hi_u8 *)"vis t9,0");
	// Display_Screen_Write((hi_u8 *)"vis n0,0");
	Display_Screen_Write((hi_u8 *)"vis n1,0");
	Display_Screen_Write((hi_u8 *)"vis n2,0");
	Display_Screen_Write((hi_u8 *)"vis n3,0");
	// Display_Screen_Write((hi_u8 *)"vis t4,0");
	Display_Screen_Write((hi_u8 *)"vis t5,0");
	Display_Screen_Write((hi_u8 *)"vis t6,0");
	Display_Screen_Write((hi_u8 *)"vis t1,0");
	Display_Screen_Write((hi_u8 *)"vis b0,0");

	while(1)
	{
		brushCard_Statu = RC522_FindCard(&user_id);
        if(brushCard_Statu == BRUSH_FIND)
        {
			printf(RC522_DEBUG "BRUSH_FIND\r\n");
            printf("user_id = [%u]\r\n", user_id);

			authority_Statu = Card_Is_Database(user_id);
			if((authority_Statu != AUTHORITY_ADMIN) && (authority_Statu != AUTHORITY_ROOT)) //刷卡的不是管理员，也不是超级用户
			{
				// 此卡不是管理员，正在退出。
				printf(DISPLAY_SCREEN_DEBUG "This card is not an administrator and is exiting.\r\n");
				printf(DISPLAY_SCREEN_DEBUG "Exiting......\r\n\r\n");

				//串口屏 "此卡不是管理员，正在退出。"
				Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
				// Display_Screen_Write((hi_u8 *)"t0.txt=\"This card is not an administrator and is exiting.\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡不是管理员/超级用户卡。\r\n\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

				usleep(DISPLAY_TIME);

				//串口屏 返回 main 界面
				Display_Screen_Write((hi_u8 *)"page main");

				break;
			}
			else //管理员或者超级用户
			{
				admin_user.userid = user_id;
				admin_user.permission = authority_Statu; //管理者的权限可能是：管理员 或者 超级用户

				//串口屏 "管理员刷卡成功。"
				Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
				// Display_Screen_Write((hi_u8 *)"t0.txt=\"Administrator brush card successfully.\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员/超级用户刷卡成功。\r\n\"");
				//串口屏 "请刷需要操作权限的卡。"
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"请刷需要操作权限的卡。\r\n\"");

				usleep(DISPLAY_TIME);

				while(1)
				{
					brushCard_Statu = RC522_FindCard(&user_id); //新用户的 ID
					if(brushCard_Statu == BRUSH_FIND)
					{
						authority_Statu = Card_Is_Database(user_id);
						if(authority_Statu == AUTHORITY_NONE) //新用户，不在数据库中，操作失败
						{
							Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"不在数据库中，操作失败。\r\n\"");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
							
							usleep(DISPLAY_TIME);

							Display_Screen_Write((hi_u8 *)"page main");

							return;
						}
						else if(authority_Statu == AUTHORITY_ROOT)  //超级用户，不可操作
						{
							Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"超级用户不可操作，操作失败\r\n\"");
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
							
							usleep(DISPLAY_TIME);

							Display_Screen_Write((hi_u8 *)"page main");

							return;
						}
						else //AUTHORITY_NO AUTHORITY_USER AUTHORITY_ADMIN 没有权限 普通用户 管理员
						{
							operate_user.userid = user_id;
							operate_user.permission = authority_Statu;
							
							// 加1的原因：如果分别是管理员和普通用户，则不允许。因为管理员需要超级用户验证
							if(admin_user.permission > operate_user.permission) //管理者的权限 大于 待操作的用户
							{
								//串口屏 "操作权限的卡刷卡成功。"
								Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
								Display_Screen_Write((hi_u8 *)"t0.txt+=\"允许操作，请设置参数。\r\n\"");
								Display_Screen_Write((hi_u8 *)"t0.txt+=\"Wait......\r\n\"");

								usleep(DISPLAY_TIME);

								// 显示控件
								Display_Screen_Write((hi_u8 *)"vis r0,1");
								Display_Screen_Write((hi_u8 *)"vis r1,1");
								Display_Screen_Write((hi_u8 *)"vis r2,1");
								Display_Screen_Write((hi_u8 *)"vis r3,1");
								Display_Screen_Write((hi_u8 *)"vis r4,1");
								Display_Screen_Write((hi_u8 *)"vis t7,1");
								Display_Screen_Write((hi_u8 *)"vis t8,1");
								Display_Screen_Write((hi_u8 *)"vis t2,1");
								Display_Screen_Write((hi_u8 *)"vis t3,1");
								Display_Screen_Write((hi_u8 *)"vis t9,1");
								Display_Screen_Write((hi_u8 *)"vis b0,1");

								while(1)
								{
									ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
									if(ret == 0)
									{
										if(strstr((const char *)Rxdata, (const char *)"return") != NULL) //成功接收字符串 "return"
										{
											printf(DISPLAY_SCREEN_DEBUG "return\r\n");
											Display_Screen_Write((hi_u8 *)"page main");

											return;
										}
										else if(strstr((const char *)Rxdata, (const char *)"ok") != NULL) //成功接收字符串 "ok"
										{
											if((ptr = strstr((const char *)Rxdata, (const char *)"forever=1")) != NULL) //永久期限
											{
												P = Find(&operate_user, RC522_Database);

												P->data.permission_time_is_forever = YES_YES; //永久

												P->data.permission_last = P->data.permission; // 上一个权限
												// operate_user.permission_last = P->data.permission_last;

												if(*(ptr+11) == '1') // 无权限
												{
													P->data.permission = AUTHORITY_NO;
													// operate_user.permission = P->data.permission;
												}
												else if(*(ptr+11) == '2') // 普通用户
												{
													P->data.permission = AUTHORITY_USER;
													// operate_user.permission = P->data.permission;
												}
												else if(*(ptr+11) == '3') // 管理员用户
												{
													if(admin_user.permission == AUTHORITY_ROOT) //超级用户才允许设置管理员
													{
														P->data.permission = AUTHORITY_ADMIN;
														// operate_user.permission = P->data.permission;
														ptr = NULL;

													}
													else
													{
														Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
														Display_Screen_Write((hi_u8 *)"t0.txt+=\"不允许操作，请经过超级用户授权。\r\n\"");
														usleep(DISPLAY_TIME);

														//串口屏 返回 main 界面
														Display_Screen_Write((hi_u8 *)"page main");
														Display_Screen_Write((hi_u8 *)"permission.r0.val=1");
														Display_Screen_Write((hi_u8 *)"permission.r1.val=0");

														return;
													}
												}
												else{}

												ptr = NULL;

												printf("operate_user.permission_time_is_forever=%d\r\n", YES_YES);
												printf("operate_user.permission=%d\r\n", P->data.permission);
												printf("operate_user.permission_last=%d\r\n", P->data.permission_last);
											}
											else if((ptr = strstr((const char *)Rxdata, (const char *)"forever=0")) != NULL) //设置期限
											{
												P = Find(&operate_user, RC522_Database);

												P->data.permission_last = P->data.permission; // 上一个权限

												P->data.permission_time_is_forever = NO_NO;
												P->data.permission_time_hours = *(ptr+11);
												P->data.permission_time_minutes = *(ptr+17);
												P->data.permission_time_seconds = *(ptr+23);
												// P->data.permission_time_seconds = *(ptr+29);

												if(*(ptr+29) == '1') // 无权限
												{
													P->data.permission = AUTHORITY_NO;
												}
												else if(*(ptr+29) == '2') // 普通用户
												{
													P->data.permission = AUTHORITY_USER;
												}
												else if(*(ptr+29) == '3') // 管理员用户
												{
													P->data.permission = AUTHORITY_ADMIN;
												}
												else{}

												ptr = NULL;

												printf("operate_user.permission_time_is_forever=%d\r\n", NO_NO);
												printf("operate_user.permission=%d\r\n", P->data.permission);
												printf("operate_user.permission_last=%d\r\n", P->data.permission_last);
												printf("operate_user.permission_time_hours=%d\r\n", P->data.permission_time_hours);
												printf("operate_user.permission_time_minutes=%d\r\n", P->data.permission_time_minutes);
												printf("operate_user.permission_time_seconds=%d\r\n", P->data.permission_time_seconds);
											}

											/* 保存进Flash */
											// 每次重新写入相同的地址需要提前擦除
											hi_flash_erase(FLASH_USERINFO_OFFSET, 4096); //擦除保存用户信息的区域
											hi_flash_erase(FLASH_USERINFO_USER_NUM, 4096); //擦除保存用户数量的区域

											Flash_Write(FLASH_USERINFO_OFFSET, RC522_Database, g_user_num, HI_TRUE); //HI_TRUE: 需要擦除重写

											printf("Operate successful.\r\n");
											printf("Exiting......\r\n");

											//串口屏 "添加成功。"
											// Display_Screen_Write((hi_u8 *)"t0.txt=\"Add successful.\"");
											Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
											Display_Screen_Write((hi_u8 *)"t0.txt+=\"操作成功。\r\n\"");
											Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

											usleep(DISPLAY_TIME);

											//串口屏 返回 main 界面
											Display_Screen_Write((hi_u8 *)"page main");
											Display_Screen_Write((hi_u8 *)"permission.r0.val=1");
											Display_Screen_Write((hi_u8 *)"permission.r1.val=0");

											return;
										}
										else
										{
											;
										}
										memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
									}

									printf("wait......\r\n");
									usleep(1000000);
								}
							}
							else //管理者的权限 不大于 待操作的用户，不允许操作，操作失败
							{
								//串口屏 "操作失败。"
								Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
								Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限不够\r\n\"");
								Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

								usleep(DISPLAY_TIME);

								//串口屏 返回 main 界面
								Display_Screen_Write((hi_u8 *)"page main");

								return;
							}
						}
					}
					else
					{
						printf(RC522_DEBUG "BRUSH_NONE\r\n");
					}

					//接收串口屏 返回
					ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
					if(ret == 0)
					{
						if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
						{
							printf(DISPLAY_SCREEN_DEBUG "return\r\n");
							Display_Screen_Write((hi_u8 *)"page main");

							return;
						}
						memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
					}

					printf("wait......\r\n");
					usleep(1000000);
				}
			}
		}
		else
		{
			printf(RC522_DEBUG "BRUSH_NONE\r\n");
		}

		//接收串口屏 返回
		ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
		if(ret == 0)
		{
			if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
			{
				printf(DISPLAY_SCREEN_DEBUG "return\r\n");
				Display_Screen_Write((hi_u8 *)"page main");

				break;
			}
			memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
		}

		printf("wait......\r\n");
		usleep(1000000);
	}
}
#endif


#define SSID_LEN_MAX 20
#define PASSWD_LEN_MAX 20
extern osThreadId_t mqtt_thread_id;
extern bool wifi_connected;
extern bool mqtt_enable;
extern struct sys_time Sys_Time;
extern bool sys_Time_Display;
extern struct scancard_time ScanCard_Time;
//设置
void Settings_Card(void)
{
	BrushCardStatus brushCard_Statu;
    unsigned int user_id;
	AuthorityStatus authority_Statu;
	unsigned char Rxdata[70] = {0}; //这个长一点，因为有ssid(length=20)和passwd(length=20)以及其他讯息
	unsigned int Rxdata_len;
	char ssid[SSID_LEN_MAX] = {0};
	char passwd[PASSWD_LEN_MAX] = {0};
	char ret;
	char *ptr1 = NULL;
	char *ptr2 = NULL;
	int connect_status;
	unsigned char tmp[2] ={0};

	printf("Settings_Card\r\n");
	//切换到 settings 界面  设置
	Display_Screen_Write((hi_u8 *)"page settings");

	//等待一小会，等串口屏刷新完页面
	usleep(500000);

	while(1)
	{
		//接收串口屏 返回
		ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 200);
		if(ret == 0)
		{
			if(strncmp((const char *)Rxdata, (const char *)"wifi", Rxdata_len) == 0) //接收字符串 "wifi"
			{
				printf(DISPLAY_SCREEN_DEBUG "wifi\r\n");
				//切换到 clock_in_time 界面  打卡时间
				Display_Screen_Write((hi_u8 *)"page wifi");

				while(1)
				{
					//接收串口屏
					ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 200);
					if(ret == 0)
					{
						// printf("Rxdata=%s\r\n",Rxdata);
						//先判断 "disconnect" ，因为 connect 是 disconnect 的子串，防止把 connect 也识别成 disconnect 。
						if(strstr((const char *)Rxdata, (const char *)"disconnect") != NULL) //接收字符串 "disconnect"
						{
							printf(DISPLAY_SCREEN_DEBUG "wifi disconnect\r\n");

							// osThreadSuspend(mqtt_thread_id); //暂停MQTT线程
							
							Wifi_Disconnect(); //断开连接
							wifi_connected = 0;
							mqtt_enable = 0; //跳出内层while(mqtt_enable)循环，当再次恢复线程时

							Display_Screen_Write((hi_u8 *)"wifi.b0.txt=\"Connect\""); //全局 Disconnect 按钮变为 Connect ，为下次连接做准备
							Display_Screen_Write((hi_u8 *)"p0.pic=2"); //page wifi 私有 wifi 图标由连通变为禁止状态
							Display_Screen_Write((hi_u8 *)"main.p0.pic=2"); //page main 全局 wifi 图标由连通变为禁止状态
						}
						//串口接收到 连接 Wi-Fi 的请求，收集相应的 "ssid" 和 "passwd"，开始 sta 连接
						else if(strstr((const char *)Rxdata, (const char *)"connect") != NULL) //接收字符串 "connect"
						{
							printf(DISPLAY_SCREEN_DEBUG "wifi connect\r\n");

							ptr1 = strstr((const char *)Rxdata, (const char *)"ssid=");
							ptr2 = strstr((const char *)Rxdata, (const char *)",passwd="); //,:逗号不能少

							*(ptr2) = '\0'; //当做ssid的结束符
							sprintf((char *)&ssid, "%s", ptr1+5);

							*(ptr2) = ','; //改回原来的值
							sprintf((char *)&passwd, "%s", ptr2+8);

							ptr1 = NULL;
							ptr2 = NULL;

							printf("SSID:%s\r\n",ssid);
							printf("PASSWD:%s\r\n",passwd);

							//Wifi 连接(直到连接成功才返回)
							connect_status = Wifi_Connect(ssid, passwd);
							if(connect_status == 0)
							{
								// osThreadResume(mqtt_thread_id); //恢复MQTT线程，MQTT线程优先级最高会立即执行
								wifi_connected = 1;
								mqtt_enable = 1; //重新进行设备注册后，再次进入内层while(mqtt_enable)循环
								//连接成功，密码正确
								Display_Screen_Write((hi_u8 *)"t3.txt=\"\""); //清空密码框

								Display_Screen_Write((hi_u8 *)"wifi.b0.txt=\"Disconnect\""); //全局 Connect 按钮变为 Disconnect ，为断开连接做准备
								Display_Screen_Write((hi_u8 *)"p0.pic=1"); //page wifi 私有 wifi 图标由禁止变为连通状态
								Display_Screen_Write((hi_u8 *)"main.p0.pic=1"); //page main 全局 wifi 图标由禁止变为连通状态
							}
							else
							{
								;
							}
						}
						else if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
						{
							memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
							printf(DISPLAY_SCREEN_DEBUG "return\r\n");
							//切换到 main 界面  主界面
							Display_Screen_Write((hi_u8 *)"page settings");

							//等待一小会，等串口屏刷新完页面
							usleep(500000);

							break;
						}
						else
						{
							;
						}
						memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
					}
					printf("wait......\r\n");
					usleep(1000000);
				}
			}
			else if(strncmp((const char *)Rxdata, (const char *)"clock_in_time", Rxdata_len) == 0) //接收字符串 "clock_in_time"
			{
				Display_Screen_Write((hi_u8 *)"page white_board");
				//等待一小会，等串口屏刷新完页面
				usleep(500000);

				//串口屏 "删除用户前需管理员通过，请使用管理员卡。"
				Display_Screen_Write((hi_u8 *)"t0.txt=\"打卡时间设置：\r\n\"");
				// Display_Screen_Write((hi_u8 *)"t0.txt+=\"Administrator is required before deleting user. Please use admin card.\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"请使用管理员/超级用户卡。\r\n\"");
				while(1)
				{
					brushCard_Statu = RC522_FindCard(&user_id);
					if(brushCard_Statu == BRUSH_FIND)
					{
						authority_Statu = Card_Is_Database(user_id);
						if((authority_Statu == AUTHORITY_ADMIN) || (authority_Statu == AUTHORITY_ROOT)) //刷卡的是管理员，或者超级用户
						{
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员/超级用户刷卡成功\r\n\"");
							usleep(DISPLAY_TIME);
							break;
						}
					}
					ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
					if(ret == 0)
					{
						if(strstr((const char *)Rxdata, (const char *)"return") != NULL)
						{
							//切换到 settings 界面  主界面
							Display_Screen_Write((hi_u8 *)"page main");
							//等待一小会，等串口屏刷新完页面
							usleep(500000);

							memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存

							return;
						}
						memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
					}
					printf("wait......\r\n");
					usleep(1000000);
				}

				printf(DISPLAY_SCREEN_DEBUG "clock_in_time\r\n");
				//切换到 clock_in_time 界面  打卡时间
				Display_Screen_Write((hi_u8 *)"page clock_in_time");

				Display_Screen_Write_Time_clock_in_time(ScanCard_Time.morning_time_hours,0);
				Display_Screen_Write_Time_clock_in_time(ScanCard_Time.morning_time_minutes,1);
				Display_Screen_Write_Time_clock_in_time(ScanCard_Time.morning_time_seconds,2);
				Display_Screen_Write_Time_clock_in_time(ScanCard_Time.afternoon_time_hours,3);
				Display_Screen_Write_Time_clock_in_time(ScanCard_Time.afternoon_time_minutes,4);
				Display_Screen_Write_Time_clock_in_time(ScanCard_Time.afternoon_time_seconds,5);

				while(1)
				{
					ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 200);
					if(ret == 0)
					{
						if((ptr1 = strstr((const char *)Rxdata, (const char *)"ok")) != NULL) //接收字符串 "edit"
						{
							printf(DISPLAY_SCREEN_DEBUG "clock_in_time ok\r\n");

							ScanCard_Time.morning_time_hours = *(ptr1+4);
							ScanCard_Time.morning_time_minutes = *(ptr1+10);
							ScanCard_Time.morning_time_seconds = *(ptr1+16);
							ScanCard_Time.afternoon_time_hours = *(ptr1+22);
							ScanCard_Time.afternoon_time_minutes = *(ptr1+28);
							ScanCard_Time.afternoon_time_seconds = *(ptr1+34);
							ptr1 = NULL;
							printf("morning_time_hours = %d\r\n", ScanCard_Time.morning_time_hours);
							printf("morning_time_minutes = %d\r\n", ScanCard_Time.morning_time_minutes);
							printf("morning_time_seconds = %d\r\n", ScanCard_Time.morning_time_seconds);
							printf("afternoon_time_hours = %d\r\n", ScanCard_Time.afternoon_time_hours);
							printf("afternoon_time_minutes = %d\r\n", ScanCard_Time.afternoon_time_minutes);
							printf("afternoon_time_seconds = %d\r\n", ScanCard_Time.afternoon_time_seconds);

							hi_flash_erase(FLASH_SCANCARD_TIME, 4096);
							Flash_Write_Scancard(FLASH_SCANCARD_TIME, HI_TRUE);

							memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
							printf(DISPLAY_SCREEN_DEBUG "ok\r\n");
							//切换到 settings 界面  主界面
							Display_Screen_Write((hi_u8 *)"page main");
							//等待一小会，等串口屏刷新完页面
							usleep(500000);

							return;
						}
						else if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
						{
							memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
							printf(DISPLAY_SCREEN_DEBUG "return\r\n");
							//切换到 settings 界面  主界面
							Display_Screen_Write((hi_u8 *)"page settings");

							//等待一小会，等串口屏刷新完页面
							usleep(500000);

							break;
						}
						else
						{
							;
						}
						memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
					}

					printf("wait......\r\n");
					usleep(1000000);
				}
			}
			else if(strncmp((const char *)Rxdata, (const char *)"system_time", Rxdata_len) == 0) //接收字符串 "system_time"
			{
				Display_Screen_Write((hi_u8 *)"page white_board");
				//等待一小会，等串口屏刷新完页面
				usleep(500000);

				//串口屏 "删除用户前需管理员通过，请使用管理员卡。"
				Display_Screen_Write((hi_u8 *)"t0.txt=\"系统时间设置：\r\n\"");
				// Display_Screen_Write((hi_u8 *)"t0.txt+=\"Administrator is required before deleting user. Please use admin card.\"");
				Display_Screen_Write((hi_u8 *)"t0.txt+=\"请使用管理员/超级用户卡。\r\n\"");
				while(1)
				{
					brushCard_Statu = RC522_FindCard(&user_id);
					if(brushCard_Statu == BRUSH_FIND)
					{
						authority_Statu = Card_Is_Database(user_id);
						if((authority_Statu == AUTHORITY_ADMIN) || (authority_Statu == AUTHORITY_ROOT)) //刷卡的是管理员，或者超级用户
						{
							Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员/超级用户刷卡成功\r\n\"");
							usleep(DISPLAY_TIME);
							break;
						}
					}
					ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
					if(ret == 0)
					{
						if(strstr((const char *)Rxdata, (const char *)"return") != NULL)
						{
							//切换到 settings 界面  主界面
							Display_Screen_Write((hi_u8 *)"page main");
							//等待一小会，等串口屏刷新完页面
							usleep(500000);

							memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存

							return;
						}
						memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
					}
					printf("wait......\r\n");
					usleep(1000000);
				}

				printf(DISPLAY_SCREEN_DEBUG "system_time\r\n");
				//切换到 system_time 界面  系统时间
				Display_Screen_Write((hi_u8 *)"page system_time");

				while(1)
				{
					//接收串口屏
					ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
					if(ret == 0)
					{
						if(strstr((const char *)Rxdata, (const char *)"edit") != NULL) //接收字符串 "edit"
						{
							printf(DISPLAY_SCREEN_DEBUG "system_time edit\r\n");

							//显示全为0（只是显示，没改数据）
							Display_Screen_Write_Time(0,0); //年
							Display_Screen_Write_Time(0,1); //月
							Display_Screen_Write_Time(0,2); //日
							Display_Screen_Write_Time(0,5); //时
							Display_Screen_Write_Time(0,4); //分
							Display_Screen_Write_Time(0,3); //秒

							sys_Time_Display = 0; //暂停时间的显示
							Display_Screen_Write((hi_u8 *)"system_time.b0.txt=\"OK\"");
						}
						else if((ptr1 = strstr((const char *)Rxdata, (const char *)"ok")) != NULL) //接收字符串 "ok"
						{
							printf(DISPLAY_SCREEN_DEBUG "system_time ok\r\n");
							
							// Sys_Time.sys_time_years = (unsigned int)(*(ptr1+4)) | (unsigned int)((*(ptr1+5)) << 8); //导致复位,异常信息: Exception Type  = 0xb
							//解决办法：
							tmp[0] = *(ptr1+4);
							tmp[1] = *(ptr1+5);
							Sys_Time.sys_time_years = ((unsigned int)tmp[1]<<8) | ((unsigned int)tmp[0]);
							printf("sys_time_years = %u\r\n", Sys_Time.sys_time_years);

							Sys_Time.sys_time_months = *(ptr1+10);
							printf("sys_time_months = %d\r\n", Sys_Time.sys_time_months);

							Sys_Time.sys_time_days = *(ptr1+16);
							printf("sys_time_days = %d\r\n", Sys_Time.sys_time_days);

							Sys_Time.sys_time_hours = *(ptr1+22);
							printf("sys_time_hours = %d\r\n", Sys_Time.sys_time_hours);

							Sys_Time.sys_time_minutes = *(ptr1+28);
							printf("sys_time_hours = %d\r\n", Sys_Time.sys_time_minutes);

							Sys_Time.sys_time_seconds = *(ptr1+34);
							printf("sys_time_seconds = %d\r\n", Sys_Time.sys_time_seconds);

							ptr1 = NULL;
							sys_Time_Display = 1; //设置完系统时间，打开时间的显示
							Display_Screen_Write((hi_u8 *)"system_time.b0.txt=\"Edit\"");
						}
						else if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
						{
							memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
							printf(DISPLAY_SCREEN_DEBUG "return\r\n");
							//切换到 main 界面  主界面
							Display_Screen_Write((hi_u8 *)"page settings");

							//等待一小会，等串口屏刷新完页面
							usleep(500000);

							break;
						}
						else
						{
							;
						}
						memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
					}

					printf("wait......\r\n");
					usleep(1000000);
				}
			}
			else if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0) //接收字符串 "return"
			{
				memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
				printf(DISPLAY_SCREEN_DEBUG "return\r\n");
				//切换到 main 界面  主界面
				Display_Screen_Write((hi_u8 *)"page main");

				break;
			}
			else
			{
				continue;
			}
			memset(&Rxdata, 0, sizeof(Rxdata)); //处理完清理缓存
		}

		printf("wait......\r\n");
		usleep(1000000);
	}
}



//在wifi_xxx.c中声明 wifi 连接函数
// char Wifi_Connect(unsigned char *ssid, unsigned char *pwd)
// {
// 	*ssid = *ssid; //临时
// 	*pwd = *pwd; //临时
// 	return 0; //临时
// }

//在wifi_xxx.c中声明 wifi 连接函数
// void Wifi_Disconnect(void)
// {

// }

// void Others_Conditions(void)
// {
// 	printf("Others_Conditions\r\n");
// }