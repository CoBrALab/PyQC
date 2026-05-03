# PyQC - Agent Instructions

## Setup & Commands

```bash
uv sync              # Install dependencies
uv run pyqc --help   # Show CLI help
uv run pyqc <files>  # Run the app
```

## Architecture

- **Entry point**: `PyQC.py:main()` → CLI args → `MainWindow`
- **GUI**: `window1.py` (auto-generated from `window1.ui` via `pyuic5`)
- **Image display**: `image_widget.py` → `SaneDefaultsImageLabel` (custom scaling)

## Codegen Workflow

`window1.ui` promotes the image label to `SaneDefaultsImageLabel` and
puts it directly inside the `QScrollArea`, so `pyuic5` produces
working code without any manual post-edits:

```bash
pyuic5 window1.ui -o window1.py
# or, without pyuic5 on $PATH:
uv run python -m PyQt5.uic.pyuic window1.ui -o window1.py
```

If you ever need to re-add a wrapper widget or replace the promoted
label, edit `window1.ui` in Qt Designer rather than patching the
generated `window1.py` by hand.

## Key Files

| File | Purpose |
|------|---------|
| `PyQC.py` | CLI entry point, MainWindow class |
| `window1.py` | Auto-generated UI code |
| `window1.ui` | Qt Designer UI definition |
| `image_widget.py` | Custom image/movie widget with scaling |

## Dependencies

- Python 3.14
- PyQt5 >= 5.15.0

## Dynamic Column Management

Right-click on any rating column header to add/remove/rename columns:

- **Add Column** - Appends a new rating column at the end
- **Rename Column** - Renames the selected column (data preserved)
- **Remove Column** - Deletes the column and all its data (with confirmation)

The "File" column (first column) is locked and cannot be modified.
