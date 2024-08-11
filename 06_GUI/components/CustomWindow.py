from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget
from PyQt5.QtCore import Qt

class CustomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LumiDepth')
        self.initUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_5:
            QApplication.quit()

    def center(self):
        frame = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())

    def initUI(self):
        pass

    def closeEvent(self, event):
        """Override the closeEvent to ensure the application quits when the window is closed."""
        QApplication.quit()
