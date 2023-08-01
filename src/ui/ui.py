# -*- coding: utf-8 -*-
"""
 @file: src/ui/ui.py
 @Description: 
 @author: sxy
 @data: 2023-08-01 14:28:46
 @update: 2023-08-01 14:28:46
"""

import sys
from PyQt5.QtWidgets import QMainWindow, QTabWidget, \
    QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget, QApplication
from PyQt5.QtGui import QIcon

class PixivMainUi(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.initUi()

    def initUi(self):
        self.setGeometry(550, 200, 950, 750)

        self.central_widget = QWidget()

        self.layout = QHBoxLayout()
        self.left_tool_tab = QTabWidget(self.central_widget)  # 左侧工具栏
        a = QWidget()
        self.left_tool_tab.addTab(a, QIcon(), "woaihdfnosijhdo")
        self.left_tool_tab.setTabPosition(QTabWidget.West)
        self.left_tool_tab.setStyleSheet("QTabBar::tab { width: 100px; height: 30px; text-align: center; }")

        self.layout.addWidget(self.left_tool_tab)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    p = PixivMainUi()
    p.show()

    app.exec_()
