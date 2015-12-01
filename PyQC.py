#!/usr/bin/env python3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QTextEdit, QWidget, QDialog, QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import glob
import csv
import os

import window1

class MainWindow(QMainWindow, window1.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.button_0.clicked.connect(self.button_0_clicked)
        self.button_05.clicked.connect(self.button_05_clicked)
        self.button_1.clicked.connect(self.button_1_clicked)

        self.shortcut_1 = QShortcut(QKeySequence(Qt.Key_1 + Qt.KeypadModifier), self)
        self.shortcut_2 = QShortcut(QKeySequence(Qt.Key_2 + Qt.KeypadModifier), self)
        self.shortcut_3 = QShortcut(QKeySequence(Qt.Key_3 + Qt.KeypadModifier), self)
        self.shortcut_1.activated.connect(self.button_1_clicked)
        self.shortcut_2.activated.connect(self.button_05_clicked)
        self.shortcut_3.activated.connect(self.button_0_clicked)

        self.actionOpen_Directory.triggered.connect(self.openDir)
        self.actionOpen_Files.triggered.connect(self.openFiles)
        self.actionSave_As.triggered.connect(self.SaveAs)

        self.filelist = list()
        self.path = None
        self.image = None
        self.listlocation = 0

        self.tableWidget.cellClicked.connect(self.switchToItem)

        if len(sys.argv) > 1:
            self.filelist = sys.argv[1:]
            self.openArgumentFiles()


    def button_0_clicked(self):
        self.tableWidget.setItem(self.listlocation,1, QTableWidgetItem("0"))
        self.listlocation += 1
        self.image = QPixmap(self.filelist[self.listlocation])
        self.label.setPixmap(self.image.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.tableWidget.scrollToItem(self.tableWidget.item(self.listlocation,0), QAbstractItemView.PositionAtCenter)
        self.tableWidget.selectRow(self.listlocation)
    def button_05_clicked(self):
        self.tableWidget.setItem(self.listlocation,1, QTableWidgetItem("0.5"))
        self.listlocation += 1
        self.image = QPixmap(self.filelist[self.listlocation])
        self.label.setPixmap(self.image.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.tableWidget.scrollToItem(self.tableWidget.item(self.listlocation,0), QAbstractItemView.PositionAtCenter)
        self.tableWidget.selectRow(self.listlocation)
    def button_1_clicked(self):
        self.tableWidget.setItem(self.listlocation,1, QTableWidgetItem("1"))
        self.listlocation += 1
        self.image = QPixmap(self.filelist[self.listlocation])
        self.label.setPixmap(self.image.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.tableWidget.scrollToItem(self.tableWidget.item(self.listlocation,0), QAbstractItemView.PositionAtCenter)
        self.tableWidget.selectRow(self.listlocation)
    def scaleImage(self, factor):
        self.label.setPixmap(self.image.scaled(self.label.pixmap().size()*factor, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))
    def wheelEvent(self,event):
        if event.angleDelta().y() > 0:
            self.scaleImage(1.1)
        else:
            self.scaleImage(0.9)

    def resizeEvent(self,resizeEvent):
        if self.image:
            self.label.setPixmap(self.image.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def openDir(self):
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.directory:
            self.filelist = glob.glob(self.directory + "/*.jpg")
            self.filelist.extend(glob.glob(self.directory + "/*.png"))
            self.filelist.extend(glob.glob(self.directory + "/*.gif"))
            self.tableWidget.setRowCount(len(self.filelist))
            for i in range(len(self.filelist)):
                item=QTableWidgetItem()
                item.setText(os.path.splitext(os.path.basename(self.filelist[i]))[0])
                self.tableWidget.setItem(i,0,item)
            self.listlocation = 0
            self.image = QPixmap(self.filelist[0])
            self.label.setPixmap(self.image.scaled(QSize(759,710), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.tableWidget.scrollToItem(self.tableWidget.item(self.listlocation,0), QAbstractItemView.PositionAtCenter)
            self.tableWidget.selectRow(self.listlocation)

    def openFiles(self):
        self.filelist, _ = QFileDialog.getOpenFileNames(self, 'Select Files', '', ("Images (*.gif *.png *.jpg)"))
        if self.filelist:
            self.tableWidget.setRowCount(len(self.filelist))
            for i in range(len(self.filelist)):
                item=QTableWidgetItem()
                item.setText(os.path.splitext(os.path.basename(self.filelist[i]))[0])
                self.tableWidget.setItem(i,0,item)
            self.listlocation = 0
            self.image = QPixmap(self.filelist[0])
            self.label.setPixmap(self.image.scaled(QSize(759,710), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.tableWidget.scrollToItem(self.tableWidget.item(self.listlocation,0), QAbstractItemView.PositionAtCenter)
            self.tableWidget.selectRow(self.listlocation)

    def openArgumentFiles(self):
        self.tableWidget.setRowCount(len(self.filelist))
        for i in range(len(self.filelist)):
            item=QTableWidgetItem()
            item.setText(os.path.splitext(os.path.basename(self.filelist[i]))[0])
            self.tableWidget.setItem(i,0,item)
        self.listlocation = 0
        self.image = QPixmap(self.filelist[0])
        self.label.setPixmap(self.image.scaled(QSize(759,710), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.tableWidget.scrollToItem(self.tableWidget.item(self.listlocation,0), QAbstractItemView.PositionAtCenter)
        self.tableWidget.selectRow(self.listlocation)

    def switchToItem(self, row, column):
        self.listlocation = row
        self.image = QPixmap(self.filelist[self.listlocation])
        self.label.setPixmap(self.image.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.tableWidget.scrollToItem(self.tableWidget.item(self.listlocation,0), QAbstractItemView.PositionAtCenter)
        self.tableWidget.selectRow(self.listlocation)

    def SaveAs(self):
        self.path,_ = QFileDialog.getSaveFileName(
                self, 'Save File', '', 'CSV(*.csv)')
        if self.path:
            with open(self.path, 'w', newline='') as f:
                writer = csv.writer(f)
                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
            f.close()

    def Save(self):
        if self.path:
            with open(self.path, 'w', newline='') as f:
                writer = csv.writer(f)
                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
        else:
            self.SaveAs()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
