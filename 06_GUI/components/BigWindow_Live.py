import sys
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication, QGraphicsView, QGraphicsScene

class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage()

    def set_image(self, image):
        self.image = image
        self.update()

    def drawBackground(self, painter, rect):
        if self.image.isNull():
            return
        painter.drawImage(rect, self.image)

class Display(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = CustomGraphicsScene(self)
        self.setScene(self.scene)

    @pyqtSlot(QImage)
    def on_image_received(self, image):
        self.scene.set_image(image)
        self.update()

class BigWindow_Live(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Set the background color to red
        self.setStyleSheet("background-color: red;")

        # Create a button and add it to the layout
        self.button = QPushButton('Click Me')
        layout.addWidget(self.button)

        # Create a display widget for live images
        self.display = Display()
        layout.addWidget(self.display)

        self.setLayout(layout)

        # Timer to simulate receiving images
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(1000 // 30)  # 30 FPS

    def update_image(self):
        # Create a dummy image for demonstration
        image = QImage(640, 480, QImage.Format_RGB32)
        image.fill(Qt.green)  # Fill the image with green color for visibility
        self.display.on_image_received(image)