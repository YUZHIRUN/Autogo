import datetime
import json
import os

from selenium.common import WebDriverException
from selenium.common import exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import error_code
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import regular_expression

g_user_id = ''
g_user_key = ''
g_browser = ''
g_visible = True
g_moderator_id = ''
g_review_type = ''
g_record_link = ''
g_close_link = ''

g_mode = ''
WAIT_TIME = 15
g_month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

err = error_code.err_class()
g_xpath = regular_expression.Xpath()


def get_chrome_driver(mode):
    global driver
    if g_browser == 'chrome' or g_browser == 'Chrome':
        from selenium.webdriver.chrome.service import Service
        # if g_visible is False:
        #     option = webdriver.ChromeOptions()
        #     option.add_argument('--headless')
        #     option.add_argument('--ignore-ssl-errors')
        #     option.add_argument('--ignore-certificate-errors')
        #     option.add_experimental_option('detach', True)
        #     driver = webdriver.Chrome(service=Service('.driver/chromedriver.exe'), options=option)
        # else:
        option = webdriver.ChromeOptions()
        option.add_experimental_option('detach', True)
        option.add_argument('--ignore-certificate-errors')
        option.add_argument('--ignore-ssl-errors')
        driver = webdriver.Chrome(service=Service('.driver/chromedriver.exe'), options=option)
    else:
        from selenium.webdriver.edge.service import Service
        # if g_visible is False:
        #     option = webdriver.EdgeOptions()
        #     option.add_argument('--headless')
        #     option.add_argument('--ignore-ssl-errors')
        #     option.add_argument('--ignore-certificate-errors')
        #     option.add_experimental_option('detach', True)
        #     driver = webdriver.Edge(service=Service('.driver/msedgedriver.exe'), options=option)
        # else:
        option = webdriver.EdgeOptions()
        option.add_argument('--ignore-certificate-errors')
        option.add_argument('--ignore-ssl-errors')
        option.add_experimental_option('detach', True)
        driver = webdriver.Edge(service=Service('.driver/msedgedriver.exe'), options=option)
    if mode == 'build':
        driver.get(g_record_link)
    else:
        driver.get(g_close_link)


# -----------------------------------------------browser operate--------------------------------------------------------
def wait_loading():
    driver.implicitly_wait(WAIT_TIME)


def get_text(xpath: str):
    res = driver.find_element(By.XPATH, value=xpath).text
    return res

def get_options(xpath: str):
    res = list()
    res = Select(driver.find_element(By.XPATH, value=xpath)).options
    return res


def context_click(xpath: str):
    ActionChains(driver).context_click(driver.find_element(By.XPATH, value=xpath)).perform()
    wait_loading()


def double_click(xpath: str):
    ActionChains(driver).double_click(driver.find_element(By.XPATH, value=xpath)).perform()
    wait_loading()


def click(xpath: str):
    driver.find_element(By.XPATH, value=xpath).click()
    wait_loading()

def clear_content(xpath: str):
    driver.find_element(By.XPATH, value=xpath).clear()

def move_to_element(xpath: str):
    ActionChains(driver).scroll_to_element(driver.find_element(By.XPATH, value=xpath)).perform()


def send_key(xpath: str, content):
    driver.find_element(By.XPATH, value=xpath).send_keys(content)
    wait_loading()


def confirm_submit(xpath: str):
    driver.find_element(By.XPATH, value=xpath).submit()


def move_mouse_to(xpath: str):
    ActionChains(driver).move_to_element(to_element=driver.find_element(By.XPATH, value=xpath)).perform()


def select_item(xpath: str, content: str):
    Select(driver.find_element(By.XPATH, value=xpath)).select_by_visible_text(content)
    wait_loading()


def wait_item_load(xpath: str):
    locator = (By.XPATH, xpath)
    WebDriverWait(driver, WAIT_TIME).until(ec.presence_of_element_located(locator))


def switch_frame(frame_name):
    driver.switch_to.frame(frame_name)


def switch_back():
    driver.switch_to.parent_frame()


# -----------------------------------------------browser operate--------------------------------------------------------
def get_cfg(config, mode='build'):
    global g_user_id, g_user_key, g_browser
    if mode == 'build':
        global g_record_link, g_moderator_id, g_review_type
        g_user_id = str(config['user id'])
        g_user_key = str(config['user key'])
        g_browser = str(config['browser'])
        g_moderator_id = config['moderator id']
        g_review_type = config['review area']
        g_record_link = str(config['record link'])
    else:
        global g_close_link
        g_user_id = str(config['user id'])
        g_user_key = str(config['user key'])
        g_browser = str(config['browser'])
        g_close_link = str(config['close link'])
    get_chrome_driver(mode)


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
    res = err.ok
    get_cfg(config)
    while True:
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
        driver.maximize_window()
        send_key(g_xpath.user_id, g_user_id)
        send_key(g_xpath.password, g_user_key)
        confirm_submit(g_xpath.register)
        wait_loading()

        review_name = get_text(g_xpath.review_name)
        click(g_xpath.review_info)
        start_data = get_text(g_xpath.review_start_time)
        start_data = time_get(start_data)
        end_data = get_text(g_xpath.review_end_time)
        end_data = time_get(end_data)
        driver.get(record_link)
        click(g_xpath.review_new_item)
        click(g_xpath.chose_moderator)
        wait_loading()
        switch_frame(g_xpath.search_frame_name)
        send_key(g_xpath.search_moderator, g_moderator_id)
        click(g_xpath.search_bt)
        click(g_xpath.chose_bt)
        confirm_submit(g_xpath.search_confirm_bt)
        switch_back()
        select_item(g_xpath.review_obj_type, 'Tracker Items')
        click(g_xpath.review_link_select)
        switch_frame('inlinedPopupIframe')
        click(g_xpath.review_link_label)
        send_key(g_xpath.review_link_input, g_record_link)
        click(g_xpath.insert_link_bt)
        switch_back()
        select_item(g_xpath.review_select_area, g_review_type)
        send_key(g_xpath.review_start_data, start_data)
        send_key(g_xpath.review_end_data, end_data)
        send_key(g_xpath.review_summary_input, review_name)
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
    get_cfg(config, mode='close')
    # register
    driver.maximize_window()
    send_key(g_xpath.user_id, g_user_id)
    send_key(g_xpath.password, g_user_key)
    confirm_submit(g_xpath.register)
    wait_loading()

    review_link = get_text(g_xpath.close_get_link)
    driver.get(review_link)
    click(g_xpath.close_feed_back)
    select_list = get_options(g_xpath.feed_back_options)
    question_num, propose_num, problem_num = get_info_num(select_list)
    driver.back()
    driver.back()
    click(g_xpath.close_edit)
    clear_content(g_xpath.close_question)
    send_key(g_xpath.close_question, question_num)
    clear_content(g_xpath.close_problem)
    send_key(g_xpath.close_problem, problem_num)
    clear_content(g_xpath.close_propose)
    send_key(g_xpath.close_propose, propose_num)
    click(g_xpath.close_save)
    click(g_xpath.submit_close)

def review_program(config):
    res = err.ok
    try:
        if config['mode'] == 'build':
            res = record_program(config)
        else:
            close_program(config)
    except (WebDriverException, Exception):
        res = err.driver_interrupt
    return res
