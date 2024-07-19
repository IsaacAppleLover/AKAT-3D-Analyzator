from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QMouseEvent, QColor
from PyQt5.QtWidgets import QLabel
import numpy as np

class ImageLabel(QLabel):
    rgb_values_signal = pyqtSignal(int, int, int, int, int, float)  # x, y, R, G, B, depth

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)  # Enable mouse tracking
        self.pixmap = None
        self.depth_map = None

    def setPixmap(self, pixmap, depth_map):
        super().setPixmap(pixmap)
        self.pixmap = pixmap
        self.depth_map = depth_map

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.pixmap is not None and self.depth_map is not None:
            x = event.pos().x()
            y = event.pos().y()
            # Calculate the top-left position of the pixmap within the label
            label_width = self.width()
            label_height = self.height()
            pixmap_width = self.pixmap.width()
            pixmap_height = self.pixmap.height()

            offset_x = max((label_width - pixmap_width) // 2, 0)
            offset_y = max((label_height - pixmap_height) // 2, 0)

            # Adjust coordinates relative to the pixmap
            pixmap_x = x - offset_x
            pixmap_y = y - offset_y

            if 0 <= pixmap_x < pixmap_width and 0 <= pixmap_y < pixmap_height:
                image = self.pixmap.toImage()  # Convert QPixmap to QImage
                color = QColor(image.pixel(pixmap_x, pixmap_y))  # Get the color of the pixel
                depth = self.depth_map[pixmap_y, pixmap_x]
                self.rgb_values_signal.emit(pixmap_x, pixmap_y, color.red(), color.green(), color.blue(), depth)
            else:
                self.rgb_values_signal.emit(x, y, -1, -1, -1, -1)  # Signal for outside the image
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        # Emit a signal to indicate that the mouse has left the label
        self.rgb_values_signal.emit(-1, -1, -1, -1, -1, -1)
        super().leaveEvent(event)
