from PyQt6.QtWidgets import QSplashScreen, QApplication, QVBoxLayout, QLabel, QWidget
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtCore import Qt, QTimer, QSize
import os


class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        
        # Create a pixmap for the splash screen (gradient background)
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(41, 128, 185))  # Blue background
        
        self.setPixmap(pixmap)
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        
        # Add text to splash screen
        self.showMessage(
            "Chargement de l'application...",
            alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            color=QColor(255, 255, 255)
        )
        
        # Center the splash screen on the screen
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - pixmap.width()) // 2
        y = (screen_geometry.height() - pixmap.height()) // 2
        self.move(x, y)
    
    def update_message(self, message):
        """Update the splash screen message"""
        self.showMessage(
            message,
            alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            color=QColor(255, 255, 255)
        )
        QApplication.processEvents()
