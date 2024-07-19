import sys
import os
import subprocess
from threading import Thread
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Pfad zur HTML-Datei
file_path = './../03_3D_Visualization/3Dvisualize.html'
os.chdir(os.path.dirname(file_path))

# Funktion zum Starten des HTTP-Servers
def start_server():
    subprocess.run(['python', '-m', 'http.server', '8000'])

# Starten des HTTP-Servers in einem separaten Thread
server_thread = Thread(target=start_server)
server_thread.setDaemon(True)
server_thread.start()

# PyQt-Setup für den Browser
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simple PyQt Browser')
        self.setGeometry(100, 100, 1200, 800)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('http://localhost:8000/' + os.path.basename(file_path)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        central_widget.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
