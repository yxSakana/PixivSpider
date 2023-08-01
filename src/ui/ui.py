# -*- coding: utf-8 -*-
"""
 @file: src/ui/ui.py
 @Description: 
 @author: sxy
 @data: 2023-08-01 14:28:46
 @update: 2023-08-01 14:28:46
"""


import sys
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget, QApplication

class PixivMainUi(QMainWindow):
    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self.initUi()

    def initUi(self):
        self.central_widget = QWidget()

        self.layout = QHBoxLayout()
        self.left_tool_tab = QTableWidget(self.central_widget)  #  左侧工具栏
        # self.layout.add
        

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    p = PixivMainUi()
    p.show()

    app.exec_()

