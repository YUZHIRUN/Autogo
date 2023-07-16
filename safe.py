import datetime
from datetime import timedelta

DeadLine = '2024/06/13'

def right_verification() -> bool:
    """

    :return: True or False
    """
    today = datetime.date.today().strftime('%Y/%m/%d')
    deadline_list = DeadLine.split('/')
    today_list = today.split('/')
    to_day = today_list[2]
    to_month = today_list[1]
    to_year = today_list[0]
    obj_year = deadline_list[0]
    obj_month = deadline_list[1]
    obj_day = deadline_list[2]
    while True:
        if to_year < obj_year:
            res = True
            break
        elif to_year > obj_year:
            res = False
            break
        else:
            if to_month < obj_month:
                res = True
                break
            elif to_month > obj_month:
                res = False
                break
            else:
                if to_day <= obj_day:
                    res = True
                    break
                else:
                    res = False
                    break
    return res

