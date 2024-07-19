from PyQt5.QtWidgets import QVBoxLayout, QLabel, QCheckBox, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from .CustomWindow import CustomWindow
from .Button import Button

class SmallWindow(CustomWindow):
    checkbox_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Kleines Fenster')
        self.setGeometry(300, 300, 400, 200)
        self.center()

        layout = QVBoxLayout()

        button1 = Button('Button 1')
        button2 = Button('Button 2')
        button3 = Button('Button 3')

        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)

        checkbox = QCheckBox('Show Label')
        checkbox.stateChanged.connect(self.emit_checkbox_state)
        layout.addWidget(checkbox)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def emit_checkbox_state(self, state):
        self.checkbox_state_changed.emit(state != Qt.Checked)
