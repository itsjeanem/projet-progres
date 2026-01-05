from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from controllers.user_controller import UserController
from views.main_window import MainWindow
from utils.session import Session


class LoginView(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Connexion")
        self.setMinimumSize(1000, 700)
        
        # Load the UI into the MainWindow
        uic.loadUi("views/ui/login.ui", self)
        
        # Get references to UI elements
        self.btn_login.clicked.connect(self.handle_login)
        
    #     # Center the window on screen
    #     self._center_window()
    
    # def _center_window(self):
    #     """Center the window on the screen"""
    #     screen = self.screen()
    #     geometry = screen.geometry()
    #     x = (geometry.width() - self.width()) // 2
    #     y = (geometry.height() - self.height()) // 2
    #     self.move(x, y)

    def handle_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        user, error = UserController.login(username, password)

        if error:
            self.label_error.setText(error)
            return
            
        # Sauvegarde session
        Session.login(user)

        # Succès → ouvrir la fenêtre principale
        self.open_main_window(user)

    def open_main_window(self, user):
        self.main_window = MainWindow(user)
        self.main_window.showMaximized()
        self.close()
