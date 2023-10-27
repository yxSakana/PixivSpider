# -*- coding: utf-8 -*-
"""  
  @projectName PixivSpiderNew
  @file PixivParser.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-05 14:20
"""

import json
import urllib.parse
from lxml import etree
from typing import NewType

from utils.logger import Logger


class PixivParser(object):
    ItemDict = NewType("ItemDict", dict)
    ItemList = NewType("ItemList", list)

    def __init__(self):
        super().__init__()

        self.logger = Logger.get_logger(self.__class__.__name__)

    def parseWorkId(self, url_or_id: int | str, base_url: str) -> tuple[str, str]:
        """
        通过传入的 url_or_id 解析出 作品的url 和 作品id
        :param url_or_id:
        :param base_url:
        :return: url, work_id
        """
        url_or_id = str(url_or_id)
        url = urllib.parse.urljoin(base_url, url=url_or_id)
        work_id = url.split("/")[-1]
        self.logger.debug("work_id: %s", work_id)

        return url, work_id

    def parseUserId(self, uid_or_url: int | str):
        return uid_or_url.split("/")[-1]

    def parse_sub_page(self, html: str, work_id: int | str) -> ItemDict:
        """works页面

        :param str html: response.text
        :param int | str work_id: 传入的页面的id
        :return dict: {
            "userId": => str

            "workId": => str

            "start_url": 图片的开始url, => str

            "title": -, => str

            "pageCount: -  => int

            "userName": , => str

            "tags": , => list

            "description": 描述 => str
        }
        """
        tree = etree.HTML(html)
        preload_data = json.loads(tree.xpath('//*[@id="meta-preload-data"]/@content')[0])

        try:
            body = preload_data["illust"][str(work_id)]
            result = {
                "userId": list(preload_data["user"].keys())[0],
                "workId": str(work_id),
                "start_url": body["urls"]["original"],
                "title": body["title"],
                "pageCount": int(body["pageCount"]),
                "userName": body["userName"],
                "tags": [tag["tag"] for tag in body["tags"]["tags"]],
                "description": body["description"] or body["illustComment"]
            }

            return result
        except KeyError as e:
            self.logger.error(e)
            raise

    def parseUserInfo(self, json_data: dict) -> ItemDict:
        """用户信息

        该api可以解析出用户的基本信息、第一页的所有插画、漫画、小说、(收藏?)
        :param json_data:
        :return:
        """
        try:
            body = json_data["body"]
            meta = body["extraData"]["meta"]
            result = {
                "mete": {
                    "home_page": meta["canonical"],
                    "description": meta["ogp"]["description"],
                    "user_name": meta["ogp"]["title"],
                    "background_image": meta["twitter"]["image"]
                }
            }
            result["mete"]["user_id"] = result["mete"]["home_page"].split("/")[-1]
            return result
        except KeyError as e:
            self.logger.error(e)
            self.logger.error("Failed: parseUserInfo()")

    def parse_get_user_works_api(self, json_data: dict) -> ItemList:
        """解析"获取用户所有作品id"api

        :param dict json_data:
        :return ItemList: 用户所有作品id
        """
        try:
            return json_data["body"]["illusts"].keys()
        except KeyError as e:
            self.logger.error(e)
            self.logger.error("Failed: parse_get_user_works_api()")
            return []

    def parse_follow_page(self, data: dict) -> ItemDict:
        """动态页面

        :param str json_text: response.text
        :return dict: {
            "ids": , => list
            "urls": , => list
        }
        """
        try:
            illust = data["body"]["thumbnails"]["illust"]
            result = {
                "ids": data["body"]["page"]["ids"],
                "urls": [i["url"] for i in illust],
            }
            return result
        except Exception:
            raise

    def parse_follow_users_page(self, json_data: dict) -> ItemList:
        """关注页面

        :param str json_data: response.text
        :return IteamList: 用户列表
        """
        try:
            return json_data["body"]["users"]
        except Exception:
            self.logger.error("Failed: Json data can't parse!")
            raise
