from selenium.common.exceptions import SessionNotCreatedException
from browser_active import *
import error_code
import regular_expression

g_code_beamer_link = r'http://172.16.200.236:8080/cb/user'
g_browser = ''
g_xpath = regular_expression.Xpath()
err = error_code.err_class()


def account_check(config):
    ret = err.ok
    global g_browser, driver_op, driver
    g_browser = config['browser']
    user_id = config['user id']
    user_key = config['user key']
    try:
        driver_op = WebDriverOp(browser=g_browser, url=g_code_beamer_link, wait_time=2, headless=True)
        driver = driver_op.driver
    except SessionNotCreatedException:
        ret = err.driver_over
        return ret
    driver_op.register_code_beamer(user_id, user_key)
    while True:
        if driver_op.check_element(g_xpath.user_check_ok) is True or driver_op.check_element(g_xpath.user_check_err) is False:
            ret = err.ok
            break
        if driver_op.check_element(g_xpath.user_check_ok) is False or driver_op.check_element(g_xpath.user_check_err) is True:
            ret = err.user_info_err
            break
        break
    driver.quit()
    return ret
