#!/usr/bin/env python3

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import (
    QKeyEvent,
    QWheelEvent,
    QResizeEvent,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QMenu,
    QAbstractItemView,
    QDialog,
)

import argparse
import csv
import os
import pathlib
import signal
import sys

import window1


class MainWindow(QMainWindow, window1.Ui_MainWindow):
    def __init__(self, files=None, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.actionOpen_Directory.triggered.connect(self.openDir)
        self.actionOpen_Files.triggered.connect(self.openFiles)
        self.actionOpen_CSV.triggered.connect(self.openCSV)
        self.actionSave_As.triggered.connect(self.SaveAs)
        self.action_Save.triggered.connect(self.Save)
        self.actionAdd_Column.triggered.connect(self.addColumn)
        self.actionRename_Column.triggered.connect(self.renameColumn)
        self.actionRemove_Column.triggered.connect(self.removeColumn)
        self.action_Quit.triggered.connect(self.close)
        self.action_Zoom_1_1.triggered.connect(self.zoomTo1_1)
        self.action_Zoom_Fit.triggered.connect(self.zoomToFit)
        self.action_Zoom_In.triggered.connect(self.zoomIn)
        self.action_Zoom_Out.triggered.connect(self.zoomOut)

        self.filelist = list()
        self.path = None
        self.image = None
        self.listlocation = 0
        self.scaleFactor = None
        self._fit_mode = False
        self.insert_column = 1
        self.column_names = ["File", "QC_Raw", "QC_Pre"]
        self._dirty = False

        self._status_label = QLabel()
        self.statusBar().addPermanentWidget(self._status_label)
        self._refresh_status()

        self.tableWidget.cellClicked.connect(self.switchToItem)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.customContextMenuRequested.connect(self.showColumnContextMenu)
        self.tableWidget.horizontalHeader().customContextMenuRequested.connect(
            self.showColumnContextMenu
        )
        self.tableWidget.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)

        self.splitter_3.setSizes([200, 600])
        self.tableWidget.resizeColumnsToContents()

        if files:
            self.openArgumentFiles(files)

    def keyPressEvent(self, a0: QKeyEvent | None) -> None:
        if a0 is None:
            return
        event = a0
        if event.text() in "0123456789":
            self.numpress(event.text())
        elif event.key() == Qt.Key_Period:  # type: ignore[attr-defined]
            self.undo()
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_Slash:  # type: ignore[attr-defined]
            self.navup()
        elif event.key() == Qt.Key_S or event.key() == Qt.Key_Asterisk:  # type: ignore[attr-defined]
            self.navdown()
        elif event.key() == Qt.Key_Plus:  # type: ignore[attr-defined]
            self.scaleImage(1.1)
        elif event.key() == Qt.Key_Minus:  # type: ignore[attr-defined]
            self.scaleImage(0.9)

    def _go_to_row(self, row):
        """Move selection to `row`, load its image, reset zoom. No-op if
        row is out of range or there are no files."""
        if not self.filelist or row < 0 or row >= len(self.filelist):
            return
        self.listlocation = row
        self.label.load(self.filelist[row])
        self.scrollArea.setWidgetResizable(True)
        self.scaleFactor = None
        self._fit_mode = False
        self.tableWidget.scrollToItem(
            self.tableWidget.item(row, 0),
            QAbstractItemView.PositionAtCenter,
        )
        self.tableWidget.selectRow(row)
        self._refresh_status()

    def _count_unrated_rows(self):
        count = 0
        for r in range(self.tableWidget.rowCount()):
            for c in range(1, self.tableWidget.columnCount()):
                item = self.tableWidget.item(r, c)
                if item is None or item.text() == "":
                    count += 1
                    break
        return count

    def _refresh_status(self):
        if not self.filelist:
            text = "No files loaded"
        else:
            text = f"{self.listlocation + 1} / {len(self.filelist)}"
            unrated = self._count_unrated_rows()
            if unrated:
                text += f"   {unrated} unrated"
            if self._dirty:
                text += "   ●"
        self._status_label.setText(text)

    def _toast(self, message, ms=3000):
        bar = self.statusBar()
        if bar is not None:
            bar.showMessage(message, ms)

    def numpress(self, key):
        rating_columns = list(range(1, self.tableWidget.columnCount()))
        if not rating_columns:
            return

        if self.insert_column not in rating_columns:
            self.insert_column = rating_columns[0]

        self.tableWidget.setItem(
            self.listlocation, self.insert_column, QTableWidgetItem(key)
        )
        self._dirty = True

        idx = rating_columns.index(self.insert_column)
        if idx == len(rating_columns) - 1:
            self.insert_column = rating_columns[0]
            if self.listlocation + 1 < len(self.filelist):
                self._go_to_row(self.listlocation + 1)
        else:
            self.insert_column = rating_columns[idx + 1]
        self._refresh_status()

    def navup(self):
        self.insert_column = 1
        self._go_to_row(self.listlocation - 1)

    def navdown(self):
        self.insert_column = 1
        self._go_to_row(self.listlocation + 1)

    def scaleImage(self, factor):
        if not self.label.content or self.label.content.size().width() == 0:
            return  # Protect against empty content and ZeroDivisionError

        if not self.scaleFactor:
            self.scaleFactor = (
                self.label.size().width() / self.label.content.size().width()
            )
        self.scaleFactor *= factor
        self._fit_mode = False
        self.scrollArea.setWidgetResizable(False)
        self.label.resize(self.scaleFactor * self.label.content.size())
        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(
            int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep() / 2))
        )

    def zoomTo1_1(self):
        if not self.label.content or self.label.content.size().width() == 0:
            return
        self._fit_mode = False
        self.scrollArea.setWidgetResizable(False)
        self.scaleFactor = 1.0
        self.label.resize(self.label.content.size())

    def zoomToFit(self):
        if not self.label.content or self.label.content.size().width() == 0:
            return
        content_size = self.label.content.size()
        viewport_size = self.scrollArea.viewport().size()
        scale_width = viewport_size.width() / content_size.width()
        scale_height = viewport_size.height() / content_size.height()
        self.scaleFactor = min(scale_width, scale_height)
        self._fit_mode = True
        self.scrollArea.setWidgetResizable(False)
        self.label.resize(self.scaleFactor * content_size)

    def zoomIn(self):
        self.scaleImage(1.1)

    def zoomOut(self):
        self.scaleImage(0.9)

    def wheelEvent(self, a0: QWheelEvent | None) -> None:
        if a0 is None:
            return
        event = a0
        if event.angleDelta().y() > 0:
            self.scaleImage(1.1)
        else:
            self.scaleImage(0.9)

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        if a0 is None:
            return
        if self._fit_mode:
            self.zoomToFit()

    def _reset_table(self):
        """Wipe table state back to defaults. Called by every loader so that
        re-opening data never inherits stale columns, ratings, or paths."""
        self.column_names = ["File", "QC_Raw", "QC_Pre"]
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(self.column_names))
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)
        self.path = None
        self.filelist = []
        self.listlocation = 0
        self.scaleFactor = None
        self._fit_mode = False
        self.insert_column = 1
        self._dirty = False
        self._refresh_status()

    def _confirm_discard_changes(self):
        """Prompt to save unsaved ratings. Returns True if the caller may
        proceed (saved or discarded), False on cancel or failed save."""
        if not self._dirty:
            return True
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved ratings. Save before continuing?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        if reply == QMessageBox.Cancel:
            return False
        if reply == QMessageBox.Yes:
            self.Save()
            return not self._dirty
        return True

    def closeEvent(self, a0):
        if not self._confirm_discard_changes():
            if a0 is not None:
                a0.ignore()
            return
        if a0 is not None:
            a0.accept()

    def openDir(self):
        if not self._confirm_discard_changes():
            return
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if directory:
            self.loadDirectory(directory)

    IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp")

    def loadDirectory(self, directory):
        """Load images from a directory, sorted, case-insensitive on suffix."""
        files = sorted(
            str(p)
            for p in pathlib.Path(directory).iterdir()
            if p.is_file() and p.suffix.lower() in self.IMAGE_EXTS
        )

        if not files:
            print("Warning: No image files found.")
            return

        self._reset_table()
        self.filelist = files
        self._populate_from_filelist()

    def openFiles(self):
        if not self._confirm_discard_changes():
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", "", ("Images (*.gif *.png *.jpg *.jpeg *.webp)")
        )
        if not files:
            return

        self._reset_table()
        self.filelist = list(files)
        self._populate_from_filelist()

    def openCSV(self):
        if not self._confirm_discard_changes():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV(*.csv)")
        if path:
            self.loadCSV(path)

    def loadCSV(self, path):
        """Load images and ratings from a CSV file.

        Expected format: a header row whose first cell is "File", followed by
        data rows of [path, rating1, rating2, ...]. CSVs without a header row
        are still accepted and assumed to use the default columns.
        """
        print("Opening CSV file: {}".format(path))
        with open(path, "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            print("Warning: CSV file is empty.")
            return

        if rows[0] and rows[0][0] == "File":
            column_names = [c for c in rows[0] if c]
            data_rows = rows[1:]
        else:
            n_cols = max(len(r) for r in rows) if rows else 3
            column_names = ["File"] + [f"Unknown_QC{i}" for i in range(1, n_cols)]
            data_rows = rows

        # Drop blank lines and rows with no path so filelist length stays in
        # sync with rowCount; otherwise _write_csv pairs filelist[i] with
        # the rating cells of a different row.
        data_rows = [r for r in data_rows if r and r[0]]

        if not data_rows:
            print("Warning: CSV file has no data rows.")
            return

        self._reset_table()
        self.path = path
        self.column_names = column_names
        self.tableWidget.setColumnCount(len(self.column_names))
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)
        self.tableWidget.setRowCount(len(data_rows))

        csv_dir = os.path.dirname(os.path.abspath(path))
        self.listlocation = len(data_rows) - 1
        first_unrated_found = False

        for row_idx, rowdata in enumerate(data_rows):
            file_path = rowdata[0]
            if not os.path.isabs(file_path):
                file_path = os.path.normpath(os.path.join(csv_dir, file_path))
            self.filelist.append(file_path)

            display = os.path.splitext(os.path.basename(file_path))[0]
            self.tableWidget.setItem(row_idx, 0, QTableWidgetItem(display))

            for column in range(1, len(self.column_names)):
                val = rowdata[column] if column < len(rowdata) else ""
                self.tableWidget.setItem(row_idx, column, QTableWidgetItem(val))

            if not first_unrated_found:
                for column in range(1, len(self.column_names)):
                    val = rowdata[column] if column < len(rowdata) else ""
                    if val == "":
                        self.listlocation = row_idx
                        first_unrated_found = True
                        break

        self.tableWidget.resizeColumnsToContents()
        self._go_to_row(self.listlocation)

    def openArgumentFiles(self, files):
        if not files:
            print("Warning: No image files provided.")
            return
        self._reset_table()
        self.filelist = list(files)
        self._populate_from_filelist()

    def _populate_from_filelist(self):
        """Render self.filelist into the table and load the first image."""
        self.tableWidget.setRowCount(len(self.filelist))
        for i, path in enumerate(self.filelist):
            display = os.path.splitext(os.path.basename(path))[0]
            self.tableWidget.setItem(i, 0, QTableWidgetItem(display))
        self._go_to_row(self.listlocation)

    def switchToItem(self, row, column):
        rating_columns = list(range(1, self.tableWidget.columnCount()))
        if column in rating_columns:
            self.insert_column = column
        elif rating_columns:
            self.insert_column = rating_columns[0]
        self._go_to_row(row)

    def undo(self):
        """Clear the most recently entered rating cell.

        On the first rating column, this means stepping back a row to its
        last rating column; otherwise it stays on the current row and steps
        insert_column one slot to the left. No-op at the very first cell.
        """
        rating_columns = list(range(1, self.tableWidget.columnCount()))
        if not rating_columns:
            return
        if self.insert_column not in rating_columns:
            self.insert_column = rating_columns[0]

        idx = rating_columns.index(self.insert_column)
        if idx > 0:
            prev_col = rating_columns[idx - 1]
            self.tableWidget.setItem(
                self.listlocation, prev_col, QTableWidgetItem("")
            )
            self.insert_column = prev_col
            self._dirty = True
            self._refresh_status()
        elif self.listlocation > 0:
            target_row = self.listlocation - 1
            last_col = rating_columns[-1]
            self.tableWidget.setItem(target_row, last_col, QTableWidgetItem(""))
            self.insert_column = last_col
            self._dirty = True
            self._go_to_row(target_row)

    def _write_csv(self, path):
        """Write column_names as the header row, then [path, rating1, ...]."""
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.column_names)
            for row in range(self.tableWidget.rowCount()):
                if row >= len(self.filelist):
                    continue
                rowdata = [self.filelist[row]]
                for column in range(1, len(self.column_names)):
                    item = self.tableWidget.item(row, column)
                    rowdata.append(item.text() if item is not None else "")
                writer.writerow(rowdata)
        self._dirty = False
        self._toast(f"Saved {os.path.basename(path)}")
        self._refresh_status()

    def SaveAs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV(*.csv)")
        if path:
            self.path = path
            self._write_csv(self.path)

    def Save(self):
        if self.path:
            self._write_csv(self.path)
        else:
            self.SaveAs()

    def showColumnContextMenu(self, pos):
        header = self.tableWidget.horizontalHeader()

        if header.underMouse():
            local_col = header.logicalIndexAt(pos)
            header_pos = header.mapToGlobal(pos)
        else:
            local_col = self.tableWidget.columnAt(pos.x())
            header_pos = header.mapToGlobal(
                self.tableWidget.viewport().mapFromGlobal(pos)
            )

        if local_col == -1:
            return

        menu = QMenu(self)

        if local_col > 0:
            add_action = menu.addAction("Add Column")  # type: ignore[assignment]
            add_action.triggered.connect(self.addColumn)  # type: ignore[union-attr]

            rename_action = menu.addAction("Rename Column")  # type: ignore[assignment]
            rename_action.triggered.connect(  # type: ignore[union-attr]
                lambda _checked=False, c=local_col: self._rename_column_at(c)
            )

            remove_action = menu.addAction("Remove Column")  # type: ignore[assignment]
            remove_action.triggered.connect(  # type: ignore[union-attr]
                lambda _checked=False, c=local_col: self._remove_column_at(c)
            )

        menu.exec_(header_pos)

    def addColumn(self):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Add Column")
        dialog.setLabelText("Column name:")
        dialog.setTextValue("QC_New")

        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.textValue().strip()
            if not new_name:
                return
            if new_name in self.column_names:
                QMessageBox.warning(
                    self,
                    "Duplicate Column",
                    f"A column named '{new_name}' already exists.",
                )
                return

            self.column_names.append(new_name)
            self.tableWidget.insertColumn(self.tableWidget.columnCount())
            header_item = QTableWidgetItem(new_name)
            header_item.setTextAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
            self.tableWidget.setHorizontalHeaderItem(
                self.tableWidget.columnCount() - 1, header_item
            )

            for row in range(self.tableWidget.rowCount()):
                self.tableWidget.setItem(
                    row, self.tableWidget.columnCount() - 1, QTableWidgetItem("")
                )

            self._dirty = True
            self.tableWidget.resizeColumnsToContents()
            self._refresh_status()

    def renameColumn(self):
        self._rename_column_at(self.tableWidget.currentColumn())

    def _rename_column_at(self, column):
        if column <= 0 or column >= len(self.column_names):
            return

        old_name = self.column_names[column]

        dialog = QInputDialog(self)
        dialog.setWindowTitle("Rename Column")
        dialog.setLabelText("New column name:")
        dialog.setTextValue(old_name)

        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.textValue().strip()
            if not new_name:
                return

            self.column_names[column] = new_name
            header_item = self.tableWidget.horizontalHeaderItem(column)
            if header_item:
                header_item.setText(new_name)
            self._dirty = True
            self.tableWidget.resizeColumnsToContents()
            self._refresh_status()

    def removeColumn(self):
        self._remove_column_at(self.tableWidget.currentColumn())

    def _remove_column_at(self, column):
        if column <= 0 or column >= len(self.column_names):
            return

        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove column '{self.column_names[column]}'? This will delete all data in this column.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.column_names.pop(column)
            self.tableWidget.removeColumn(column)

            rating_columns = list(range(1, self.tableWidget.columnCount()))
            if rating_columns and self.insert_column not in rating_columns:
                self.insert_column = rating_columns[0]

            self._dirty = True

            if self.tableWidget.columnCount() > 0:
                self.tableWidget.setHorizontalHeaderLabels(self.column_names)
                self.tableWidget.resizeColumnsToContents()
            self._refresh_status()


def main():
    parser = argparse.ArgumentParser(
        description="PyQC - A tool for reviewing QC images and storing ratings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Keyboard Shortcuts:
  0-9    Assign rating to current image (alternates between QC_Raw and QC_Pre)
  W / /  Navigate up without rating
  S / *  Navigate down without rating
  .      Undo - clear the most recently entered rating cell
  +/-    Zoom in/out

Examples:
  pyqc image1.jpg image2.png
  pyqc --directory /path/to/images
  pyqc --csv ratings.csv
        """,
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Image files to review (supports: jpg, png, gif, webp, jpeg)",
    )
    parser.add_argument(
        "-d",
        "--directory",
        help="Directory containing images to review",
    )
    parser.add_argument(
        "-c",
        "--csv",
        help="CSV file to load (resumes from first unrated image)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="PyQC 0.1.0",
    )

    args = parser.parse_args()

    app = QApplication(sys.argv)

    # Handle Ctrl-C gracefully. The timer wakes the interpreter every
    # 200ms so Python's signal handler can run between Qt events;
    # without it the GUI sleeps and SIGINT only fires when the user
    # interacts with the window.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sigint_timer = QTimer()
    sigint_timer.start(200)
    sigint_timer.timeout.connect(lambda: None)

    # Handle conflicting arguments
    if args.directory and args.csv:
        parser.error("Cannot specify both --directory and --csv")
    if args.directory and args.files:
        parser.error("Cannot specify both --directory and file arguments")
    if args.csv and args.files:
        parser.error("Cannot specify both --csv and file arguments")

    form = MainWindow()

    # Load files based on arguments
    if args.files:
        form.openArgumentFiles(args.files)
    elif args.directory:
        form.loadDirectory(args.directory)
    elif args.csv:
        form.loadCSV(args.csv)

    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
