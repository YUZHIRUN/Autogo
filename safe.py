import datetime
from datetime import timedelta

DeadLine = '2024/06/12'

def right_verification() -> bool:
    # """
    #
    # :return: True or False
    # """
    # today = datetime.date.today().strftime('%Y/%m/%d')
    # deadline_list = DeadLine.split('/')
    # today_list = today.split('/')
    # while True:
    #     if int(today_list[0]) > int(deadline_list[0]):
    #         res = False
    #         break
    #     elif int(today_list[0]) == int(today_list[0]):
    #         if int(today_list[1]) > int(deadline_list[1]):
    #             res = False
    #             break
    #         elif int(today_list[1]) == int(deadline_list[1]):
    #             if int(today_list[2]) > int(deadline_list[2]):
    #                 res = False
    #                 break
    #             else:
    #                 res = True
    #         else:
    #             res = True
    #     else:
    #         res = True
    #     break
    return True

