from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt
from utils.session import Session
from views.clients_view import ClientsView
from views.products_view import ProductsView
from views.sales_view import SalesView
from views.dashboard_view import DashboardView


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()

        if not Session.is_authenticated():
            raise Exception("Accès refusé : utilisateur non authentifié")

        self.user = user
        self.setWindowTitle("Gestion Commerciale")
        self.setMinimumSize(1000, 700)

        self.build_ui()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        
        # En-tête
        header = QHBoxLayout()
        self.label_user = QLabel(
            f"Connecté : {self.user['username']} ({self.user['role']})"
        )
        self.btn_logout = QPushButton("Déconnexion")
        self.btn_logout.clicked.connect(self.logout)

        header.addWidget(self.label_user)
        header.addStretch()
        header.addWidget(self.btn_logout)
        main_layout.addLayout(header)

        # Navigation + contenu
        content_layout = QHBoxLayout()
        
        # Sidebar avec navigation
        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("Menu"))
        
        self.btn_dashboard = QPushButton("📊 Dashboard")
        self.btn_dashboard.setMinimumWidth(120)
        self.btn_dashboard.clicked.connect(self.show_dashboard)
        
        self.btn_clients = QPushButton("👥 Clients")
        self.btn_clients.setMinimumWidth(120)
        self.btn_clients.clicked.connect(self.show_clients)
        
        self.btn_products = QPushButton("📦 Produits")
        self.btn_products.setMinimumWidth(120)
        self.btn_products.clicked.connect(self.show_products)
        
        self.btn_sales = QPushButton("💰 Ventes")
        self.btn_sales.setMinimumWidth(120)
        self.btn_sales.clicked.connect(self.show_sales)
        
        sidebar.addWidget(self.btn_dashboard)
        sidebar.addWidget(self.btn_clients)
        sidebar.addWidget(self.btn_products)
        sidebar.addWidget(self.btn_sales)
        sidebar.addStretch()
        
        # Stack Widget pour les différentes vues
        self.stacked_widget = QStackedWidget()
        
        # Vue d'accueil - Dashboard
        self.home_view = DashboardView()
        self.stacked_widget.addWidget(self.home_view)
        
        # Vue Clients
        self.clients_view = ClientsView()
        self.stacked_widget.addWidget(self.clients_view)
        
        # Vue Produits
        self.products_view = ProductsView()
        self.stacked_widget.addWidget(self.products_view)
        
        # Vue Ventes
        self.sales_view = SalesView()
        self.stacked_widget.addWidget(self.sales_view)
        
        # Ajouter au layout
        content_layout.addLayout(sidebar)
        content_layout.addWidget(self.stacked_widget, 1)
        
        main_layout.addLayout(content_layout)
        
        central.setLayout(main_layout)

    def show_dashboard(self):
        """Afficher le dashboard"""
        self.stacked_widget.setCurrentWidget(self.home_view)

    def show_clients(self):
        """Afficher la vue clients"""
        self.stacked_widget.setCurrentWidget(self.clients_view)
        self.clients_view.load_clients()

    def show_products(self):
        """Afficher la vue produits"""
        self.stacked_widget.setCurrentWidget(self.products_view)
        self.products_view.load_products()

    def show_sales(self):
        """Afficher la vue ventes"""
        self.stacked_widget.setCurrentWidget(self.sales_view)
        self.sales_view.load_sales()

    def logout(self):
        Session.logout()
        from views.login_view import LoginView
        self.login_window = LoginView()
        self.login_window.show()
        self.close()
