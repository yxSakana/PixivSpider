# -*- coding: utf-8 -*-
"""  
  @projectName PixivSpider
  @file qt_utils.py.py
  @brief 
 
 
 
  @author yx 
  @date 2023-08-01 19:47
"""

from PyQt5.QtWidgets import QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QObject


class ModelToolkit(QObject):
    @staticmethod
    def setKeyModel(info: dict, model: QStandardItemModel):
        model.setHorizontalHeaderLabels(["key", "val"])

        for row, (key, val) in enumerate(info.items()):
            key_item = QStandardItem(key)
            val_item = QStandardItem(str(val))
            model.setItem(row, 0, key_item)
            model.setItem(row, 1, val_item)


def initModel(data: dict, model: QStandardItemModel, count: int = 2):
    model.setColumnCount(count)

    for row, (key, val) in enumerate(data.items()):
        key_item = model.item(row, 0)
        if not key_item:
            key_item = QStandardItem()
            model.setItem(row, 0, key_item)
        key_item.setText(key)

        val_item = model.item(row, 1)
        if not val_item:
            val_item = QStandardItem()
            model.setItem(row, 1, val_item)
        val_item.setText(str(val))
        setTabelViewAlignCenter(model)


def setTabelViewAlignCenter(model):
    """
    设置表格内容居中对齐
    :param model:
    :return:
    """
    for row in range(model.rowCount()):
        for column in range(model.columnCount()):
            model.setData(model.index(row, column), Qt.AlignCenter, Qt.TextAlignmentRole)


def addDataToItem(model, row, col, data):
    item = model.item(row, col)
    if not item:
        item = QStandardItem()
        model.setItem(row, col, item)
    item.setText(str(data))
