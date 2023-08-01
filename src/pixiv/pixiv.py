# -*- coding: utf-8 -*-
"""
 @file: src/pixiv/pixiv.py
 @Description: 

    单个作品              √
    某个用户的所有作品     √
    动态                 √
    关注的用户的所有作品   √
 
 @author: sxy
 @data: 2023-07-16 19:55:15
 @update: 2023-07-16 19:55:15
"""


import os
import re
import sys
import json
import threading
from time import sleep
from typing import Literal, NewType

import requests
import urllib.parse
from lxml import etree

from utils.base_spider import BaseSpider
from utils.logger import Logger
from utils.thread_utils import ThreadUtils
from utils.mongodb import MongoDB


class Pixiv(BaseSpider):
    FollowRequestsMode = Literal["all", "r18"]
    IteamDict = NewType("Iteam", dict)
    IteamList = NewType("Iteam", list)
    
    def __init__(self, config_filename: str = "config.json") -> None:
        super().__init__(config_filename)
        self.session = requests.session()
        self.mongodb = MongoDB("mongodb://yingxue:SunXinYang0306@47.94.110.64:27017/?directConnection=true&appName=mongosh")
        self.mongodb.connentCollection("spider", "pixiv")
        self.mongodb_lock = threading.Lock()
        
        self.__version_val = "dce12e1f9118277ca2839d13e317c59d7ae9ac6e"
        
        self.__user_page_api = "https://www.pixiv.net/users/"  # 用户主页
        self.__get_user_all_works_api = "https://www.pixiv.net/ajax/user/{uid}/profile/all"  # 获取用户所有作品
        self.__get_user_works_api = "https://www.pixiv.net/ajax/user/{uid}/profile/illusts"  # 获取用户作品
        
        self.__subpage_api = "https://www.pixiv.net/artworks/"  # 一个作品页面
        self.__follow_api = "https://www.pixiv.net/ajax/follow_latest/illust?"  # 动态(关注的人发布的作品分散杂乱的分布，按时间排布)
        self.__follow_users_api = "https://www.pixiv.net/ajax/user/{uid}/following"  # "关注" 页面接口
        
        self.header["referer"] = "https://pixiv.net/"
        self.header["cookie"] = self.cookies_pools[0]

        self.follow_header = self.header.copy()
        try:
            self.uid = re.findall("PHPSESSID=(\d+?)_", self.cookies_pools[0])[0]
            self.follow_header["X-User-Id"] = self.uid
            self.__follow_users_api = self.__follow_users_api.format(uid=self.uid)
        except IndexError:
            self.logger.error("Failed to get uid!")
            # self.follow_header["X-User-Id"] = "50341679"
        self.follow_header["referer"] = "https://www.pixiv.net/bookmark_new_illust_r18.php"
        
        self.requests_failed_count = 0

        self.logger = Logger.get_logger(__class__.__name__)
    
    def requests_sub_page(self, url: str, 
                          headers: dict | None=None, 
                          params: dict | None=None) -> requests.Response | None:
        """子页面请求

        :param str url:
        :return requests.Response | None:
        """
        if self.requests_failed_count >= 4:
            sleep(10)
            self.requests_failed_count -= 1
        for i in range(5):
            response = self.session.get(url, headers=headers or self.header, params=params)
            if response.status_code == 200:
                self.logger.debug(f"{url} status code: {response.status_code}")       
                return response
            else:
                self.requests_failed_count += 1
                if self.requests_failed_count >= 4:
                    sleep(10)
                    self.requests_failed_count -= 1
                self.logger.warning(f"Requests Failed: {url} status code: {response.status_code}(count: {self.requests_failed_count})")
                continue
        return None

    def requests_follow_page(self, page: int, mode: FollowRequestsMode="r18") -> requests.Response | None:
        """关注页面请求

        :param int page: 
        :param FollowRequestsMode mode: 模式 => "all", "r18"
        :return requests.Response | None:
        """
        api = self.__follow_api
        params = {
            "p": page,
            "mode": "r18",
            "lang": "zh",
            "version": self.__version_val,
        }
        api += urllib.parse.urlencode(params)
        return self.requests_sub_page(url=api)  # TODO: ?? headers=self.follow_headers?
        
    def requests_follow_users_page(self, offset: int=0, limit: int=24) -> requests.Response:
        """请求关注的用户的列表

        :param int offset: 偏移量, defaults to 0
        :param int limit: 张数?固定24就好, defaults to 24
        :return requests.Response: 
        """
        params = {
            "offset": offset,
            "limit": limit,
            "tag": "",
            "lang": "zh",
            "rest": "show",
            "acceptingRequests": 0,
            "version": self.__version_val,
        }
        return self.requests_sub_page(self.__follow_users_api, headers=self.follow_header, params=params)

    def requests_user_info_api(self, uid: int | str) -> requests.Response:
        """requests-用户信息接口

        :param int | str uid: uid
        :return requests.Response:
        """
        api_url = self.__user_page_api + str(uid)
        return self.requests_sub_page(api_url)
    
    def requests_get_user_works_api(self, uid: int | str) -> requests.Response:
        """请求-获取用户所有作品id接口

        :param int | str uid: uid
        :return requests.Response:
        """
        api_url = self.__get_user_all_works_api.format(uid=str(uid))
        params = {
            "lang": "zh",
            "version": self.__version_val
        }
        return self.requests_sub_page(api_url, headers=self.follow_header, params=params)
    
    def requests_user_works_api(self, uid: int | str, works_id: int | str) -> requests.Response:
        """请求-用户作品接口(弃用)

        :param int | str works_id: 作品id
        :return requests.Response:
        """
        api = self.__get_user_works_api.format(uid=uid)
        params = {
            "ids[]": works_id,
            "is_first_page": 1,
            "work_category": "illustManga",
            "version": "dce12e1f9118277ca2839d13e317c59d7ae9ac6e",
            "lang": "zh",
        }
        return self.requests_sub_page(api, params=params)

    
    def parse_sub_page(self, html: str, work_id: int | str) -> IteamDict:
        """works页面解析

        :param str html: response.text
        :param int | str work_id: 传入的页面的id
        :return dict: {
            "userId": => str

            "workId": => str

            "start_url": 图片的开始url, => str

            "titile": -, => str

            "pageCount: -  => int

            "userName": , => str

            "tags": , => list

            "description": 描述 => str
        }
        """
        result = {
            "userId": "",
            "workId": str(work_id),
            "start_url": None,
            "title": "NoTitle",
            "pageCount": 0,
            "userName": "NoUserName",
            "tags": [], 
            "description": ""
        }
        tree = etree.HTML(html)
        # global_data = json.loads(tree.xpath('//*[@id="meta-global-data"]/@content')[0])
        preload_data = json.loads(tree.xpath('//*[@id="meta-preload-data"]/@content')[0])

        try:
            body = preload_data["illust"][str(work_id)]
            result["userId"] = list(preload_data["user"].keys())[0]
            result["start_url"] = body["urls"]["original"]
            result["title"] = body["title"]
            result["pageCount"] = int(body["pageCount"])
            result["userName"] = body["userName"]
            result["tags"] = [tag["tag"] for tag in body["tags"]["tags"]]
            result["description"] = body["description"] or body["illustComment"]
            
            return result
        except KeyError as e:
            self.logger.error(e)
            raise

    def parse_follow_page(self, data: dict) -> IteamDict:
        """解析-"动态"页面

        :param str json_text: response.text
        :return dict: {
            "ids": , => list
            "urls": , => list
        }
        """
        result = {
            "ids": [],
            "urls": [],
        }
        try:
            illust = data["body"]["thumbnails"]["illust"]
            result["ids"] = data["body"]["page"]["ids"]
            result["urls"] = [i["url"] for i in illust]
        except Exception:
            raise

        return result
    
    def parse_follow_users_page(self, json_data: dict) -> IteamList:
        """解析"关注"页面

        :param str json_text: response.text
        :return IteamList: 用户列表
        """
        try:
            return json_data["body"]["users"]
        except Exception:
            self.logger.error("Failed: Json data can't parse!")
            raise
    
    def parse_get_user_works_api(self, json_data: dict) -> IteamList:
        """解析-"获取用户所有作品id"api

        :param dict json_data: 
        :return IteamList: 用户所有作品id
        """
        try:
            return json_data["body"]["illusts"].keys()
        except KeyError as e:
            self.logger.error(e)
            self.logger.error("Failed: parse_get_user_works_api()")
            return []

    def parse_works_api(self, json_data: dict, works_id: int | str) -> IteamDict:
        """(弃用)

        :param dict json_data: _description_
        :param int | str works_id: _description_
        :return IteamDict: _description_
        """
        result = {
            "title": None,
            "start_url": None,
            "tags": None
        }
        try:
            works_info = json_data["body"]["works"][str(works_id)]
            result["title"] = works_info["title"]
            result["start_url"] = works_info["url"]
            result["tags"] = works_info["tags"]

            return result
        except Exception as e:
            self.logger.error(e)
            raise


    def download_image(self, url: str, dir_name: str="NoDir", _filename: str=None) -> bool:
        """下载图片(会自动创建不存在路劲)

        :param str url: 
        :param str dir_name: , defaults to "NoDir"
        :param str _filename: 如果有则按测参数来, defaults to None
        :return bool: 是否成功
        """
        for i in range(5):
            try:
                response = self.session.get(url, headers=self.header)
                break
            except requests.exceptions.ConnectionError:
                sleep(10)

        dir_name = os.path.normpath(os.path.sep.join([self.base_download_path, dir_name]))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        if response.status_code == 200:
            self.logger.debug(f"{url} status code: {response.status_code}")
            data = response.content
            filename = os.path.sep.join([dir_name, _filename or url.split("/")[-1]])
            self.logger.debug(f"download dir: {dir_name}")
            with open(filename, "wb") as file:
                self.logger.debug(f"downloading: {filename}")
                file.write(data)
            return True
        else:
            self.logger.warning(f"Requests Failed: {url} status code: {response.status_code}")
            self.requests_failed_count += 1
            return False

    def tmp_save(self, user_id, work_id, info):
        # self.mongodb.collection.insert_one()
        self.mongodb_lock.acquire()
        try:
            filter = {"userId": user_id}
            update = {"$push": {"works": {work_id: info}}}
            save_result = self.mongodb.collection.update_one(filter, update)
            if save_result.matched_count == 0:
                self.logger.error(f"Matched count: {save_result.matched_count}")
            else:
                self.logger.info(f"Save To MongoDB: {work_id}(workId)<==>{user_id}(userId)")
        finally:
            self.mongodb_lock.release()


    def spider_once_work_page(self, url_or_id: str | int) -> None:
        """爬取一次一个works(作品)页面

        :param str url:
        """
        url_or_id = str(url_or_id)
        url = urllib.parse.urljoin(self.__subpage_api, url=url_or_id)
        work_id = url.split("/")[-1]
        
        try:
            int(work_id)
        except Exception:
            self.logger.error("Failed to get page id!")
            raise

        response = self.requests_sub_page(url)
        if not response:
            self.logger.warning(f"{url} response is None!")
            return

        result = self.parse_sub_page(response.text, work_id)  # 解析
        image_url = result["start_url"]
        dir_name = os.sep.join([result["userName"], result["title"]])
        illustComment = result.get("illustComment", None) or ""  # TODO: 是否需要改???

        query = {"userId": result['userId'], "works": {"$elemMatch": {work_id: {"$exists": True}}}}
        if self.mongodb.collection.find_one(query) is None:  # TODO
            result["image_urls"] = []
            for i in range(result["pageCount"]):
                result["image_urls"].append(image_url)
                self.download_image(image_url, dir_name)
                try:
                    index = int(re.findall("p(\d+)[_\.]", image_url)[0])
                    index += 1
                    image_url = re.sub("_p\d+", f"_p{str(index)}", image_url, count=1)
                except IndexError:
                    self.logger.error("failed to match next image url!")
                if self.requests_failed_count >= 6:
                    sleep(5)
                    self.requests_failed_count = 0
                    continue
                sleep(0.5)

            with open(os.sep.join([self.base_download_path, dir_name, "illustComment.txt"]), "w", encoding="utf-8") as file:
                file.write(illustComment)

            # save to db
            user_id = str(result.pop("userId"))
            ThreadUtils.createAndRunThread(self.tmp_save, user_id, result["workId"], result)
        else:
            self.logger.info(f"Exists: {work_id}(workId)<==>{result['userId']}(userId)")
        return
    
    def spider_once_follow_page(self, page: int, mode: FollowRequestsMode="r18") -> None:
        """爬取一页关注页面

        :param int page: page
        :param FollowRequestsMode mode: 模式 => "all", "r18"
        """
        response = self.requests_follow_page(page, mode=mode)
        image_info_arr = self.parse_follow_page(response.json())
        for i in range(len(image_info_arr["ids"])):
            sub_page_url = self.__subpage_api + str(image_info_arr["ids"][i])
            self.logger.debug(f"Current spider sub page url: {sub_page_url})({i})")
            ThreadUtils.createAndRunThread(self.spider_once_work_page, (str(sub_page_url), mode))
            sleep(3)

    def spider_user_page(self, uid: int | str) -> None:
        """爬取用户all works

        :param int | str uid: user id
        """
        response = self.requests_get_user_works_api(uid)
        all_works_id = self.parse_get_user_works_api(response.json())
        for work_id in all_works_id:
            ThreadUtils.createAndRunThread(self.spider_once_work_page, str(work_id))
            sleep(3)
            # self.spider_once_work_page(work_id)

    def spider_follow_page(self, mode: FollowRequestsMode="r18") -> None:
        """爬取关注(动态?)页面(all in)
        
        :param FollowRequestsMode mode: 模式 => "all", "r18"
        """
        for i in range(2, 100):
            self.spider_once_follow_page(i, mode=mode)
    
    def spider_follow_users_page(self) -> None:
        """爬取所有的关注的用户的所有作品
        """
        offset: int = 0
        limit: int = 24
        while True:
            response = self.requests_follow_users_page(offset, limit)
            data = self.parse_follow_users_page(response.json())
            for i in range(len(data)):
                iteam = data[i]

                try:
                    dir_name = os.path.normpath(iteam["userName"])
                    image_url = iteam["profileImageUrl"]
                    uid = iteam["userId"]
                except KeyError as e:
                    self.logger.error(e)

                # by image to download image of user
                self.download_image(image_url, dir_name, "image.jpg")
                # write user info
                info = {
                    "userId": uid,
                    "userName": iteam["userName"],
                    "image_url": image_url,
                    "userComment": iteam["userComment"],
                    "tags": [illust["tags"] for illust in iteam["illusts"]]
                }
                filename = os.sep.join([self.base_download_path, dir_name, "info.json"])
                self.logger.debug(filename)
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(json.dumps(info, indent=4, ensure_ascii=False))

                # save to db 
                filter = {"userId": info["userId"]}
                if self.mongodb.collection.find_one(filter) is None:
                    save_result = self.mongodb.collection.insert_one(info)
                    if save_result.acknowledged:
                        self.logger.info(f"Sava To MongoDB: {info['userId']}(userID)")
                    else:
                        self.logger.error(f"Failed: Save to MongoDB => {info['userId']}(userID)")
                else:
                    self.logger.info(f"Exists: {info['userId']}(userID)")
                
                # by id to requests user page
                self.spider_user_page(uid=uid)
                # ThreadUtils.createAndRunThread(self.spider_user_page, uid)