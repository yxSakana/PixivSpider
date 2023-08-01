# -*- coding: utf-8 -*-
"""
 @file: src/ui/pixiv_ui.py
 @Description: 
 @author: sxy
 @data: 2023-07-17 13:58:41
 @update: 2023-07-17 13:58:41
"""


import sys
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QTableWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QStackedLayout, QPushButton


class PixivUi(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
    
    def initUi(self):
        # self.setCentralWidget()
        self.setWindowTitle("Pixiv")

        self.central_widget = QWidget()
        left_tab_widget = QTableWidget()
        right_stacked = QStackedLayout()

        