#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <malloc.h>
#include "cmsis_os2.h"
#include <hi_types_base.h>
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
#define RC522_NSS_SetValue(value) GpioSetOutputVal(WIFI_IOT_GPIO_IDX_9,value)
#define RC522_RST_SetValue(value) GpioSetOutputVal(WIFI_IOT_GPIO_IDX_10,value)
void WriteRawRC(unsigned char Address, unsigned char value)
{
    unsigned char ucAddr;
    RC522_NSS_SetValue(0);
    ucAddr = ((Address<<1)&0x7E);
    SPI0_ReadWriteByte(ucAddr);
    SPI0_ReadWriteByte(value);
    RC522_NSS_SetValue(1);
}
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
void ClearBitMask(unsigned char reg,unsigned char mask)
{
    char tmp = 0x0;
    tmp = ReadRawRC(reg);
    WriteRawRC(reg, tmp & ~mask);
}
void SetBitMask(unsigned char reg,unsigned char mask)
{
    char tmp = 0x0;
    tmp = ReadRawRC(reg);
    WriteRawRC(reg,tmp | mask);
}
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
    WriteRawRC(ModeReg, 0x3D);
    WriteRawRC(TReloadRegL, 30);
    WriteRawRC(TReloadRegH, 0);
    WriteRawRC(TModeReg, 0x8D);
    WriteRawRC(TPrescalerReg, 0x3E);
    WriteRawRC(TxAutoReg, 0x40);

    return MI_OK;
}
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
    i = 600;
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
    SetBitMask(ControlReg,0x80);
    WriteRawRC(CommandReg,PCD_IDLE);
    return status;
}
void PcdAntennaOff()
{
    ClearBitMask(TxControlReg, 0x03);
}
void PcdAntennaOn()
{
    unsigned char i;
    i = ReadRawRC(TxControlReg);
    if (!(i & 0x03))
    {
        SetBitMask(TxControlReg, 0x03);
    }
}
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
void RC522_GPIO_Init(void)
{



    GpioInit();
    IoSetFunc(WIFI_IOT_IO_NAME_GPIO_6, WIFI_IOT_IO_FUNC_GPIO_6_SPI0_CK);

    IOSetDriverStrength(WIFI_IOT_IO_NAME_GPIO_6, WIFI_IOT_IO_DRIVER_STRENGTH_2);
    IoSetFunc(WIFI_IOT_IO_NAME_GPIO_7, WIFI_IOT_IO_FUNC_GPIO_7_SPI0_RXD);
    IoSetFunc(WIFI_IOT_IO_NAME_GPIO_8, WIFI_IOT_IO_FUNC_GPIO_8_SPI0_TXD);
    IOSetDriverStrength(WIFI_IOT_IO_NAME_GPIO_8, WIFI_IOT_IO_DRIVER_STRENGTH_0);
    IoSetFunc(WIFI_IOT_IO_NAME_GPIO_9, WIFI_IOT_IO_FUNC_GPIO_9_GPIO);
    GpioSetDir(WIFI_IOT_IO_NAME_GPIO_9, WIFI_IOT_GPIO_DIR_OUT);
    IoSetFunc(WIFI_IOT_IO_NAME_GPIO_10, WIFI_IOT_IO_FUNC_GPIO_10_GPIO);
    GpioSetDir(WIFI_IOT_IO_NAME_GPIO_10, WIFI_IOT_GPIO_DIR_OUT);
    SPI0_Init();
}
void RC522_HW_Config(void)
{
    PcdReset();
    PcdAntennaOff();
    usleep(5000);
    PcdAntennaOn();
}
void RC522_Init(void)
{
    RC522_GPIO_Init();
    RC522_HW_Config();
}
void RC522_Test(void)
{
    unsigned char i;
    unsigned char status;
    unsigned char g_ucTempbuf[4];
    unsigned char UID[4];
    status = PcdRequest(PICC_REQALL, g_ucTempbuf);
    if (status != MI_OK)
    {
        printf("PcdRequest failed\r\n");
        return;
    }
    printf("PcdRequest success\r\n");
    status = PcdAnticoll(UID);
    if (status != MI_OK)
    {
        printf("PcdAnticoll failed\r\n");
        return;
    }
    printf("PcdAnticoll success\r\n");
    PcdReset();
    printf("RC522-ID:");
    for(i=0;i<4;i++)
        printf("[%2X]",UID[i]);
    printf("\r\n");
}
BrushCardStatus RC522_FindCard(unsigned int *card_ID)
{
    unsigned char i;
    unsigned char status;
    unsigned char g_ucTempbuf[4];

    status = PcdRequest(PICC_REQALL, g_ucTempbuf);
    if (status != MI_OK)
    {
        *card_ID = 0;
        printf("PcdRequest failed\r\n");

        return BRUSH_NONE;
    }
    printf("PcdRequest success\r\n");
    status = PcdAnticoll(g_ucTempbuf);
    if (status != MI_OK)
    {
        *card_ID = 0;
        printf("PcdAnticoll failed\r\n");

        return BRUSH_NONE;
    }
    printf("PcdAnticoll success\r\n");
    PcdReset();

    for(i=0;i<4;i++)
    {
        printf("user ID[%d] = %X\r\n", i, g_ucTempbuf[i]);
    }





    *card_ID = ((unsigned int)g_ucTempbuf[0]<<24) | ((unsigned int)g_ucTempbuf[1]<<16) | ((unsigned int)g_ucTempbuf[2]<<8) | ((unsigned int)g_ucTempbuf[3]);
    return BRUSH_FIND;
}
extern LinkList RC522_Database;
extern unsigned char g_user_num;
extern struct sys_time Sys_Time;
extern struct scancard_time ScanCard_Time;
extern struct sys_record_info ScanRecord_Info[50];
extern unsigned char record_num;
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

    ret = hi_factory_nv_read(HI_FACTORY_NV_DEMO_ID, &cfg, sizeof(cfg), 0);
    if (ret != HI_ERR_SUCCESS) {
        printf("factory nv read fail\r\n");
        return;
    }
    printf("factory nv read success, cfg.nv_demo_test_num0:%d\r\n", cfg.nv_factory_demo_test_num0);
    if(cfg.nv_factory_demo_test_num0 == 0)
    {
        sys_Running_First = 1;
        cfg1.nv_factory_demo_test_num0 = 0x3;

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
void Database_Init(void)
{
    RC522_Database = CreateListHead();
    UserInfo user1 = {

        .userid = 1240396216,
        .name = "root",

        .permission = AUTHORITY_ROOT,
        .permission_last = AUTHORITY_RESERVE,
        .permission_time_is_forever = YES_YES,
        .permission_time_hours = 255,
        .permission_time_minutes = 255,
        .permission_time_seconds = 255,

        .scancard_time_is_same = YES_YES,
        .morning_time_hours = 255,
        .morning_time_minutes = 255,
        .morning_time_seconds = 255,
        .afternoon_time_hours = 255,
        .afternoon_time_minutes = 255,
        .afternoon_time_seconds = 255,
    };

    UserInfo user2 = {

        .userid = 1246919551,
        .name = "admin",

        .permission = AUTHORITY_ADMIN,
        .permission_last = AUTHORITY_RESERVE,
        .permission_time_is_forever = YES_YES,
        .permission_time_hours = 255,
        .permission_time_minutes = 255,
        .permission_time_seconds = 255,

        .scancard_time_is_same = YES_YES,
        .morning_time_hours = 255,
        .morning_time_minutes = 255,
        .morning_time_seconds = 255,
        .afternoon_time_hours = 255,
        .afternoon_time_minutes = 255,
        .afternoon_time_seconds = 255,
    };

    UserInfo user3 = {

        .userid = 3388891059,
        .name = "user_test",
        .permission = AUTHORITY_USER,
        .permission_last = AUTHORITY_RESERVE,
        .permission_time_is_forever = YES_YES,
        .permission_time_hours = 255,
        .permission_time_minutes = 255,
        .permission_time_seconds = 255,

        .scancard_time_is_same = YES_YES,
        .morning_time_hours = 255,
        .morning_time_minutes = 255,
        .morning_time_seconds = 255,
        .afternoon_time_hours = 255,
        .afternoon_time_minutes = 255,
        .afternoon_time_seconds = 255,
    };








    factory_nv_demo();
    if(sys_Running_First)
    {
        Insert(&user1, RC522_Database);
        Insert(&user2, RC522_Database);
        Insert(&user3, RC522_Database);

        g_user_num = 3;

        hi_flash_erase(FLASH_USERINFO_OFFSET, 4096);
        Flash_Write(FLASH_USERINFO_OFFSET, RC522_Database, g_user_num, HI_FALSE);
        return;
    }


    Flash_Read(FLASH_USERINFO_OFFSET, RC522_Database, &g_user_num);
}
#else
void Database_Init(void)
{
    RC522_Database = CreateListHead();
    g_user_num = 3;

    Flash_Read_Name(RC522_Database);

    Flash_Read_Others(RC522_Database);
}
#endif
AuthorityStatus Card_Is_Database(unsigned int card)
{
    UserInfo user;
    char ret;
    user.userid = card;
    ret = Find_Permission(&user, RC522_Database);
    if(ret != 0)
    {
        printf("not find user : [%u]\r\n", card);
        return AUTHORITY_NONE;
    }

    switch(user.permission)
    {
        case AUTHORITY_NO:
            return AUTHORITY_NO;
            break;
        case AUTHORITY_USER:
            return AUTHORITY_USER;
            break;
        case AUTHORITY_ADMIN:
            return AUTHORITY_ADMIN;
            break;
        case AUTHORITY_ROOT:
            return AUTHORITY_ROOT;
            break;
        default:
            return AUTHORITY_RESERVE;
            break;
    }
}
extern osMessageQueueId_t mid_MsgQueue;
void Scan_Card(void)
{
    BrushCardStatus brushCard_Statu;
    unsigned int user_id;
    LinkList P;
    UserInfo find_user;
    unsigned char str[100] = {0};
    unsigned char i;
    app_msg_t *app_msg;
    brushCard_Statu = RC522_FindCard(&user_id,jk);
    if(brushCard_Statu == BRUSH_NONE)
    {
        printf(RC522_DEBUG "BRUSH_NONE\r\n");
        return;
    }
    else
    {

        Display_Screen_Write((hi_u8 *)"page white_board");

        usleep(500000);

        Display_Screen_Write((hi_u8 *)"vis b0,0");
        find_user.userid = user_id;

        P = Find(&find_user, RC522_Database);
        if(P == NULL)
        {
            Display_Screen_Write((hi_u8 *)"t0.txt=\"刷卡情况：刷卡失败\r\n\"");
            Display_Screen_Write((hi_u8 *)"t0.txt+=\"ID：无\r\n\"");
            Display_Screen_Write((hi_u8 *)"t0.txt+=\"您的身份是：无\r\n\"");
            Display_Screen_Write((hi_u8 *)"t0.txt+=\"打卡情况：无\r\n\"");
            Display_Screen_Write((hi_u8 *)"t0.txt+=\"打卡时间：无\r\n\"");
        }

        else
        {

            Display_Screen_Write((hi_u8 *)"t0.txt=\"刷卡情况：刷卡成功\r\n\"");

            Display_Screen_Write((hi_u8 *)"t0.txt+=\"ID：\"");
            Display_Screen_Write_Custom(&P->data.name[0]);

            Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n您的身份是：\"");
            if(P->data.permission == AUTHORITY_USER)
            {
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"普通用户\"");
            }
            else if(P->data.permission == AUTHORITY_ADMIN)
            {
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员\"");
            }
            else if(P->data.permission == AUTHORITY_ROOT)
            {
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"超级用户\"");
            }
            else if(P->data.permission == AUTHORITY_NO)
            {
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"无权限\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡情况：打卡失败\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡时间：无\"");

                usleep(2000000);

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

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡情况：打卡成功\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡时间：\"");
                sprintf((char *)str, "%d/%d/%d,%d:%d:%d", Sys_Time.sys_time_years, Sys_Time.sys_time_months, Sys_Time.sys_time_days,
                                                        Sys_Time.sys_time_hours, Sys_Time.sys_time_minutes, Sys_Time.sys_time_seconds);
                Display_Screen_Write_Custom(str);

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

                sprintf((char *)str, "ID:%s,Identity:%d,Time:%d/%d/%d %d:%d:%d", &P->data.name[0], P->data.permission,
                                                        Sys_Time.sys_time_years, Sys_Time.sys_time_months, Sys_Time.sys_time_days,
                                                        Sys_Time.sys_time_hours, Sys_Time.sys_time_minutes, Sys_Time.sys_time_seconds);
                app_msg = malloc(sizeof(app_msg_t));
                if(app_msg != NULL)
                {
                    app_msg->msg_type = en_msg_report;

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
                record_num = record_num + 1;
                if(record_num >= 50)
                {
                    record_num = 0;
                }
            }
            else
            {

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡情况：打卡失败\"");
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"\r\n打卡超时 或 未到打卡时间\"");
            }
        }

        usleep(2000000);

        Display_Screen_Write((hi_u8 *)"page main");
    }
}
#define RECORD_ONE_PAGE_MAX 5
void printf_ScanRecord(unsigned char record_start_index,unsigned char num)
{
    unsigned char i;
    unsigned char str[50] = {0};
    unsigned char index;

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

        if(ScanRecord_Info[index].authority == AUTHORITY_USER)
        {
            Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限=普通用户,\"");
        }
        else if(ScanRecord_Info[index].authority == AUTHORITY_ADMIN)
        {
            Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限=管理员,\"");
        }
        else if(ScanRecord_Info[index].authority == AUTHORITY_ROOT)
        {
            Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限=超级用户,\"");
        }
        else if(ScanRecord_Info[index].authority == AUTHORITY_NO)
        {
            Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限=无权限,\"");
        }
        else
        {}
        sprintf((char *)str, "id=%u\r\n",ScanRecord_Info[index].id);
        Display_Screen_Write_Custom(str);
    }
}
#define MIN(a,b) ((a)<(b)?(a):(b))
#ifdef DISPLAY_SCREEN_SCANRECORD
void Scan_Record(void)
{
    unsigned char Rxdata[50] = {0};
    unsigned int Rxdata_len;
    char ret;
    unsigned char str[50] = {0};
    unsigned char i;
    unsigned char page_num = (record_num + RECORD_ONE_PAGE_MAX - 1)/RECORD_ONE_PAGE_MAX;
    unsigned char page_index;
    unsigned char record_num_tmp;
    printf("Scan_Record\r\n");

    Display_Screen_Write((hi_u8 *)"page record");

    usleep(500000);

    if(record_num > 0)
    {

        page_index = 1;



        printf_ScanRecord(0, MIN(record_num, RECORD_ONE_PAGE_MAX));
    }
    else
    {
        Display_Screen_Write((hi_u8 *)"t0.txt+=\"无\"");
    }

    while(1)
    {

        ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
        if(ret == 0)
        {

            if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
            {
                printf(DISPLAY_SCREEN_DEBUG "return\r\n");

                Display_Screen_Write((hi_u8 *)"page main");
                break;
            }

            else if(strncmp((const char *)Rxdata, (const char *)"next_page", Rxdata_len) == 0)
            {
                printf(DISPLAY_SCREEN_DEBUG "next_page\r\n");
                if(page_num > 1)
                {

                    page_index++;
                    if(page_index >= page_num)
                    {
                        page_index = page_num;

                        Display_Screen_Write((hi_u8 *)"vis b2,0");
                    }
                    record_num_tmp = (page_index - 1)*RECORD_ONE_PAGE_MAX;
                    printf_ScanRecord(record_num_tmp, MIN(record_num - record_num_tmp, RECORD_ONE_PAGE_MAX));

                    Display_Screen_Write((hi_u8 *)"vis b1,1");
                }
                else
                {}
            }

            else if(strncmp((const char *)Rxdata, (const char *)"previous_page", Rxdata_len) == 0)
            {
                printf(DISPLAY_SCREEN_DEBUG "previous_page\r\n");
                page_index--;
                if(page_index <= 1)
                {
                    page_index = 1;

                    Display_Screen_Write((hi_u8 *)"vis b1,0");
                }
                else
                {}
                record_num_tmp = (page_index - 1)*RECORD_ONE_PAGE_MAX;
                printf_ScanRecord(record_num_tmp, RECORD_ONE_PAGE_MAX);

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
#ifdef DISPLAY_SCREEN_ADDUSER
extern hi_u8 g_tf_pdata[TEST_SIZE];
extern hi_u8 g_tf_pdata_back[TEST_SIZE];
void Add_Card(void)
{
    BrushCardStatus brushCard_Statu;
    unsigned int user_id;


    unsigned char Rxdata[60] = {0};
    unsigned int Rxdata_len;
    char ret;
    unsigned char i;
    char *ptr = NULL;
    AuthorityStatus authority_Statu;
    UserInfo add_user;
    printf("Add_Card\r\n");

    if(g_user_num >= USER_NUM_MAX)
    {
        Display_Screen_Write((hi_u8 *)"page white_board");

        usleep(500000);
        Display_Screen_Write((hi_u8 *)"vis b0,0");


        Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
        Display_Screen_Write((hi_u8 *)"t0.txt+=\"数据库已满，请扩容。\r\n\"");
        Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
        usleep(DISPLAY_TIME);

        Display_Screen_Write((hi_u8 *)"page main");
        return;
    }

    Display_Screen_Write((hi_u8 *)"page adduser");

    usleep(500000);



    Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
    Display_Screen_Write((hi_u8 *)"t0.txt+=\"添加用户前需管理员通过，请使用管理员卡。\r\n\"");

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
        brushCard_Statu = RC522_FindCard(&user_id);
        if(brushCard_Statu == BRUSH_FIND)
        {
            printf(RC522_DEBUG "BRUSH_FIND\r\n");
            printf("user_id = [%u]\r\n", user_id);
            authority_Statu = Card_Is_Database(user_id);
            if((authority_Statu != AUTHORITY_ADMIN) && (authority_Statu != AUTHORITY_ROOT))
            {

                printf(DISPLAY_SCREEN_DEBUG "This card is not an administrator and is exiting.\r\n");
                printf(DISPLAY_SCREEN_DEBUG "Exiting......\r\n\r\n");


                Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡不是管理员，正在退出。\r\n\"");
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
                usleep(DISPLAY_TIME);

                Display_Screen_Write((hi_u8 *)"page main");
                break;
            }
            else
            {


                Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员/超级用户刷卡成功。\r\n\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"请刷一张新卡。\r\n\"");
                usleep(DISPLAY_TIME);
                while(1)
                {
                    brushCard_Statu = RC522_FindCard(&user_id);
                    if(brushCard_Statu == BRUSH_FIND)
                    {
                        authority_Statu = Card_Is_Database(user_id);
                        if(authority_Statu != AUTHORITY_NONE)
                        {


                            Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"已在数据库中，添加失败。\r\n\"");

                            usleep(DISPLAY_TIME);
                            Display_Screen_Write((hi_u8 *)"page main");
                            return;
                        }
                        else
                        {


                            Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"刷卡成功。\r\n\"");

                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"请输入参数。\r\n\"");

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

                                ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 100);
                                if(ret == 0)
                                {
                                    if(strstr((const char *)Rxdata, (const char *)"return") != NULL)
                                    {
                                        printf(DISPLAY_SCREEN_DEBUG "return\r\n");
                                        Display_Screen_Write((hi_u8 *)"page main");
                                        return;
                                    }
                                    else if(strstr((const char *)Rxdata, (const char *)"ok") != NULL)
                                    {

                                        add_user.userid = user_id;

                                        for(i=0;i<NAME_BYTE_LEN;i++)
                                        {
                                            add_user.name[i] = '\0';
                                        }


                                        add_user.permission = AUTHORITY_USER;
                                        add_user.permission_last = AUTHORITY_NO;
                                        add_user.permission_time_is_forever = YES_YES;
                                        add_user.permission_time_hours = 255;
                                        add_user.permission_time_minutes = 255;
                                        add_user.permission_time_seconds = 255;

                                        add_user.scancard_time_is_same = YES_YES,
                                        add_user.morning_time_hours = 255;
                                        add_user.morning_time_minutes = 255;
                                        add_user.morning_time_seconds = 255;
                                        add_user.afternoon_time_hours = 255;
                                        add_user.afternoon_time_minutes = 255;
                                        add_user.afternoon_time_seconds = 255;

                                        if((ptr = strstr((const char *)Rxdata, (const char *)"forever=1")) != NULL)
                                        {
                                            add_user.permission_time_is_forever = YES_YES;
                                            sprintf((char *)&add_user.name[0], "%s", &ptr[14]);
                                            ptr = NULL;
                                            printf("add_user.permission_time_is_forever=%d\r\n", YES_YES);
                                            printf("add_user.name=%s\r\n", add_user.name);
                                        }
                                        else if((ptr = strstr((const char *)Rxdata, (const char *)"forever=0")) != NULL)
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
                                        Insert(&add_user, RC522_Database);
                                        g_user_num++;


                                        hi_flash_erase(FLASH_USERINFO_OFFSET, 4096);
                                        hi_flash_erase(FLASH_USERINFO_USER_NUM, 4096);
                                        Flash_Write(FLASH_USERINFO_OFFSET, RC522_Database, g_user_num, HI_TRUE);
                                        printf("Add successful.\r\n");
                                        printf("Exiting......\r\n");



                                        Display_Screen_Write((hi_u8 *)"t0.txt=\"添加用户：\r\n\"");
                                        Display_Screen_Write((hi_u8 *)"t0.txt+=\"添加成功。\r\n\"");
                                        Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
                                        usleep(DISPLAY_TIME);

                                        Display_Screen_Write((hi_u8 *)"page main");
                                        Display_Screen_Write((hi_u8 *)"adduser.r0.val=1");
                                        Display_Screen_Write((hi_u8 *)"adduser.r1.val=0");
                                        Display_Screen_Write((hi_u8 *)"adduser.t1.txt=\"\"");

                                        return;
                                    }
                                    else
                                    {
                                        ;
                                    }
                                    memset(&Rxdata, 0, sizeof(Rxdata));
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

                    ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
                    if(ret == 0)
                    {
                        if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
                        {
                            printf(DISPLAY_SCREEN_DEBUG "return\r\n");
                            Display_Screen_Write((hi_u8 *)"page main");
                            return;
                        }
                        memset(&Rxdata, 0, sizeof(Rxdata));
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

        ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
        if(ret == 0)
        {
            if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
            {
                printf(DISPLAY_SCREEN_DEBUG "return\r\n");
                Display_Screen_Write((hi_u8 *)"page main");
                break;
            }
            memset(&Rxdata, 0, sizeof(Rxdata));
        }
        printf("wait......\r\n");
        usleep(1000000);
    }
}
#endif
#ifdef DISPLAY_SCREEN_DELUSER
void Del_Card(void)
{
    BrushCardStatus brushCard_Statu;
    unsigned int user_id;
    unsigned char Rxdata[50] = {0};
    unsigned int Rxdata_len;
    char ret;
    AuthorityStatus authority_Statu;
    UserInfo del_user;
    UserInfo admin_user;
    printf("Del_Card\r\n");

    if(g_user_num <= 1)
    {
        Display_Screen_Write((hi_u8 *)"page white_board");

        usleep(500000);
        Display_Screen_Write((hi_u8 *)"vis b0,0");


        Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
        Display_Screen_Write((hi_u8 *)"t0.txt+=\"数据库已空，不可删除。\r\n\"");
        Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
        usleep(DISPLAY_TIME);

        Display_Screen_Write((hi_u8 *)"page main");
        return;
    }

    Display_Screen_Write((hi_u8 *)"page deluser");

    usleep(500000);

    Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");

    Display_Screen_Write((hi_u8 *)"t0.txt+=\"删除用户前需管理员/超级用户通过，请使用管理员/超级用户卡。\r\n\"");
    while (1)
    {
        brushCard_Statu = RC522_FindCard(&user_id);
        if(brushCard_Statu == BRUSH_FIND)
        {
            printf(RC522_DEBUG "BRUSH_FIND\r\n");
            printf("user_id = [%u]\r\n", user_id);
            authority_Statu = Card_Is_Database(user_id);
            if((authority_Statu != AUTHORITY_ADMIN) && (authority_Statu != AUTHORITY_ROOT))
            {

                printf(DISPLAY_SCREEN_DEBUG "This card is not an administrator and is exiting.\r\n");
                printf(DISPLAY_SCREEN_DEBUG "Exiting......\r\n\r\n");

                Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡不是管理员/超级用户，正在退出。\r\n\"");
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
                usleep(DISPLAY_TIME);

                Display_Screen_Write((hi_u8 *)"page main");
                break;
            }
            else
            {
                admin_user.permission = authority_Statu;

                Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员/超级用户刷卡成功。\r\n\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"请刷需要删除的卡。\r\n\"");
                usleep(DISPLAY_TIME);
                while(1)
                {
                    brushCard_Statu = RC522_FindCard(&user_id);
                    if(brushCard_Statu == BRUSH_FIND)
                    {
                        authority_Statu = Card_Is_Database(user_id);
                        if(authority_Statu == AUTHORITY_NONE)
                        {

                            Display_Screen_Write((hi_u8 *)"t0.txt=\"\"");
                            Display_Screen_Write((hi_u8 *)"page deluser");

                            Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");

                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡不在数据库中，无法删除，请重新刷卡。\r\n\"");
                            usleep(500000);
                        }
                        else if(authority_Statu == AUTHORITY_ROOT)
                        {

                            Display_Screen_Write((hi_u8 *)"t0.txt=\"\"");
                            Display_Screen_Write((hi_u8 *)"page deluser");

                            Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");

                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡是超级用户，无法删除，请重新刷卡。\r\n\"");
                        }
                        else
                        {
                            del_user.userid = user_id;
                            del_user.permission = authority_Statu;
                            if(admin_user.permission > del_user.permission)
                            {
                                Delete(&del_user, RC522_Database);
                                g_user_num--;


                                hi_flash_erase(FLASH_USERINFO_OFFSET, 4096);
                                hi_flash_erase(FLASH_USERINFO_USER_NUM, 4096);
                                Flash_Write(FLASH_USERINFO_OFFSET, RC522_Database, g_user_num, HI_TRUE);

                                Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"删除成功。\r\n\"");
                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
                                usleep(DISPLAY_TIME);

                                Display_Screen_Write((hi_u8 *)"page main");
                                return;
                            }
                            else
                            {

                                Display_Screen_Write((hi_u8 *)"t0.txt=\"删除用户：\r\n\"");
                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"删除失败。\r\n\"");
                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"此用户的权限需小于验证用户\r\n\"");
                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
                                usleep(DISPLAY_TIME);

                                Display_Screen_Write((hi_u8 *)"page main");
                                return;
                            }
                        }
                    }
                    else
                    {
                        printf(RC522_DEBUG "BRUSH_NONE\r\n");
                    }

                    ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
                    if(ret == 0)
                    {
                        if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
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

        ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
        if(ret == 0)
        {
            if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
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

    usleep(500000);


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
            if((authority_Statu == AUTHORITY_NO) || (authority_Statu == AUTHORITY_USER))
            {

                printf(DISPLAY_SCREEN_DEBUG "This card is not an administrator and is exiting.\r\n");
                printf(DISPLAY_SCREEN_DEBUG "Exiting......\r\n\r\n");

                Display_Screen_Write((hi_u8 *)"t0.txt=\"Login time limit setting:\"\r\n");
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"This card is not an administrator and is exiting.\"\r\n");
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\"");
                usleep(DISPLAY_TIME);

                Display_Screen_Write((hi_u8 *)"page main");
                break;
            }
            else
            {

                Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员刷卡成功。\"\r\n");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"请选择要设置时间限制的用户卡。\"");
                usleep(DISPLAY_TIME);
                admin_user.permission = authority_Statu;
                while(1)
                {
                    brushCard_Statu = RC522_FindCard(&user_id);
                    if(brushCard_Statu == BRUSH_FIND)
                    {
                        authority_Statu = Card_Is_Database(user_id);
                        login_time_user.userid = user_id;
                        login_time_user.permission = authority_Statu;
                        if(login_time_user.permission == AUTHORITY_NO)
                        {

                            Display_Screen_Write((hi_u8 *)"t0.txt=\"\"");
                            Display_Screen_Write((hi_u8 *)"page login");

                            Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"不在数据库中，请重新刷卡。\"");
                        }
                        else if(login_time_user.permission < admin_user.permission)
                        {

                            Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"刷卡成功。\"\r\n");
                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"请输入限制登录时间：\"");
                            usleep(DISPLAY_TIME);
                            while(1)
                            {

                                ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
                                if(ret == 0)
                                {
                                    if(strstr((const char *)Rxdata, (const char *)"return") != NULL)
                                    {
                                        printf(DISPLAY_SCREEN_DEBUG "return\r\n");
                                        return;
                                    }
                                    else if(strstr((const char *)Rxdata, (const char *)"ok") != NULL)
                                    {
                                        if(strstr((const char *)Rxdata, (const char *)"forever=1") != NULL)
                                        {
                                            login_time_user.time_is_forever = FOREVER_YES;
                                            printf("login_time_user.time_is_forever=%d\r\n", FOREVER_YES);
                                            if(login_time_user.permission == AUTHORITY_ADMIN)
                                            {
                                                printf("Failed to promote permission\r\n");
                                                printf("Exiting......\r\n");

                                                Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
                                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"提升权限失败。\"\r\n");
                                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\"");
                                                usleep(DISPLAY_TIME);

                                                Display_Screen_Write((hi_u8 *)"page main");
                                                Display_Screen_Write((hi_u8 *)"login.r0.val=0");
                                                Display_Screen_Write((hi_u8 *)"login.r1.val=1");
                                                return;
                                            }
                                        }
                                        else if((ptr = strstr((const char *)Rxdata, (const char *)"forever=0")) != NULL)
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
                                            P->data.permission = login_time_user.permission + 1;
                                        }
                                        printf("Login time limit setting successful.\r\n");
                                        printf("Exiting......\r\n");

                                        Display_Screen_Write((hi_u8 *)"t0.txt=\"登录时间限制设置：\"\r\n");
                                        Display_Screen_Write((hi_u8 *)"t0.txt+=\"操作成功。\"\r\n");
                                        Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\"");
                                        usleep(DISPLAY_TIME);

                                        Display_Screen_Write((hi_u8 *)"page main");
                                        Display_Screen_Write((hi_u8 *)"login.r0.val=0");
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

                    ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
                    if(ret == 0)
                    {
                        if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
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

        ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
        if(ret == 0)
        {
            if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
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
    UserInfo admin_user;
    UserInfo operate_user;
    LinkList P;
    printf("Permission_Card\r\n");

    Display_Screen_Write((hi_u8 *)"page permission");

    usleep(500000);

    Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");

    Display_Screen_Write((hi_u8 *)"t0.txt+=\"请使用管理员/超级用户卡。\r\n\"");

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

    Display_Screen_Write((hi_u8 *)"vis n1,0");
    Display_Screen_Write((hi_u8 *)"vis n2,0");
    Display_Screen_Write((hi_u8 *)"vis n3,0");

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
            if((authority_Statu != AUTHORITY_ADMIN) && (authority_Statu != AUTHORITY_ROOT))
            {

                printf(DISPLAY_SCREEN_DEBUG "This card is not an administrator and is exiting.\r\n");
                printf(DISPLAY_SCREEN_DEBUG "Exiting......\r\n\r\n");

                Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"此卡不是管理员/超级用户卡。\r\n\"");
                Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
                usleep(DISPLAY_TIME);

                Display_Screen_Write((hi_u8 *)"page main");
                break;
            }
            else
            {
                admin_user.userid = user_id;
                admin_user.permission = authority_Statu;

                Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"管理员/超级用户刷卡成功。\r\n\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"请刷需要操作权限的卡。\r\n\"");
                usleep(DISPLAY_TIME);
                while(1)
                {
                    brushCard_Statu = RC522_FindCard(&user_id);
                    if(brushCard_Statu == BRUSH_FIND)
                    {
                        authority_Statu = Card_Is_Database(user_id);
                        if(authority_Statu == AUTHORITY_NONE)
                        {
                            Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"不在数据库中，操作失败。\r\n\"");
                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

                            usleep(DISPLAY_TIME);
                            Display_Screen_Write((hi_u8 *)"page main");
                            return;
                        }
                        else if(authority_Statu == AUTHORITY_ROOT)
                        {
                            Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"超级用户不可操作，操作失败\r\n\"");
                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");

                            usleep(DISPLAY_TIME);
                            Display_Screen_Write((hi_u8 *)"page main");
                            return;
                        }
                        else
                        {
                            operate_user.userid = user_id;
                            operate_user.permission = authority_Statu;


                            if(admin_user.permission > operate_user.permission)
                            {

                                Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"允许操作，请设置参数。\r\n\"");
                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"Wait......\r\n\"");
                                usleep(DISPLAY_TIME);

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
                                        if(strstr((const char *)Rxdata, (const char *)"return") != NULL)
                                        {
                                            printf(DISPLAY_SCREEN_DEBUG "return\r\n");
                                            Display_Screen_Write((hi_u8 *)"page main");
                                            return;
                                        }
                                        else if(strstr((const char *)Rxdata, (const char *)"ok") != NULL)
                                        {
                                            if((ptr = strstr((const char *)Rxdata, (const char *)"forever=1")) != NULL)
                                            {
                                                P = Find(&operate_user, RC522_Database);
                                                P->data.permission_time_is_forever = YES_YES;
                                                P->data.permission_last = P->data.permission;

                                                if(*(ptr+11) == '1')
                                                {
                                                    P->data.permission = AUTHORITY_NO;

                                                }
                                                else if(*(ptr+11) == '2')
                                                {
                                                    P->data.permission = AUTHORITY_USER;

                                                }
                                                else if(*(ptr+11) == '3')
                                                {
                                                    if(admin_user.permission == AUTHORITY_ROOT)
                                                    {
                                                        P->data.permission = AUTHORITY_ADMIN;

                                                        ptr = NULL;
                                                    }
                                                    else
                                                    {
                                                        Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
                                                        Display_Screen_Write((hi_u8 *)"t0.txt+=\"不允许操作，请经过超级用户授权。\r\n\"");
                                                        usleep(DISPLAY_TIME);

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
                                            else if((ptr = strstr((const char *)Rxdata, (const char *)"forever=0")) != NULL)
                                            {
                                                P = Find(&operate_user, RC522_Database);
                                                P->data.permission_last = P->data.permission;
                                                P->data.permission_time_is_forever = NO_NO;
                                                P->data.permission_time_hours = *(ptr+11);
                                                P->data.permission_time_minutes = *(ptr+17);
                                                P->data.permission_time_seconds = *(ptr+23);

                                                if(*(ptr+29) == '1')
                                                {
                                                    P->data.permission = AUTHORITY_NO;
                                                }
                                                else if(*(ptr+29) == '2')
                                                {
                                                    P->data.permission = AUTHORITY_USER;
                                                }
                                                else if(*(ptr+29) == '3')
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


                                            hi_flash_erase(FLASH_USERINFO_OFFSET, 4096);
                                            hi_flash_erase(FLASH_USERINFO_USER_NUM, 4096);
                                            Flash_Write(FLASH_USERINFO_OFFSET, RC522_Database, g_user_num, HI_TRUE);
                                            printf("Operate successful.\r\n");
                                            printf("Exiting......\r\n");


                                            Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
                                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"操作成功。\r\n\"");
                                            Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
                                            usleep(DISPLAY_TIME);

                                            Display_Screen_Write((hi_u8 *)"page main");
                                            Display_Screen_Write((hi_u8 *)"permission.r0.val=1");
                                            Display_Screen_Write((hi_u8 *)"permission.r1.val=0");
                                            return;
                                        }
                                        else
                                        {
                                            ;
                                        }
                                        memset(&Rxdata, 0, sizeof(Rxdata));
                                    }
                                    printf("wait......\r\n");
                                    usleep(1000000);
                                }
                            }
                            else
                            {

                                Display_Screen_Write((hi_u8 *)"t0.txt=\"权限管理：\r\n\"");
                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"权限不够\r\n\"");
                                Display_Screen_Write((hi_u8 *)"t0.txt+=\"Exiting......\r\n\"");
                                usleep(DISPLAY_TIME);

                                Display_Screen_Write((hi_u8 *)"page main");
                                return;
                            }
                        }
                    }
                    else
                    {
                        printf(RC522_DEBUG "BRUSH_NONE\r\n");
                    }

                    ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
                    if(ret == 0)
                    {
                        if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
                        {
                            printf(DISPLAY_SCREEN_DEBUG "return\r\n");
                            Display_Screen_Write((hi_u8 *)"page main");
                            return;
                        }
                        memset(&Rxdata, 0, sizeof(Rxdata));
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

        ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
        if(ret == 0)
        {
            if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
            {
                printf(DISPLAY_SCREEN_DEBUG "return\r\n");
                Display_Screen_Write((hi_u8 *)"page main");
                break;
            }
            memset(&Rxdata, 0, sizeof(Rxdata));
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
void Settings_Card(void)
{
    BrushCardStatus brushCard_Statu;
    unsigned int user_id;
    AuthorityStatus authority_Statu;
    unsigned char Rxdata[70] = {0};
    unsigned int Rxdata_len;
    char ssid[SSID_LEN_MAX] = {0};
    char passwd[PASSWD_LEN_MAX] = {0};
    char ret;
    char *ptr1 = NULL;
    char *ptr2 = NULL;
    int connect_status;
    unsigned char tmp[2] ={0};
    printf("Settings_Card\r\n");

    Display_Screen_Write((hi_u8 *)"page settings");

    usleep(500000);
    while(1)
    {

        ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 200);
        if(ret == 0)
        {
            if(strncmp((const char *)Rxdata, (const char *)"wifi", Rxdata_len) == 0)
            {
                printf(DISPLAY_SCREEN_DEBUG "wifi\r\n");

                Display_Screen_Write((hi_u8 *)"page wifi");
                while(1)
                {

                    ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 200);
                    if(ret == 0)
                    {


                        if(strstr((const char *)Rxdata, (const char *)"disconnect") != NULL)
                        {
                            printf(DISPLAY_SCREEN_DEBUG "wifi disconnect\r\n");


                            Wifi_Disconnect();
                            wifi_connected = 0;
                            mqtt_enable = 0;
                            Display_Screen_Write((hi_u8 *)"wifi.b0.txt=\"Connect\"");
                            Display_Screen_Write((hi_u8 *)"p0.pic=2");
                            Display_Screen_Write((hi_u8 *)"main.p0.pic=2");
                        }

                        else if(strstr((const char *)Rxdata, (const char *)"connect") != NULL)
                        {
                            printf(DISPLAY_SCREEN_DEBUG "wifi connect\r\n");
                            ptr1 = strstr((const char *)Rxdata, (const char *)"ssid=");
                            ptr2 = strstr((const char *)Rxdata, (const char *)",passwd=");
                            *(ptr2) = '\0';
                            sprintf((char *)&ssid, "%s", ptr1+5);
                            *(ptr2) = ',';
                            sprintf((char *)&passwd, "%s", ptr2+8);
                            ptr1 = NULL;
                            ptr2 = NULL;
                            printf("SSID:%s\r\n",ssid);
                            printf("PASSWD:%s\r\n",passwd);

                            connect_status = Wifi_Connect(ssid, passwd);
                            if(connect_status == 0)
                            {

                                wifi_connected = 1;
                                mqtt_enable = 1;

                                Display_Screen_Write((hi_u8 *)"t3.txt=\"\"");
                                Display_Screen_Write((hi_u8 *)"wifi.b0.txt=\"Disconnect\"");
                                Display_Screen_Write((hi_u8 *)"p0.pic=1");
                                Display_Screen_Write((hi_u8 *)"main.p0.pic=1");
                            }
                            else
                            {
                                ;
                            }
                        }
                        else if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
                        {
                            memset(&Rxdata, 0, sizeof(Rxdata));
                            printf(DISPLAY_SCREEN_DEBUG "return\r\n");

                            Display_Screen_Write((hi_u8 *)"page settings");

                            usleep(500000);
                            break;
                        }
                        else
                        {
                            ;
                        }
                        memset(&Rxdata, 0, sizeof(Rxdata));
                    }
                    printf("wait......\r\n");
                    usleep(1000000);
                }
            }
            else if(strncmp((const char *)Rxdata, (const char *)"clock_in_time", Rxdata_len) == 0)
            {
                Display_Screen_Write((hi_u8 *)"page white_board");

                usleep(500000);

                Display_Screen_Write((hi_u8 *)"t0.txt=\"打卡时间设置：\r\n\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"请使用管理员/超级用户卡。\r\n\"");
                while(1)
                {
                    brushCard_Statu = RC522_FindCard(&user_id);
                    if(brushCard_Statu == BRUSH_FIND)
                    {
                        authority_Statu = Card_Is_Database(user_id);
                        if((authority_Statu == AUTHORITY_ADMIN) || (authority_Statu == AUTHORITY_ROOT))
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

                            Display_Screen_Write((hi_u8 *)"page main");

                            usleep(500000);
                            memset(&Rxdata, 0, sizeof(Rxdata));
                            return;
                        }
                        memset(&Rxdata, 0, sizeof(Rxdata));
                    }
                    printf("wait......\r\n");
                    usleep(1000000);
                }
                printf(DISPLAY_SCREEN_DEBUG "clock_in_time\r\n");

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
                        if((ptr1 = strstr((const char *)Rxdata, (const char *)"ok")) != NULL)
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
                            memset(&Rxdata, 0, sizeof(Rxdata));
                            printf(DISPLAY_SCREEN_DEBUG "ok\r\n");

                            Display_Screen_Write((hi_u8 *)"page main");

                            usleep(500000);
                            return;
                        }
                        else if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
                        {
                            memset(&Rxdata, 0, sizeof(Rxdata));
                            printf(DISPLAY_SCREEN_DEBUG "return\r\n");

                            Display_Screen_Write((hi_u8 *)"page settings");

                            usleep(500000);
                            break;
                        }
                        else
                        {
                            ;
                        }
                        memset(&Rxdata, 0, sizeof(Rxdata));
                    }
                    printf("wait......\r\n");
                    usleep(1000000);
                }
            }
            else if(strncmp((const char *)Rxdata, (const char *)"system_time", Rxdata_len) == 0)
            {
                Display_Screen_Write((hi_u8 *)"page white_board");

                usleep(500000);

                Display_Screen_Write((hi_u8 *)"t0.txt=\"系统时间设置：\r\n\"");

                Display_Screen_Write((hi_u8 *)"t0.txt+=\"请使用管理员/超级用户卡。\r\n\"");
                while(1)
                {
                    brushCard_Statu = RC522_FindCard(&user_id);
                    if(brushCard_Statu == BRUSH_FIND)
                    {
                        authority_Statu = Card_Is_Database(user_id);
                        if((authority_Statu == AUTHORITY_ADMIN) || (authority_Statu == AUTHORITY_ROOT))
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

                            Display_Screen_Write((hi_u8 *)"page main");

                            usleep(500000);
                            memset(&Rxdata, 0, sizeof(Rxdata));
                            return;
                        }
                        memset(&Rxdata, 0, sizeof(Rxdata));
                    }
                    printf("wait......\r\n");
                    usleep(1000000);
                }
                printf(DISPLAY_SCREEN_DEBUG "system_time\r\n");

                Display_Screen_Write((hi_u8 *)"page system_time");
                while(1)
                {

                    ret = Display_Screen_Read_Timeout(Rxdata, &Rxdata_len, 50);
                    if(ret == 0)
                    {
                        if(strstr((const char *)Rxdata, (const char *)"edit") != NULL)
                        {
                            printf(DISPLAY_SCREEN_DEBUG "system_time edit\r\n");

                            Display_Screen_Write_Time(0,0);
                            Display_Screen_Write_Time(0,1);
                            Display_Screen_Write_Time(0,2);
                            Display_Screen_Write_Time(0,5);
                            Display_Screen_Write_Time(0,4);
                            Display_Screen_Write_Time(0,3);
                            sys_Time_Display = 0;
                            Display_Screen_Write((hi_u8 *)"system_time.b0.txt=\"OK\"");
                        }
                        else if((ptr1 = strstr((const char *)Rxdata, (const char *)"ok")) != NULL)
                        {
                            printf(DISPLAY_SCREEN_DEBUG "system_time ok\r\n");



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
                            sys_Time_Display = 1;
                            Display_Screen_Write((hi_u8 *)"system_time.b0.txt=\"Edit\"");
                        }
                        else if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
                        {
                            memset(&Rxdata, 0, sizeof(Rxdata));
                            printf(DISPLAY_SCREEN_DEBUG "return\r\n");

                            Display_Screen_Write((hi_u8 *)"page settings");

                            usleep(500000);
                            break;
                        }
                        else
                        {
                            ;
                        }
                        memset(&Rxdata, 0, sizeof(Rxdata));
                    }
                    printf("wait......\r\n");
                    usleep(1000000);
                }
            }
            else if(strncmp((const char *)Rxdata, (const char *)"return", Rxdata_len) == 0)
            {
                memset(&Rxdata, 0, sizeof(Rxdata));
                printf(DISPLAY_SCREEN_DEBUG "return\r\n");

                Display_Screen_Write((hi_u8 *)"page main");
                break;
            }
            else
            {
                continue;
            }
            memset(&Rxdata, 0, sizeof(Rxdata));
        }
        printf("wait......\r\n");
        usleep(1000000);
    }
}
