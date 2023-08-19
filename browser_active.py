from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import regular_expression
import time

class WebDriverOp:
    def __init__(self, browser='Chrome', url=None, implicitly_wait=True, wait_time=15, headless=False):
        self.browser = browser
        self.url = url
        self.wait_time = wait_time
        self.headless = headless
        self.driver = None
        self.mention = None
        self.browser_version = ''
        self.__get_driver(link=url)
        self.xpath = regular_expression.Xpath()
        if implicitly_wait is True:
            self.__wait_loading()

    # -----------------------------------------------browser operate--------------------------------------------------------
    def __prompt(self):
        pass

    def __get_driver(self, link):
        if self.browser == 'chrome' or self.browser == 'Chrome':
            from selenium.webdriver.chrome.service import Service
            option = webdriver.ChromeOptions()
            if self.headless is True:
                option.add_argument('--headless')
            option.add_argument('--start-maximized')  # max window
            option.add_argument('--incognito')  # implicit mode
            option.add_argument('--ignore-certificate-errors')
            option.add_argument('--ignore-ssl-errors')
            self.driver = webdriver.Chrome(service=Service('.driver/chromedriver.exe'), options=option)
            self.browser_version = self.driver.capabilities['browserVersion']
        else:
            from selenium.webdriver.edge.service import Service
            option = webdriver.EdgeOptions()
            if self.headless is True:
                option.add_argument('--headless')
            option.add_argument('--start-maximized')
            option.add_argument('--ignore-certificate-errors')
            option.add_argument('--ignore-ssl-errors')
            self.driver = webdriver.Edge(service=Service('.driver/msedgedriver.exe'), options=option)
            self.browser_version = self.driver.capabilities['browserVersion']
        self.driver.get(link)

    def __wait_loading(self):
        self.driver.implicitly_wait(self.wait_time)

    def switch_to_frame(self, xpath: str):
        frame = self.driver.find_element(By.XPATH, value=xpath)
        self.driver.switch_to.frame(frame)

    def web_refresh(self):
        self.driver.refresh()

    def switch_to_back(self):
        self.driver.switch_to.default_content()

    def context_click(self, xpath: str):
        ActionChains(self.driver).context_click(self.driver.find_element(By.XPATH, value=xpath)).perform()

    def double_click(self, xpath: str):
        ActionChains(self.driver).double_click(self.driver.find_element(By.XPATH, value=xpath)).perform()

    def click(self, xpath: str):
        self.driver.find_element(By.XPATH, value=xpath).click()

    def move_to_element(self, xpath: str):
        ActionChains(self.driver).scroll_to_element(self.driver.find_element(By.XPATH, value=xpath)).perform()

    def send_key(self, xpath: str, content: str):
        self.driver.find_element(By.XPATH, value=xpath).send_keys(content)

    def clear_content(self, xpath: str):
        self.driver.find_element(By.XPATH, value=xpath).clear()

    def move_mouse_to(self, xpath: str):
        ActionChains(self.driver).move_to_element(to_element=self.driver.find_element(By.XPATH, value=xpath)).perform()

    def drag_element_to(self, start_xpath, end_xpath):
        start_ele = self.driver.find_element(By.XPATH, value=start_xpath)
        end_ele = self.driver.find_element(By.XPATH, value=end_xpath)
        ActionChains(self.driver).drag_and_drop(start_ele, end_ele).perform()

    def select_item(self, xpath: str, content: str):
        Select(self.driver.find_element(By.XPATH, value=xpath)).select_by_visible_text(content)

    def wait_item_load(self, xpath: str):
        locator = (By.XPATH, xpath)
        WebDriverWait(self.driver, self.wait_time).until(ec.presence_of_element_located(locator))

    def wait_item_visible(self, xpath: str):
        locator = (By.XPATH, xpath)
        WebDriverWait(self.driver, self.wait_time).until(ec.visibility_of_element_located(locator))

    def wait_item_clickable(self, xpath: str):
        locator = (By.XPATH, xpath)
        WebDriverWait(self.driver, self.wait_time).until(ec.element_to_be_clickable(locator))

    def wait_element_invisible(self, xpath: str):
        locator = (By.XPATH, xpath)
        WebDriverWait(self.driver, self.wait_time).until(ec.invisibility_of_element_located(locator))

    def check_element(self, xpath: str) -> bool:
        ret = False
        elements = self.driver.find_elements(By.XPATH, value=xpath)
        if len(elements) != 0:
            ret = True
        return ret

    def register_code_beamer(self, user, key):
        self.send_key(self.xpath.user_id, user)
        self.send_key(self.xpath.password, key)
        self.driver.find_element(By.XPATH, value=self.xpath.register).submit()
        time.sleep(0.5)

# -----------------------------------------------browser operate--------------------------------------------------------
