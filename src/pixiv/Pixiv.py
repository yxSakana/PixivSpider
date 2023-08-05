# -*- coding: utf-8 -*-
"""
 @file: Pixiv.py
 @Description: 

    单个作品             √
    某个用户的所有作品     √
    动态                √
    关注的用户的所有作品   √
 
 @author: sxy
 @data: 2023-07-16 19:55:15
 @update: 2023-07-16 19:55:15
"""

import os
import re
from time import sleep

from PyQt5.QtCore import QObject, pyqtSignal

from pixiv.PixivConfigure import PixivConfigure
from pixiv.PixivRequester import PixivRequester
from pixiv.PixivParser import PixivParser
from pixiv.PixivDownloader import PixivDownloader
from pixiv.PixivMongodb import PixivMongodb
from utils.thread_utils import ThreadUtils
from utils.logger import Logger


class PixivSpider(QObject):
    # signal
    get_user_workId_signal = pyqtSignal(int)
    trends_info_signal = pyqtSignal(int, str, str, str)

    def __init__(self, config_filename: str = "config/config.json", parent: QObject | None = None):
        super().__init__(parent)

        self.configure = PixivConfigure(config_filename)
        self.requester = PixivRequester(self.configure)
        self.parser = PixivParser()
        self.downloader = PixivDownloader(self.requester, self.configure)
        self.mongodb = PixivMongodb(self.configure)

        self.logger = Logger.get_logger(self.__class__.__name__)

    def reloadConfigure(self):
        self.configure.reloadConfigure()
        self.requester.reloadConfigure()
        self.downloader.reloadConfigure()
        self.mongodb.reloadConfigure()

    def searchWorkInfo(self, url_or_id: str | int) -> tuple[bool, dict]:
        """搜索单个作品的信息

        :param url_or_id:
        :return: is_ok, PixivParser.parse_sub_page
        @see PixivParser.parse_sub_page
        """
        self.logger.debug(f"解析 {url_or_id} 页面...")
        url, work_id = self.parser.parseWorkId(url_or_id, self.requester.api["work"])
        try:
            int(work_id)
        except Exception:
            self.logger.error(f"Failed to get page id!: \n"
                              f"int(work_id) failed => work_id: \n"
                              f"\tval: {work_id}, "
                              f"\ttype: {type(work_id)}")
            raise
        response = self.requester.get(url)
        if not response:
            self.logger.error(f"{url} response is None!")
            return False, {}
        else:
            result = self.parser.parse_sub_page(response.text, work_id)  # 解析
            return True, result

    def searchUserInfo(self, uid_or_url: str | int) -> tuple[bool, dict]:
        """

        :param uid_or_url:
        :return:
        """
        uid = self.parser.parseUserId(uid_or_url)
        response = self.requester.requestsUserInfoApi(uid)
        info = self.parser.parseUserInfo(response.json())

        return True, info

    def spiderOneWork(self, url_or_id: str | int) -> tuple[bool, dict]:
        """爬取一次一个works(作品)页面

        :param url_or_id:
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
        # 搜索作品信息
        _, info_data = self.searchWorkInfo(url_or_id)
        if not _:
            return _, info_data
        result = {}

        # 提取信息
        work_id = info_data["workId"]
        image_url = info_data["start_url"]
        dir_name = os.sep.join([info_data["userName"], info_data["title"]])
        illust_comment = info_data.get("description", None) or ""  # TODO: 是否需要改???
        info_data["image_urls"] = []

        # 排除重复
        db_exist_result = self.mongodb.isRepeat(info_data, work_id)
        if db_exist_result is None:
            self.logger.info(f"No Exists: {image_url}")
            # download all image
            for i in range(info_data["pageCount"]):
                try:
                    image_url = re.sub("_p\\d+", f"_p{str(i)}", image_url, count=1)
                    self.downloader.downloadPixivImage(image_url, dir_name)
                    info_data["image_urls"].append(image_url)
                except IndexError:
                    self.logger.error("failed to match next image url!")
                    continue
            # download 简介
            self.downloader.downloadComment(illust_comment, dir_name)
            # save to db
            user_id = str(info_data.pop("userId"))
            ThreadUtils.createAndRunThread(self.mongodb.saveData, user_id, info_data["workId"], info_data)

            result = info_data.copy()
        else:
            result = list((_data for _data in db_exist_result["works"] if work_id in _data))[0][work_id]
            result["userId"] = db_exist_result["userId"]
            self.logger.info(f"Exists: {work_id}(workId)<==>{info_data['userId']}(userId)")
        return True, result

    def spiderOneTrendsPage(self, page: int, mode: PixivRequester.FollowRequestsMode = "r18") -> None:
        """爬取动态页面的指定页

        :param int page: 要爬取动态的哪一页
        :param FollowRequestsMode mode: 模式 => "all", "r18"
        """
        response = self.requester.requestsTrendsPage(page, mode=mode)
        image_info_arr = self.parser.parse_follow_page(response.json())
        for i in range(len(image_info_arr["ids"])):
            sub_page_url = self.requester.api["work"] + str(image_info_arr["ids"][i])
            self.trends_info_signal.emit(page,
                                         str(image_info_arr["ids"][i]), image_info_arr["urls"][i],
                                         sub_page_url)  # 发送信号
            ThreadUtils.createAndRunThread(self.spiderOneWork, sub_page_url)

            self.logger.debug(f"Current spider sub page url: {sub_page_url})({i})")
            sleep(3)

    def spider_trends_pages(self, mode: PixivRequester.FollowRequestsMode = "r18") -> None:
        """爬取动态页面的所有作品

        :param FollowRequestsMode mode: 模式 => "all", "r18"
        """
        self.logger.info("开始爬取动态页面...")

        for i in range(1, 100):  # TODO: 把固定的100页改的更合理
            self.spiderOneTrendsPage(i, mode=mode)

    def spider_user_works(self, uid_or_url: int | str) -> None:
        """爬取指定用户的所有作品

        :param uid_or_url:
        """
        self.logger.info(f"开始爬取{uid_or_url}的作品...")

        uid = self.parser.parseUserId(uid_or_url)
        response = self.requester.requests_get_user_works_api(uid)
        all_works_id = self.parser.parse_get_user_works_api(response.json())
        for work_id in all_works_id:
            self.get_user_workId_signal.emit(int(work_id))
            ThreadUtils.createAndRunThread(self.spiderOneWork, str(work_id))
            sleep(3)

    def spider_follow_users_works(self) -> None:
        """爬取所有的关注的用户的所有作品
        """
        self.logger.info("开始爬取关注的所有用户的所有作品...")

        offset: int = 0
        limit: int = 24
        while True:
            response = self.requester.requests_follow_users_page(offset, limit)
            data = self.parser.parse_follow_users_page(response.json())
            for i in range(len(data)):
                item = data[i]
                try:
                    user_name = os.path.normpath(item["userName"])
                    image_url = item["profileImageUrl"]
                    uid = item["userId"]

                    # by image to download image of user
                    self.downloader.downloadPixivImage(image_url, user_name + "image.jpg")

                    # write user info
                    info = {
                        "userId": uid,
                        "userName": item["userName"],
                        "image_url": image_url,
                        "userComment": item["userComment"],
                        "tags": [illust["tags"] for illust in item["illusts"]]
                    }
                    filename = os.sep.join([user_name, "info.json"])
                    self.downloader.downloadJsonObj(info, filename)

                    # save to db
                    _filter = {"userId": info["userId"]}
                    if self.mongodb.collection.find_one(_filter) is None:
                        save_result = self.mongodb.collection.insert_one(info)
                        if save_result.acknowledged:
                            self.logger.info(f"Sava To MongoDB: {info['userId']}(userID)")
                        else:
                            self.logger.error(f"Failed: Save to MongoDB => {info['userId']}(userID)")
                    else:
                        self.logger.info(f"Exists: {info['userId']}(userID)")

                    # by id to requests user page
                    self.spider_user_works(uid)
                except KeyError as e:
                    self.logger.error(e)
