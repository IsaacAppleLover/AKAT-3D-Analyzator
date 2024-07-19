import sys
import os
import subprocess
from threading import Thread
from PyQt5.QtCore import QUrl, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Path to the HTML file
file_path = os.path.abspath('./03_3D_Visualization/3Dvisualize.html')
os.chdir(os.path.dirname(file_path))

# Function to start the HTTP server
def start_server():
    subprocess.run(['python', '-m', 'http.server', '8000'])

# Start the HTTP server in a separate thread
server_thread = Thread(target=start_server)
server_thread.setDaemon(True)
server_thread.start()

# PyQt setup for the browser
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

        self.control_window = ControlWindow(self.browser)
        self.control_window.show()

class ControlWindow(QMainWindow):
    def __init__(self, browser):
        super().__init__()
        self.setWindowTitle('Control Panel')
        self.setGeometry(1300, 100, 300, 200)
        self.browser = browser

        layout = QVBoxLayout()

        self.solid_button = QPushButton('Solid')
        self.solid_button.clicked.connect(self.set_solid)
        layout.addWidget(self.solid_button)

        self.point_cloud_button = QPushButton('Point Cloud')
        self.point_cloud_button.clicked.connect(self.set_point_cloud)
        layout.addWidget(self.point_cloud_button)

        self.wireframe_button = QPushButton('Wireframe')
        self.wireframe_button.clicked.connect(self.set_wireframe)
        layout.addWidget(self.wireframe_button)

        self.slider_label = QLabel('Depth')
        layout.addWidget(self.slider_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(5)
        self.slider.setValue(1)
        self.slider.setSingleStep(1)
        self.slider.sliderReleased.connect(self.slider_released)
        layout.addWidget(self.slider)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    @pyqtSlot()
    def set_solid(self):
        self.browser.page().runJavaScript('document.getElementById("solidButton1").click(); document.getElementById("solidButton2").click();')

    @pyqtSlot()
    def set_point_cloud(self):
        self.browser.page().runJavaScript('document.getElementById("pointCloudButton1").click(); document.getElementById("pointCloudButton2").click();')

    @pyqtSlot()
    def set_wireframe(self):
        self.browser.page().runJavaScript('document.getElementById("wireframeButton1").click(); document.getElementById("wireframeButton2").click();')

    @pyqtSlot()
    def slider_released(self):
        value = self.slider.value()
        js_code = f"""
        document.getElementById("depthSlider1").value = {value};
        document.getElementById("depthSlider2").value = {value};
        var event = new Event('input', {{
            'bubbles': true,
            'cancelable': true
        }});
        document.getElementById("depthSlider1").dispatchEvent(event);
        document.getElementById("depthSlider2").dispatchEvent(event);
        """
        self.browser.page().runJavaScript(js_code)

def main():
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
