from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from controllers.client_controller import ClientController
from utils.path import resource_path
from utils.validators import ClientValidator
from utils.excel_exporter import ClientExporter
from utils.pdf_generator import ClientPDFGenerator
from datetime import datetime


class ClientsView(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi(resource_path("views/ui/clients.ui"), self)
        
        self.clients_data = []
        
        # Connexions des signaux
        self.btnAdd.clicked.connect(self.open_add_dialog)
        self.btnExportExcel.clicked.connect(self.export_excel)
        self.btnExportPDF.clicked.connect(self.export_pdf)
        self.searchInput.textChanged.connect(self.search_clients)
        self.clientsTable.doubleClicked.connect(self.edit_client)
        
        # Menu contextuel
        self.clientsTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.clientsTable.customContextMenuRequested.connect(self.show_context_menu)
        
        # Charger les données
        self.load_clients()

    def load_clients(self):
        """Charger et afficher tous les clients"""
        self.clients_data = ClientController.get_all_clients()
        self.refresh_table(self.clients_data)
        self.update_stats()

    def refresh_table(self, clients):
        """Rafraîchir le tableau avec les clients"""
        self.clientsTable.setRowCount(0)
        self.clientsTable.setColumnCount(7)
        self.clientsTable.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Téléphone", "Email", "Ville", "Actions"])
        self.clientsTable.verticalHeader().setDefaultSectionSize(44)
        
        for row_idx, client in enumerate(clients):
            self.clientsTable.insertRow(row_idx)
            
            # ID
            id_item = QTableWidgetItem(str(client.get('id', '')))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.clientsTable.setItem(row_idx, 0, id_item)
            
            # Nom
            self.clientsTable.setItem(row_idx, 1, QTableWidgetItem(client.get('nom', '')))
            
            # Prénom
            self.clientsTable.setItem(row_idx, 2, QTableWidgetItem(client.get('prenom', '')))
            
            # Téléphone
            self.clientsTable.setItem(row_idx, 3, QTableWidgetItem(client.get('telephone', '') or ''))
            
            # Email
            self.clientsTable.setItem(row_idx, 4, QTableWidgetItem(client.get('email', '') or ''))
            
            # Ville
            self.clientsTable.setItem(row_idx, 5, QTableWidgetItem(client.get('ville', '') or ''))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(8)
            
            edit_btn = QPushButton("✏️ Modifier")
            edit_btn.setProperty("variant", "tableAction")
            edit_btn.setMinimumWidth(110)
            edit_btn.clicked.connect(lambda checked, cid=client.get('id'): self.edit_client_by_id(cid))
            
            delete_btn = QPushButton("🗑️ Supprimer")
            delete_btn.setProperty("variant", "tableAction")
            delete_btn.setMinimumWidth(120)
            delete_btn.clicked.connect(lambda checked, cid=client.get('id'): self.delete_client(cid))
            
            history_btn = QPushButton("📊 Historique")
            history_btn.setProperty("variant", "tableAction")
            history_btn.setMinimumWidth(120)
            history_btn.clicked.connect(lambda checked, cid=client.get('id'): self.show_history(cid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(history_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            actions_widget.setLayout(actions_layout)
            self.clientsTable.setCellWidget(row_idx, 6, actions_widget)
        
        # Ajuster les largeurs
        self.clientsTable.resizeColumnsToContents()
        # NOTE: Qt may ignore cellWidget sizes during resizeColumnsToContents.
        # Make sure the Actions column remains wide enough to show button text.
        self.clientsTable.setColumnWidth(6, 390)
        self.clientsTable.horizontalHeader().setStretchLastSection(True)

    def search_clients(self, search_term):
        """Rechercher les clients"""
        if search_term.strip():
            results = ClientController.search_clients(search_term)
            self.refresh_table(results)
        else:
            self.refresh_table(self.clients_data)

    def update_stats(self):
        """Mettre à jour les statistiques"""
        total = len(self.clients_data)
        self.statsLabel.setText(f"Total clients : {total}")

    def open_add_dialog(self):
        """Ouvrir le dialogue pour ajouter un client"""
        dialog = ClientFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_clients()

    def edit_client(self, index):
        """Éditer un client (double-clic)"""
        if index.isValid():
            client_id = int(self.clientsTable.item(index.row(), 0).text())
            self.edit_client_by_id(client_id)

    def edit_client_by_id(self, client_id):
        """Éditer un client par ID"""
        client = ClientController.get_client(client_id)
        if client:
            dialog = ClientFormDialog(self, client)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_clients()

    def delete_client(self, client_id):
        """Supprimer un client"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce client ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = ClientController.delete_client(client_id)
            if success:
                QMessageBox.information(self, "Succès", message)
                self.load_clients()
            else:
                QMessageBox.warning(self, "Erreur", message)

    def show_history(self, client_id):
        """Afficher l'historique des achats"""
        client = ClientController.get_client(client_id)
        if client:
            history = ClientController.get_client_history(client_id)
            stats = ClientController.get_client_stats(client_id)
            
            dialog = HistoryDialog(self, client, history, stats)
            dialog.exec()

    def export_excel(self):
        """Exporter les clients en Excel"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en Excel",
            f"clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if filepath:
            success, message = ClientExporter.export_to_excel(self.clients_data, filepath)
            if success:
                QMessageBox.information(self, "Succès", message)
            else:
                QMessageBox.warning(self, "Erreur", message)

    def export_pdf(self):
        """Exporter les clients en PDF"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en PDF",
            f"clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if filepath:
            success, message = ClientPDFGenerator.export_clients_list(self.clients_data, filepath)
            if success:
                QMessageBox.information(self, "Succès", message)
            else:
                QMessageBox.critical(self, "Erreur", message)

    def show_context_menu(self, position):
        """Afficher un menu contextuel"""
        item = self.clientsTable.itemAt(position)
        if item:
            row = item.row()
            client_id = int(self.clientsTable.item(row, 0).text())
            
            menu = QMessageBox()
            menu.setWindowTitle("Options")
            menu.setText("Que voulez-vous faire ?")
            
            edit_btn = menu.addButton("Modifier", QMessageBox.ButtonRole.ActionRole)
            delete_btn = menu.addButton("Supprimer", QMessageBox.ButtonRole.ActionRole)
            history_btn = menu.addButton("Historique", QMessageBox.ButtonRole.ActionRole)
            cancel_btn = menu.addButton("Annuler", QMessageBox.ButtonRole.RejectRole)
            
            menu.exec()


class ClientFormDialog(QDialog):
    """Dialogue pour ajouter/modifier un client"""
    
    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.client = client
        self.init_ui()
        
        if client:
            self.load_client_data()

    def init_ui(self):
        """Initialiser l'interface"""
        self.setWindowTitle("Formulaire Client")
        self.setGeometry(100, 100, 400, 500)
        
        layout = QVBoxLayout()
        
        # Nom
        layout.addWidget(QLabel("Nom *"))
        self.nom_input = QLineEdit()
        layout.addWidget(self.nom_input)
        
        # Prénom
        layout.addWidget(QLabel("Prénom *"))
        self.prenom_input = QLineEdit()
        layout.addWidget(self.prenom_input)
        
        # Téléphone
        layout.addWidget(QLabel("Téléphone"))
        self.telephone_input = QLineEdit()
        layout.addWidget(self.telephone_input)
        
        # Email
        layout.addWidget(QLabel("Email"))
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)
        
        # Adresse
        layout.addWidget(QLabel("Adresse"))
        self.adresse_input = QLineEdit()
        layout.addWidget(self.adresse_input)
        
        # Ville
        layout.addWidget(QLabel("Ville"))
        self.ville_input = QLineEdit()
        layout.addWidget(self.ville_input)
        
        # Code postal
        layout.addWidget(QLabel("Code postal"))
        self.code_postal_input = QLineEdit()
        layout.addWidget(self.code_postal_input)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save_client)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def load_client_data(self):
        """Charger les données du client"""
        self.nom_input.setText(self.client.get('nom', ''))
        self.prenom_input.setText(self.client.get('prenom', ''))
        self.telephone_input.setText(self.client.get('telephone', '') or '')
        self.email_input.setText(self.client.get('email', '') or '')
        self.adresse_input.setText(self.client.get('adresse', '') or '')
        self.ville_input.setText(self.client.get('ville', '') or '')
        self.code_postal_input.setText(self.client.get('code_postal', '') or '')

    def save_client(self):
        """Enregistrer le client"""
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        telephone = self.telephone_input.text().strip() or None
        email = self.email_input.text().strip() or None
        adresse = self.adresse_input.text().strip() or None
        ville = self.ville_input.text().strip() or None
        code_postal = self.code_postal_input.text().strip() or None
        
        # Validation
        is_valid, error = ClientValidator.validate_client_form(
            nom, prenom, telephone, email, code_postal
        )
        
        if not is_valid:
            QMessageBox.warning(self, "Erreur de validation", error)
            return
        
        # Enregistrer
        if self.client:
            # Modification
            success, message = ClientController.update_client(
                self.client['id'], nom, prenom, telephone, email, adresse, ville, code_postal
            )
        else:
            # Création
            success, message = ClientController.create_client(
                nom, prenom, telephone, email, adresse, ville, code_postal
            )
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)


class HistoryDialog(QDialog):
    """Dialogue pour afficher l'historique des achats"""
    
    def __init__(self, parent=None, client=None, history=None, stats=None):
        super().__init__(parent)
        self.client = client
        self.history = history or []
        self.stats = stats or {}
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface"""
        self.setWindowTitle(f"Historique - {self.client['nom']} {self.client['prenom']}")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        # Informations client
        info_text = f"""
        Nom : {self.client['nom']} {self.client['prenom']}
        Téléphone : {self.client.get('telephone', 'N/A')}
        Email : {self.client.get('email', 'N/A')}
        """
        layout.addWidget(QLabel(info_text))
        
        # Statistiques
        if self.stats:
            stats_text = f"""
            Nombre d'achats : {self.stats.get('nombre_achats', 0) or 0}
            CA Total : {self.stats.get('ca_total', 0) or 0:.2f} XOF
            Montant moyen : {self.stats.get('montant_moyen', 0) or 0:.2f} XOF
            Dernière visite : {self.stats.get('derniere_visite', 'N/A')}
            """
            layout.addWidget(QLabel(stats_text))
        
        layout.addWidget(QLabel("Historique des achats :"))
        
        # Tableau historique
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["N° Facture", "Date", "Montant", "Statut"])
        table.setRowCount(len(self.history))
        
        for row_idx, item in enumerate(self.history):
            table.setItem(row_idx, 0, QTableWidgetItem(item.get('numero_facture', '')))
            table.setItem(row_idx, 1, QTableWidgetItem(str(item.get('date_vente', ''))))
            table.setItem(row_idx, 2, QTableWidgetItem(f"{item.get('montant_total', 0):.2f} XOF"))
            table.setItem(row_idx, 3, QTableWidgetItem(item.get('statut', '')))
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("📊 Exporter")
        export_btn.clicked.connect(self.export_history)
        
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(export_btn)
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def export_history(self):
        """Exporter l'historique en Excel"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter l'historique",
            f"historique_{self.client['nom']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if filepath:
            client_name = f"{self.client['nom']} {self.client['prenom']}"
            success, message = ClientExporter.export_client_history(client_name, self.history, filepath)
            if success:
                QMessageBox.information(self, "Succès", message)
            else:
                QMessageBox.warning(self, "Erreur", message)
