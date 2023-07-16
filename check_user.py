from selenium import webdriver
from selenium.common import WebDriverException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

import error_code
import regular_expression

g_codebeamer_link = r'http://172.16.200.236:8080/cb/user'
WAIT_TIME = 3
g_browser = ''
g_xpath = regular_expression.Xpath()
err = error_code.err_class()


def get_chrome_driver():
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
        option.add_argument('--headless')
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
        option.add_argument('--headless')
        option.add_argument('--ignore-certificate-errors')
        option.add_argument('--ignore-ssl-errors')
        option.add_experimental_option('detach', True)
        driver = webdriver.Edge(service=Service('.driver/msedgedriver.exe'), options=option)
    driver.get(g_codebeamer_link)


# -----------------------------------------------browser operate--------------------------------------------------------
def click(xpath: str):
    driver.find_element(By.XPATH, value=xpath).click()


def send_key(xpath: str, content):
    driver.find_element(By.XPATH, value=xpath).send_keys(content)


def confirm_submit(xpath: str):
    driver.find_element(By.XPATH, value=xpath).submit()


def wait_load():
    driver.implicitly_wait(3)
# -----------------------------------------------browser operate--------------------------------------------------------

def check_element(xpath: str):
    elements = driver.find_elements(By.XPATH, value=xpath)
    if len(elements) == 0:
        res = False
    else:
        res = True
    return res


def account_check(config):
    ret = err.ok
    global g_browser
    g_browser = config['browser']
    user_id = config['user id']
    user_key = config['user key']
    try:
        get_chrome_driver()
    except SessionNotCreatedException:
        ret = err.driver_over
        return ret
    driver.maximize_window()
    send_key(g_xpath.user_id, user_id)
    send_key(g_xpath.password, user_key)
    confirm_submit(g_xpath.register)
    # wait_load()
    while True:
        if check_element(g_xpath.user_check_ok) is True or check_element(g_xpath.user_check_err) is False:
            ret = err.ok
            break
        if check_element(g_xpath.user_check_ok) is False or check_element(g_xpath.user_check_err) is True:
            ret = err.user_info_err
            break
        break
    driver.close()
    return ret
