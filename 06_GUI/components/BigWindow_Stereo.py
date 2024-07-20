import sys
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel
from .ImageLabel import ImageLabel

class BigWindow_Stereo(QWidget):
    IMAGE_DIR = "../02_Utils/Images/00_3D_Visualization/01_Images/"

    def __init__(self):
        super().__init__()
        self.initUI()
        self.pixmap = None
        self.depth_map = None

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = ImageLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.rgb_label = QLabel(self)
        self.rgb_label.setObjectName("rgbLabel")
        self.rgb_label.setAlignment(Qt.AlignCenter)
        self.rgb_label.hide()

        self.load_and_display_image(f"{BigWindow_Stereo.IMAGE_DIR}Stereo-Test02.jpg")

        self.set_rgb_label_css('background-color: transparent; border: transparent; color: transparent;')

        self.label.rgb_values_signal.connect(self.update_rgb_label)

    def load_and_display_image(self, image_path):
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            RED_TEXT = "\033[91m"
            RESET_TEXT = "\033[0m"
            print(f"{RED_TEXT}Failed to load image from {image_path}{RESET_TEXT}")
            sys.exit(-1)

        screen_size = self.screen().size()
        scaled_pixmap = pixmap.scaled(screen_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.depth_map = np.random.rand(scaled_pixmap.height(), scaled_pixmap.width()) * 255
        self.label.setPixmap(scaled_pixmap, self.depth_map)

    def update_rgb_label(self, x, y, r, g, b, depth):
        if x == -1 and y == -1:
            self.rgb_label.hide()
        else:
            if r == -1 and g == -1 and b == -1:
                self.rgb_label.setText('Outside Image')
            else:
                self.rgb_label.setText(f'RGB ({r}, {g}, {b}), Depth: {depth:.2f}')

            self.rgb_label.adjustSize()
            offsetX = 500
            offsetY = 0
            self.rgb_label.move(x + offsetX, y + offsetY)
            self.rgb_label.show()

    def set_rgb_label_css(self, css):
        self.rgb_label.setStyleSheet(css)
