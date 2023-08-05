# -*- coding: utf-8 -*-
"""  
  @projectName WeatherSpider
  @file Downloader.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-04 19:53
"""
import json
import os
import sys

from spider_toolkit.Configure import Configure
from spider_toolkit.Request import Requester
from utils.logger import Logger


class Downloader(object):
    DOWNLOAD_IMAGE_COUNT = 0
    DOWNLOAD_JSON_OBJ_COUNT = 0

    def __init__(self, requester: Requester, configure: Configure):
        self.download_path = ""

        self.requester = requester
        self.configure = configure
        self.logger = Logger.get_logger(self.__class__.__name__)

        self.initConfig()

    def initConfig(self) -> None:
        try:
            self.download_path = self.configure.config_json["spider"]["Downloader"]["download_path"]
        except KeyError as e:
            self.logger.error("KeyError: %s", e)
            sys.exit(1)

    def reloadConfigure(self):
        self.initConfig()

    def downloadImage(self, url: str, filename: str) -> tuple[str, str]:
        """

        :param url:
        :param filename: author/filename.png
        :return: download => filename, path
        """
        # 检查文件路径
        filename = os.sep.join([self.download_path, filename]) if not os.path.isabs(filename) else filename
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = os.path.abspath(filename)
        self.logger.debug(filename)
        # save
        with open(filename, "wb") as file:
            _ = self.requester.get(url)
            if _:
                data = _.content
                file.write(data)

                self.logger.debug(filename)
                Downloader.DOWNLOAD_IMAGE_COUNT += 1
                return filename, directory
            else:
                return "", ""

    def downloadJsonObj(self, json_obj: dict, filename: str, encoding: str = "utf-8") -> tuple[str, str]:
        """

        :param json_obj:
        :param filename: author/filename.png
        :param encoding:
        :return:
        """
        filename = os.sep.join([self.download_path, filename]) if not os.path.isabs(filename) else filename
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = os.path.abspath(filename)
        self.logger.debug(filename)
        try:
            data = json.dumps(json_obj, indent=4, ensure_ascii=False if encoding == "utf-8" else True)
            with open(filename, "w", encoding=encoding) as file:
                file.write(data)
                Downloader.DOWNLOAD_JSON_OBJ_COUNT += 1

            return filename, directory
        except TypeError as e:
            self.logger.error(e)
            # TODO: 失败后返回什么?
