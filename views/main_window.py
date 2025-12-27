from PyQt6.QtWidgets import QMainWindow, QLabel


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()

        self.user = user
        self.setWindowTitle("Gestion Commerciale")

        label = QLabel(
            f"Bienvenue {user['username']} (rôle: {user['role']})",
            self
        )
        label.move(30, 30)
        label.resize(400, 40)

        self.setMinimumSize(600, 400)
