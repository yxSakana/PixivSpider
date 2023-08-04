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
from PyQt5.QtCore import QThread
from utils.logger import Logger


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
    def runQThread(cls, qthread, mode=True):

        def func() :
            qthread.start()
            qthread.wait()

        thread = threading.Thread(target=func)
        thread.setDaemon(mode)
        thread.start()
        return thread
