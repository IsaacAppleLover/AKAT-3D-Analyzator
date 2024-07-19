from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtCore import Qt

class Button(QPushButton):
    def __init__(self, text, shadowOn=False):
        super().__init__(text)
        self.setObjectName("Button")
        self.shadowOn = shadowOn
        self.shadow = None

    def enterEvent(self, event):
        self.setCursor(QCursor(Qt.PointingHandCursor))
        if self.shadowOn:
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(10)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(5)
            self.shadow.setColor(QColor(0, 0, 0, 60))
            self.setGraphicsEffect(self.shadow)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.unsetCursor()
        self.setGraphicsEffect(None)
        self.shadow = None
        super().leaveEvent(event)

    def setShadowOn(self, enable):
        self.shadowOn = enable
        if not enable:
            self.setGraphicsEffect(None)
            self.shadow = None
