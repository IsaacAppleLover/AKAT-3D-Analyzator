import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy
from components import Button, CustomWindow, BigWindow, SmallWindow

class StartWindow(CustomWindow):
    def initUI(self):
        self.setWindowTitle('Startfenster')
        self.setGeometry(100, 100, 250, 100)
        self.center()

        layout = QVBoxLayout()

        # Create and add a custom widget with QLabel
        label_container = QWidget(self)
        label_layout = QHBoxLayout(label_container)
        label_layout.setContentsMargins(0, 0, 0, 0)

        spacer_left = QWidget(self)
        spacer_left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        label_layout.addWidget(spacer_left)

        self.label = QLabel("", self)
        self.label.setProperty("customClass", "LOGO")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label_layout.addWidget(self.label)

        spacer_right = QWidget(self)
        spacer_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        label_layout.addWidget(spacer_right)

        label_container.setLayout(label_layout)
        layout.addWidget(label_container)

        start_button = Button('START', shadowOn=True)
        start_button.setProperty("customClass", "StartButton")
        start_button.clicked.connect(self.startButtonClicked)
        layout.addWidget(start_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.big_window = None
        self.small_window = None

    def resizeEvent(self, event):
        # Ensure the label remains square
        side = int(self.width() * 0.3)  # 80% of the width
        self.label.setFixedSize(side, side)
        super().resizeEvent(event)

    def startButtonClicked(self):
        print("Start button clicked")
        self.hide()

        screens = QApplication.screens()
        if len(screens) > 1:
            # Show the big window on the second screen
            print("Multiple screens detected")
            second_screen = screens[1]
            self.big_window = BigWindow()
            self.big_window.setGeometry(second_screen.geometry())
            self.big_window.showMaximized()
        else:
            # Show the big window on the main screen
            print("Single screen detected")
            self.big_window = BigWindow()
            self.big_window.showMaximized()

        print("Showing SmallWindow")
        self.small_window = SmallWindow()
        self.small_window.checkbox_state_changed.connect(self.handle_checkbox_state_changed)
        self.small_window.show()

    def handle_checkbox_state_changed(self, not_checked):
        if not_checked:
            self.big_window.set_rgb_label_css('background-color: transparent; border: transparent; color: transparent;')
        else:
            self.big_window.set_rgb_label_css('')

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply the stylesheet from a CSS file
    with open("styles.css", "r") as file:
        app.setStyleSheet(file.read())

    # List all available fonts
    font_db = QFontDatabase()
    available_fonts = font_db.families()

    # Check if Montserrat is available, otherwise use Arial
    if "Montserrat" in available_fonts:
        print("Montserrat font is available.")
        font = QFont("Montserrat", 8)
    else:
        print("Montserrat font is not available. Using Arial instead.")
        font = QFont("Arial", 8)

    app.setFont(font)

    start_window = StartWindow()
    start_window.show()

    sys.exit(app.exec_())
