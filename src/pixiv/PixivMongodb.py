# -*- coding: utf-8 -*-
"""  
  @projectName PixivSpiderNew
  @file PixivMongodb.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-05 15:33
"""
import threading

from spider_toolkit.Configure import Configure
from spider_toolkit.mongodb import MongoDB
from utils.logger import Logger


class PixivMongodb(MongoDB):
    DB_SAVED_COUNT = 0
    DB_EXIST_COUNT = 0

    def __init__(self, configure: Configure) -> None:
        self.configure = configure
        self.configure_json = {}
        self.initConfigure()
        super().__init__(self.configure_json)  # 连接Mongo

        self.connectCollection(self.configure_json["db_name"], self.configure_json["collection"])  # 连接数据集
        self.mongodb_lock = threading.Lock()

        self.logger = Logger.get_logger(self.__class__.__name__)

    def initConfigure(self):
        self.configure_json = self.configure.config_json["spider"]["Database"]["mongo"]

    def reloadConfigure(self):
        self.initConfigure()

    def isRepeat(self, data: dict, work_id: int):
        query = {"userId": data['userId'], "works": {"$elemMatch": {work_id: {"$exists": True}}}}
        db_exist_result = self.collection.find_one(query)
        if db_exist_result:
            PixivMongodb.DB_EXIST_COUNT += 1
        return db_exist_result

    def saveData(self, user_id, work_id, info):
        self.mongodb_lock.acquire()
        try:
            _filter = {"userId": user_id}
            update = {"$push": {"works": {work_id: info}}}
            save_result = self.collection.update_one(_filter, update, upsert=True)
            if save_result.matched_count == 0 and self.collection.find_one(_filter, update):
                self.logger.error(f"Matched count: {save_result.matched_count}")
            else:
                PixivMongodb.DB_SAVED_COUNT += 1
                self.logger.info(f"Save To MongoDB: {work_id}(workId)<==>{user_id}(userId)")
        finally:
            self.mongodb_lock.release()
