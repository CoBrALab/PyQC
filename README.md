# PyQC

A tool for reviewing QC images and storing ratings.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for Python package management.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## Running

```bash
# Show help
uv run pyqc --help

# Review specific images
uv run pyqc image1.jpg image2.png

# Review all images in a directory
uv run pyqc --directory /path/to/images

# Load from CSV (resumes from first unrated image)
uv run pyqc --csv ratings.csv
```

## Usage

Load data via the command line or use the GUI menu options:
- **Open Directory**: Load all images from a folder
- **Open Files**: Select specific image files
- **Open CSV**: Load a previous CSV file and resume reviewing

### Keyboard Shortcuts

| Key(s) | Action |
|--------|--------|
| 0-9 | Assign rating (alternates between QC_Raw and QC_Pre) |
| W or / | Navigate up without rating |
| S or * | Navigate down without rating |
| . | Undo - clear the most recently entered rating cell |
| +/- | Zoom in/out |
| Mouse wheel | Zoom in/out |

View Control Settings
- Menu->Fit to page
- Menu->Full size

## Development notes

### To re-generate the GUI:

`window1.ui` promotes the image label to `SaneDefaultsImageLabel`, so
`pyuic5` generates a working `window1.py` with no manual edits:

```bash
pyuic5 window1.ui -o window1.py
```

