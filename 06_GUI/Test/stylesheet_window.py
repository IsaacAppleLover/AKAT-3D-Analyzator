import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class StyleSheetWindow(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)

        self.parent = parent
        self.main_window = main_window  # Zugriff auf das Hauptfenster
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Zweites Fenster')
        self.setGeometry(900, 100, 500, 800)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)

        # Lade das Stylesheet aus der Datei und setze es in das QTextEdit
        stylesheet_path = os.path.join(os.path.dirname(__file__), "stylesheet.css")
        try:
            with open(stylesheet_path, "r") as file:
                stylesheet = file.read()
                self.text_edit.setText(stylesheet)
        except FileNotFoundError:
            self.text_edit.setText("Stylesheet-Datei nicht gefunden.")

        self.apply_button = QPushButton('Stylesheet anwenden', self)
        self.apply_button.clicked.connect(self.apply_stylesheet)

        layout.addWidget(self.text_edit)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def apply_stylesheet(self):
        stylesheet = self.text_edit.toPlainText()

        # Stylesheet auf das Hauptfenster anwenden
        if self.main_window:
            self.main_window.set_custom_stylesheet(stylesheet)

        # Stylesheet auf das zweite Fenster anwenden
        self.setStyleSheet(stylesheet)

        # Speichere das Stylesheet in der Datei
        stylesheet_path = os.path.join(os.path.dirname(__file__), "stylesheet.css")
        with open(stylesheet_path, "w") as file:
            file.write(stylesheet)

    def keyPressEvent(self, event):
        # Prüfe, ob Strg + S gedrückt wurde
        if event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            self.apply_button.click()  # Button auslösen

    def closeEvent(self, event):
        # Wenn das zweite Fenster geschlossen wird, beende die Anwendung
        QApplication.quit()

