from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QDialog, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QFileDialog, QTextEdit,
    QTableWidget, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from controllers.sale_controller import SaleController
from controllers.product_controller import ProductController
from controllers.client_controller import ClientController
from utils.validators import SaleValidator
from utils.session import Session
from utils.excel_exporter import export_sales_to_excel
from datetime import datetime


class SalesView(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("views/ui/sales.ui", self)

        # Make sure row height is enough for embedded action widgets
        self.salesTable.verticalHeader().setDefaultSectionSize(44)
        
        self.sales_data = []
        
        # Connexions
        self.btnNewSale.clicked.connect(self.open_new_sale_dialog)
        self.btnUnpaid.clicked.connect(self.show_unpaid_sales)
        self.btnExport.clicked.connect(self.export_excel)
        self.searchInput.textChanged.connect(self.search_sales)
        self.statusFilter.currentIndexChanged.connect(self.filter_by_status)
        self.salesTable.doubleClicked.connect(self.view_sale_details)
        
        # Menu contextuel
        self.salesTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.salesTable.customContextMenuRequested.connect(self.show_context_menu)
        
        # Charger les données
        self.load_sales()

    def load_sales(self):
        """Charger toutes les ventes"""
        self.sales_data = SaleController.get_all_sales(limit=1000)
        self.refresh_table(self.sales_data)
        self.update_stats()

    def refresh_table(self, sales):
        """Rafraîchir le tableau"""
        self.salesTable.setRowCount(len(sales))
        
        for row_idx, sale in enumerate(sales):
            # Numéro facture
            numero = sale.get('numero_facture', '')
            self.salesTable.setItem(row_idx, 0, QTableWidgetItem(str(numero)))
            
            # Client
            client = sale.get('client_nom', 'N/A')
            self.salesTable.setItem(row_idx, 1, QTableWidgetItem(str(client)))
            
            # Date
            date_str = str(sale.get('date_vente', ''))[:10]
            self.salesTable.setItem(row_idx, 2, QTableWidgetItem(date_str))
            
            # Montant total
            montant = float(sale.get('montant_total', 0))
            item_montant = QTableWidgetItem(f"{montant:.2f}€")
            item_montant.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.salesTable.setItem(row_idx, 3, item_montant)
            
            # Montant payé
            paye = float(sale.get('montant_paye', 0))
            item_paye = QTableWidgetItem(f"{paye:.2f}€")
            item_paye.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.salesTable.setItem(row_idx, 4, item_paye)
            
            # Statut
            statut = sale.get('statut', 'en_cours')
            item_statut = QTableWidgetItem(statut)
            
            # Colorer le statut
            if statut == 'payee':
                item_statut.setBackground(QColor(144, 238, 144))  # Vert clair
            elif statut == 'partielle':
                item_statut.setBackground(QColor(255, 218, 185))  # Orange clair
            elif statut == 'en_cours':
                item_statut.setBackground(QColor(255, 200, 200))  # Rouge clair
            elif statut == 'annulee':
                item_statut.setBackground(QColor(200, 200, 200))  # Gris
            
            self.salesTable.setItem(row_idx, 5, item_statut)
            
            # Actions
            btn_actions = QPushButton("⋮ Actions")
            btn_actions.setProperty("variant", "tableAction")
            btn_actions.setMinimumWidth(110)
            btn_actions.clicked.connect(lambda checked, s=sale: self.show_sale_menu(s))
            self.salesTable.setCellWidget(row_idx, 6, btn_actions)
        
        self.salesTable.resizeColumnsToContents()
        self.salesTable.horizontalHeader().setStretchLastSection(True)
        # Ensure the actions column stays readable
        self.salesTable.setColumnWidth(6, 140)

    def update_stats(self):
        """Mettre à jour les statistiques"""
        stats = SaleController.get_sales_statistics()
        
        total_ventes = stats.get('total_ventes', 0)
        ca_total = stats.get('ca_total', 0)
        ticket_moyen = stats.get('ticket_moyen', 0)
        montant_reste = stats.get('montant_reste', 0)
        
        self.statsLabel.setText(
            f"📊 Statistiques du jour : Ventes: {total_ventes} | "
            f"CA: {ca_total:.2f}€ | Ticket moyen: {ticket_moyen:.2f}€ | "
            f"Impayés: {montant_reste:.2f}€"
        )

    def search_sales(self, query):
        """Rechercher une vente"""
        if not query:
            self.load_sales()
            return
        
        # Rechercher par numéro ou client
        if query.isdigit():
            results = SaleController.search_sales(query, 'numero')
        else:
            results = SaleController.search_sales(query, 'client')
        
        filtered = self.filter_by_status_internal(results)
        self.refresh_table(filtered)

    def filter_by_status(self):
        """Filtrer par statut"""
        filtered = self.filter_by_status_internal(self.sales_data)
        self.refresh_table(filtered)

    def filter_by_status_internal(self, sales):
        """Filtrer les ventes par statut sélectionné"""
        status_text = self.statusFilter.currentText()
        
        status_map = {
            'En cours': 'en_cours',
            'Payées': 'payee',
            'Partielles': 'partielle',
            'Annulées': 'annulee'
        }
        
        if status_text == 'Tous les statuts':
            return sales
        
        target_status = status_map.get(status_text)
        return [s for s in sales if s.get('statut') == target_status]

    def open_new_sale_dialog(self):
        """Ouvrir le dialogue de création de vente"""
        dialog = SaleFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_sales()

    def view_sale_details(self, index):
        """Afficher les détails d'une vente"""
        if index.row() < len(self.sales_data):
            sale = self.sales_data[index.row()]
            dialog = SaleDetailsDialog(sale, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_sales()

    def show_unpaid_sales(self):
        """Afficher les ventes impayées"""
        unpaid = SaleController.get_unpaid_sales()
        self.sales_data = unpaid
        self.refresh_table(unpaid)

    def export_excel(self):
        """Exporter les ventes en Excel"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les ventes", "", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                export_sales_to_excel(self.sales_data, file_path)
                QMessageBox.information(self, "Succès", f"Export réussi : {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Erreur export : {str(e)}")

    def show_sale_menu(self, sale):
        """Afficher le menu d'actions pour une vente"""
        dialog = SaleActionsDialog(sale, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_sales()

    def show_context_menu(self, position):
        """Afficher le menu contextuel"""
        item = self.salesTable.itemAt(position)
        if item:
            row = item.row()
            if row < len(self.sales_data):
                self.show_sale_menu(self.sales_data[row])


class SaleFormDialog(QDialog):
    """Dialogue de création/édition de vente"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle Vente")
        self.setGeometry(100, 100, 900, 600)
        self.articles = []
        try:
            self.init_ui()
        except Exception as e:
            print(f"Erreur lors de l'initialisation du formulaire de vente : {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'initialisation : {str(e)}")

    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout()
        
        # Sélection client
        client_layout = QHBoxLayout()
        client_layout.addWidget(QLabel("Client *"))
        self.client_combo = QComboBox()
        self.load_clients()
        client_layout.addWidget(self.client_combo)
        layout.addLayout(client_layout)
        
        # Sélection produits
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel("Produit à ajouter"))
        self.product_combo = QComboBox()
        self.load_products()
        product_layout.addWidget(self.product_combo)
        
        product_layout.addWidget(QLabel("Quantité"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(1000)
        self.quantity_input.setValue(1)
        product_layout.addWidget(self.quantity_input)
        
        btn_add_product = QPushButton("Ajouter")
        btn_add_product.clicked.connect(self.add_product)
        product_layout.addWidget(btn_add_product)
        layout.addLayout(product_layout)
        
        # Tableau des articles
        layout.addWidget(QLabel("Articles de la vente :"))
        self.articles_table = QTableWidget()
        self.articles_table.setColumnCount(5)
        self.articles_table.setHorizontalHeaderLabels(["Produit", "Quantité", "P. Unit.", "Total", "Suppr."])
        self.articles_table.setMaximumHeight(200)
        layout.addWidget(self.articles_table)
        
        # Options de calcul
        calc_layout = QHBoxLayout()
        
        calc_layout.addWidget(QLabel("TVA (%) :"))
        self.tva_input = QDoubleSpinBox()
        self.tva_input.setValue(20)
        self.tva_input.setMaximum(100)
        self.tva_input.valueChanged.connect(self.update_totals)
        calc_layout.addWidget(self.tva_input)
        
        calc_layout.addWidget(QLabel("Remise :"))
        self.remise_input = QDoubleSpinBox()
        self.remise_input.setMaximum(10000)
        self.remise_input.valueChanged.connect(self.update_totals)
        calc_layout.addWidget(self.remise_input)
        
        self.remise_type_combo = QComboBox()
        self.remise_type_combo.addItems(["montant", "pourcentage"])
        self.remise_type_combo.currentIndexChanged.connect(self.update_totals)
        calc_layout.addWidget(self.remise_type_combo)
        
        calc_layout.addStretch()
        layout.addLayout(calc_layout)
        
        # Affichage des totaux
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        totals_layout.addWidget(QLabel("Total HT :"))
        self.total_ht_label = QLabel("0.00€")
        self.total_ht_label.setStyleSheet("font-weight: bold")
        totals_layout.addWidget(self.total_ht_label)
        totals_layout.addWidget(QLabel("TVA :"))
        self.tva_label = QLabel("0.00€")
        self.tva_label.setStyleSheet("font-weight: bold")
        totals_layout.addWidget(self.tva_label)
        totals_layout.addWidget(QLabel("Total TTC :"))
        self.total_ttc_label = QLabel("0.00€")
        self.total_ttc_label.setStyleSheet("font-weight: bold; color: green")
        totals_layout.addWidget(self.total_ttc_label)
        layout.addLayout(totals_layout)
        
        # Notes
        layout.addWidget(QLabel("Notes (optionnel)"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(self.notes_input)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        btn_save = QPushButton("✓ Créer vente")
        btn_save.clicked.connect(self.save_sale)
        
        btn_cancel = QPushButton("✗ Annuler")
        btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addWidget(btn_save)
        buttons_layout.addWidget(btn_cancel)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def load_clients(self):
        """Charger la liste des clients"""
        try:
            clients = ClientController.get_all_clients()
            self.client_combo.clear()
            
            if not clients:
                self.client_combo.addItem("Aucun client disponible", None)
                QMessageBox.warning(self, "Base de données", "Aucun client trouvé. Vérifiez que la base de données est connectée et contient des clients.")
                return
            
            for client in clients:
                try:
                    nom = client.get('nom', 'N/A')
                    prenom = client.get('prenom', 'N/A')
                    client_id = client.get('id')
                    
                    if client_id is None:
                        continue
                    
                    nom_complet = f"{nom} {prenom}"
                    self.client_combo.addItem(nom_complet, client_id)
                except Exception as e:
                    print(f"Erreur lors du chargement du client : {e}")
                    continue
        except Exception as e:
            error_msg = str(e)
            print(f"Erreur lors du chargement des clients : {error_msg}")
            self.client_combo.clear()
            self.client_combo.addItem("⚠️ Erreur de connexion", None)
            QMessageBox.critical(self, "Erreur de connexion", 
                f"Impossible de charger les clients.\n\n"
                f"Vérifiez que le serveur MySQL est démarré.\n\n"
                f"Détails: {error_msg}")

    def load_products(self):
        """Charger la liste des produits"""
        try:
            products = ProductController.get_all_products()
            self.product_combo.clear()
            
            if not products:
                self.product_combo.addItem("Aucun produit disponible", None)
                QMessageBox.warning(self, "Base de données", "Aucun produit trouvé. Vérifiez que la base de données est connectée et contient des produits.")
                return
            
            for prod in products:
                try:
                    # Récupérer les données avec gestion des valeurs manquantes
                    nom = prod.get('nom', 'Produit sans nom')
                    categorie = prod.get('categorie', 'N/A')
                    prix_vente = prod.get('prix_vente', 0)
                    produit_id = prod.get('id')
                    
                    # Vérifier les valeurs
                    if produit_id is None:
                        continue
                    
                    # Convertir le prix en float
                    try:
                        prix = float(prix_vente) if prix_vente else 0.0
                    except (ValueError, TypeError):
                        prix = 0.0
                    
                    # Ajouter au combo box
                    display_text = f"{nom} ({categorie}) - {prix:.2f}€"
                    self.product_combo.addItem(display_text, (produit_id, prix))
                except Exception as e:
                    print(f"Erreur lors du chargement du produit : {e}")
                    continue
        except Exception as e:
            error_msg = str(e)
            print(f"Erreur lors du chargement des produits : {error_msg}")
            self.product_combo.clear()
            self.product_combo.addItem("⚠️ Erreur de connexion", None)
            QMessageBox.critical(self, "Erreur de connexion", 
                f"Impossible de charger les produits.\n\n"
                f"Vérifiez que le serveur MySQL est démarré.\n\n"
                f"Détails: {error_msg}")

    def add_product(self):
        """Ajouter un produit aux articles"""
        if self.product_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un produit")
            return
        
        current_data = self.product_combo.currentData()
        if current_data is None or not isinstance(current_data, tuple):
            QMessageBox.warning(self, "Erreur", "Produit invalide")
            return
        
        try:
            product_id, prix_unitaire = current_data
            prix_unitaire = float(prix_unitaire)
            quantite = self.quantity_input.value()
            
            # Vérifier si produit déjà présent
            for article in self.articles:
                if article['produit_id'] == product_id:
                    article['quantite'] += quantite
                    self.update_articles_table()
                    self.update_totals()
                    return
            
            # Extraire le nom du produit de manière sécurisée
            combo_text = self.product_combo.currentText()
            # Format: "Nom (Catégorie) - Prix€"
            if '(' in combo_text:
                nom = combo_text.split('(')[0].strip()
            else:
                nom = combo_text
            
            # Ajouter nouvel article
            self.articles.append({
                'produit_id': product_id,
                'quantite': quantite,
                'prix_unitaire': prix_unitaire,
                'nom': nom
            })
            
            self.update_articles_table()
            self.update_totals()
        except (ValueError, TypeError) as e:
            QMessageBox.warning(self, "Erreur", f"Erreur de conversion de données : {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'ajout du produit : {str(e)}")

    def update_articles_table(self):
        """Mettre à jour l'affichage des articles"""
        self.articles_table.setRowCount(len(self.articles))
        
        for row, article in enumerate(self.articles):
            self.articles_table.setItem(row, 0, QTableWidgetItem(article['nom']))
            self.articles_table.setItem(row, 1, QTableWidgetItem(str(article['quantite'])))
            
            prix = article['prix_unitaire']
            self.articles_table.setItem(row, 2, QTableWidgetItem(f"{prix:.2f}€"))
            
            total = article['quantite'] * prix
            self.articles_table.setItem(row, 3, QTableWidgetItem(f"{total:.2f}€"))
            
            btn_remove = QPushButton("✗")
            btn_remove.clicked.connect(lambda checked, r=row: self.remove_article(r))
            self.articles_table.setCellWidget(row, 4, btn_remove)

    def remove_article(self, row):
        """Supprimer un article"""
        if 0 <= row < len(self.articles):
            self.articles.pop(row)
            self.update_articles_table()
            self.update_totals()

    def update_totals(self):
        """Mettre à jour les totaux"""
        montant_ht = sum(art['quantite'] * art['prix_unitaire'] for art in self.articles)
        
        # Appliquer remise
        remise = self.remise_input.value()
        if self.remise_type_combo.currentText() == 'pourcentage':
            montant_remise = montant_ht * (remise / 100)
        else:
            montant_remise = remise
        
        montant_ht_net = montant_ht - montant_remise
        tva_pct = self.tva_input.value()
        montant_tva = montant_ht_net * (tva_pct / 100)
        montant_ttc = montant_ht_net + montant_tva
        
        self.total_ht_label.setText(f"{montant_ht_net:.2f}€")
        self.tva_label.setText(f"{montant_tva:.2f}€")
        self.total_ttc_label.setText(f"{montant_ttc:.2f}€")

    def open_new_client_dialog(self):
        """Ouvrir le dialogue de création de client"""
        from views.clients_view import ClientFormDialog
        dialog = ClientFormDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_clients()

    def save_sale(self):
        """Créer la vente"""
        if self.client_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Client obligatoire")
            return
        
        if not self.articles:
            QMessageBox.warning(self, "Erreur", "Au moins un article obligatoire")
            return
        
        client_id = self.client_combo.currentData()
        user = Session.get_user()
        user_id = user.get('id') if user else None
        
        tva = self.tva_input.value()
        remise = self.remise_input.value()
        remise_type = self.remise_type_combo.currentText()
        notes = self.notes_input.toPlainText()
        
        success, message = SaleController.create_sale(
            client_id, user_id, self.articles, tva, remise, remise_type, notes
        )
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)


class SaleDetailsDialog(QDialog):
    """Dialogue de détails de vente"""
    def __init__(self, sale, parent=None):
        super().__init__(parent)
        self.sale = sale
        self.setWindowTitle(f"Vente {sale.get('numero_facture', '')}")
        self.setGeometry(100, 100, 900, 600)
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout()
        
        # Infos vente
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"<b>Facture:</b> {self.sale.get('numero_facture')}"))
        info_layout.addWidget(QLabel(f"<b>Client:</b> {self.sale.get('client_nom')}"))
        info_layout.addWidget(QLabel(f"<b>Date:</b> {str(self.sale.get('date_vente', ''))[:10]}"))
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Articles
        layout.addWidget(QLabel("Articles :"))
        
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels(["Produit", "Quantité", "P. Unit.", "Total"])
        
        details = SaleController.get_sale_details(self.sale['id'])
        self.details_table.setRowCount(len(details))
        
        for row, detail in enumerate(details):
            self.details_table.setItem(row, 0, QTableWidgetItem(detail.get('produit_nom', '')))
            self.details_table.setItem(row, 1, QTableWidgetItem(str(detail.get('quantite', ''))))
            self.details_table.setItem(row, 2, QTableWidgetItem(f"{float(detail.get('prix_unitaire', 0)):.2f}€"))
            total = float(detail.get('sous_total', 0))
            self.details_table.setItem(row, 3, QTableWidgetItem(f"{total:.2f}€"))
        
        self.details_table.resizeColumnsToContents()
        layout.addWidget(self.details_table)
        
        # Paiements
        layout.addWidget(QLabel("Paiements :"))
        
        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel(f"<b>Montant total:</b> {float(self.sale.get('montant_total', 0)):.2f}€"))
        payment_layout.addWidget(QLabel(f"<b>Montant payé:</b> {float(self.sale.get('montant_paye', 0)):.2f}€"))
        payment_layout.addWidget(QLabel(f"<b>Montant restant:</b> {float(self.sale.get('montant_reste', 0)):.2f}€"))
        payment_layout.addStretch()
        layout.addLayout(payment_layout)
        
        # Historique paiements
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(2)
        self.payments_table.setHorizontalHeaderLabels(["Date", "Montant"])
        
        payments = SaleController.get_payment_history(self.sale['id'])
        self.payments_table.setRowCount(len(payments))
        
        for row, payment in enumerate(payments):
            self.payments_table.setItem(row, 0, QTableWidgetItem(str(payment.get('date_paiement', ''))[:10]))
            self.payments_table.setItem(row, 1, QTableWidgetItem(f"{float(payment.get('montant', 0)):.2f}€"))
        
        layout.addWidget(self.payments_table)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        if self.sale.get('statut') != 'payee':
            btn_payment = QPushButton("💰 Enregistrer paiement")
            btn_payment.clicked.connect(self.open_payment_dialog)
            buttons_layout.addWidget(btn_payment)
        
        btn_print = QPushButton("🖨️ Imprimer")
        btn_print.clicked.connect(self.print_invoice)
        buttons_layout.addWidget(btn_print)
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_close)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def open_payment_dialog(self):
        """Ouvrir le dialogue de paiement"""
        dialog = PaymentDialog(self.sale, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.accept()

    def print_invoice(self):
        """Imprimer la facture"""
        try:
            # Demander le chemin de sauvegarde
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Exporter la facture en PDF", 
                f"Facture_{self.sale['numero_facture'].replace('/', '-')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Informations entreprise (à adapter selon vos besoins)
                company_info = {
                    'name': 'Votre Entreprise',
                    'address': '123 Rue de la Paix, 75000 Paris',
                    'phone': '01 23 45 67 89',
                    'email': 'contact@entreprise.fr'
                }
                
                success, message = SaleController.export_sale_to_pdf(
                    self.sale['id'],
                    file_path,
                    company_info
                )
                
                if success:
                    QMessageBox.information(self, "Succès", message)
                else:
                    QMessageBox.critical(self, "Erreur", message)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export PDF : {str(e)}")


class PaymentDialog(QDialog):
    """Dialogue de paiement"""
    def __init__(self, sale, parent=None):
        super().__init__(parent)
        self.sale = sale
        self.setWindowTitle("Enregistrer un paiement")
        self.setGeometry(200, 200, 400, 300)
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout()
        
        montant_total = float(self.sale.get('montant_total', 0))
        montant_paye = float(self.sale.get('montant_paye', 0))
        montant_restant = montant_total - montant_paye
        
        layout.addWidget(QLabel(f"<b>Montant total:</b> {montant_total:.2f}€"))
        layout.addWidget(QLabel(f"<b>Montant payé:</b> {montant_paye:.2f}€"))
        layout.addWidget(QLabel(f"<b>Montant restant:</b> {montant_restant:.2f}€"))
        layout.addWidget(QLabel(""))
        
        layout.addWidget(QLabel("Montant à payer *"))
        self.montant_paiement = QDoubleSpinBox()
        self.montant_paiement.setMaximum(montant_restant)
        self.montant_paiement.setValue(montant_restant)
        self.montant_paiement.setDecimals(2)
        layout.addWidget(self.montant_paiement)
        
        layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        
        btn_save = QPushButton("✓ Valider paiement")
        btn_save.clicked.connect(self.save_payment)
        
        btn_cancel = QPushButton("✗ Annuler")
        btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addWidget(btn_save)
        buttons_layout.addWidget(btn_cancel)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def save_payment(self):
        """Enregistrer le paiement"""
        montant_paiement = self.montant_paiement.value()
        
        success, message = SaleController.record_payment(self.sale['id'], montant_paiement)
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)


class SaleActionsDialog(QDialog):
    """Dialogue d'actions sur une vente"""
    def __init__(self, sale, parent=None):
        super().__init__(parent)
        self.sale = sale
        self.setWindowTitle(f"Actions - {sale.get('numero_facture')}")
        self.setGeometry(200, 200, 400, 250)
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"<b>Facture:</b> {self.sale.get('numero_facture')}"))
        layout.addWidget(QLabel(f"<b>Statut actuel:</b> {self.sale.get('statut')}"))
        layout.addWidget(QLabel(""))
        
        buttons_layout = QVBoxLayout()
        
        if self.sale.get('statut') != 'payee':
            btn_payment = QPushButton("💰 Enregistrer paiement")
            btn_payment.clicked.connect(self.record_payment)
            buttons_layout.addWidget(btn_payment)
        
        btn_view = QPushButton("👁️ Voir détails")
        btn_view.clicked.connect(self.view_details)
        buttons_layout.addWidget(btn_view)
        
        btn_print = QPushButton("🖨️ Imprimer facture")
        btn_print.clicked.connect(self.print_invoice)
        buttons_layout.addWidget(btn_print)
        
        if self.sale.get('statut') != 'annulee':
            btn_cancel = QPushButton("❌ Annuler vente")
            btn_cancel.clicked.connect(self.cancel_sale)
            buttons_layout.addWidget(btn_cancel)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)

    def record_payment(self):
        """Enregistrer un paiement"""
        dialog = PaymentDialog(self.sale, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.accept()

    def view_details(self):
        """Voir les détails"""
        dialog = SaleDetailsDialog(self.sale, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.accept()

    def print_invoice(self):
        """Imprimer la facture"""
        try:
            # Demander le chemin de sauvegarde
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Exporter la facture en PDF", 
                f"Facture_{self.sale['numero_facture'].replace('/', '-')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Informations entreprise (à adapter selon vos besoins)
                company_info = {
                    'name': 'Votre Entreprise',
                    'address': '123 Rue de la Paix, 75000 Paris',
                    'phone': '01 23 45 67 89',
                    'email': 'contact@entreprise.fr'
                }
                
                success, message = SaleController.export_sale_to_pdf(
                    self.sale['id'],
                    file_path,
                    company_info
                )
                
                if success:
                    QMessageBox.information(self, "Succès", message)
                else:
                    QMessageBox.critical(self, "Erreur", message)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export PDF : {str(e)}")

    def cancel_sale(self):
        """Annuler la vente"""
        reply = QMessageBox.question(self, "Confirmation", "Êtes-vous sûr d'annuler cette vente?")
        if reply == QMessageBox.StandardButton.Yes:
            success, message = SaleController.update_sale_status(self.sale['id'], 'annulee')
            if success:
                QMessageBox.information(self, "Succès", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", message)
