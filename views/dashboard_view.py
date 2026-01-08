from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QTableWidget, 
    QTableWidgetItem, QGroupBox, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QIcon
from controllers.statistics_controller import StatisticsController
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class DashboardView(QWidget):
    """Vue du tableau de bord avec statistiques et rapports"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        
        # Titre
        title = QLabel("📊 Tableau de Bord")
        title.setObjectName("pageTitle")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Scroll area pour le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(12)
        
        # Section Top Products & Clients
        scroll_layout.addWidget(self.create_top_section())
        
        # Section Charts
        scroll_layout.addWidget(self.create_charts_section())
        
        # Section Low Stock
        # scroll_layout.addWidget(self.create_low_stock_section())
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
        # Charger les données
        self.load_data()

    def create_kpi_section(self):
        """Créer la section des KPIs (Key Performance Indicators)"""
        group = QGroupBox("📈 Performances")
        layout = QGridLayout()
        
        # Récupérer les données
        summary = StatisticsController.get_dashboard_summary()
        
        # Cards de KPIs
        kpis = [
            ("📅 Aujourd'hui", f"{summary['ca_today']:.2f} XOF", "#4CAF50"),
            ("📊 Cette semaine", f"{summary['ca_week']:.2f} XOF", "#2196F3"),
            ("📆 Ce mois", f"{summary['ca_month']:.2f} XOF", "#FF9800"),
            ("💰 Ventes aujourd'hui", f"{summary['sales_today']}", "#9C27B0"),
        ]
        
        col = 0
        for title, value, color in kpis:
            card = self.create_card(title, value, color)
            layout.addWidget(card, 0, col)
            col += 1
        
        group.setLayout(layout)
        return group

    def create_card(self, title, value, color):
        """Créer une carte KPI"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.setSpacing(5)
        
        card.setLayout(layout)
        card.setMinimumHeight(100)
        return card

    def create_top_section(self):
        """Créer la section des tops produits et clients"""
        group = QGroupBox("🏆 Top Ventes")
        layout = QHBoxLayout()
        
        # Récupérer les données
        summary = StatisticsController.get_dashboard_summary()
        
        # Top Produits
        top_products_group = QGroupBox("🔥 Top 5 Produits")
        top_products_layout = QVBoxLayout()
        
        products_table = QTableWidget()
        products_table.setColumnCount(3)
        products_table.setHorizontalHeaderLabels(["Produit", "Quantité", "CA"])
        products_table.setMaximumHeight(200)
        
        products = summary.get('top_products', [])
        products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            products_table.setItem(row, 0, QTableWidgetItem(product.get('nom', '')))
            products_table.setItem(row, 1, QTableWidgetItem(str(product.get('quantite_vendue', ''))))
            ca = float(product.get('ca', 0))
            products_table.setItem(row, 2, QTableWidgetItem(f"{ca:.2f} XOF"))
        
        products_table.resizeColumnsToContents()
        top_products_layout.addWidget(products_table)
        top_products_group.setLayout(top_products_layout)
        
        # Top Clients
        top_clients_group = QGroupBox("⭐ Top 5 Clients")
        top_clients_layout = QVBoxLayout()
        
        clients_table = QTableWidget()
        clients_table.setColumnCount(3)
        clients_table.setHorizontalHeaderLabels(["Client", "Achats", "CA"])
        clients_table.setMaximumHeight(200)
        
        clients = summary.get('top_clients', [])
        clients_table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            clients_table.setItem(row, 0, QTableWidgetItem(client.get('client_nom', '')))
            clients_table.setItem(row, 1, QTableWidgetItem(str(client.get('nombre_achats', ''))))
            ca = float(client.get('ca_total', 0))
            clients_table.setItem(row, 2, QTableWidgetItem(f"{ca:.2f} XOF"))
        
        clients_table.resizeColumnsToContents()
        top_clients_layout.addWidget(clients_table)
        top_clients_group.setLayout(top_clients_layout)
        
        layout.addWidget(top_products_group)
        layout.addWidget(top_clients_group)
        
        group.setLayout(layout)
        return group

    def create_charts_section(self):
        """Créer la section des graphiques"""
        group = QGroupBox("📈 Graphiques")
        layout = QHBoxLayout()
        
        # Récupérer les données
        summary = StatisticsController.get_dashboard_summary()
        
        # Graphique 1 : Évolution CA
        ca_evolution = summary.get('ca_evolution', [])
        if ca_evolution:
            dates = [str(item['date']) for item in ca_evolution]
            values = [float(item['ca']) for item in ca_evolution]
            
            fig1 = Figure(figsize=(5, 3), dpi=100)
            ax1 = fig1.add_subplot(111)
            ax1.plot(dates, values, marker='o', linestyle='-', color='#2196F3', linewidth=2)
            ax1.set_title('Évolution du CA (30 derniers jours)', fontweight='bold')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('CA (XOF)')
            ax1.grid(True, alpha=0.3)
            fig1.tight_layout()
            
            canvas1 = FigureCanvas(fig1)
            layout.addWidget(canvas1)
        
        # Graphique 2 : Répartition par catégorie
        ca_by_cat = summary.get('ca_by_category', [])
        if ca_by_cat:
            categories = [item['categorie'] or 'Non classé' for item in ca_by_cat]
            values = [float(item['ca']) for item in ca_by_cat]
            colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
            
            fig2 = Figure(figsize=(5, 3), dpi=100)
            ax2 = fig2.add_subplot(111)
            ax2.pie(values, labels=categories, autopct='%1.1f%%', colors=colors[:len(categories)])
            ax2.set_title('Répartition par Catégorie', fontweight='bold')
            fig2.tight_layout()
            
            canvas2 = FigureCanvas(fig2)
            layout.addWidget(canvas2)
        
        group.setLayout(layout)
        return group

    # def create_low_stock_section(self):
    #     """Créer la section des stocks critiques"""
    #     group = QGroupBox("⚠️ Stocks Critiques")
    #     layout = QVBoxLayout()
        
    #     # Récupérer les données
    #     summary = StatisticsController.get_dashboard_summary()
    #     low_stock = summary.get('low_stock', [])
        
    #     if not low_stock:
    #         no_data = QLabel("✓ Aucun produit en rupture de stock")
    #         no_data.setStyleSheet("color: #4CAF50; font-weight: bold;")
    #         layout.addWidget(no_data)
    #     else:
    #         table = QTableWidget()
    #         table.setColumnCount(5)
    #         table.setHorizontalHeaderLabels(["Produit", "Catégorie", "Stock Actuel", "Stock Min", "Déficit"])
    #         table.setMaximumHeight(250)
            
    #         table.setRowCount(len(low_stock))
            
    #         for row, product in enumerate(low_stock):
    #             # Produit
    #             table.setItem(row, 0, QTableWidgetItem(product.get('nom', '')))
    #             # Catégorie
    #             table.setItem(row, 1, QTableWidgetItem(product.get('categorie', 'N/A')))
    #             # Stock actuel
    #             stock_item = QTableWidgetItem(str(product.get('stock_actuel', '')))
    #             stock_item.setBackground(QColor('#FFE5E5'))
    #             table.setItem(row, 2, stock_item)
    #             # Stock min
    #             table.setItem(row, 3, QTableWidgetItem(str(product.get('stock_min', ''))))
    #             # Déficit
    #             deficit_item = QTableWidgetItem(str(product.get('deficit', '')))
    #             deficit_item.setBackground(QColor('#FF6B6B'))
    #             deficit_item.setForeground(QColor('white'))
    #             table.setItem(row, 4, deficit_item)
            
    #         table.resizeColumnsToContents()
    #         layout.addWidget(table)
        
    #     group.setLayout(layout)
    #     return group

    def load_data(self):
        """Charger les données du dashboard"""
        # Les données sont chargées automatiquement lors de la création des widgets
        pass
