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
uv run pyqc
```

Or pass image files as arguments:

```bash
uv run pyqc image1.jpg image2.png ...
```

## Usage

Load data via either the command line or the open files
open directory function.

Use the numeric keys on the keybord to assign that score
to current image.

Use `w` and `s` or `/` and `*` to navigatge up and down the list without
assigning a rating. Use `.` to undo previous rating.
`+` and `-` control image zoom.

## TODO

- loading from prior CSV data

View Control Settings
- Menu->Fit to page
- Menu->Full size

## Development notes

### To re-generate GUI:

First, use `pyuic5` to automatically generate the python code from the user interface `.ui` file:

``pyuic5 window1.ui -o window1.py``

Then, modify window1.py as follows:

- import from `image_widgets.py`:

```python
# Add the following:
from image_widget import *
```

- Switch from `QtWidgets.QLabel` to `SaneDefaultsImageLabel`:

```python
# Replace (around line 90):
self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)

# with
self.label = SaneDefaultsImageLabel()
```

- Switch from `scrollAreaWidgetContents` to `label`:

```python
# Replace (around line 100):
self.scrollArea.setWidget(self.scrollAreaWidgetContents)

# with
self.scrollArea.setWidget(self.label)
```

