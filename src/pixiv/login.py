from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from utils.logger import Logger


class Login(object):
    def __init__(self) -> None:
        self.__login_api = "https://accounts.pixiv.net/login"
        self.logger = Logger.get_logger(__class__.__name__)

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-infobars")  # 禁止顶部信息栏
        options.add_argument("--disable-notifications")  # 禁止网页通知
        options.add_argument("--disable-popup-blocking")  # 禁止弹出窗口拦截功能
        options.add_argument("--disable-extensions")  # 禁止网页拓展
        options.add_argument("--start-maximized")  # 最大化
        # options.add_argument("--headless")  # 无界面
        # options.add_argument("--disable-gpu")  # 禁止GPU加速
        self.driver = webdriver.Chrome(options)

    def login(self, username: str, passwd: str) -> str:
        """login to get cookies

        :param str username:
        :param str passwd:
        :return str: cookies
        """
        try:
            self.driver.get(self.__login_api)
            uname_input = self.driver.find_element(By.XPATH, '//input[contains(@class, sc-bn9ph6) and contains(@class, "degQSE")]')
            passwd_input = self.driver.find_element(By.XPATH, '//input[contains(@class, sc-bn9ph6) and contains(@class, "hfoSmp")]')
            uname_input.send_keys(username)
            passwd_input.send_keys(passwd)
            uname_input.submit()
            sleep(4)
            try:
                self.driver.find_element(By.XPATH, '//a[@data-gtm-category="mail_address_notice_confirmation" and @data-gtm-action="remind_me_later"]').click()
            except NoSuchElementException as e:
                self.logger.error(e)

            cookies_list = self.driver.get_cookies()
            cookies = ""
            for cookie in cookies_list:
                cookies += cookie["name"] + " = " + cookie["value"] + ";"
            cookies = cookies[:-1]
            self.driver.quit()
            return cookies
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Failed to login!")
            return ""
