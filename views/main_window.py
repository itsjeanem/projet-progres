from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt
from utils.session import Session
from utils.permissions import check_permission, check_role, Permission
from views.clients_view import ClientsView
from views.products_view import ProductsView
from views.sales_view import SalesView
from views.dashboard_view import DashboardView
from views.settings_view import SettingsView


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
        central.setObjectName("appCentral")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # En-tête avec infos utilisateur et permissions
        header_widget = QWidget()
        header_widget.setObjectName("headerBar")
        header = QHBoxLayout(header_widget)
        header.setContentsMargins(14, 12, 14, 12)
        header.setSpacing(10)

        role_display = self._get_role_display()
        self.label_user = QLabel(
            f"Connecté : {self.user['username']} | Rôle: {role_display}"
        )
        self.btn_logout = QPushButton("Déconnexion")
        self.btn_logout.setObjectName("btn_logout")
        self.btn_logout.clicked.connect(self.logout)

        header.addWidget(self.label_user)
        header.addStretch()
        header.addWidget(self.btn_logout)
        main_layout.addWidget(header_widget)

        # Navigation + contenu
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        
        # Sidebar avec navigation basée sur les rôles
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setContentsMargins(12, 12, 12, 12)
        sidebar.setSpacing(8)

        menu_label = QLabel("Menu")
        menu_label.setObjectName("sidebarTitle")
        sidebar.addWidget(menu_label)
        
        # Dashboard - visible pour tous
        if check_permission(Permission.VIEW_DASHBOARD):
            self.btn_dashboard = QPushButton("📊 Dashboard")
            self.btn_dashboard.setMinimumWidth(120)
            self.btn_dashboard.clicked.connect(self.show_dashboard)
            sidebar.addWidget(self.btn_dashboard)
        
        # Clients - vendeurs et managers
        if check_permission(Permission.VIEW_CLIENTS):
            self.btn_clients = QPushButton("👥 Clients")
            self.btn_clients.setMinimumWidth(120)
            self.btn_clients.clicked.connect(self.show_clients)
            sidebar.addWidget(self.btn_clients)
        
        # Produits - vendeurs et managers
        if check_permission(Permission.VIEW_PRODUCTS):
            self.btn_products = QPushButton("📦 Produits")
            self.btn_products.setMinimumWidth(120)
            self.btn_products.clicked.connect(self.show_products)
            sidebar.addWidget(self.btn_products)
        
        # Ventes - tous
        if check_permission(Permission.VIEW_SALES):
            self.btn_sales = QPushButton("💰 Ventes")
            self.btn_sales.setMinimumWidth(120)
            self.btn_sales.clicked.connect(self.show_sales)
            sidebar.addWidget(self.btn_sales)
        
        # Paramètres - admins
        if check_permission(Permission.VIEW_SETTINGS):
            self.btn_settings = QPushButton("⚙️ Paramètres")
            self.btn_settings.setMinimumWidth(120)
            self.btn_settings.clicked.connect(self.show_settings)
            sidebar.addWidget(self.btn_settings)
        
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
        
        # Vue Paramètres
        self.settings_view = SettingsView()
        self.stacked_widget.addWidget(self.settings_view)
        
        # Ajouter au layout
        sidebar_widget.setMinimumWidth(220)
        content_layout.addWidget(sidebar_widget)
        content_layout.addWidget(self.stacked_widget, 1)
        
        main_layout.addLayout(content_layout)
        
        central.setLayout(main_layout)

    def _get_role_display(self):
        """Get human readable role name"""
        role = self.user.get('role', 'vendeur')
        role_names = {
            'admin': 'Administrateur',
            'manager': 'Manager',
            'vendeur': 'Vendeur'
        }
        return role_names.get(role, role)

    def show_dashboard(self):
        """Afficher le dashboard"""
        if check_permission(Permission.VIEW_DASHBOARD):
            self.stacked_widget.setCurrentWidget(self.home_view)

    def show_clients(self):
        """Afficher la vue clients"""
        if check_permission(Permission.VIEW_CLIENTS):
            self.stacked_widget.setCurrentWidget(self.clients_view)
            self.clients_view.load_clients()

    def show_products(self):
        """Afficher la vue produits"""
        if check_permission(Permission.VIEW_PRODUCTS):
            self.stacked_widget.setCurrentWidget(self.products_view)
            self.products_view.load_products()

    def show_sales(self):
        """Afficher la vue ventes"""
        if check_permission(Permission.VIEW_SALES):
            self.stacked_widget.setCurrentWidget(self.sales_view)
            self.sales_view.load_sales()

    def show_settings(self):
        """Afficher la vue paramètres"""
        if check_permission(Permission.VIEW_SETTINGS):
            self.stacked_widget.setCurrentWidget(self.settings_view)

    def logout(self):
        Session.logout()
        from views.login_view import LoginView
        self.login_window = LoginView()
        self.login_window.show()
        self.close()

