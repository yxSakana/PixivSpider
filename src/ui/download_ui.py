# -*- coding: utf-8 -*-
"""
 @file: src/ui/download_ui.py
 @Description: 
 @author: sxy
 @data: 2023-08-01 14:28:46
 @update: 2023-08-01 14:28:46
"""


import sys

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import \
    QApplication, QWidget, QTabWidget, \
    QPushButton, QAction, QLineEdit, QLabel, QMessageBox, \
    QVBoxLayout, QHBoxLayout, \
    QTableView, QHeaderView, QSizePolicy
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

        self.pixiv.spider_once_work_page(url_or_id)

    def loadEmptyModel(self):
        data = {
            "userId": "",
            "wordId": "",
            "start_url": "",
            "title": "",
            "pageCount": "",
            "userName": "",
            "tags": "",
            "description": ""
        }
        initModel(data, self.model)
        self.model_view.setModel(self.model)


class PixivUserWorksDownloadUi(QWidget):
    def __init__(self, pixiv, parent: QWidget):
        super().__init__(parent)

        self.pixiv = pixiv
        self.work_count = 0

        # init Ui
        # url 输入
        self.url_label = QLabel("url(uid): ", self)
        self.url_edit = QLineEdit(self)
        self.start_pb = QPushButton("Download", self)
        self.layout_1 = QHBoxLayout()
        self.layout_1.addWidget(self.url_label)
        self.layout_1.addWidget(self.url_edit)
        self.layout_1.addWidget(self.start_pb)
        # 数据显示视图
        self.model_view = QTableView()
        self.model = QStandardItemModel()
        self.model.setColumnCount(2)
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
        self.pixiv.get_user_workId_signal.connect(lambda work_id: ThreadUtils.createAndRunThread(self.addItem, work_id))

    def onStart(self):
        url_or_id = self.url_edit.text()
        if not url_or_id:
            QMessageBox.warning(self, "Url Input Error", "输入为空!")
            return

        self.pixiv.spider_user_page(url_or_id)

    def addItem(self, work_id: int):
        """
        添加新的 wordId 到视图上
        :param work_id:
        :return:
        """
        key_item = self.model.item(self.work_count, 0)
        if not key_item:
            key_item = QStandardItem()
            self.model.setItem(self.work_count, 0, key_item)
        key_item.setText("workId")

        val_item = self.model.item(self.work_count, 1)
        if not val_item:
            val_item = QStandardItem()
            self.model.setItem(self.work_count, 0, val_item)
        val_item.setText(str(work_id))
        # 设置表格内容居中对齐
        for row in range(self.model.rowCount()):
            for column in range(self.model.columnCount()):
                self.model.setData(self.model.index(row, column), Qt.AlignCenter, Qt.TextAlignmentRole)

        self.model_view.setModel(self.model)


class PixivDownloadUi(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.pixiv = Pixiv("config/config.json")

        # init Action
        self.download_once_work = QAction(QIcon(), "Download Once Work", self)
        self.download_user_works = QAction(QIcon(), "Download User Works", self)
        self.download_trends = QAction(QIcon(), "Download Trends", self)
        self.download_follow_users_works = QAction(QIcon(), "Download Follow Users Works", self)

        # init Ui
        self.top_tool_bar = QTabWidget(self)
        once_work_widget = PixivOnceWorksDownloadUi(pixiv=self.pixiv, parent=self)
        user_works_download_ui = PixivUserWorksDownloadUi(self.pixiv, self)
        self.top_tool_bar.addTab(once_work_widget, QIcon("resource/fill.png"), "单个作品")
        self.top_tool_bar.addTab(user_works_download_ui, QIcon("resource/多素材.png"), "用户的所有作品")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.top_tool_bar)
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    p = PixivDownloadUi()
    p.show()

    app.exec_()
