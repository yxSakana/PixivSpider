# -*- coding: utf-8 -*-
"""  
  @projectName WeatherSpider
  @file Configure.py
  @brief 

    {
        "spider": {
            "website": "",
            "Downloader": {
                "download_path": ""
            },
            "Requests": {
                "cookie_files": [
                    "config/cookies.txt"
                ],
                "proxies": {
                    "http": "127.0.0.1:7890",
                    "https": "127.0.0.1:7890"
                },
                "timeout": 5,  # 请求超时时间
                "how_many_error_sleep": 4,  # 发生多少请求错误后sleep
                "interval_after_error": 5  # 请求发生指定数目错误后sleep的时间
            },
            "Database": {
                "mongo": {
                    "username": "",
                    "password": "",
                    "ip": "",
                    "port": "",
                    "db_name": "",
                    "collection": ""
                }
            }
        },
        "logged": true
    }
 
  @author yx 
  @date 2023-08-04 19:09
"""

import json
import logging
import os.path
import sys
from typing import Optional

from utils.logger import Logger


class Configure(object):
    def __init__(self, config_name: str = "config/config.json"):
        self.config_filename = os.path.abspath(config_name)
        self.config_json = {}

        self.logger = Logger.get_logger(self.__class__.__name__)

        self.readConfigFile()

    def readConfigFile(self, encoding: str = "utf-8"):
        # read config file => JSON
        try:
            data = self.readFile(self.config_filename, self.logger, encoding)
            self.config_json = json.loads(data)
        except json.decoder.JSONDecodeError:
            self.logger.error(f"File Read Failed: Json decode error => {self.config_filename}")
            sys.exit(1)

    def reloadConfigure(self):
        self.readConfigFile()

    @staticmethod
    def readFile(filename: str, logger: logging.Logger, encoding: str = "utf-8") -> Optional[str]:
        if os.path.exists(filename):
            with open(filename, "r", encoding=encoding) as file:
                return file.read()
        else:
            logger.error(f"File Read Failed: File does not exist! => {filename}")
