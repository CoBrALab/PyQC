# PyQC

A tool for reviewing QC images and storing ratings.

Load data via either the command line or the open files
open directory function.

Use the numeric keys on the keybord to assign that score
to current image.

Use `w` and `s` or `/` and `*` to navigatge up and down the list without
assigning a rating. Use `.` to undo previous rating.
`+` and `-` control image zoom.

## Dependencies

PyQt5 (python3-pyqt5 in Ubuntu)

## TODO

- loading from prior CSV data

View Control Settings
- Menu->Fit to page
- Menu->Full size

## Development notes
To re-generate GUI:
``pyuic5 window1.ui -o window1.py``
