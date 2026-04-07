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

When modifying `window1.ui`:

```bash
pyuic5 window1.ui -o window1.py
```

Then apply these modifications to `window1.py`:
1. Add `from image_widget import *`
2. Replace `QtWidgets.QLabel` with `SaneDefaultsImageLabel`
3. Replace `self.scrollArea.setWidget(self.scrollAreaWidgetContents)` with `self.scrollArea.setWidget(self.label)`

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
