from PyQt5.QtWidgets import QVBoxLayout, QRadioButton, QCheckBox, QWidget, QApplication, QButtonGroup
from PyQt5.QtCore import Qt, pyqtSignal
from .CustomWindow import CustomWindow
from .Button import Button
from .InformationLabel import InformationLabel
from .MenuBar import MenuBar  # Import the MenuBar component
import sys

class SmallWindow(CustomWindow):
    checkbox_state_changed = pyqtSignal(bool)
    radio_button_changed = pyqtSignal(str)  # Signal to indicate which radio button is selected

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 400, 200)
        self.center()

        layout = QVBoxLayout()

        self.button1 = Button('Button 1')
        self.informationLabel1 = InformationLabel(true_text="This text is green.", false_text="This text is red.")
        self.button2 = Button('Button 2')
        self.informationLabel2 = InformationLabel(true_text="All systems go.", false_text="Error detected.")
        self.button3 = Button('Button 3')

        self.button1.clicked.connect(self.toggle_label1)
        self.button2.clicked.connect(self.toggle_label2)

        layout.addWidget(self.button1)
        layout.addWidget(self.informationLabel1)
        layout.addWidget(self.button2)
        layout.addWidget(self.informationLabel2)
        layout.addWidget(self.button3)

        # Checkbox for label
        checkbox = QCheckBox('Show Label')
        checkbox.stateChanged.connect(self.emit_checkbox_state)
        layout.addWidget(checkbox)

        # Radio buttons for switching between BigWindow types
        self.radio_group = QButtonGroup(self)

        stereo_radio = QRadioButton('Stereo')
        stereo_radio.setChecked(True)  # Set default selection
        self.radio_group.addButton(stereo_radio)
        layout.addWidget(stereo_radio)

        red_radio = QRadioButton('Red')
        self.radio_group.addButton(red_radio)
        layout.addWidget(red_radio)

        browser_radio = QRadioButton('Browser')
        self.radio_group.addButton(browser_radio)
        layout.addWidget(browser_radio)

        live_radio = QRadioButton('Live')
        self.radio_group.addButton(live_radio)
        layout.addWidget(live_radio)

        self.radio_group.buttonClicked.connect(self.emit_radio_button_state)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Use the custom MenuBar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

    def toggle_label1(self):
        new_value = not self.informationLabel1.value
        self.informationLabel1.set_value(new_value)

    def toggle_label2(self):
        new_value = not self.informationLabel2.value
        self.informationLabel2.set_value(new_value)

    def emit_checkbox_state(self, state):
        self.checkbox_state_changed.emit(state != Qt.Checked)

    def emit_radio_button_state(self, button):
        self.radio_button_changed.emit(button.text())  # Emit the text of the selected radio button

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmallWindow()
    window.show()
    sys.exit(app.exec_())
