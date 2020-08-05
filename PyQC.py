#!/usr/bin/env python3

from __future__ import (
    absolute_import,
    division,
    print_function,
    with_statement,
    unicode_literals,
)

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys
import glob
import csv
import os

import window1


class MainWindow(QMainWindow, window1.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.tableWidget.setColumnWidth(1, 35)

        self.actionOpen_Directory.triggered.connect(self.openDir)
        self.actionOpen_Files.triggered.connect(self.openFiles)
        self.actionSave_As.triggered.connect(self.SaveAs)
        self.action_Save.triggered.connect(self.Save)

        self.filelist = list()
        self.path = None
        self.image = None
        self.listlocation = 0
        self.scaleFactor = None

        self.tableWidget.cellClicked.connect(self.switchToItem)

        if len(sys.argv) > 1:
            self.filelist = sys.argv[1:]
            self.openArgumentFiles()

    def keyPressEvent(self, event):
        if event.text().isnumeric():
            self.numpress(event.text())
        elif event.key() == Qt.Key_Period:
            self.undo()
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_Slash:
            self.navup()
        elif event.key() == Qt.Key_S or event.key() == Qt.Key_Asterisk:
            self.navdown()
        elif event.key() == Qt.Key_Plus:
            self.scaleImage(1.1)
        elif event.key() == Qt.Key_Minus:
            self.scaleImage(0.9)

    def numpress(self, key):
        self.tableWidget.setItem(self.listlocation, 1, QTableWidgetItem(key))
        if (self.listlocation + 1) != len(self.filelist):
            self.listlocation += 1
            self.label.load(self.filelist[self.listlocation])
            self.scrollArea.setWidgetResizable(True)
            self.scaleFactor = None
            self.tableWidget.scrollToItem(
                self.tableWidget.item(self.listlocation, 0),
                QAbstractItemView.PositionAtCenter,
            )
            self.tableWidget.selectRow(self.listlocation)

    def navup(self):
        if not ((self.listlocation - 1) < 0):
            self.listlocation -= 1
            self.label.load(self.filelist[self.listlocation])
            self.scrollArea.setWidgetResizable(True)
            self.scaleFactor = None
            self.tableWidget.scrollToItem(
                self.tableWidget.item(self.listlocation, 0),
                QAbstractItemView.PositionAtCenter,
            )
            self.tableWidget.selectRow(self.listlocation)

    def navdown(self):
        if (self.listlocation + 1) != len(self.filelist):
            self.listlocation += 1
            self.label.load(self.filelist[self.listlocation])
            self.scrollArea.setWidgetResizable(True)
            self.scaleFactor = None
            self.tableWidget.scrollToItem(
                self.tableWidget.item(self.listlocation, 0),
                QAbstractItemView.PositionAtCenter,
            )
            self.tableWidget.selectRow(self.listlocation)

    def scaleImage(self, factor):
        # self.label.setPixmap(self.image.scaled(self.label.pixmap().size()*factor, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if not self.scaleFactor:
            self.scaleFactor = (
                self.label.size().width() / self.label.content.size().width()
            )
        self.scaleFactor *= factor
        self.scrollArea.setWidgetResizable(False)
        self.label.resize(self.scaleFactor * self.label.content.size())
        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(
            int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep() / 2))
        )

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scaleImage(1.1)
        else:
            self.scaleImage(0.9)

    def openDir(self):
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.directory:
            self.filelist = glob.glob(self.directory + "/*.jpg")
            self.filelist.extend(glob.glob(self.directory + "/*.png"))
            self.filelist.extend(glob.glob(self.directory + "/*.gif"))
            self.tableWidget.setRowCount(len(self.filelist))
            for i in range(len(self.filelist)):
                item = QTableWidgetItem()
                item.setText(os.path.splitext(os.path.basename(self.filelist[i]))[0])
                self.tableWidget.setItem(i, 0, item)
            self.listlocation = 0
            self.label.load(self.filelist[self.listlocation])
            self.tableWidget.scrollToItem(
                self.tableWidget.item(self.listlocation, 0),
                QAbstractItemView.PositionAtCenter,
            )
            self.tableWidget.selectRow(self.listlocation)

    def openFiles(self):
        self.filelist, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", "", ("Images (*.gif *.png *.jpg)")
        )
        if self.filelist:
            self.tableWidget.setRowCount(len(self.filelist))
            for i in range(len(self.filelist)):
                item = QTableWidgetItem()
                item.setText(os.path.splitext(os.path.basename(self.filelist[i]))[0])
                self.tableWidget.setItem(i, 0, item)
            self.listlocation = 0
            self.label.load(self.filelist[self.listlocation])
            self.tableWidget.scrollToItem(
                self.tableWidget.item(self.listlocation, 0),
                QAbstractItemView.PositionAtCenter,
            )
            self.tableWidget.selectRow(self.listlocation)

    def openArgumentFiles(self):
        self.tableWidget.setRowCount(len(self.filelist))
        for i in range(len(self.filelist)):
            item = QTableWidgetItem()
            item.setText(os.path.splitext(os.path.basename(self.filelist[i]))[0])
            self.tableWidget.setItem(i, 0, item)
        self.listlocation = 0
        self.label.load(self.filelist[self.listlocation])
        self.tableWidget.scrollToItem(
            self.tableWidget.item(self.listlocation, 0),
            QAbstractItemView.PositionAtCenter,
        )
        self.tableWidget.selectRow(self.listlocation)

    def switchToItem(self, row, column):
        self.listlocation = row
        self.label.load(self.filelist[self.listlocation])
        self.scrollArea.setWidgetResizable(True)
        self.scaleFactor = None
        self.tableWidget.scrollToItem(
            self.tableWidget.item(self.listlocation, 1),
            QAbstractItemView.PositionAtCenter,
        )
        self.tableWidget.selectRow(self.listlocation)

    def undo(self):
        if not ((self.listlocation - 1) < 0):
            self.listlocation = self.listlocation - 1
            self.tableWidget.setItem(self.listlocation, 1, QTableWidgetItem(""))
            self.label.load(self.filelist[self.listlocation])
            self.scrollArea.setWidgetResizable(True)
            self.scaleFactor = None
            self.tableWidget.scrollToItem(
                self.tableWidget.item(self.listlocation, 1),
                QAbstractItemView.PositionAtCenter,
            )
            self.tableWidget.selectRow(self.listlocation)

    def SaveAs(self):
        self.path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV(*.csv)")
        if self.path:
            with open(self.path, "w", newline="") as f:
                writer = csv.writer(f)
                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append("")
                    writer.writerow(rowdata)
            f.close()

    def Save(self):
        if self.path:
            with open(self.path, "w", newline="") as f:
                writer = csv.writer(f)
                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append("")
                    writer.writerow(rowdata)
        else:
            self.SaveAs()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
