import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from views.login_view import LoginView
from views.splash_screen import SplashScreen
from PyQt6.QtCore import QFile


def main():
    app = QApplication(sys.argv)

    # Show splash screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # Charger le style
    splash.update_message("Chargement des styles...")
    with open("resources/styles/main.qss", "r") as f:
        app.setStyleSheet(f.read())
    app.processEvents()

    # Créer la fenêtre de connexion
    splash.update_message("Initialisation de l'application...")
    login = LoginView()
    app.processEvents()

    # Fermer le splash screen et afficher la connexion
    splash.finish(login)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
