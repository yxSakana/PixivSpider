import sys
import json
from os import makedirs
from pathlib import Path
# import logging
# from traceback import format_exc
try:
    from PyQt5.QtCore import QObject
    meta_class = QObject
except ModuleNotFoundError:
    from abc import ABC
    meta_class = ABC

from utils.logger import Logger

USER_AGENT = {
    "google_chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}


class BaseSpider(meta_class):
    def __init__(self, config_filename: str = "config/config.json") -> None:
        super().__init__()
        self.config_filename = config_filename
        self.header = {
            "User-Agent": USER_AGENT["google_chrome"]
        }
        self.website = ""
        self.base_path = ""
        self.base_download_path = ""
        self.cookies_pools = []  # 存储的是cookies的具体内容(配置文件中指定的是文件名)
        self.cookies_filenames = []
        self.mongo_config = {}
        self.proxies = {}
        self.config_json = {}  # JSON配置文件

        self.logger = Logger.get_logger(self.__class__.__name__)

        self.readConfig()

    def reloadConfig(self) -> None:
        """
        重新读取配置文件
        :return:
        """
        self.readConfig()

    def readConfig(self) -> None:
        """读取配置文件

        加载 website、base_path、base_download_path、cookies_pools
        """
        try:
            self.config_json = json.loads(self.openFile(self.config_filename))
            self.website = self.config_json["spider"]["website"]
            self.base_path = Path(self.config_json["spider"]["base_path"]).resolve()
            self.base_download_path = Path(self.config_json["spider"]["base_download_path"]).resolve()
            self.cookies_filenames = self.config_json["spider"]["cookies_pools"]
            self.proxies = self.config_json["spider"]["proxies"]
        except KeyError as e:
            self.logger.error("Key Error: %s", e)
            sys.exit(1)
        # 读取cookie池
        for filename in self.cookies_filenames:
            cookie = self.openFile(filename)
            self.cookies_pools.append(cookie)
        # 检测路径是否存在
        if not self.base_path.exists:
            makedirs(self.base_path)
        
        self.base_path = str(self.base_path)
        self.base_download_path = str(self.base_download_path)

        # mongo db
        self.mongo_config = self.config_json["mongo"]

    def openFile(self, filename: str, mode: str="r", encoding: str="utf-8") -> any:
        """打开文件

        :param str filename: 
        :param str mode: , defaults to "r"
        :param str encoding: , defaults to "utf-8"
        :return Any: file content 
        """
        try:
            with open(filename, mode, encoding=encoding) as file:
                data = file.read()
                return data
        except FileNotFoundError:
            self.logger.error("not find file: %s", Path(filename).resolve())
            sys.exit(1)

    def toString(self):
        self.logger.info(self.config_filename)
        self.logger.info(self.config_json)
        self.logger.info(self.website)
        self.logger.info(self.base_path)
        self.logger.info(self.base_download_path)
        self.logger.info(self.cookies_pools)
        self.logger.info(self.cookies_filenames)
        self.logger.info(self.proxies)
        self.logger.info(self.header)
