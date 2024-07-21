import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QLineEdit, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class BigWindow_Browser(QWidget):
    def __init__(self):
        super(BigWindow_Browser, self).__init__()

        self.browser = QWebEngineView()

        self.init_ui()
        self.load_default_html()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        self.setLayout(layout)

    def load_default_html(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.abspath(os.path.join(script_dir, os.pardir, os.pardir))
        local_html_path = os.path.join(project_dir, '03_3D_Visualization', '3Dvisualize.html')
        local_html_url = QUrl.fromLocalFile(local_html_path)
        self.browser.setUrl(local_html_url)