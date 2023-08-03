# -*- coding: utf-8 -*-
"""
 @file: test\test_pixiv.py
 @Description: 
 @author: sxy
 @data: 2023-07-16 21:47:07
 @update: 2023-07-16 21:47:07
"""

import sys
from pathlib import Path
sys.path.append(str(Path.cwd()) + "\\src")
import json
from pprint import pprint
import logging

import requests
import urllib
from urllib.parse import urlencode

from pixiv.pixiv import Pixiv
from utils.logger import Logger


if __name__ == "__main__":
    test_api = "https://www.pixiv.net/artworks/106544761/"
    test_params = {
        "ids[]": 106544761,
        "is_first_page": 1,
        "work_category": "illustManga",
        "version": "dce12e1f9118277ca2839d13e317c59d7ae9ac6e",
        "lang": "zh",
    }
    test_filename = "resource/once_works_page.html"

    logger = Logger.get_module_logger()
    
    p = Pixiv("config/config.json")
    # p.logger.setLevel(logging.DEBUG)
    # p.logger.handlers[0].setLevel(logging.DEBUG)

    # test_image_url = "https://i.pximg.net/c/250x250_80_a2/img-master/img/2023/03/25/17/35/48/106544761_p1_square1200.jpg"
    # s = p.download_image(test_image_url, "test")

    # response = requests.get(test_api, headers=p.header, params=test_params)
    # response = requests.get(test_api, headers=p.header)
    # logger.info(response.status_code)
    # if response.status_code == 200:
    #     with open(test_filename, "w", encoding="utf-8") as file:
    #         # file.write(json.dumps(json.loads(response.text), indent=4, ensure_ascii=False))
    #         file.write(response.text)
    # urls = [110003569, 110003424, 109999672, 109980396]
    # for url in urls:
    #     p.spider_once_work_page(url)
    p.spider_once_work_page("https://www.pixiv.net/artworks/110322362")
    
    # p.spider_follow_page()
