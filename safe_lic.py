import datetime
from cryptography.fernet import Fernet
import os

KEY_PATH = r'.private/__cryptograpy/__uncptgph.cy'
LIC_PATH = r'.private/__cryptograpy/__cptgpy.cy'
DeadLine = ''


def check_cryptograpy_file():
    if os.path.exists(KEY_PATH) is False or os.path.exists(LIC_PATH) is False:
        return False
    else:
        return True


def verification():
    global DeadLine
    ret = True
    if check_cryptograpy_file() is False:
        ret = False
    else:
        with open('.private/__cryptograpy/__uncptgph.cy', mode='rb') as key_obj:
            key = key_obj.read()
        with open('.private/__cryptograpy/__cptgpy.cy', mode='rb') as obj:
            content = obj.read()
            cipher_suite = Fernet(key)
            deadline = cipher_suite.decrypt(content).decode()
            DeadLine = deadline
    return ret


def right_verification() -> bool:
    """

    :return: True or False
    """
    if verification() is False:
        return False
    else:
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
