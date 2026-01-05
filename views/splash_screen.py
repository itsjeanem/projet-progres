from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtGui import QPixmap, QColor, QPainter, QLinearGradient, QFont
from PyQt6.QtCore import Qt, QTimer, QSize
import os


class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        
        # Create a pixmap for the splash screen (soft gradient background)
        width, height = 640, 420
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0.0, QColor(0, 120, 215))   # #0078d7
        gradient.setColorAt(1.0, QColor(0, 95, 163))    # #005fa3
        painter.fillRect(0, 0, width, height, gradient)

        # Foreground "card" area for text
        card_margin = 36
        painter.setPen(QColor(255, 255, 255, 40))
        painter.setBrush(QColor(255, 255, 255, 24))
        painter.drawRoundedRect(card_margin, card_margin, width - card_margin * 2, height - card_margin * 2, 18, 18)

        # App title
        title_font = QFont("Segoe UI", 26)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(0, 120, width, 40, Qt.AlignmentFlag.AlignHCenter, "GestCo")

        subtitle_font = QFont("Segoe UI", 11)
        subtitle_font.setBold(False)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(255, 255, 255, 220))
        painter.drawText(0, 160, width, 24, Qt.AlignmentFlag.AlignHCenter, "Gestion commerciale")

        painter.end()
        
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
