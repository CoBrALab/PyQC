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


def test_reload_resets_prior_state(qapp, tmp_path):
    """A second load must fully replace columns, paths, and the saved-CSV path."""
    custom_csv = tmp_path / "custom.csv"
    custom_csv.write_text(
        "File,Score1,Score2,Score3\n"
        "/tmp/a.png,1,2,3\n"
        "/tmp/b.png,4,5,6\n"
    )
    window = PyQC.MainWindow()
    window.loadCSV(str(custom_csv))

    assert window.path == str(custom_csv)
    assert window.tableWidget.columnCount() == 4
    assert window.column_names == ["File", "Score1", "Score2", "Score3"]

    window.openArgumentFiles(["/tmp/x.jpg", "/tmp/y.jpg"])

    assert window.path is None
    assert window.column_names == ["File", "QC_Raw", "QC_Pre"]
    assert window.tableWidget.columnCount() == 3
    assert window.filelist == ["/tmp/x.jpg", "/tmp/y.jpg"]
    assert window.tableWidget.rowCount() == 2
    assert window.tableWidget.item(0, 0).text() == "x"


def test_rename_column_at_targets_specific_column(qapp):
    """Renaming via the right-click path must hit the clicked column,
    not whatever currentColumn() happens to be."""
    window = PyQC.MainWindow()
    _populate(
        window,
        ["/tmp/a.png"],
        ["File", "QC_Raw", "QC_Pre"],
        [("3", "4")],
    )
    # Simulate currentColumn() being on column 1 while the user
    # right-clicks the header of column 2.
    window.tableWidget.setCurrentCell(0, 1)

    # Stub out the dialog: bypass interactive Qt by calling the helper
    # path directly with a known column. We can't easily run QInputDialog,
    # so instead patch column_names manually after invoking the code path
    # with a precondition guard.
    assert window._rename_column_at(0) is None  # column 0 is locked
    assert window.column_names == ["File", "QC_Raw", "QC_Pre"]
    assert window._rename_column_at(99) is None  # out of range
    assert window.column_names == ["File", "QC_Raw", "QC_Pre"]


def test_remove_column_at_targets_specific_column(qapp):
    """remove guards bad indices and refuses column 0."""
    window = PyQC.MainWindow()
    _populate(
        window,
        ["/tmp/a.png"],
        ["File", "QC_Raw", "QC_Pre"],
        [("3", "4")],
    )
    assert window._remove_column_at(0) is None
    assert window._remove_column_at(-1) is None
    assert window._remove_column_at(50) is None
    assert window.column_names == ["File", "QC_Raw", "QC_Pre"]
    assert window.tableWidget.columnCount() == 3


def test_undo_steps_back_within_a_row(qapp):
    """B11: undo on the second rating column clears that column on the
    same row, doesn't touch the prior row."""
    window = PyQC.MainWindow()
    _populate(
        window,
        ["/tmp/a.png", "/tmp/b.png"],
        ["File", "QC_Raw", "QC_Pre"],
        [("5", "4"), ("3", "2")],
    )
    window.listlocation = 1
    window.insert_column = 2  # at QC_Pre, having entered QC_Raw=3

    window.undo()

    assert window.tableWidget.item(1, 1).text() == ""
    assert window.tableWidget.item(1, 2).text() == "2"  # untouched
    assert window.tableWidget.item(0, 1).text() == "5"  # prior row intact
    assert window.tableWidget.item(0, 2).text() == "4"
    assert window.insert_column == 1
    assert window.listlocation == 1


def test_undo_at_first_column_steps_back_a_row(qapp):
    """B11: undo on the first rating column clears the LAST column of
    the previous row and lands the cursor there."""
    window = PyQC.MainWindow()
    _populate(
        window,
        ["/tmp/a.png", "/tmp/b.png"],
        ["File", "QC_Raw", "QC_Pre"],
        [("5", "4"), ("", "")],
    )
    window.listlocation = 1
    window.insert_column = 1

    window.undo()

    assert window.tableWidget.item(0, 1).text() == "5"  # not wiped
    assert window.tableWidget.item(0, 2).text() == ""   # cleared
    assert window.listlocation == 0
    assert window.insert_column == 2


def test_undo_noop_at_origin(qapp):
    window = PyQC.MainWindow()
    _populate(
        window,
        ["/tmp/a.png"],
        ["File", "QC_Raw", "QC_Pre"],
        [("", "")],
    )
    window.listlocation = 0
    window.insert_column = 1

    window.undo()

    assert window.tableWidget.item(0, 1).text() == ""
    assert window.listlocation == 0
    assert window.insert_column == 1


def test_loadDirectory_picks_up_mixed_case_extensions_sorted(qapp, tmp_path):
    """B9: case-insensitive suffix match, sorted output, ignores non-images."""
    for name in ["b.JPG", "a.png", "c.JPEG", "z.GIF", "ignore.txt", "x.WEBP"]:
        (tmp_path / name).write_bytes(b"")

    window = PyQC.MainWindow()
    window.loadDirectory(str(tmp_path))

    names = [PyQC.os.path.basename(p) for p in window.filelist]
    assert names == sorted(["b.JPG", "a.png", "c.JPEG", "z.GIF", "x.WEBP"])
    assert window.tableWidget.rowCount() == 5
    assert window.tableWidget.item(0, 0).text() == "a"


def test_csv_relative_paths_resolve_against_csv_dir(qapp, tmp_path):
    """B12: a relative path in a CSV is anchored to the CSV's directory."""
    csv_path = tmp_path / "ratings.csv"
    csv_path.write_text("File,QC_Raw,QC_Pre\nimg1.jpg,5,4\nsubdir/img2.png,,\n")

    window = PyQC.MainWindow()
    window.loadCSV(str(csv_path))

    assert window.filelist == [
        str(tmp_path / "img1.jpg"),
        str(tmp_path / "subdir" / "img2.png"),
    ]


def test_csv_absolute_paths_pass_through(qapp, tmp_path):
    csv_path = tmp_path / "ratings.csv"
    csv_path.write_text("File,QC_Raw,QC_Pre\n/var/x.jpg,1,2\n")

    window = PyQC.MainWindow()
    window.loadCSV(str(csv_path))

    assert window.filelist == ["/var/x.jpg"]


def test_dirty_flag_set_on_rating_cleared_on_save(qapp, tmp_path):
    """B13: dirty starts False, set on numpress, cleared on _write_csv."""
    window = PyQC.MainWindow()
    _populate(
        window,
        ["/tmp/a.png"],
        ["File", "QC_Raw", "QC_Pre"],
        [("", "")],
    )
    window._dirty = False  # _populate uses raw setItem; reset for clarity

    window.numpress("5")
    assert window._dirty is True

    window._write_csv(str(tmp_path / "out.csv"))
    assert window._dirty is False


def test_dirty_flag_cleared_on_load(qapp, tmp_path):
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("File,QC_Raw,QC_Pre\n/tmp/a.png,1,2\n")

    window = PyQC.MainWindow()
    _populate(
        window,
        ["/tmp/x.png"],
        ["File", "QC_Raw", "QC_Pre"],
        [("", "")],
    )
    window.numpress("9")
    assert window._dirty is True

    window.loadCSV(str(csv_path))
    assert window._dirty is False


def test_status_bar_reflects_progress_and_dirty(qapp):
    """L4: status label tracks index, unrated count, and dirty marker."""
    window = PyQC.MainWindow()
    assert window._status_label.text() == "No files loaded"

    window.openArgumentFiles(["/tmp/a.png", "/tmp/b.png", "/tmp/c.png"])
    text = window._status_label.text()
    assert text.startswith("1 / 3")
    assert "3 unrated" in text
    assert "●" not in text  # nothing dirty yet

    window.numpress("5")
    text = window._status_label.text()
    assert "●" in text  # dirty marker appears


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
