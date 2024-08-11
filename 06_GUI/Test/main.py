# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from stylesheet_window import StyleSheetWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Lade das Stylesheet
    stylesheet_path = os.path.join(os.path.dirname(__file__), "stylesheet.css")
    try:
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
    except FileNotFoundError:
        stylesheet = ""

    main_window = MainWindow()
    second_window = StyleSheetWindow(main_window=main_window)

    # Wende das Stylesheet auf beide Fenster an
    main_window.set_custom_stylesheet(stylesheet)
    second_window.setStyleSheet(stylesheet)

    # Zeige beide Fenster sofort an
    main_window.show()
    second_window.show()

    sys.exit(app.exec_())
