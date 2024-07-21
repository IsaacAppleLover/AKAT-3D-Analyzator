import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy
from components import Button, CustomWindow, BigWindow, SmallWindow
from components.BigWindow_Stereo import BigWindow_Stereo
from components.BigWindow_Browser import BigWindow_Browser

COLOR_BLACK = "\033[30m"
COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"
COLOR_MAGENTA = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_WHITE = "\033[37m"
COLOR_RESET = "\033[0m"

def color_text(text, color):
    return f"{color}{text}{COLOR_RESET}"

class StartWindow(CustomWindow):
    def initUI(self):
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
        print(color_text("Look for Screens...", COLOR_BLUE))
        if len(screens) > 1:
            # Show the big window on the second screen
            print(color_text("\tMultiple screens detected", COLOR_GREEN))
            second_screen = screens[1]
            mainWidget = BigWindow_Browser()
            self.big_window = BigWindow(mainWidget)
            self.big_window.setGeometry(second_screen.geometry())
            self.big_window.showMaximized()
        else:
            # Show the big window on the main screen
            print(color_text("\tSingle screen detected", COLOR_YELLOW))
            mainWidget = BigWindow_Browser()
            self.big_window = BigWindow(mainWidget)
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

    print(color_text("Look for CSS-File...", COLOR_BLUE))
    # Apply the stylesheet from a CSS file
    try:
        with open("styles.css", "r") as file:
            app.setStyleSheet(file.read())
            print(color_text("\tCSS file 'styles.css' loaded successfully.", COLOR_GREEN))
    except FileNotFoundError:
        print(color_text("\tCSS file 'styles.css' not found.", COLOR_RED))

    # List all available fonts
    font_db = QFontDatabase()
    available_fonts = font_db.families()

    print(color_text("Look for Font...", COLOR_BLUE))
    # Check if Montserrat is available, otherwise use Arial
    if "Montserrat" in available_fonts:
        print(color_text("\tMontserrat font is available.", COLOR_GREEN))
        font = QFont("Montserrat", 8)
    else:
        print(color_text("\t Montserrat font is not available. Using Arial instead.", COLOR_YELLOW))
        font = QFont("Arial", 8)

    app.setFont(font)

    start_window = StartWindow()
    start_window.show()

    sys.exit(app.exec_())
