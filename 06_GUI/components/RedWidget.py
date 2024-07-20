import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication

class RedWidget(QWidget):
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

        self.setLayout(layout)