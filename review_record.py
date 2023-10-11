import datetime
import json
import os
from selenium.common import WebDriverException
from selenium.common import exceptions, SessionNotCreatedException
import error_code
from datetime import timedelta
from selenium.webdriver.common.by import By
import browser_active
import regular_expression

g_user_id = ''
g_user_key = ''
g_browser = ''
g_visible = True
g_moderator_id = ''
g_review_type = ''
g_link = ''

g_mode = ''
WAIT_TIME = 15
g_month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

err = error_code.err_class()
g_xpath = regular_expression.Xpath()


def confirm_submit(xpath: str):
    driver.find_element(By.XPATH, value=xpath).submit()


def get_cfg(config, mode='build'):
    ret = err.ok
    global g_user_id, g_user_key, g_browser, g_link, driver_op, driver
    if mode == 'build':
        global g_moderator_id, g_review_type
        g_user_id = str(config['user id'])
        g_user_key = str(config['user key'])
        g_browser = str(config['browser'])
        g_moderator_id = config['moderator id']
        g_review_type = config['review area']
        g_link = str(config['record link'])
    else:
        g_user_id = str(config['user id'])
        g_user_key = str(config['user key'])
        g_browser = str(config['browser'])
        g_link = str(config['close link'])
    try:
        driver_op = browser_active.WebDriverOp(browser=g_browser, url=g_link)
        driver = driver_op.driver
    except SessionNotCreatedException:
        ret = err.driver_over
    return ret



def time_get(input_time: str):
    today_time = datetime.date.today()
    yesterday_time = today_time - timedelta(days=1)
    tomorrow_time = today_time - timedelta(days=-1)
    now_year = today_time.strftime('%m %d %Y').split(' ')[2]
    if input_time.count('Yesterday') != 0:
        res_day = yesterday_time.strftime('%m %d %Y')
        res_day_month = int(res_day.split(' ')[0])
        res_day = res_day.replace(res_day.split(' ')[0], g_month[res_day_month - 1], 1)
    elif input_time.count('Today') != 0:
        res_day = today_time.strftime('%m %d %Y')
        res_day_month = int(res_day.split(' ')[0])
        res_day = res_day.replace(res_day.split(' ')[0], g_month[res_day_month - 1], 1)
    elif input_time.count('Tomorrow') != 0:
        res_day = tomorrow_time.strftime('%m %d %Y')
        res_day_month = int(res_day.split(' ')[0])
        res_day = res_day.replace(res_day.split(' ')[0], g_month[res_day_month - 1], 1)
    else:
        day_list = input_time.split(' ')
        month = day_list[0]
        day = day_list[1]
        year = now_year
        res_day = month + ' ' + day + ' ' + year
    return res_day


def record_program(config):
    res = get_cfg(config)
    while True:
        if res != err.ok:
            break
        with open('.private/_record_link.json', 'r') as cfg_obj:
            cfg = json.load(cfg_obj)
            if os.path.exists('.private/_record_link.json') is False:
                res = err.cfg_err
                break
            if err.void_check(cfg['record link']) is True:
                res = err.cfg_err
                break
            record_link = cfg['record link']
        # register
        driver_op.register_code_beamer(g_user_id, g_user_key)

        review_name = driver_op.get_text(g_xpath.review_name)
        driver_op.click(g_xpath.review_info)
        start_data = driver_op.get_text(g_xpath.review_start_time)
        start_data = time_get(start_data)
        end_data = driver_op.get_text(g_xpath.review_end_time)
        end_data = time_get(end_data)
        driver.get(record_link)
        driver_op.click(g_xpath.review_new_item)
        driver_op.click(g_xpath.chose_moderator)
        driver_op.switch_to_frame(g_xpath.chose_moderator_frame)
        driver_op.send_key(g_xpath.search_moderator, g_moderator_id)
        driver_op.click(g_xpath.search_bt)
        driver_op.click(g_xpath.chose_bt)
        confirm_submit(g_xpath.search_confirm_bt)
        driver_op.switch_to_back()
        driver_op.select_item(g_xpath.review_obj_type, 'Tracker Items')
        driver_op.click(g_xpath.review_link_select)
        driver_op.switch_to_frame(g_xpath.chose_moderator_frame)
        driver_op.click(g_xpath.review_link_label)
        driver_op.send_key(g_xpath.review_link_input, g_link)
        driver_op.click(g_xpath.insert_link_bt)
        driver_op.switch_to_back()
        driver_op.select_item(g_xpath.review_select_area, g_review_type)
        driver_op.send_key(g_xpath.review_start_data, start_data)
        driver_op.send_key(g_xpath.review_end_data, end_data)
        driver_op.send_key(g_xpath.review_summary_input, review_name)
        break
    return res


# ----------------------------------------------------------------------------------------------------------------------
def get_info_num(input_list):
    qus_num = 0
    propose_num = 0
    problem_num = 0
    for option in input_list:
        option_content: str = option.text
        if option_content.count('Question') != 0:
            bracket_index = option_content.index('(')
            qus_num = int(option_content[bracket_index + 1])
        elif option_content.count('Proposed') != 0:
            bracket_index = option_content.index('(')
            propose_num = int(option_content[bracket_index + 1])
        elif option_content.count('Problem') != 0:
            bracket_index = option_content.index('(')
            problem_num = int(option_content[bracket_index + 1])
        else:
            continue
    return qus_num, propose_num, problem_num


def close_program(config):
    ret = get_cfg(config, mode='close')
    if ret != err.ok:
        return ret
    # register
    driver_op.register_code_beamer(g_user_id, g_user_key)

    review_link = driver_op.get_text(g_xpath.close_get_link)
    driver.get(review_link)
    driver_op.click(g_xpath.close_feed_back)
    select_list = driver_op.get_options(g_xpath.feed_back_options)
    question_num, propose_num, problem_num = get_info_num(select_list)
    driver.back()
    driver.back()
    driver_op.click(g_xpath.close_edit)
    driver_op.clear_content(g_xpath.close_question)
    driver_op.send_key(g_xpath.close_question, str(question_num))
    driver_op.clear_content(g_xpath.close_problem)
    driver_op.send_key(g_xpath.close_problem, str(problem_num))
    driver_op.clear_content(g_xpath.close_propose)
    driver_op.send_key(g_xpath.close_propose, str(propose_num))
    driver_op.click(g_xpath.close_save)
    driver_op.click(g_xpath.submit_close)
    return ret


def review_program(config):
    res = err.ok
    try:
        if config['mode'] == 'build':
            res = record_program(config)
        else:
            res = close_program(config)
    except (WebDriverException, Exception):
        res = err.driver_interrupt
    return res
