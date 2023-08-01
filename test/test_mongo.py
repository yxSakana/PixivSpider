import sys
from pathlib import Path
sys.path.append(str(Path.cwd()) + "\\src")
from utils.mongodb import MongoDB
from utils.logger import Logger


logger = Logger.get_module_logger()
mongodb = MongoDB("mongodb://yingxue:SunXinYang0306@47.94.110.64:27017/?directConnection=true&appName=mongosh")
mongodb.connentCollection("spider", "pixiv")

# work_id = "12341"
# logger.info(mongodb.isExists({"userId": "19603375"}))
from pymongo import MongoClient

# 连接数据库
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
collection = db['mycollection']

user_id = "27686375"
work_id = "104463457"

# 构建查询条件


if result is not None:
    print("指定的键存在于 works 列表中的子文档中")
else:
    print("指定的键不存在于 works 列表中的子文档中")


# result = mongodb.collection.find_one({"userId": "27686375", "works": {"$elemMatch": "101311321"}})
# if result.alive:
#     for doc in result:
#         if doc["keyExists"]:
#             print("指定的键存在于 works 列表中")
#         else:
#             print("指定的键不存在于 works 列表中")
# else:
#     print("未找到匹配的文档")
# result = mongodb.collection.update_one({"userId": "19603375"}, {"$set": {f"works.{work_id}":  "result"}})
# logger.info(result.matched_count)
