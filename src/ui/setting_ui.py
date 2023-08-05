# -*- coding: utf-8 -*-
"""  
  @projectName PixivSpider
  @file setting_ui.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-03 14:26
"""
import os
import sys
import json

from PyQt5.QtWidgets import \
    QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, \
    QHBoxLayout, QVBoxLayout, \
    QFileDialog
from PyQt5.QtGui import QIcon

from pixiv.Pixiv import PixivSpider


class PixivSettingUi(QWidget):
    def __init__(self, pixiv: PixivSpider, parent: QWidget | None = None):
        super().__init__(parent)
        self.pixiv = pixiv

        # init ui
        # config
        self.name_label_config = QLabel("Config File: ", self)
        self.content_edit_config = QLineEdit(os.path.abspath(self.pixiv.configure.config_filename), self)
        self.content_edit_config.setReadOnly(True)
        layout_config = QHBoxLayout()
        layout_config.addWidget(self.name_label_config)
        layout_config.addWidget(self.content_edit_config)
        # horizontal line
        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.HLine)
        horizontal_line.setFrameShadow(QFrame.Sunken)
        # download path
        self.name_label_download_path = QLabel("Download Path: ", self)
        self.content_edit_download_path = QLineEdit(self.pixiv.downloader.download_path, self)
        self.pb_download_path = QPushButton(QIcon("resource/Directory.png"), "", self)
        layout_download_path = QHBoxLayout()
        layout_download_path.addWidget(self.name_label_download_path)
        layout_download_path.addWidget(self.content_edit_download_path)
        layout_download_path.addWidget(self.pb_download_path)
        # cookie files
        self.name_label_cookie_files = QLabel("Cookies Files:     ", self)
        with open(self.pixiv.configure.config_filename, "r") as f:
            _filename = os.path.abspath(json.loads(f.read())["spider"]["Requests"]["cookie_files"][0])
        self.content_edit_cookie_files = QLineEdit(_filename, self)
        self.pb_cookie_files = QPushButton(QIcon("resource/cookie.png"), "", self)
        self.text_edit_cookie_files = QTextEdit(self.pixiv.requester.headers["cookie"], self)
        layout_cookie_files = QVBoxLayout()
        layout_cookie_files_1 = QHBoxLayout()
        layout_cookie_files_1.addWidget(self.name_label_cookie_files)
        layout_cookie_files_1.addWidget(self.content_edit_cookie_files)
        layout_cookie_files_1.addWidget(self.pb_cookie_files)
        layout_cookie_files.addLayout(layout_cookie_files_1)
        layout_cookie_files.addWidget(self.text_edit_cookie_files)

        # layout
        layout = QVBoxLayout()
        layout.addLayout(layout_config)
        layout.addWidget(horizontal_line)
        layout.addLayout(layout_download_path)
        layout.addLayout(layout_cookie_files)
        self.setLayout(layout)

        # slot sign connect
        self.pb_download_path.clicked.connect(self.onSelectDownloadPath)
        self.pb_cookie_files.clicked.connect(self.onSelectCookieFiles)

    def onSelectDownloadPath(self):
        result = QFileDialog.getExistingDirectory(self, "select download path", os.getcwd())
        if result:
            self.pixiv.base_path = result
            self.pixiv.base_download_path = result
            print(self.pixiv.configure.config_filename)
            with open(self.pixiv.configure.config_filename, "r", encoding="utf-8") as file:
                data = json.loads(file.read())
            data["spider"]["Downloader"]["download_path"] = result
            with open(self.pixiv.configure.config_filename, "w", encoding="utf-8") as file:
                file.write(json.dumps(data, indent=4, ensure_ascii=False))
            self.pixiv.reloadConfigure()
            self.content_edit_download_path.setText(self.pixiv.downloader.download_path)

    def onSelectCookieFiles(self):
        result = QFileDialog.getOpenFileName(self, "select cookies files", os.getcwd())
        if result:
            with open(self.pixiv.configure.config_filename, "r", encoding="utf-8") as file:
                data = json.loads(file.read())
            data["spider"]["Requests"]["cookie_files"][0] = result[0]
            with open(self.pixiv.configure.config_filename, "w", encoding="utf-8") as file:
                file.write(json.dumps(data, indent=4, ensure_ascii=False))
            self.pixiv.reloadConfigure()
            self.pixiv.requester.headers["cookie"] = self.pixiv.requester.cookie_pools[0]
            self.text_edit_cookie_files.setText(self.pixiv.requester.headers["cookie"])


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    p = PixivSpider("config/config.json")
    t = PixivSettingUi(p)
    t.show()

    app.exec_()
