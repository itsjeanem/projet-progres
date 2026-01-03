from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QDialog, QMessageBox, QComboBox, QSpinBox,
    QDoubleSpinBox, QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from controllers.settings_controller import SettingsController
from utils.session import Session


class SettingsView(QWidget):
    """Vue des paramètres et configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Vérifier que l'utilisateur est admin
        user = Session.get_user()
        if user.get('role') != 'admin':
            self.init_no_access()
            return
        
        self.init_ui()

    def init_no_access(self):
        """Afficher un message d'accès refusé"""
        layout = QVBoxLayout()
        label = QLabel("❌ Accès refusé : Seuls les administrateurs peuvent accéder aux paramètres")
        label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        layout.addWidget(label)
        layout.addStretch()
        self.setLayout(layout)

    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("⚙️ Paramètres")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Onglet Entreprise
        # tabs.addTab(self.create_company_tab(), "🏢 Entreprise")
        
        # Onglet Utilisateurs
        tabs.addTab(self.create_users_tab(), "👥 Utilisateurs")
        
        # Onglet Paramètres généraux
        # tabs.addTab(self.create_general_tab(), "⚙️ Paramètres généraux")
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_company_tab(self):
        """Créer l'onglet entreprise"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Charger les infos
        company_info = SettingsController.get_company_info()
        
        # Nom entreprise
        layout.addWidget(QLabel("Nom de l'entreprise *"))
        self.company_name = QLineEdit()
        self.company_name.setText(company_info.get('company_name', ''))
        layout.addWidget(self.company_name)
        
        # Adresse
        layout.addWidget(QLabel("Adresse"))
        self.company_address = QLineEdit()
        self.company_address.setText(company_info.get('company_address', ''))
        layout.addWidget(self.company_address)
        
        # Téléphone
        layout.addWidget(QLabel("Téléphone"))
        self.company_phone = QLineEdit()
        self.company_phone.setText(company_info.get('company_phone', ''))
        layout.addWidget(self.company_phone)
        
        # Email
        layout.addWidget(QLabel("Email"))
        self.company_email = QLineEdit()
        self.company_email.setText(company_info.get('company_email', ''))
        layout.addWidget(self.company_email)
        
        # Site web
        layout.addWidget(QLabel("Site web"))
        self.company_website = QLineEdit()
        self.company_website.setText(company_info.get('company_website', ''))
        layout.addWidget(self.company_website)
        
        # Logo
        layout.addWidget(QLabel("Logo"))
        logo_layout = QHBoxLayout()
        self.company_logo = QLineEdit()
        self.company_logo.setText(company_info.get('company_logo', ''))
        self.company_logo.setReadOnly(True)
        logo_layout.addWidget(self.company_logo)
        
        btn_upload = QPushButton("📤 Sélectionner")
        btn_upload.clicked.connect(self.upload_logo)
        logo_layout.addWidget(btn_upload)
        
        layout.addLayout(logo_layout)
        
        # Bouton Sauvegarder
        layout.addSpacing(20)
        btn_save = QPushButton("✓ Sauvegarder")
        btn_save.clicked.connect(self.save_company_info)
        layout.addWidget(btn_save)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def upload_logo(self):
        """Uploader le logo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le logo", "", "Images (*.png *.jpg *.jpeg *.gif)"
        )
        if file_path:
            self.company_logo.setText(file_path)

    def save_company_info(self):
        """Sauvegarder les infos entreprise"""
        name = self.company_name.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom de l'entreprise est obligatoire")
            return
        
        success, message = SettingsController.update_company_info(
            name,
            self.company_address.text(),
            self.company_phone.text(),
            self.company_email.text(),
            self.company_website.text(),
            self.company_logo.text() if self.company_logo.text() else None
        )
        
        if success:
            QMessageBox.information(self, "Succès", message)
        else:
            QMessageBox.warning(self, "Erreur", message)

    def create_users_tab(self):
        """Créer l'onglet utilisateurs"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tableau des utilisateurs
        layout.addWidget(QLabel("Gestion des utilisateurs"))
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["ID", "Utilisateur", "Email", "Rôle", "Actif"])
        
        self.load_users()
        layout.addWidget(self.users_table)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        btn_add = QPushButton("➕ Nouvel utilisateur")
        btn_add.clicked.connect(self.open_new_user_dialog)
        buttons_layout.addWidget(btn_add)
        
        btn_edit = QPushButton("✏️ Modifier")
        btn_edit.clicked.connect(self.edit_selected_user)
        buttons_layout.addWidget(btn_edit)
        
        btn_reset_pwd = QPushButton("🔑 Réinitialiser mot de passe")
        btn_reset_pwd.clicked.connect(self.reset_password)
        buttons_layout.addWidget(btn_reset_pwd)
        
        btn_deactivate = QPushButton("❌ Désactiver")
        btn_deactivate.clicked.connect(self.deactivate_user)
        buttons_layout.addWidget(btn_deactivate)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def load_users(self):
        """Charger la liste des utilisateurs"""
        users = SettingsController.get_all_users()
        
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user.get('id', ''))))
            self.users_table.setItem(row, 1, QTableWidgetItem(user.get('username', '')))
            self.users_table.setItem(row, 2, QTableWidgetItem(user.get('email', '')))
            self.users_table.setItem(row, 3, QTableWidgetItem(user.get('role', '')))
            
            active = "✓" if user.get('is_active') else "✗"
            self.users_table.setItem(row, 4, QTableWidgetItem(active))
        
        self.users_table.resizeColumnsToContents()

    def open_new_user_dialog(self):
        """Ouvrir le dialogue de création d'utilisateur"""
        dialog = UserFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()

    def edit_selected_user(self):
        """Éditer l'utilisateur sélectionné"""
        row = self.users_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un utilisateur")
            return
        
        user_id = int(self.users_table.item(row, 0).text())
        # À implémenter : ouvrir un dialogue d'édition
        QMessageBox.information(self, "Info", "Fonctionnalité à développer")

    def reset_password(self):
        """Réinitialiser le mot de passe"""
        row = self.users_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un utilisateur")
            return
        
        user_id = int(self.users_table.item(row, 0).text())
        username = self.users_table.item(row, 1).text()
        
        dialog = ResetPasswordDialog(user_id, username, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()

    def deactivate_user(self):
        """Désactiver un utilisateur"""
        row = self.users_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un utilisateur")
            return
        
        user_id = int(self.users_table.item(row, 0).text())
        username = self.users_table.item(row, 1).text()
        
        reply = QMessageBox.question(self, "Confirmation", f"Désactiver l'utilisateur {username}?")
        if reply == QMessageBox.StandardButton.Yes:
            success, message = SettingsController.deactivate_user(user_id)
            if success:
                QMessageBox.information(self, "Succès", message)
                self.load_users()
            else:
                QMessageBox.warning(self, "Erreur", message)

    def create_general_tab(self):
        """Créer l'onglet paramètres généraux"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Charger les paramètres
        settings = SettingsController.get_general_settings()
        
        # Devise
        layout.addWidget(QLabel("Devise"))
        self.currency = QLineEdit()
        self.currency.setText(settings.get('currency', '€'))
        layout.addWidget(self.currency)
        
        # TVA par défaut
        layout.addWidget(QLabel("TVA par défaut (%)"))
        self.tva = QDoubleSpinBox()
        self.tva.setMaximum(100)
        tva_value = settings.get('tva_default', 20)
        tva_float = float(tva_value) if tva_value and str(tva_value).strip() else 20
        self.tva.setValue(tva_float)
        layout.addWidget(self.tva)
        
        # Préfixe factures
        layout.addWidget(QLabel("Préfixe des factures"))
        self.invoice_prefix = QLineEdit()
        self.invoice_prefix.setText(settings.get('invoice_prefix', 'FAC'))
        layout.addWidget(self.invoice_prefix)
        
        # Format date
        layout.addWidget(QLabel("Format de date"))
        self.date_format = QComboBox()
        self.date_format.addItems(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        current_format = settings.get('date_format', 'DD/MM/YYYY')
        self.date_format.setCurrentText(current_format)
        layout.addWidget(self.date_format)
        
        # Fuseau horaire
        layout.addWidget(QLabel("Fuseau horaire"))
        self.timezone = QComboBox()
        self.timezone.addItems(["Europe/Paris", "Europe/London", "Europe/Berlin", "UTC"])
        current_tz = settings.get('timezone', 'Europe/Paris')
        self.timezone.setCurrentText(current_tz)
        layout.addWidget(self.timezone)
        
        # Bouton Sauvegarder
        layout.addSpacing(20)
        btn_save = QPushButton("✓ Sauvegarder")
        btn_save.clicked.connect(self.save_general_settings)
        layout.addWidget(btn_save)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def save_general_settings(self):
        """Sauvegarder les paramètres généraux"""
        success, message = SettingsController.update_general_settings(
            self.currency.text(),
            self.tva.value(),
            self.invoice_prefix.text(),
            self.date_format.currentText(),
            self.timezone.currentText()
        )
        
        if success:
            QMessageBox.information(self, "Succès", message)
        else:
            QMessageBox.warning(self, "Erreur", message)


class UserFormDialog(QDialog):
    """Dialogue de création d'utilisateur"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvel Utilisateur")
        self.setGeometry(200, 200, 400, 350)
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Nom d'utilisateur *"))
        self.username = QLineEdit()
        layout.addWidget(self.username)
        
        layout.addWidget(QLabel("Email *"))
        self.email = QLineEdit()
        layout.addWidget(self.email)
        
        layout.addWidget(QLabel("Mot de passe *"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)
        
        layout.addWidget(QLabel("Rôle"))
        self.role = QComboBox()
        self.role.addItems(["vendeur", "manager", "admin"])
        layout.addWidget(self.role)
        
        buttons_layout = QHBoxLayout()
        
        btn_save = QPushButton("✓ Créer")
        btn_save.clicked.connect(self.save_user)
        
        btn_cancel = QPushButton("✗ Annuler")
        btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addWidget(btn_save)
        buttons_layout.addWidget(btn_cancel)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def save_user(self):
        """Créer l'utilisateur"""
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text()
        role = self.role.currentText()
        
        if not username or not email or not password:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires")
            return
        
        success, message = SettingsController.create_user(username, email, password, role)
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)


class ResetPasswordDialog(QDialog):
    """Dialogue de réinitialisation de mot de passe"""
    def __init__(self, user_id, username, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle(f"Réinitialiser mot de passe - {username}")
        self.setGeometry(200, 200, 400, 200)
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Nouveau mot de passe *"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_password)
        
        layout.addWidget(QLabel("Confirmer mot de passe *"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password)
        
        buttons_layout = QHBoxLayout()
        
        btn_save = QPushButton("✓ Réinitialiser")
        btn_save.clicked.connect(self.reset_password)
        
        btn_cancel = QPushButton("✗ Annuler")
        btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addWidget(btn_save)
        buttons_layout.addWidget(btn_cancel)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def reset_password(self):
        """Réinitialiser le mot de passe"""
        password = self.new_password.text()
        confirm = self.confirm_password.text()
        
        if not password or not confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe sont obligatoires")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Erreur", "Le mot de passe doit contenir au moins 6 caractères")
            return
        
        success, message = SettingsController.reset_password(self.user_id, password)
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)
