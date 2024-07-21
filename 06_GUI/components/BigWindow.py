from PyQt5.QtCore import Qt
from .CustomWindow import CustomWindow
from .BigWindow_Stereo import BigWindow_Stereo
from .BigWindow_Red import RedWidget


class BigWindow(CustomWindow):
    def __init__(self, content_widget=None):
        super().__init__()
        self.initUI(content_widget)

    def initUI(self, content_widget=None):
        self.setWindowFlags(Qt.FramelessWindowHint)

        if self.centralWidget() is not None:
            self.centralWidget().deleteLater()

        if content_widget is None:
            content_widget = RedWidget()
        self.setCentralWidget(content_widget)

        self.showFullScreen()
