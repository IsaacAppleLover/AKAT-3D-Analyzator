from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QMessageBox, QMainWindow, QApplication
from PyQt5.QtCore import Qt, QEvent
import sys
import os

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Save reference to parent window
        self.initUI()
        self.installEventFilter(self)

    def initUI(self):
        # Create File menu
        file_menu = QMenu("File", self)
        self.addMenu(file_menu)

        # Add actions to File menu
        open_action = QAction("Open Image ...", self)
        open_action.triggered.connect(self.trigger_open_image)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)  # Ensure application quits
        file_menu.addAction(open_action)
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

        # Install event filters for all menus and actions
        self._install_event_filters()

    def trigger_open_image(self):
        # Trigger the signal to open the image dialog
        if self.parent_window:
            self.parent_window.open_image_signal.emit()

    def _install_event_filters(self):
        # Apply event filter to top-level menus
        for menu in self.findChildren(QMenu):
            menu.installEventFilter(self)
            self._install_event_filter_to_actions(menu)

    def _install_event_filter_to_actions(self, menu):
        # Recursively apply event filters to actions and their submenus
        for action in menu.actions():
            if action.menu():
                action.menu().installEventFilter(self)
                self._install_event_filter_to_actions(action.menu())

    def show_about_dialog(self):
        # Implement a simple about dialog
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("About")
        about_dialog.setText("This is a PyQt5 application.")
        about_dialog.exec_()

    def eventFilter(self, obj, event):
        if isinstance(obj, (QMenu, QMenuBar)):
            if event.type() == QEvent.Enter:
                QApplication.setOverrideCursor(Qt.PointingHandCursor)
            elif event.type() == QEvent.Leave:
                QApplication.restoreOverrideCursor()
        return super(MenuBar, self).eventFilter(obj, event)

    def addMenu(self, menu):
        # Ensure the event filter is applied when adding new menus dynamically
        menu.installEventFilter(self)
        self._install_event_filter_to_actions(menu)
        return super(MenuBar, self).addMenu(menu)
