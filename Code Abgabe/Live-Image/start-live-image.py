import sys

try:
    from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QMainWindow
except ImportError:
    from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QMainWindow

from mainwindow import MainWindow


def main():
    a = QApplication(sys.argv)
    w = MainWindow() #window for first camera
    w2 = MainWindow() #window for second camera

    # Create a main widget to hold both windows
    main_widget = QWidget() # combine the two live streams into one window
    layout = QHBoxLayout(main_widget)
    layout.setSpacing(0)  # Set spacing to zero
    layout.addWidget(w)
    layout.addWidget(w2)

    # Create a main window to hold the main widget
    main_window = QMainWindow()
    main_window.setCentralWidget(main_widget)
    main_window.showFullScreen()

    try:
        return a.exec()
    except AttributeError:
        return a.exec_()


if __name__ == "__main__":
    sys.exit(main())
