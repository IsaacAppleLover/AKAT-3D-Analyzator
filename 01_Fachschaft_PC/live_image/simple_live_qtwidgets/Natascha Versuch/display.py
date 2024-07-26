# \file    display.py
# \author  IDS Imaging Development Systems GmbH
# \date    2021-01-15
# \since   1.2.0
#
# \brief   The Display class implements an easy way to display images from a
#          camera in a QT widgets window. It can be used for other QT widget
#          applications as well.
#
# \version 1.3.0
#
# Copyright (C) 2021 - 2024, IDS Imaging Development Systems GmbH.
#
# The information in this document is subject to change without notice
# and should not be construed as a commitment by IDS Imaging Development Systems GmbH.
# IDS Imaging Development Systems GmbH does not assume any responsibility for any errors
# that may appear in this document.
#
# This document, or source code, is provided solely as an example of how to utilize
# IDS Imaging Development Systems GmbH software libraries in a sample application.
# IDS Imaging Development Systems GmbH does not assume any responsibility
# for the use or reliability of any portion of this document.
#
# General permission to copy or modify is hereby granted.

import math

try:
    from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QWidget
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtCore import QRectF, Slot
except ImportError:
    from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QWidget
    from PySide2.QtGui import QImage, QPainter
    from PySide2.QtCore import QRectF, Slot


class Display(QGraphicsView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__scene = CustomGraphicsScene(self)
        self.setScene(self.__scene)

    @Slot(QImage)
    def on_image_received(self, image: QImage):
        self.__scene.set_image(image)
        self.update()


class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, parent: Display = None):
        super().__init__(parent)
        self.__parent = parent
        self.__image = QImage()

    def set_image(self, image: QImage):
        self.__image = image
        self.update()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        # Display size
        display_width = self.__parent.width()
        display_height = self.__parent.height()

        # Image size
        image_width = self.__image.width()
        image_height = self.__image.height()

        # Return if we don't have an image yet
        if image_width == 0 or image_height == 0:
            return

        # Calculate aspect ratio of display
        ratio1 = display_width / display_height
        # Calculate aspect ratio of image
        ratio2 = image_width / image_height

        if ratio1 > ratio2:
            # The height with must fit to the display height.So h remains and w must be scaled down
            image_width = display_height * ratio2
            image_height = display_height
        else:
            # The image with must fit to the display width. So w remains and h must be scaled down
            image_width = display_width
            image_height = display_height / ratio2

        image_pos_x = -1.0 * (image_width / 2.0)
        image_pox_y = -1.0 * (image_height / 2.0)

        # Remove digits after point
        image_pos_x = math.trunc(image_pos_x)
        image_pox_y = math.trunc(image_pox_y)

        rect = QRectF(image_pos_x, image_pox_y, image_width, image_height)

        painter.drawImage(rect, self.__image)
