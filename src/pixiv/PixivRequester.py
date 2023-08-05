# -*- coding: utf-8 -*-
"""  
  @projectName PixivSpiderNew
  @file PixivRequester.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-05 14:19
"""

import re
import urllib.parse
from typing import Literal

import requests

from spider_toolkit.Request import Requester
from pixiv.PixivConfigure import PixivConfigure
from utils.logger import Logger


class PixivRequester(Requester):
    # data model
    FollowRequestsMode = Literal["all", "r18"]

    def __init__(self, configure: PixivConfigure):
        super().__init__(configure)

        self.__api = {
            "work": "https://www.pixiv.net/artworks/",  # 单个work,
            "user_info": "https://www.pixiv.net/ajax/user/{uid}/profile/top",  #
            # "user_info": "https://www.pixiv.net/users/{uid}",  # 用户info => html 弃用
            "get_user_all_works": "https://www.pixiv.net/ajax/user/{uid}/profile/all",  # 获取用户所有work
            "get_follow_users": "https://www.pixiv.net/ajax/user/{uid}/following",  # 获取所有关注的用户
            "trends_page": "https://www.pixiv.net/ajax/follow_latest/illust?"  # 动态
        }
        self.__version_val = "12bf979348f8a251a88224d94a7ba55705d943fe"

        # header
        self.headers["referer"] = "https://pixiv.net/"
        # follow_header
        self.follow_header = self.headers.copy()
        try:
            self.uid = re.findall("PHPSESSID=(\\d+?)_", self.cookie_pools[0])[0]
            self.follow_header["X-User-Id"] = self.uid
            self.__api["get_follow_users"] = self.__api["get_follow_users"].format(uid=self.uid)
        except IndexError:
            self.logger.error("Failed: get uid from cookie!")
        self.follow_header["referer"] = "https://www.pixiv.net/bookmark_new_illust_r18.php"

        self.logger = Logger.get_logger(self.__class__.__name__)

    def reloadConfigure(self):
        super().reloadConfigure()
        try:
            self.uid = re.findall("PHPSESSID=(\d+?)_", self.cookie_pools[0])[0]
            self.follow_header["X-User-Id"] = self.uid
            self.__api["get_follow_users"] = self.__api["get_follow_users"].format(uid=self.uid)
        except IndexError:
            self.logger.error("Failed: get uid from cookie!")

    @property
    def api(self):
        return self.__api

    @property
    def version_val(self):
        return self.__version_val

    def requestsTrendsPage(self, page: int, mode: FollowRequestsMode = "r18") -> requests.Response | None:
        """动态页面

        :param int page:
        :param FollowRequestsMode mode: 模式 => "all", "r18"
        :return requests.Response | None:
        """
        api = self.api["trends_page"]
        params = {
            "p": page,
            "mode": "r18",
            "lang": "zh",
            "version": self.version_val,
        }
        api += urllib.parse.urlencode(params)
        return self.get(api)  # TODO: ?? headers=self.follow_headers?

    def requests_follow_users_page(self, offset: int = 0, limit: int = 24) -> requests.Response:
        """关注的用户的列表

        :param int offset: 偏移量, defaults to 0
        :param int limit: 张数?固定24就好, defaults to 24
        :return requests.Response:
        """
        api = self.api["get_follow_users"]
        params = {
            "offset": offset,
            "limit": limit,
            "tag": "",
            "lang": "zh",
            "rest": "show",
            "acceptingRequests": 0,
            "version": self.__version_val,
        }
        return self.get(api, headers=self.follow_header, params=params)

    def requestsUserInfoApi(self, uid: int | str) -> requests.Response:
        """用户信息接口

        :param int | str uid: uid
        :return requests.Response:
        """
        api = self.api["user_info"].format(uid=uid)
        params = {
            "lang": "zh",
            "version": "f17e4808608ed5d09cbde2491b8c9999df4f3962"
        }
        return self.get(api, params=params, headers=self.follow_header)

    def requests_get_user_works_api(self, uid: int | str) -> requests.Response:
        """获取用户所有作品id

        :param int | str uid: uid
        :return requests.Response:
        """
        api = self.api["get_user_all_works"].format(uid=str(uid))
        params = {
            "lang": "zh",
            "version": self.__version_val
        }
        return self.get(api, headers=self.follow_header, params=params)
