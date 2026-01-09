from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QDialog, QVBoxLayout, QHBoxLayout, QSpinBox,
    QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from controllers.product_controller import ProductController
from utils.path import resource_path
from utils.validators import ProductValidator
from utils.session import Session
from datetime import datetime


class ProductsView(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi(resource_path("views/ui/products.ui"), self)
        
        self.products_data = []
        self.categories = []
        
        # Connexions
        self.btnAdd.clicked.connect(self.open_add_dialog)
        self.btnLowStock.clicked.connect(self.show_low_stock)
        self.searchInput.textChanged.connect(self.search_products)
        self.categoryFilter.currentIndexChanged.connect(self.filter_by_category)
        self.productsTable.doubleClicked.connect(self.edit_product)
        
        # Menu contextuel
        self.productsTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.productsTable.customContextMenuRequested.connect(self.show_context_menu)
        
        # Charger les données
        self.load_categories()
        self.load_products()

    def load_categories(self):
        """Charger les catégories"""
        self.categories = ProductController.get_all_categories()
        self.categoryFilter.clear()
        self.categoryFilter.addItem("Toutes les catégories", -1)
        for cat in self.categories:
            self.categoryFilter.addItem(cat.get('nom', ''), cat.get('id'))

    def load_products(self):
        """Charger et afficher tous les produits"""
        self.products_data = ProductController.get_all_products()
        self.refresh_table(self.products_data)
        self.update_stats()

    def refresh_table(self, products):
        """Rafraîchir le tableau"""
        self.productsTable.setRowCount(0)
        self.productsTable.setColumnCount(8)
        self.productsTable.setHorizontalHeaderLabels(
            ["ID", "Catégorie", "Produit", "P. Achat", "P. Vente", "Marge %", "Stock", "Actions"]
        )
        self.productsTable.verticalHeader().setDefaultSectionSize(44)
        
        for row_idx, product in enumerate(products):
            self.productsTable.insertRow(row_idx)
            
            # ID
            id_item = QTableWidgetItem(str(product.get('id', '')))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.productsTable.setItem(row_idx, 0, id_item)
            
            # Catégorie
            cat_item = QTableWidgetItem(product.get('categorie', ''))
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.productsTable.setItem(row_idx, 1, cat_item)
            
            # Produit
            prod_item = QTableWidgetItem(product.get('nom', ''))
            prod_item.setFlags(prod_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.productsTable.setItem(row_idx, 2, prod_item)
            
            # Prix achat
            pa_item = QTableWidgetItem(f"{product.get('prix_achat', 0):.2f} XOF")
            pa_item.setFlags(pa_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.productsTable.setItem(row_idx, 3, pa_item)
            
            # Prix vente
            pv_item = QTableWidgetItem(f"{product.get('prix_vente', 0):.2f} XOF")
            pv_item.setFlags(pv_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.productsTable.setItem(row_idx, 4, pv_item)
            
            # Marge %
            margin = ProductController.calculate_margin(
                product.get('prix_achat', 0),
                product.get('prix_vente', 0)
            )
            margin_item = QTableWidgetItem(f"{margin:.1f}%")
            margin_item.setFlags(margin_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.productsTable.setItem(row_idx, 5, margin_item)
            
            # Stock
            stock = product.get('stock_actuel', 0)
            stock_min = product.get('stock_min', 0)
            stock_item = QTableWidgetItem(f"{stock}/{stock_min}")
            
            # Colorer si stock bas
            if stock <= stock_min:
                stock_item.setBackground(QColor(255, 200, 200))
            
            stock_item.setFlags(stock_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.productsTable.setItem(row_idx, 6, stock_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(8)
            
            edit_btn = QPushButton("✏️ Modifier")
            edit_btn.setProperty("variant", "tableAction")
            edit_btn.setMinimumWidth(110)
            edit_btn.clicked.connect(lambda checked, pid=product.get('id'): self.edit_product_by_id(pid))
            
            stock_btn = QPushButton("📦 Stock")
            stock_btn.setProperty("variant", "tableAction")
            stock_btn.setMinimumWidth(90)
            stock_btn.clicked.connect(lambda checked, pid=product.get('id'): self.manage_stock(pid))
            
            delete_btn = QPushButton("🗑️ Supprimer")
            delete_btn.setProperty("variant", "tableAction")
            delete_btn.setMinimumWidth(120)
            delete_btn.clicked.connect(lambda checked, pid=product.get('id'): self.delete_product(pid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(stock_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            actions_widget.setLayout(actions_layout)
            self.productsTable.setCellWidget(row_idx, 7, actions_widget)
        
        self.productsTable.resizeColumnsToContents()
        # Ensure actions column stays readable (cell widgets aren't always considered by autosize)
        self.productsTable.setColumnWidth(7, 360)
        self.productsTable.horizontalHeader().setStretchLastSection(True)

    def search_products(self, search_term):
        """Rechercher les produits"""
        if search_term.strip():
            results = ProductController.search_products(search_term)
        else:
            results = self.products_data
        
        # Appliquer aussi le filtre catégorie si nécessaire
        if self.categoryFilter.currentData() != -1:
            cat_id = self.categoryFilter.currentData()
            results = [p for p in results if p.get('category_id') == cat_id]
        
        self.refresh_table(results)

    def filter_by_category(self):
        """Filtrer par catégorie"""
        cat_id = self.categoryFilter.currentData()
        
        if cat_id == -1:
            results = self.products_data
        else:
            results = ProductController.get_products_by_category(cat_id)
        
        # Appliquer aussi la recherche si nécessaire
        if self.searchInput.text().strip():
            search = self.searchInput.text().strip()
            results = [p for p in results if search.lower() in p.get('nom', '').lower()]
        
        self.refresh_table(results)

    def update_stats(self):
        """Mettre à jour les statistiques"""
        total = len(self.products_data)
        low_stock = len(ProductController.get_low_stock_products())
        self.statsLabel.setText(f"Total produits : {total} | Stocks bas : {low_stock}")

    def open_add_dialog(self):
        """Ouvrir le dialogue pour ajouter"""
        dialog = ProductFormDialog(self, self.categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()

    def edit_product(self, index):
        """Éditer un produit (double-clic)"""
        if index.isValid():
            product_id = int(self.productsTable.item(index.row(), 0).text())
            self.edit_product_by_id(product_id)

    def edit_product_by_id(self, product_id):
        """Éditer un produit par ID"""
        product = ProductController.get_product(product_id)
        if product:
            dialog = ProductFormDialog(self, self.categories, product)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_products()

    def delete_product(self, product_id):
        """Supprimer un produit"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce produit ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = ProductController.delete_product(product_id)
            if success:
                QMessageBox.information(self, "Succès", message)
                self.load_products()
            else:
                QMessageBox.warning(self, "Erreur", message)

    def manage_stock(self, product_id):
        """Gérer le stock d'un produit"""
        product = ProductController.get_product(product_id)
        if product:
            dialog = StockManagementDialog(self, product)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_products()

    def show_low_stock(self):
        """Afficher les produits en rupture de stock"""
        low_stock = ProductController.get_low_stock_products()
        self.refresh_table(low_stock)
        QMessageBox.information(
            self,
            "Stocks bas",
            f"{len(low_stock)} produit(s) avec stock faible ou critique"
        )

    def show_context_menu(self, position):
        """Menu contextuel"""
        item = self.productsTable.itemAt(position)
        if item:
            row = item.row()
            product_id = int(self.productsTable.item(row, 0).text())
            
            menu = QMessageBox()
            menu.setWindowTitle("Options")
            menu.setText("Que voulez-vous faire ?")
            
            edit_btn = menu.addButton("Modifier", QMessageBox.ButtonRole.ActionRole)
            stock_btn = menu.addButton("Gérer Stock", QMessageBox.ButtonRole.ActionRole)
            delete_btn = menu.addButton("Supprimer", QMessageBox.ButtonRole.ActionRole)
            cancel_btn = menu.addButton("Annuler", QMessageBox.ButtonRole.RejectRole)
            
            menu.exec()


class ProductFormDialog(QDialog):
    """Dialogue pour ajouter/modifier un produit"""
    
    def __init__(self, parent=None, categories=None, product=None):
        super().__init__(parent)
        self.product = product
        self.categories = categories or []
        self.init_ui()
        
        if product:
            self.load_product_data()

    def init_ui(self):
        """Initialiser l'interface"""
        self.setWindowTitle("Formulaire Produit")
        self.setGeometry(100, 100, 500, 600)
        
        layout = QVBoxLayout()
        
        # Catégorie
        layout.addWidget(QLabel("Catégorie *"))
        self.category_combo = QComboBox()
        for cat in self.categories:
            self.category_combo.addItem(cat.get('nom', ''), cat.get('id'))
        layout.addWidget(self.category_combo)
        
        # Nom
        layout.addWidget(QLabel("Nom du produit *"))
        self.nom_input = QLineEdit()
        layout.addWidget(self.nom_input)
        
        # Description
        layout.addWidget(QLabel("Description"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)
        
        # Prix achat
        layout.addWidget(QLabel("Prix d'achat *"))
        self.prix_achat_input = QLineEdit()
        self.prix_achat_input.setPlaceholderText("XOF")
        layout.addWidget(self.prix_achat_input)
        
        # Prix vente
        layout.addWidget(QLabel("Prix de vente *"))
        self.prix_vente_input = QLineEdit()
        self.prix_vente_input.setPlaceholderText("XOF")
        layout.addWidget(self.prix_vente_input)
        
        # Affichage marge en temps réel
        layout.addWidget(QLabel("Marge bénéficiaire"))
        self.margin_label = QLabel("0.0%")
        self.margin_label.setStyleSheet("font-weight: bold; color: green;")
        layout.addWidget(self.margin_label)
        
        self.prix_vente_input.textChanged.connect(self.update_margin)
        self.prix_achat_input.textChanged.connect(self.update_margin)
        
        # Stock minimum
        layout.addWidget(QLabel("Stock minimum *"))
        self.stock_min_input = QSpinBox()
        self.stock_min_input.setValue(5)
        self.stock_min_input.setMinimum(0)
        layout.addWidget(self.stock_min_input)
        
        # Stock actuel
        layout.addWidget(QLabel("Stock actuel"))
        self.stock_actuel_input = QSpinBox()
        self.stock_actuel_input.setMinimum(0)
        layout.addWidget(self.stock_actuel_input)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save_product)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def load_product_data(self):
        """Charger les données du produit"""
        self.nom_input.setText(self.product.get('nom', ''))
        self.description_input.setText(self.product.get('description', '') or '')
        self.prix_achat_input.setText(str(self.product.get('prix_achat', '')))
        self.prix_vente_input.setText(str(self.product.get('prix_vente', '')))
        self.stock_min_input.setValue(self.product.get('stock_min', 5))
        self.stock_actuel_input.setValue(self.product.get('stock_actuel', 0))
        
        # Sélectionner la catégorie
        cat_id = self.product.get('category_id')
        index = self.category_combo.findData(cat_id)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.update_margin()

    def update_margin(self):
        """Calculer et afficher la marge"""
        try:
            pa = float(self.prix_achat_input.text() or 0)
            pv = float(self.prix_vente_input.text() or 0)
            
            if pa > 0:
                margin = ((pv - pa) / pa) * 100
                self.margin_label.setText(f"{margin:.1f}%")
                
                # Couleur selon marge
                if margin < 20:
                    self.margin_label.setStyleSheet("font-weight: bold; color: orange;")
                elif margin < 10:
                    self.margin_label.setStyleSheet("font-weight: bold; color: red;")
                else:
                    self.margin_label.setStyleSheet("font-weight: bold; color: green;")
            else:
                self.margin_label.setText("0.0%")
        except:
            self.margin_label.setText("Erreur")

    def save_product(self):
        """Enregistrer le produit"""
        nom = self.nom_input.text().strip()
        description = self.description_input.toPlainText().strip() or None
        category_id = self.category_combo.currentData()
        
        try:
            prix_achat = float(self.prix_achat_input.text())
            prix_vente = float(self.prix_vente_input.text())
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Les prix doivent être des nombres")
            return
        
        stock_min = self.stock_min_input.value()
        stock_actuel = self.stock_actuel_input.value()
        
        # Validation
        is_valid, error = ProductValidator.validate_product_form(
            nom, prix_achat, prix_vente, stock_min, category_id
        )
        
        if not is_valid:
            QMessageBox.warning(self, "Erreur de validation", error)
            return
        
        # Enregistrer
        if self.product:
            success, message = ProductController.update_product(
                self.product['id'], category_id, nom, description, prix_achat, prix_vente, stock_min
            )
        else:
            success, message = ProductController.create_product(
                category_id, nom, description, prix_achat, prix_vente, stock_min, stock_actuel
            )
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)


class StockManagementDialog(QDialog):
    """Dialogue pour gérer le stock"""
    
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface"""
        self.setWindowTitle(f"Gestion Stock - {self.product['nom']}")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        # Infos produit
        info = f"Produit : {self.product['nom']}\nStock actuel : {self.product['stock_actuel']}\nStock minimum : {self.product['stock_min']}"
        layout.addWidget(QLabel(info))
        
        layout.addWidget(QLabel("Quantité à ajouter/retirer (négatif pour retirer) *"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(-1000, 1000)
        layout.addWidget(self.quantity_input)
        
        layout.addWidget(QLabel("Type de mouvement *"))
        self.reason_input = QComboBox()
        self.reason_input.addItems(["entree", "sortie", "ajustement"])
        layout.addWidget(self.reason_input)
        
        layout.addWidget(QLabel("Description (optionnel)"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Ex: Réapprovisionnement, Casse...")
        layout.addWidget(self.description_input)
        
        # Historique
        layout.addWidget(QLabel("Historique des mouvements :"))
        
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Date", "Type", "Quantité", "Description", "Utilisateur"])
        self.history_table.setMaximumHeight(150)
        
        movements = ProductController.get_stock_movements(self.product['id'])
        self.history_table.setRowCount(len(movements))
        
        for row_idx, movement in enumerate(movements):
            self.history_table.setItem(row_idx, 0, QTableWidgetItem(str(movement.get('date_mouvement', ''))))
            self.history_table.setItem(row_idx, 1, QTableWidgetItem(movement.get('type', '')))
            self.history_table.setItem(row_idx, 2, QTableWidgetItem(str(movement.get('quantite', ''))))
            self.history_table.setItem(row_idx, 3, QTableWidgetItem(movement.get('description', '')))
            self.history_table.setItem(row_idx, 4, QTableWidgetItem(movement.get('username', '') or 'N/A'))
        
        self.history_table.resizeColumnsToContents()
        layout.addWidget(self.history_table)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Valider mouvement")
        add_btn.clicked.connect(self.record_movement)
        
        cancel_btn = QPushButton("Fermer")
        cancel_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def record_movement(self):
        """Enregistrer un mouvement de stock"""
        quantite = self.quantity_input.value()
        type_mouvement = self.reason_input.currentText()
        description = self.description_input.text().strip()
        
        if not type_mouvement:
            QMessageBox.warning(self, "Erreur", "Le type de mouvement est obligatoire")
            return
        
        if quantite == 0:
            QMessageBox.warning(self, "Erreur", "La quantité doit être différente de 0")
            return
        
        user = Session.get_user()
        user_id = user.get('id') if user else None
        
        success, message = ProductController.update_product_stock(
            self.product['id'], quantite, type_mouvement, user_id, description
        )
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)
