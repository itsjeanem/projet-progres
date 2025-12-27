import sys
from PyQt6.QtWidgets import QApplication
from views.login_view import LoginView
from PyQt6.QtCore import QFile


def main():
    app = QApplication(sys.argv)

    # Charger le style
    with open("resources/styles/main.qss", "r") as f:
        app.setStyleSheet(f.read())

    login = LoginView()
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
