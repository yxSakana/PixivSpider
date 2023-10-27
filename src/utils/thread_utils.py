# -*- coding: utf-8 -*-
"""
 @file: thread_utils.py
 @Description: 
 @author: sxy
 @data: 2023-07-17 09:52:13
 @update: 2023-07-17 09:52:13
"""


import sys
import threading
import time
from typing import Optional

from PyQt5.QtCore import QObject, QThread, QMutex, QMutexLocker, QWaitCondition, pyqtSignal
from utils.logger import Logger


class SThread(QThread):
    pause_sign = pyqtSignal()
    pursue_sign = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self.mutex = QMutex()
        self.condition = QWaitCondition()

        self.pause_sign.connect(self.pause)
        self.pursue_sign.connect(self.pursue)

    def pause(self):
        print("pause暂停()")
        locker = QMutexLocker(self.mutex)
        # self.condition.wait(self.mutex)

    def pursue(self):
        print("pursue重新执行()")
        locker = QMutexLocker(self.mutex)
        self.condition.wakeAll()

    def run(self) -> None:
        while True:
            print("a")
            time.sleep(0.5)
        # pass


class ThreadUtils(object):
    logger = Logger.get_logger("ThreadUtils")

    @classmethod
    def createAndRunThread(cls, func, *args):
        try:
            thread = threading.Thread(target=func, args=args)
            thread.setDaemon(True)
            thread.start()
        except Exception as e:
            cls.logger.error(f"Failed: Thread Erroe => {e}")

        return thread

    @classmethod
    def runQThread(cls, qthread: QThread, mode=True):

        def func() :
            qthread.start()
            qthread.wait()

        thread = threading.Thread(target=func)
        thread.setDaemon(mode)
        thread.start()
        return thread


if __name__ == '__main__':
    t = SThread()
    t.start()
    time.sleep(3)
    t.pause_sign.emit()
    time.sleep(3)
    t.pursue_sign.emit()
