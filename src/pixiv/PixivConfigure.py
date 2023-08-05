# -*- coding: utf-8 -*-
"""  
  @projectName PixivSpiderNew
  @file PixivConfigure.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-05 14:20
"""


from spider_toolkit.Configure import Configure


class PixivConfigure(Configure):
    def __init__(self, config_filename: str = "config/config.json"):
        super().__init__(config_filename)
