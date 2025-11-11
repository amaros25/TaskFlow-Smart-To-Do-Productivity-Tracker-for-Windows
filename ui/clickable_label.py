from PySide6.QtWidgets import QLabel # pylint: disable=no-name-in-module
from PySide6.QtCore import Signal # pylint: disable=no-name-in-module

class ClickableLabel(QLabel):
    """Clickable Label class to handle mouse press events"""
    clicked = Signal()

    def mousePressEvent(self, event):
        """Handles mouse press events"""
        self.clicked.emit()
        super().mousePressEvent(event)
