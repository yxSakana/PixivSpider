from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

from utils.logger import Logger

class Login(object):
    def __init__(self) -> None:
        self.__login_api = "https://accounts.pixiv.net/login"
        self.logger = Logger.get_logger(__class__.__name__)

    def login(self, username: str, passwd: str) -> str:
        """login to get cookies

        :param str username:
        :param str passwd:
        :return str: cookies
        """
        try:
            driver = webdriver.Chrome()
            driver.get(self.__login_api)
            unaem_input = driver.find_element(By.XPATH, '//input[contains(@class, sc-bn9ph6) and contains(@class, "degQSE")]')
            passwd_input = driver.find_element(By.XPATH, '//input[contains(@class, sc-bn9ph6) and contains(@class, "hfoSmp")]')
            unaem_input.send_keys(username)
            passwd_input.send_keys(passwd)
            unaem_input.submit()
            sleep(4)
            driver.find_element(By.XPATH, '//a[@data-gtm-category="mail_address_notice_confirmation" and @data-gtm-action="remind_me_later"]').click()

            cookies_list = driver.get_cookies()
            cookies = ""
            for cookie in cookies_list:
                cookies += cookie["name"] + " = " + cookie["value"] + ";"
            cookies = cookies[:-1] 
            return cookie
        except Exception:
            self.logger.erroe("Failed to login!")
            return None
