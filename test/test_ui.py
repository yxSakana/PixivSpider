# -*- coding: utf-8 -*-
"""
 @file: test\\test_ui.py
 @Description: 
 @author: sxy
 @data: 2023-07-20 17:01:01
 @update: 2023-07-20 17:01:01
"""

import sys
from pathlib import Path
sys.path.append(str(Path.cwd()) + "\\src")
from ui.pixiv_ui import PixivUi
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui = PixivUi()
    ui.show()
    
    sys.exit(app.exec_())  
