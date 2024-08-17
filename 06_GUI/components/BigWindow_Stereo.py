import sys
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageQt
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QFileDialog
from .ImageLabel import ImageLabel

class BigWindow_Stereo(QWidget):
    IMAGE_DIRS = ["../02_Utils/Images/", "./02_Utils/Images/"]

    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_images = {}

    def initUI(self):
        self.showFullScreen()  # Set window to fullscreen mode

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = ImageLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.image_label)

        self.rgb_label = QLabel(self, objectName="rgbLabel", alignment=Qt.AlignCenter)
        self.set_rgb_label_css('background-color: transparent; border: transparent; color: transparent;')
        self.rgb_label.hide()

        self.image_label.rgb_values_signal.connect(self.update_rgb_label)

        self.try_load_image("StartGUI_2.jpg")

    def try_load_image(self, image_name):
        for image_path in (os.path.join(d, image_name) for d in BigWindow_Stereo.IMAGE_DIRS):
            if self.load_and_display_image(image_path):
                return
        print("Failed to load image from both directories")
        sys.exit(-1)

    def load_and_display_image(self, image_input):
        # Prüfen, ob der Input ein Pfad (String) oder direkt ein Bild ist
        if isinstance(image_input, str):
            pixmap = QPixmap(image_input)
            if pixmap.isNull():
                return False
        elif isinstance(image_input, QPixmap):
            pixmap = image_input
        elif isinstance(image_input, np.ndarray):
            # Konvertiere das NumPy-Array zu einem QImage und dann zu einem QPixmap
            height, width, channel = image_input.shape
            bytes_per_line = 3 * width
            qimage = QImage(image_input.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
        else:
            raise ValueError("Invalid input type. Expected str, QPixmap, or np.ndarray.")
        
        # Resize pixmap to match the full screen, keeping aspect ratio
        screen_size = self.screen().size()
        pixmap = pixmap.scaled(screen_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.depth_map = np.random.rand(pixmap.height(), pixmap.width()) * 255
        self.image_label.setPixmap(pixmap, self.depth_map)
        return True

    def update_rgb_label(self, x, y, r, g, b, depth):
        if x == -1 and y == -1:
            self.rgb_label.hide()
        else:
            self.rgb_label.setText(f'RGB ({r}, {g}, {b}), Depth: {depth:.2f}' if r != -1 else 'Outside Image')
            self.rgb_label.move(x + 500, y)
            self.rgb_label.show()

    def set_rgb_label_css(self, css):
        self.rgb_label.setStyleSheet(css)

    def open_image_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp);;All Files (*)")
        if file_name:
            self.load_and_display_image(file_name)

    def capture(self):
        print("capture begin")
        self.current_images['left'] = self.create_colored_image((0, 0, 255))  # Blaues Bild
        self.current_images['right'] = self.create_colored_image((255, 0, 0))  # Rotes Bild
        combined_image = self.combine_images(self.current_images['left'], self.current_images['right'])
        self.current_images['combined'] = combined_image

        # Konvertiere PIL-Bild in QPixmap
        qim = ImageQt(combined_image)  # Konvertiere PIL-Bild in QImage
        pixmap = QPixmap.fromImage(qim)  # Konvertiere QImage in QPixmap
        
        self.load_and_display_image(pixmap)
        print("capture end")

    def create_colored_image(self, color):
        # Erstelle ein Bild mit der angegebenen Farbe
        image = Image.new("RGB", (100, 100), color)
        return image

    def combine_images(self, image_left, image_right):
        combined_image = Image.new("RGB", (image_left.width + image_right.width, max(image_left.height, image_right.height)))
        combined_image.paste(image_left, (0, 0))
        combined_image.paste(image_right, (image_left.width, 0))
        return combined_image

    def save_images(self):
        if not self.current_images:
            print("No images to save.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        directory = os.path.join("02_Utils", "Images", "captured", timestamp)
        os.makedirs(directory, exist_ok=True)

        for name, image in self.current_images.items():
            image_path = os.path.join(directory, f"{name}.png")
            image.save(image_path)
            print(f"Saved {name} image to {image_path}")
