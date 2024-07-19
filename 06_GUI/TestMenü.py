from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QMessageBox, QMainWindow, QApplication
from PyQt5.QtCore import Qt
import sys
import os


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.apply_stylesheet()
        self.installEventFilter(self)

    def initUI(self):
        # Create File menu
        file_menu = QMenu("File", self)
        self.addMenu(file_menu)

        # Add actions to File menu
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.parent().close)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        # Create Edit menu
        edit_menu = QMenu("Edit", self)
        self.addMenu(edit_menu)

        # Add actions to Edit menu
        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # Create About menu
        about_menu = QMenu("About", self)
        self.addMenu(about_menu)

        # Add actions to About menu
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        about_menu.addAction(about_action)

    def show_about_dialog(self):
        # Implement a simple about dialog
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("About")
        about_dialog.setText("This is a PyQt5 application.")
        about_dialog.exec_()

    def apply_stylesheet(self):
        css_file = os.path.join(os.path.dirname(__file__), "MenuBar.css")
        if os.path.exists(css_file):
            with open(css_file, "r") as file:
                self.setStyleSheet(file.read())

    def eventFilter(self, obj, event):
        if isinstance(obj, (QMenu, QMenuBar)):
            if event.type() == event.Enter:
                QApplication.setOverrideCursor(Qt.PointingHandCursor)
            elif event.type() == event.Leave:
                QApplication.restoreOverrideCursor()
        return super(MenuBar, self).eventFilter(obj, event)

    def addMenu(self, menu):
        menu.installEventFilter(self)
        for action in menu.actions():
            if action.menu():
                action.menu().installEventFilter(self)
        return super(MenuBar, self).addMenu(menu)
