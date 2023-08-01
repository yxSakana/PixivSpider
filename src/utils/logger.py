# -*- coding: UTF-8 -*-
# @Filename: logger.py
# @Author: sxy
# @Date: 2023-05-29 16:21

import os
import logging.config


class Logger(object):
    def __init__(self, name: str, filename: str=""):
        self.name = name
        self.filename = filename

        # level config configure
        self.level_config = {
            "logger": {
                "root": "INFO",
                self.name: "INFO"
            },
            "console": {
                "root": "DEBUG",
                self.name: "DEBUG"
            }
        }
        # logger configure
        self.log_config = {
            "version": 1,
            # Formatter settings 格式化设置
            "formatters": {
                # file Farmatter
                "fileFormatter": {
                    "format": "[%(asctime)s]-%(name)s-[%(levelname)s]: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                # Color Formatter
                "coloredFormatter": {
                    "()": "colorlog.ColoredFormatter",
                    "format": "${log_color}[${asctime}]${name_log_color}${name}${levelname_log_color}[${levelname}]: ${message_log_color}${message}",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "log_colors": {
                        'DEBUG': 'white',
                        'INFO': 'white',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'bold_red',
                    },
                    "secondary_log_colors": {
                        "message": {
                            "DEBUG": "purple",
                            "INFO": "blue"
                        },
                        "name": {
                            "DEBUG": "purple",
                            "INFO": "purple"
                        },
                        "levelname": {
                            "DEBUG": "white",
                            "INFO": "green"
                        }
                    },
                    "style": "$"
                }
            },
            "filters": {},
            # Handler settings
            "handlers": {
                # console Handler -- settings of "root"
                "consoleHandler": {
                    "class": "logging.StreamHandler",
                    "level": self.level_config["console"]["root"],
                    "formatter": "coloredFormatter",
                    "stream": "ext://sys.stdout"
                },
                # color Handler -- settings of "self.name logger"
                "coloredHandler": {
                    "class": "logging.StreamHandler",
                    "level": self.level_config["console"][self.name],
                    "formatter": "coloredFormatter",
                    "stream": "ext://sys.stdout"
                }
            },
            # logger settings
            # root
            "root": {
                "level": self.level_config["logger"]["root"],
                "handlers": ["consoleHandler"]
            },
            # create logger config
            "loggers": {
                self.name: {
                    "level": self.level_config["logger"][self.name],
                    "propagate": 0,
                    "handlers": ["coloredHandler"]
                }
            },
            "incremental": False,
            "disable_existing_loggers": False
        }

        if self.filename:
            self.log_config["handlers"]["fileHandler"] = {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "fileFormatter",
                    "filename": self.filename,
                    "mode": "a",  # mode
                    "maxBytes": 102400,  # 最大文件大小
                    "backupCount": 10,  # 保留的文件个数
                    "encoding": "utf-8",
                    "delay": False  # 延迟
            } 
            self.log_config["loggers"][self.name]["handlers"] = ["fileHandler"]


    @staticmethod
    def get_module_name() -> str:
        """get current module name

        :return str: module
        """
        current_dir = os.getcwd()
        project_name = os.path.basename(current_dir)
        
        return project_name


    @staticmethod
    def get_logger(name: str, filename: str="") -> logging.Logger:
        """create by name

        :param str name: name
        :return logging.Logger: logger
        """
        log_config = Logger(name, filename)
        logging.config.dictConfig(log_config.log_config)
        logger = logging.getLogger(name)

        return logger


    @staticmethod
    def get_module_logger() -> logging.Logger:
        """get logger by current mdule name create

        :return logging.Logger: logger
        """
        module_name = Logger.get_module_name()

        return Logger.get_logger(module_name)
