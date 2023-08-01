# -*- coding: utf-8 -*-#
"""
  @projectName PixivSpider
  @file action.cpp
  @brief



  @author yx
  @date 2023-08-01 16:30
"""

from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from pixiv.pixiv import Pixiv


class AOnceWork(QAction):
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon())
        self.setText("once work")
        self.setStatusTip("下载单个作品")

