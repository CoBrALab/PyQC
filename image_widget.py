#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Example code for a PyQt image-display widget which Just Works™

TODO: Split this into a loader wrapper and a widget wrapper so it can be used
      in designs which maintain a preloaded queue of upcoming images to improve
      the perception of quick load times.
      reworke adaptScale() so they have the same type signature.

Note from HeleleMama:
    Based on Stephan Sokolow's work, I did the following:
    1) re-arrange his structure to make things clearer.
    2) Fix wrong image size while reloading image/Fix GIF flicker while loading
    3) add adjustSize(), which performs like QLabel.adjustSize()
    4) inherit from QLabel directly

"""

from __future__ import (
    absolute_import,
    division,
    print_function,
    with_statement,
    unicode_literals,
)

__author__ = "Stephan Sokolow (deitarion/SSokolow); HeleleMama"
__license__ = "MIT"

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QImageReader, QMovie, QPalette, QPixmap
from PyQt5.QtWidgets import QLabel


class SaneQMovie(QMovie):
    """add adaptScale method"""

    def __init__(self, *args, **kwargs):
        super(SaneQMovie, self).__init__(*args, **kwargs)
        self.jumpToFrame(0)
        # Save the original aspect for later use
        self.orig_size = self.currentImage().size()
        self.aspect = self.orig_size.width() / self.orig_size.height()

    def adaptScale(self, size):
        """Manually implement aspect-preserving scaling for QMovie"""
        # Thanks to Spencer @ https://stackoverflow.com/a/50166220/435253
        # for figuring out that this approach must be taken to get smooth
        # up-scaling out of QMovie.
        width = size.height() * self.aspect
        if width <= size.width():
            n_size = QSize(width, size.height())
        else:
            height = size.width() / self.aspect
            n_size = QSize(size.width(), height)
        self.setScaledSize(n_size)

    def size(self):
        """Return original size"""
        return self.orig_size


class SaneQPixmap(QPixmap):
    """add adaptScale method"""

    def adaptScale(self, size):
        """aspect-preserving scaling for QPixmap"""
        # To avoid having to change which widgets are hidden and shown,
        # do our upscaling manually.
        #
        # This probably won't be suitable for widgets intended to be
        # resized as part of normal operation (aside from initially, when
        # the window appears) but it works well enough for my use cases and
        # was the quickest, simplest thing to implement.
        #
        # If your problem is downscaling very large images, I'd start by
        # making this one- or two-line change to see if it's good enough:
        #  1. Use Qt.FastTransformation to scale to the closest power of
        #     two (eg. 1/2, 1/4, 1/8, etc.) that's still bigger and gives a
        #     decent looking intermediate result.
        #  2. Use Qt.SmoothTransform to take the final step to the desired
        #     size.
        #
        # If it's not or you need actual animation, you'll want to look up
        # how to do aspect-preserving display of images and animations
        # under QML (embeddable in a QWidget GUI using QQuickWidget) so Qt
        # can offload the scaling to the GPU.
        return self.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def _sizeCheck(c_size, n_size):
    """Check if new size alter current dimension"""
    if c_size.width() == n_size.width() and c_size.height() <= n_size.height():
        return False
    if c_size.height() == n_size.height() and c_size.width() <= n_size.width():
        return False
    return True


class SaneDefaultsImageLabel(QLabel):
    """Compound widget to work around some shortcomings in Qt image display.

    - Animated GIFs will animate, like in a browser, by transparently switching
      between QImage and QMovie internally depending on the number of frames
      detected by QImageReader.
    - Content will scale up or down to fit the widget while preserving its
      aspect ratio and will do so without imposing a minimum size of 100%.
    - Letterbox/pillarbox borders will default to transparent.
      (It's a bit of a toss-up whether an application will want this or the
       default window background colour, so this defaults to the choice that
       provides an example of how to accomplish it.)

    Note that QImageReader doesn't have an equivalent to GdkPixbufLoader's
    `area-prepared` and `area-updated` signals, so incremental display for
    for high-speed scanning (ie. hitting "next" based on a partially loaded
    images) isn't really possible. The closest one can get is to experiment
    with QImageReader's support for loading just part of a JPEG file to see if
    it can be done without significantly adding to the whole-image load time.
    (https://wiki.qt.io/Loading_Large_Images)
    """

    def __init__(self):
        super(SaneDefaultsImageLabel, self).__init__()

        # Default Alignment set to Center
        self.setAlignment(Qt.AlignCenter)

        # Set the letterbox/pillarbox bars to be transparent
        # https://wiki.qt.io/How_to_Change_the_Background_Color_of_QWidget
        pal = self.palette()
        pal.setColor(QPalette.Background, Qt.transparent)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        # Reserve a slot for actual content
        self.content = None

    def load(self, source, adaptSize=True):
        """Load anything that QImageReader or QMovie constructors accept
            adaptSize=True: Initial image size to fit container
            adaptSize=False: Set container's size the same as image
        """

        # Use QImageReader to identify animated GIFs for separate handling
        # (Thanks to https://stackoverflow.com/a/20674469/435253 for this)
        size = QSize(self.width(), self.height())
        image_reader = QImageReader(source)
        if image_reader.supportsAnimation() and image_reader.imageCount() > 1:
            # Set content as Movie
            self.content = SaneQMovie(source)
            # Adjust the widget size
            if adaptSize:
                self.content.adaptScale(size)
            else:
                # Resizing container will trigger resizeEvent()
                self.resize(self.content.size())
            # Start Movie replay
            self.setMovie(self.content)
            self.content.start()

        else:
            # Set content as Image
            self.content = SaneQPixmap(image_reader.read())
            # Adjust the widget size
            if adaptSize:
                self.setPixmap(self.content.adaptScale(size))
            else:
                # Resizing container will trigger resizeEvent()
                self.resize(self.content.size())
                self.setPixmap(self.content)

        # Keep the image from preventing downscaling
        self.setMinimumSize(1, 1)

    def adjustSize(self):
        """Reset content size"""
        # Retrieve content size
        if self.content:
            size = self.content.size()
            # Reset container size
            # Let resizeEvent() to do the rest
            self.resize(size)

    def resizeEvent(self, _event=None):
        """Resize handler to update dimensions of displayed image/animation"""
        size = QSize(self.width(), self.height())
        # super(SaneDefaultsImageLabel, self).resizeEvent(_event)
        # Check both content and current label to prevent false triggering
        if isinstance(self.content, SaneQMovie) and self.movie():
            if _sizeCheck(self.content.currentImage().size(), size):
                self.content.adaptScale(size)

        # Check both content and current label to prevent false triggering
        elif isinstance(self.content, SaneQPixmap) and self.pixmap():
            # Don't waste CPU generating a new pixmap if the resize didn't
            # alter the dimension that's currently bounding its size
            if _sizeCheck(self.pixmap().size(), size):
                self.setPixmap(self.content.adaptScale(size))


def main():
    """Main entry point for demonstration code"""
    # import sys
    # from PyQt5.QtWidgets import QApplication
    if len(sys.argv) != 2:
        print("Usage: {} <image path>".format(sys.argv[0]))
        sys.exit(1)

    # I don't know how reliable it is, but making `app` a global which outlives
    # `main()` seems to fix the "segmentation fault on exit" bug caused by
    # Python and Qt disagreeing on the destruction order for the QObject tree
    # and it's certainly the most concise solution I've yet found.
    global app  # pylint: disable=global-statement, global-variable-undefined

    app = QApplication(sys.argv)

    # Take advantage of how any QWidget subclass can be used as a top-level
    # window for demonstration purposes
    window = SaneDefaultsImageLabel()
    window.load(sys.argv[1])
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    main()

# vim: set sw=4 sts=4 expandtab :
