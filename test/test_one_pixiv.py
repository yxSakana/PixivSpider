# -*- coding: utf-8 -*-
"""
 @file: src\main.py
 @Description: 
 @author: sxy
 @data: 2023-07-16 20:09:07
 @update: 2023-07-16 20:09:07
"""


import sys
from pathlib import Path
sys.path.append(str(Path.cwd()) + "\\src")
from pixiv.pixiv import Pixiv
import requests
from pathlib import Path
from lxml import etree
import json
from time import sleep


if __name__ == "__main__":
    print(str(Path.cwd()))

    p = Pixiv("config/config.json")

    response = requests.get("https://www.pixiv.net/artworks/109784861", headers=p.header)
    print(response.status_code)
    with open("data/page.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    tree = etree.HTML(response.text)
    global_data = json.loads(tree.xpath('//*[@id="meta-global-data"]/@content')[0])
    preload_data = json.loads(tree.xpath('//*[@id="meta-preload-data"]/@content')[0])
    with open("data/preload_data.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(preload_data, indent=4, ensure_ascii=False))
    # print(preload_data)
    a = preload_data["illust"]["109784861"]["urls"]["original"]
    print(a)
    sleep(4)
    img_response = requests.get(a, headers=p.header)
    from pprint import pprint
    pprint(p.header)
    print(img_response.status_code)
    with open("data/img.png", "wb") as file:
        file.write(img_response.content)
    # print(json.loads(preload_data))
