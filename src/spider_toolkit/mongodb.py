from pymongo import MongoClient
import pymongo
from typing import Union

from utils.logger import Logger


class MongoDB(object):
    def __init__(self, info: Union[dict, str]) -> None:
        if isinstance(info, dict):
            host = info["ip"]
            port = int(info.get("port", 27017))
            username = info.get("username", None)
            password = info.get("password", None)
            self.client = MongoClient(host, port, username=username, password=password)
        elif isinstance(info, str):
            self.client = MongoClient(info)

        self.db = None
        self.collection = None

        self.logger = Logger.get_logger(__class__.__name__)

        try:
            with pymongo.timeout(5):
                server_info = self.client.server_info()
            self.logger.info("Connected MongoDB!")
        except pymongo.errors.ServerSelectionTimeoutError:
            self.logger.error("connect timeout!")

    def connectCollection(self, db_name: str, collection_name: str) -> None:
        """

        :param db_name:
        :param collection_name:
        :return:
        """
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def isExists(self, filter: dict) -> bool:
        return bool(self.collection.find_one(filter))
