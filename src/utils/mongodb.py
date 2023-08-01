from pymongo import MongoClient
import pymongo

from utils.logger import Logger


class MongoDB(object):
    def __init__(self, info: dict | str) -> None:
        if isinstance(info, dict):
            host = info["host"]
            port = info.get["port", 27017]
            username = info.get["usernamer", None]
            password = info.get["password", None]
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
            self.logger.error("connent tiemout!")

    def connentCollection(self, db_name: str, collection_name: str) -> None:
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def isExists(self, filter: dict) -> bool:
        return bool(self.collection.find_one(filter))


if __name__ == "__main__":
    # db = MongoDB("localhost")
    # db = MongoDB("mongodb://yingxue:SunXinYang0306@47.94.110.64:27017/?directConnection=true&appName=mongosh")
    db = MongoDB("47.94.110.6", 27017, "yingxue", "SunXinYang0306")
    db.connentCollection("a", "b")
