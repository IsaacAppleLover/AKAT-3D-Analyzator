import importlib.util
import sys
import os
import glob
import shutil  # Neu hinzugefügt, um Verzeichnisse zu löschen
import tempfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageQt import ImageQt
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QFileDialog
from .ImageLabel import ImageLabel  # Import korrigiert

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import colors

def import_module_from_path(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

#gemini_module = import_module_from_path("test_alex_gemini", os.path.join("01_Fachschaft_PC", "test_alex_gemini.py"))
#gemini_main = gemini_module.main

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

        self.try_load_image("StartGUI.jpg")

    def try_load_image(self, image_name):
        for image_path in (os.path.join(d, image_name) for d in BigWindow_Stereo.IMAGE_DIRS):
            if self.load_and_display_image(image_path):
                return
        print("Failed to load image from both directories")
        sys.exit(-1)

    def load_and_display_image(self, image_input):
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
        print(colors.color_text("Start Capture...", colors.COLOR_GREEN))
        gemini_main()
        print(colors.color_text("\tCapture successful...", colors.COLOR_GREEN))

        # Pfad zum Verzeichnis, in dem die Bilder gespeichert werden
        base_dir = r'02_Utils\Images\04_capturedImages'
        
        # Den neuesten Ordner im Verzeichnis finden
        list_of_dirs = glob.glob(os.path.join(base_dir, '*'))
        latest_dir = max(list_of_dirs, key=os.path.getmtime)
        
        # Pfad zu den Bildern "links" und "rechts"
        left_image_path = os.path.join(latest_dir, 'left.bmp')
        right_image_path = os.path.join(latest_dir, 'right.bmp')
        
        # Bilder laden und kombinieren
        left_image = Image.open(left_image_path)
        right_image = Image.open(right_image_path)
        combined_image = self.combine_images(left_image, right_image)
        
        # Kombiniertes Bild speichern
        combined_image_path = os.path.join(latest_dir, 'combined.bmp')
        combined_image.save(combined_image_path)
        
        # Kombiniertes Bild als QPixmap laden
        pixmap = QPixmap(combined_image_path)
        
        # Pixmap laden und anzeigen
        self.load_and_display_image(pixmap)

    def combine_images(self, image_left, image_right):
        combined_image = Image.new("RGB", (image_left.width + image_right.width, max(image_left.height, image_right.height)))
        combined_image.paste(image_left, (0, 0))
        combined_image.paste(image_right, (image_left.width, 0))
        return combined_image

    def delete(self):
        base_dir = r'02_Utils\Images\04_capturedImages'
        
        # Den neuesten Ordner im Verzeichnis finden
        list_of_dirs = glob.glob(os.path.join(base_dir, '*'))
        if not list_of_dirs:
            print(colors.color_text(f"\tNo directories found to delete.", colors.COLOR_RED))
            return
        
        latest_dir = max(list_of_dirs, key=os.path.getmtime)
        
        # Verzeichnis löschen
        shutil.rmtree(latest_dir)
        print(colors.color_text(f"\tImage successfully deleted.", colors.COLOR_GREEN))
        
        # StartGUI.jpg wieder anzeigen
        self.try_load_image("StartGUI.jpg")

