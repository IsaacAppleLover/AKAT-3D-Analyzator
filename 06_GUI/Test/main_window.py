import sys
from PyQt5.QtWidgets import *

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Erstes Fenster')
        self.setGeometry(500, 300, 300, 300)

        # Menüleiste hinzufügen
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu('File')

        # Aktionen zum File-Menü hinzufügen
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        # Edit-Menü erstellen und Aktionen hinzufügen
        edit_menu = QMenu("Edit", self)
        self.menu_bar.addMenu(edit_menu)

        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # About-Menü erstellen und Aktionen hinzufügen
        about_menu = QMenu("About", self)
        self.menu_bar.addMenu(about_menu)

        about_action = QAction("About", self)
        about_menu.addAction(about_action)

        # Layout für das Hauptfenster
        layout = QVBoxLayout()
        layout.setMenuBar(self.menu_bar)

        self.button = QPushButton('Button1', self)
        layout.addWidget(self.button)

        self.label = QLabel("This Text is green.", self)
        layout.addWidget(self.label)

        self.button = QPushButton('Button2', self)
        layout.addWidget(self.button)

        self.label = QLabel("This Text is green.", self)
        layout.addWidget(self.label)

        self.button = QPushButton('Button3', self)
        layout.addWidget(self.button)

        checkbox = QCheckBox('Show Label')
        layout.addWidget(checkbox)

        # GroupBox for Radio buttons
        radio_group_box = QGroupBox("Select an Option")
        radio_layout = QVBoxLayout()

        self.radio_group = QButtonGroup(self)

        stereo_radio = QRadioButton('Stereo')
        stereo_radio.setChecked(True)  # Set default selection
        self.radio_group.addButton(stereo_radio)
        radio_layout.addWidget(stereo_radio)

        red_radio = QRadioButton('Red')
        self.radio_group.addButton(red_radio)
        radio_layout.addWidget(red_radio)

        browser_radio = QRadioButton('Browser')
        self.radio_group.addButton(browser_radio)
        radio_layout.addWidget(browser_radio)

        live_radio = QRadioButton('Live')
        self.radio_group.addButton(live_radio)
        radio_layout.addWidget(live_radio)

        # Adding the new Radio Button
        new_radio = QRadioButton('New Option')
        self.radio_group.addButton(new_radio)
        radio_layout.addWidget(new_radio)

        self.radio_group.buttonClicked.connect(self.emit_radio_button_state)

        radio_group_box.setLayout(radio_layout)
        layout.addWidget(radio_group_box)

        self.setLayout(layout)

    def emit_radio_button_state(self):
        selected_button = self.radio_group.checkedButton()
        if selected_button:
            print(f'Selected: {selected_button.text()}')

    def set_custom_stylesheet(self, stylesheet):
        self.setStyleSheet(stylesheet)

    def closeEvent(self, event):
        # Wenn das Hauptfenster geschlossen wird, beende die Anwendung
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
