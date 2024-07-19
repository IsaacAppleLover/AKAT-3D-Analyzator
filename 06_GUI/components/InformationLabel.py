from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPalette, QColor


class InformationLabel(QLabel):
    def __init__(self, value=True, parent=None, true_text="", false_text=""):
        super().__init__(parent)

        self.true_text = true_text
        self.false_text = false_text
        self.value = value

        # Set initial text and color based on the value parameter
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
        color = QColor('green') if self.value else QColor('red')
        text = self.true_text if self.value else self.false_text

        palette = self.palette()
        palette.setColor(QPalette.WindowText, color)
        self.setPalette(palette)

        self.setText(text)