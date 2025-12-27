from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from controllers.user_controller import UserController
from views.main_window import MainWindow


class LoginView(QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi("views/ui/login.ui", self)

        self.btn_login.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        user, error = UserController.login(username, password)

        if error:
            self.label_error.setText(error)
            return

        # Succès → ouvrir la fenêtre principale
        self.open_main_window(user)

    def open_main_window(self, user):
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()
