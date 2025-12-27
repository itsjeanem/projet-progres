from PyQt6.QtWidgets import QMainWindow,QLabel,QPushButton,QWidget,QVBoxLayout,QHBoxLayout
from utils.session import Session


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()

        if not Session.is_authenticated():
            raise Exception("Accès refusé : utilisateur non authentifié")

        self.user = user
        self.setWindowTitle("Gestion Commerciale")
        self.setMinimumSize(800, 500)

        self.build_ui()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        header = QHBoxLayout()

        # Infos utilisateur
        self.label_user = QLabel(
            f"Connecté : {self.user['username']} ({self.user['role']})"
        )

        # Bouton logout
        self.btn_logout = QPushButton("Déconnexion")
        self.btn_logout.clicked.connect(self.logout)

        header.addWidget(self.label_user)
        header.addStretch()
        header.addWidget(self.btn_logout)

        main_layout.addLayout(header)

        # Zone principale (future navigation)
        self.content = QLabel("Bienvenue dans l'application")
        main_layout.addWidget(self.content)

        central.setLayout(main_layout)

    def logout(self):
        Session.logout()
        from views.login_view import LoginView
        self.login_window = LoginView()
        self.login_window.show()
        self.close()
