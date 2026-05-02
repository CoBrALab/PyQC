from PyQt5.QtWidgets import QTableWidgetItem

import PyQC


def _populate(window, filelist, column_names, rating_grid):
    """Fill a window's tableWidget with paths in column 0 and ratings in 1..N."""
    window.filelist = list(filelist)
    window.column_names = list(column_names)
    window.tableWidget.setColumnCount(len(column_names))
    window.tableWidget.setHorizontalHeaderLabels(column_names)
    window.tableWidget.setRowCount(len(filelist))
    for row_idx, (path, ratings) in enumerate(zip(filelist, rating_grid)):
        import os

        display = os.path.splitext(os.path.basename(path))[0]
        window.tableWidget.setItem(row_idx, 0, QTableWidgetItem(display))
        for col_idx, val in enumerate(ratings, start=1):
            window.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(val))


def test_csv_roundtrip_default_columns(qapp, tmp_path):
    window = PyQC.MainWindow()
    filelist = ["/tmp/img1.jpg", "/tmp/img2.jpg", "/tmp/img3.jpg"]
    _populate(
        window,
        filelist,
        ["File", "QC_Raw", "QC_Pre"],
        [("5", "4"), ("3", "2"), ("", "")],
    )

    csv_path = str(tmp_path / "out.csv")
    window._write_csv(csv_path)

    with open(csv_path) as f:
        lines = f.read().splitlines()
    assert lines[0] == "File,QC_Raw,QC_Pre"
    assert lines[1] == "/tmp/img1.jpg,5,4"
    assert lines[2] == "/tmp/img2.jpg,3,2"
    assert lines[3] == "/tmp/img3.jpg,,"

    window2 = PyQC.MainWindow()
    window2.loadCSV(csv_path)

    assert window2.column_names == ["File", "QC_Raw", "QC_Pre"]
    assert window2.filelist == filelist
    assert window2.tableWidget.rowCount() == 3
    assert window2.tableWidget.columnCount() == 3
    assert window2.tableWidget.item(0, 0).text() == "img1"
    assert window2.tableWidget.item(0, 1).text() == "5"
    assert window2.tableWidget.item(0, 2).text() == "4"
    assert window2.tableWidget.item(2, 1).text() == ""
    assert window2.listlocation == 2


def test_csv_roundtrip_custom_columns(qapp, tmp_path):
    window = PyQC.MainWindow()
    filelist = ["/tmp/a.png", "/tmp/b.png"]
    _populate(
        window,
        filelist,
        ["File", "Score1", "Score2", "Score3"],
        [("1", "2", "3"), ("4", "5", "6")],
    )

    csv_path = str(tmp_path / "custom.csv")
    window._write_csv(csv_path)

    window2 = PyQC.MainWindow()
    window2.loadCSV(csv_path)

    assert window2.column_names == ["File", "Score1", "Score2", "Score3"]
    assert window2.tableWidget.columnCount() == 4
    assert window2.filelist == filelist
    assert window2.tableWidget.item(0, 1).text() == "1"
    assert window2.tableWidget.item(0, 3).text() == "3"
    assert window2.tableWidget.item(1, 2).text() == "5"


def test_csv_load_no_header_uses_defaults(qapp, tmp_path):
    csv_path = tmp_path / "no_header.csv"
    csv_path.write_text("/tmp/x.jpg,7,8\n/tmp/y.jpg,9,1\n")

    window = PyQC.MainWindow()
    window.loadCSV(str(csv_path))

    assert window.column_names == ["File", "QC_Raw", "QC_Pre"]
    assert window.filelist == ["/tmp/x.jpg", "/tmp/y.jpg"]
    assert window.tableWidget.item(0, 1).text() == "7"
    assert window.tableWidget.item(1, 2).text() == "1"


def test_save_skips_rows_past_filelist(qapp, tmp_path):
    """Defensive: extra blank rowCount past filelist length must not crash."""
    window = PyQC.MainWindow()
    _populate(window, ["/tmp/only.jpg"], ["File", "QC_Raw", "QC_Pre"], [("3", "")])
    window.tableWidget.setRowCount(5)

    csv_path = str(tmp_path / "trim.csv")
    window._write_csv(csv_path)

    with open(csv_path) as f:
        lines = f.read().splitlines()
    assert lines == ["File,QC_Raw,QC_Pre", "/tmp/only.jpg,3,"]


def test_listlocation_lands_on_first_unrated(qapp, tmp_path):
    csv_path = tmp_path / "partial.csv"
    csv_path.write_text(
        "File,QC_Raw,QC_Pre\n"
        "/tmp/a.jpg,5,4\n"
        "/tmp/b.jpg,3,\n"
        "/tmp/c.jpg,,\n"
    )

    window = PyQC.MainWindow()
    window.loadCSV(str(csv_path))

    assert window.listlocation == 1
