# -*- coding: utf-8 -*-
"""
 @file: src/ui/main_ui.py
 @Description: 
 @author: sxy
 @data: 2023-08-01 14:28:46
 @update: 2023-08-01 14:28:46
"""

import sys
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QMainWindow, \
    QTabBar, QStylePainter, QStyleOptionTab, QStyle

from ui.download_ui import *
from ui.setting_ui import PixivSettingUi


class TabBar(QTabBar):
    """
    重构QTabWidget使其竖直选项卡文字水平
    """
    def tabSizeHint(self, index):

        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event) :

        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()) :
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class TabWidget(QTabWidget) :
    """
    重构QTabWidget使其竖直选项卡文字水平
    """
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))


class PixivMainUi(QMainWindow):
    def __init__(self, pixiv: Pixiv, parent: QWidget = None):
        super().__init__(parent)

        self.pixiv = pixiv

        # initUi
        self.setGeometry(550, 200, 950, 750)

        # TabWidget
        self.tab_widget = TabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.download_ui = PixivDownloadUi(self.pixiv, self)
        self.setting_ui = PixivSettingUi(self.pixiv, self)

        self.tab_widget.addTab(self.download_ui, QIcon("resource/Download.png"), "Download")
        self.tab_widget.addTab(self.setting_ui, QIcon("resource/Settings.png"), "Setting")

        # 布局
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.tab_widget)
        # central widget of MainWindow
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
