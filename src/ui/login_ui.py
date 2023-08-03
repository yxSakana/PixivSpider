# -*- coding: utf-8 -*-
"""  
  @projectName PixivSpider
  @file login_ui.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-03 20:12
"""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import \
    QWidget, \
    QLabel, QLineEdit, QPushButton, QMessageBox, QSpacerItem, \
    QFormLayout, QVBoxLayout

from pixiv.login import Login
from pixiv.pixiv import Pixiv
from utils.thread_utils import ThreadUtils


class PixivLogin(QWidget):
    login_signal = pyqtSignal()

    def __init__(self, pixiv: Pixiv, parent: QWidget | None = None):
        super().__init__(parent)
        self.login_script = Login()
        self.pixiv = pixiv

        # init ui
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setGeometry(500, 500, 500, 250)
        name_label_username = QLabel("username: ", self)
        self.edit_username = QLineEdit(self)
        self.edit_username.setPlaceholderText("输入用户名")
        name_label_pwd = QLabel("password: ", self)
        self.edit_pwd = QLineEdit(self)
        self.edit_pwd.setPlaceholderText("输入密码")

        self.login_pb = QPushButton("login", self)

        # 布局
        form_layout = QFormLayout()
        tmp = QSpacerItem(5, 30)
        form_layout.addItem(tmp)
        form_layout.addRow(name_label_username, self.edit_username)
        form_layout.addItem(tmp)
        form_layout.addRow(name_label_pwd, self.edit_pwd)
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.login_pb)
        self.setLayout(layout)

        # sign slot connect
        self.login_pb.clicked.connect(lambda: ThreadUtils.createAndRunThread(self.onLogin))

    def onLogin(self):
        self.login_pb.setText("logging in")
        self.login_pb.setEnabled(False)
        username = self.edit_username.text()
        pwd = self.edit_pwd.text()
        if not (username or pwd):
            QMessageBox.warning(self, "Error", "username OR password 为空")
            self.login_pb.setEnabled(True)
            return

        cookies = self.login_script.login(username, pwd)
        if cookies:
            with open(self.pixiv.cookies_filenames[0], "w") as file:
                file.write(cookies)
            self.login_signal.emit()
            self.hide()
        else:
            QMessageBox.warning(self, "Error", "用户名或密码错误!")
