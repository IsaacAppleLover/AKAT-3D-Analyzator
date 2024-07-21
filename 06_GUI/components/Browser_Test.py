import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Lokale HTML Seite anzeigen')
        self.setGeometry(100, 100, 800, 600)

        # Erstellen eines zentralen Widgets und Layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # QWebEngineView Widget erstellen
        self.browser = QWebEngineView()

        # Pfad zur lokalen HTML-Seite festlegen
        # Annahme: HTML-Datei befindet sich im Hauptverzeichnis
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
        local_html_path = os.path.join(project_dir, 'test.html')
        local_html_url = QUrl.fromLocalFile(local_html_path)

        # Lokale HTML-Seite laden
        self.browser.setUrl(local_html_url)

        # Browser Widget zum Layout hinzufügen
        layout.addWidget(self.browser)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())
