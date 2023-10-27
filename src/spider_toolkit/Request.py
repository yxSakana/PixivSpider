# -*- coding: utf-8 -*-
"""  
  @projectName WeatherSpider
  @file Request.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-04 19:08
"""
import os.path
import sys
from time import sleep
from typing import Optional

import requests.sessions

from spider_toolkit.Configure import Configure
from utils.logger import Logger


USER_AGENT = {
    "google_chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}


class Requester(object):
    REQUESTS_SUCCESS_COUNT = 0
    REQUESTS_FAILED_COUNT = 0

    def __init__(self, config: Configure):
        self.configure_content: dict = {}
        self.headers: dict = {
            "User-Agent": USER_AGENT["google_chrome"]
        }  # headers 的 cookie 默认为指定的第一个 cookie 文件的内容
        self.cookie_files: list = []
        self.cookie_pools: list = []
        self.proxies: dict = {
            "http": "",
            "https": ""
        }
        self.requests_failed_count: int = 0

        self.session: requests.Session = requests.session()
        self.configure: Configure = config
        self.logger = Logger.get_logger(self.__class__.__name__)

        self.initConfigure()

    def initConfigure(self) -> None:
        try:
            self.configure_content = self.configure.config_json["spider"]["Requests"]

            self.proxies = self.configure_content["proxies"]
            self.cookie_files = [os.path.abspath(_) for _ in self.configure_content["cookie_files"]]
            for cookie_file in self.cookie_files:
                self.cookie_pools.append(Configure.readFile(cookie_file, self.logger) or None)
            self.headers["cookie"] = self.cookie_pools[0]
        except KeyError as e:
            self.logger.error("KeyError: %s", e)
            sys.exit(1)

    def reloadConfigure(self):
        self.initConfigure()

    def get(self,
            url: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None,
            cookie: Optional[str] = None) -> requests.Response:
        """

        :param url:
        :param params:
        :param headers: if None: header = self.headers
        :param cookie: if None: headers["cookie"] = self.headers["cookie"]
        :return:
        """
        headers = headers or self.headers
        headers["cookie"] = cookie or self.headers["cookie"]
        for i in range(4):
            if self.requests_failed_count >= self.configure_content["how_many_error_sleep"]:
                self.requests_failed_count -= 1
                sleep(self.configure_content["interval_after_error"])
            try:
                response = self.session.get(url, params=params, headers=headers,
                                            proxies=self.proxies, timeout=self.configure_content["timeout"])
                if response.ok:
                    Requester.REQUESTS_SUCCESS_COUNT += 1
                    return response
                else:
                    self.logger.warning("Required Failed: Required Code Error(%d) => %s", response.status_code, url)
                    self.requestsFailedHandle()
            except requests.exceptions.ReadTimeout:
                self.logger.warning("Required Failed: timeout => %s", url)
                self.requestsFailedHandle()

    def requestsFailedHandle(self) -> None:
        Requester.REQUESTS_FAILED_COUNT += 1
        self.requests_failed_count += 1
        if self.requests_failed_count >= self.configure_content["how_many_error_sleep"]:
            self.requests_failed_count -= 1
            sleep(self.configure_content["interval_after_error"])
