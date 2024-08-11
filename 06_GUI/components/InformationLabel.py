from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class InformationLabel(QLabel):
    def __init__(self, value=True, parent=None, true_text="", false_text=""):
        super().__init__(parent)

        self.true_text = true_text
        self.false_text = false_text
        self.value = value

        # Set initial text and style based on the value parameter
        self.update_label()

    def set_texts(self, true_text=None, false_text=None):
        if true_text is not None:
            self.true_text = true_text
        if false_text is not None:
            self.false_text = false_text
        self.update_label()

    def set_value(self, value):
        if self.value != value:
            self.value = value
            self.update_label()

    def update_label(self):
        # Set the style based on the value
        if self.value:
            self.setStyleSheet("color: green;")
            self.setText(self.true_text)
        else:
            self.setStyleSheet("color: red;")
            self.setText(self.false_text)
