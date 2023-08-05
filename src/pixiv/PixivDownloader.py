# -*- coding: utf-8 -*-
"""  
  @projectName PixivSpiderNew
  @file PixivDownloader.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-05 14:20
"""

import os.path

from pixiv.PixivConfigure import PixivConfigure
from pixiv.PixivRequester import PixivRequester
from spider_toolkit.Downloader import Downloader


class PixivDownloader(Downloader):
    def __init__(self, requester: PixivRequester, configure: PixivConfigure):
        super().__init__(requester, configure)

    def downloadPixivImage(self, url: str, filename: str) -> tuple[str, str]:
        filename = os.path.sep.join([filename, url.split("/")[-1]])
        return self.downloadImage(url, filename)

    def downloadComment(self, data: str, dir_name: str):
        if not data:
            return
        filename = os.sep.join([self.download_path, dir_name, "illustComment.txt"])
        with open(filename, "w",encoding="utf-8") as file:
            file.write(data)
