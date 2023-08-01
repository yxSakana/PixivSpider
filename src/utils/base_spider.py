import sys
import json
from abc import ABC
from os import makedirs
from pathlib import Path
import logging
# from traceback import format_exc

from PyQt5.QtCore import QObject

from utils.logger import Logger

USER_AGENT = {
    "google_chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}

class BaseSpider(QObject):
    def __init__(self, config_filename: str="config.json") -> None:
        super().__init__()
        self.config_filename = config_filename
        self.header = {
            "User-Agent": USER_AGENT["google_chrome"]
        }
        self.website = ""
        self.base_path = ""
        self.base_download_path = ""
        self.cookies_pools = []

        self.logger = Logger.get_logger(self.__class__.__name__)

        self.readConfig()

    def readConfig(self) -> None:
        """读取配置文件
        """
        try:
            config_data = json.loads(self.openFile(self.config_filename))
            self.website = config_data["spider"]["website"]
            self.base_path = Path(config_data["spider"]["base_path"]).resolve()
            self.base_download_path = Path(config_data["spider"]["base_download_path"]).resolve()
            cookie_filenames = config_data["spider"]["cookies_pools"]
        except KeyError as e:
            self.logger.error("Key Error: %s", e)
            sys.exit(1)
        # 读取cookie池
        for filename in cookie_filenames:
            cookie = self.openFile(filename)
            self.cookies_pools.append(cookie)
        # 检测路径是否存在
        if not self.base_path.exists:
            makedirs(self.base_path)
        
        self.base_path = str(self.base_path)
        self.base_download_path = str(self.base_download_path)

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
        self.logger.debug(self.website)
        self.logger.debug(self.base_path)
        self.logger.debug(self.base_download_path)
        self.logger.debug(self.cookies_pools)

        self.logger.info(self.website)
        self.logger.info(self.base_path)
        self.logger.info(self.base_download_path)
        self.logger.info(self.cookies_pools)

        

if __name__ == "__main__":
    class T(BaseSpider):
        def __init__(self, config_filename: str = "new_\\config.json") -> None:
            super().__init__(config_filename)
    
    t = T()
    # t.logger.handlers[0].setLevel(logging.DEBUG)
    # t.logger.setLevel(logging.DEBUG)
    # t.toString()

    # root_logger = logging.getLogger("root")
    # root_logger.info("asd")
    # logging.root.info("i")
    # # 获取所有的 Logger 对象
    # loggers = logging.Logger.manager.loggerDict

    # # 打印 Logger 的数量
    # print("Number of loggers:", len(loggers))

    # # 遍历打印每个 Logger 的名称
    # for logger_name in loggers:
    #     print("Logger name:", logger_name)
