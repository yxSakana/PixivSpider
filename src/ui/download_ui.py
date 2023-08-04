# -*- coding: utf-8 -*-
"""
 @file: download_ui.py
 @Description: 
 @author: sxy
 @data: 2023-08-01 14:28:46
 @update: 2023-08-01 14:28:46
"""


import sys

from PyQt5.QtWidgets import \
    QApplication, QWidget, QTabWidget, \
    QPushButton, QRadioButton, QLineEdit, QLabel, QMessageBox, \
    QVBoxLayout, QHBoxLayout, \
    QHeaderView, QSizePolicy
from PyQt5.QtGui import QIcon

from pixiv.pixiv import Pixiv
from utils.qt_utils import *
from utils.thread_utils import ThreadUtils


class PixivOnceWorksDownloadUi(QWidget):
    """
    单个作品
    """
    def __init__(self, pixiv, parent: QWidget = None):
        super().__init__(parent=parent)

        self.pixiv = pixiv

        # init Ui
        # url 输入
        self.url_label = QLabel("url(pid): ", self)
        self.url_edit = QLineEdit(self)
        self.url_edit.setPlaceholderText("输入作品链接(或 id)")
        self.start_pb = QPushButton("Download", self)
        self.layout_1 = QHBoxLayout()
        self.layout_1.addWidget(self.url_label)
        self.layout_1.addWidget(self.url_edit)
        self.layout_1.addWidget(self.start_pb)
        # 数据显示视图
        self.model_view = QTableView()
        self.model = QStandardItemModel()
        self.loadEmptyModel()
        # 设置视图随窗口调节大小
        self.model_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 设置表头自适应大小
        self.model_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格视图自适应大小
        self.model_view.resizeColumnsToContents()
        self.model_view.resizeRowsToContents()

        # 总布局
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.layout_1)
        self.layout.addWidget(self.model_view)
        self.setLayout(self.layout)

        # connect slot
        self.start_pb.clicked.connect(self.onStart)

    def onStart(self):
        url_or_id = self.url_edit.text()
        if not url_or_id:
            QMessageBox.warning(self, "Url Input Error", "输入为空!")
            return

        is_ok, result = self.pixiv.spider_once_work_page(url_or_id)
        if is_ok:
            initModel(result, self.model)
            self.model_view.setModel(self.model)

    def loadEmptyModel(self):
        data = {
            "userId": "",
            "wordId": "",
            "start_url": "",
            "title": "",
            "pageCount": "",
            "userName": "",
            "tags": "",
            "description": "",
        }
        initModel(data, self.model)
        self.model.setHorizontalHeaderLabels(["key", "value"])
        self.model_view.setModel(self.model)


class PixivUserWorksDownloadUi(QWidget):
    """
    用户
    """
    def __init__(self, pixiv, parent: QWidget):
        super().__init__(parent)

        self.pixiv = pixiv
        self.work_count = 0

        # init Ui
        # url 输入
        self.url_label = QLabel("url(uid): ", self)
        self.url_edit = QLineEdit(self)
        self.url_edit.setPlaceholderText("输入用户id(仅仅包含id)")
        self.start_pb = QPushButton("Download", self)
        self.layout_1 = QHBoxLayout()
        self.layout_1.addWidget(self.url_label)
        self.layout_1.addWidget(self.url_edit)
        self.layout_1.addWidget(self.start_pb)
        # 数据显示视图
        self.model_view = QTableView()
        self.model = QStandardItemModel()
        self.model.setColumnCount(2)
        self.model.setHorizontalHeaderLabels(["key", "value"])
        self.model_view.setModel(self.model)
        # 设置视图随窗口调节大小
        self.model_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 设置表头自适应大小
        self.model_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格视图自适应大小
        self.model_view.resizeColumnsToContents()
        self.model_view.resizeRowsToContents()

        # 总布局
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.layout_1)
        self.layout.addWidget(self.model_view)
        self.setLayout(self.layout)

        # connect slot
        self.start_pb.clicked.connect(lambda: ThreadUtils.createAndRunThread(self.onStart))
        self.pixiv.get_user_workId_signal.connect(self.addItem)

    def onStart(self):
        url_or_id = self.url_edit.text()
        if not url_or_id:
            QMessageBox.warning(self, "Url Input Error", "输入为空!")
            return

        self.pixiv.spider_user_works(url_or_id)

    def addItem(self, work_id: int):
        """
        添加新的 wordId 到视图上
        :param work_id:
        :return:
        """
        addDataToItem(self.model, self.work_count, 0, "workId")
        addDataToItem(self.model, self.work_count, 1, work_id)
        setTabelViewAlignCenter(model=self.model)

        self.model_view.setModel(self.model)
        self.work_count += 1


class PixivTrendsDownloadUi(QWidget):
    """
    动态
    """
    def __init__(self, pixiv: Pixiv, parent: QWidget | None = None):
        super().__init__(parent)

        self.pixiv = pixiv

        # init Ui
        self.all_mode = QRadioButton("all", self)
        self.r18_mode = QRadioButton("r18", self)
        self.r18_mode.click()
        layout_1 = QHBoxLayout()
        layout_1.addSpacing(250)
        layout_1.addWidget(self.all_mode)
        layout_1.addWidget(self.r18_mode)

        self.start_pb = QPushButton("Start", self)

        # 数据显示视图
        self.model_view = QTableView()
        self.model = QStandardItemModel()
        self.model.setColumnCount(4)
        self.model_count = 0
        header = ["page", "workId", "url1", "url2"]
        self.model.setHorizontalHeaderLabels(header)
        self.model_view.setModel(self.model)
        # 设置视图随窗口调节大小
        self.model_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 设置表头自适应大小
        self.model_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格视图自适应大小
        self.model_view.resizeColumnsToContents()
        self.model_view.resizeRowsToContents()

        # layout
        self.layout = QVBoxLayout()
        self.layout.addLayout(layout_1)
        self.layout.addWidget(self.start_pb)
        self.layout.addWidget(self.model_view)

        self.setLayout(self.layout)

        # slot connect
        self.start_pb.clicked.connect(lambda: ThreadUtils.createAndRunThread(self.onStart))
        self.pixiv.trends_info_signal.connect(self.addItem)

    def onStart(self):
        mode = "all" if self.all_mode.isChecked() else "r18"
        self.pixiv.spider_trends_pages(mode)

    def addItem(self, page: int, work_id: str, url_1: str, url_2: str):
        addDataToItem(self.model, self.model_count, 0, page)
        addDataToItem(self.model, self.model_count, 1, work_id)
        addDataToItem(self.model, self.model_count, 2, url_1)
        addDataToItem(self.model, self.model_count, 3, url_2)

        setTabelViewAlignCenter(model=self.model)  # 居中

        self.model_view.setModel(self.model)
        self.model_count += 1


class PixivFollowDownloadUi(QWidget):
    def __init__(self, pixiv: Pixiv, parent: QWidget | None = None):
        super().__init__()

        self.pixiv = pixiv

        # init Ui
        self.start_pb = QPushButton("Start", self)

        # layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.start_pb)
        self.setLayout(self.layout)

        # connect
        self.start_pb.clicked.connect(lambda: ThreadUtils.createAndRunThread(self.onStart))

    def onStart(self):
        self.pixiv.spider_follow_users_works()


class PixivDownloadUi(QWidget):
    def __init__(self, pixiv: Pixiv, parent: QWidget = None):
        super().__init__(parent)

        self.pixiv = pixiv

        # init Ui
        self.top_tool_bar = QTabWidget(self)
        once_work_widget = PixivOnceWorksDownloadUi(pixiv=self.pixiv, parent=self)
        user_works_download_ui = PixivUserWorksDownloadUi(self.pixiv, self)
        trends_download_ui = PixivTrendsDownloadUi(self.pixiv, self)
        follow_download_ui = PixivFollowDownloadUi(self.pixiv, self)
        self.top_tool_bar.addTab(once_work_widget, QIcon("resource/fill.png"), "单个作品")
        self.top_tool_bar.addTab(user_works_download_ui, QIcon("resource/User.png"), "用户")
        self.top_tool_bar.addTab(trends_download_ui, QIcon("resource/Trends.png"), "动态")
        self.top_tool_bar.addTab(follow_download_ui, QIcon("resource/Follow.png"), "关注")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.top_tool_bar)
        self.setLayout(self.layout)
