from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from components import Button, CustomWindow, BigWindow, SmallWindow
from components.BigWindow_Stereo import BigWindow_Stereo
from components.BigWindow_Browser import BigWindow_Browser
from components.BigWindow_Red import BigWindow_Red
from components.BigWindow_Live import BigWindow_Live
import sys
import os
import colors

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
        side = int(self.width() * 0.3)  # 30% of the width
        self.label.setFixedSize(side, side)
        super().resizeEvent(event)

    def startButtonClicked(self):
        print("Start button clicked")
        self.hide()

        screens = QApplication.screens()
        print(colors.color_text("Look for Screens...", colors.COLOR_BLUE))
        if len(screens) > 1:
            # Show the big window on the second screen
            print(colors.color_text("\tMultiple screens detected", colors.COLOR_GREEN))
            second_screen = screens[1]
            mainWidget = BigWindow_Stereo()  # Default to BigWindow_Stereo
            self.big_window = BigWindow(mainWidget)
            self.big_window.setGeometry(second_screen.geometry())
            self.big_window.showMaximized()
        else:
            # Show the big window on the main screen
            print(colors.color_text("\tSingle screen detected", colors.COLOR_YELLOW))
            mainWidget = BigWindow_Stereo()  # Default to BigWindow_Stereo
            self.big_window = BigWindow(mainWidget)
            self.big_window.showMaximized()

        print("Showing SmallWindow")
        self.small_window = SmallWindow()
        self.small_window.checkbox_state_changed.connect(self.handle_checkbox_state_changed)
        self.small_window.radio_button_changed.connect(self.handle_radio_button_changed)

        # Verbindung zwischen SmallWindow und BigWindow_Stereo herstellen
        self.small_window.open_image_signal.connect(self.big_window.centralWidget().open_image_dialog)
        
        # Verbinde den Capture-Button mit der Capture-Funktion von BigWindow_Stereo
        self.small_window.capture_button.clicked.connect(self.big_window.centralWidget().capture)

        # Verbinde den Save-Button mit der Save-Funktion von BigWindow_Stereo
        self.small_window.save_button.clicked.connect(self.big_window.centralWidget().save_images)

        self.small_window.show()

    def handle_checkbox_state_changed(self, not_checked):
        if not_checked:
            self.big_window.centralWidget().set_rgb_label_css('background-color: transparent; border: transparent; color: transparent;')
        else:
            self.big_window.centralWidget().set_rgb_label_css('')

    def handle_radio_button_changed(self, text):
        if text == 'Stereo':
            mainWidget = BigWindow_Stereo()
        elif text == 'Red':
            mainWidget = BigWindow_Red()
        elif text == 'Browser':
            mainWidget = BigWindow_Browser()
        elif text == 'Live':
            mainWidget = BigWindow_Live()

        self.big_window.initUI(mainWidget)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    print(colors.color_text("Look for CSS-File...", colors.COLOR_BLUE))
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    print(colors.color_text(f"CSS file path: {css_path}", colors.COLOR_WHITE))
    if os.path.exists(css_path):
        with open(css_path, "r") as file:
            app.setStyleSheet(file.read())
    else: 
        print(colors.color_text(f"\tCSS file '{css_path}' not found.", colors.COLOR_RED))

    # List all available fonts
    font_db = QFontDatabase()
    available_fonts = font_db.families()

    print(colors.color_text("Look for Font...", colors.COLOR_BLUE))
    # Check if Montserrat is available, otherwise use Arial
    if "Montserrat" in available_fonts:
        print(colors.color_text("\tMontserrat font is available.", colors.COLOR_GREEN))
        font = QFont("Montserrat", 8)
    else:
        print(colors.color_text("\t Montserrat font is not available. Using Arial instead.", colors.COLOR_YELLOW))
        font = QFont("Arial", 8)

    app.setFont(font)

    start_window = StartWindow()
    start_window.show()

    sys.exit(app.exec_())
