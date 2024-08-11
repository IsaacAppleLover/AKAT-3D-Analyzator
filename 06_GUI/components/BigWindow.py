import os
import colors
from PyQt5.QtCore import Qt
from .CustomWindow import CustomWindow
from .BigWindow_Stereo import BigWindow_Stereo
from .BigWindow_Red import BigWindow_Red
from PyQt5.QtWidgets import QLabel

class BigWindow(CustomWindow):
    def __init__(self, content_widget=None):
        super().__init__()
        self.initUI(content_widget)
        self.apply_stylesheet('BigWindow.css')

    def initUI(self, content_widget=None):
        self.setWindowFlags(Qt.FramelessWindowHint)

        if self.centralWidget() is not None:
            self.centralWidget().deleteLater()

        if content_widget is None:
            content_widget = BigWindow_Red()
        self.setCentralWidget(content_widget)

        self.rgb_label = QLabel(self)
        self.rgb_label.setObjectName("rgbLabel")
        self.rgb_label.setAlignment(Qt.AlignCenter)
        self.rgb_label.hide()

        #self.set_rgb_label_css('background-color: transparent; border: transparent; color: transparent;')

        self.showFullScreen()

    def set_rgb_label_css(self, css):
        self.rgb_label.setStyleSheet(css)

    def apply_stylesheet(self, css):
        css_file = os.path.join(os.path.dirname(__file__), css)
        if os.path.exists(css_file):
            with open(css_file, "r") as file:
                self.setStyleSheet(file.read())
        else: 
            print(colors.color_text(f"\tCSS file '{css}' not found.", colors.COLOR_RED))