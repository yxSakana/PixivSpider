# -*- coding: utf-8 -*-
"""
 @file: src/main.py
 @Description: 
 @author: sxy
 @data: 2023-07-16 20:09:07
 @update: 2023-07-16 20:09:07
"""
import sys

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

from pixiv.pixiv import Pixiv
from ui.login_ui import PixivLogin
from ui.main_ui import PixivMainUi


class PixivApp(QObject):
    def __init__(self, config_filename: str = "config/config.json", parent: QObject | None = None):
        super().__init__(parent)
        self.pixiv = Pixiv(config_filename)
        self.login_ui = PixivLogin(self.pixiv)
        self.main_ui = PixivMainUi(self.pixiv)

        self.login_ui.login_signal.connect(self.logged)

    def logged(self):
        self.main_ui.show()
        self.pixiv.reloadConfig()

    def app(self):
        if self.pixiv.config_json["logged"] and self.pixiv.cookies_pools[0]:
            self.main_ui.show()
        else:
            self.login_ui.show()
            with open(self.pixiv.config_filename, "w") as f:
                self.pixiv.config_json["logged"] = "false"
                f.write(self.pixiv.config_json)
                self.pixiv.reloadConfig()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pixiv_app = PixivApp()
    pixiv_app.app()

    app.exec_()
