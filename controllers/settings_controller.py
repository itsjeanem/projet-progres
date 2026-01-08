from models.settings import Settings


class SettingsController:

    # ==================== Company Configuration ====================
    
    @staticmethod
    def get_company_info():
        """Récupérer les infos entreprise"""
        return Settings.get_company_info()

    @staticmethod
    def update_company_info(company_name, address, phone, email, website, logo_path=None):
        """Mettre à jour les infos entreprise"""
        return Settings.update_company_info(company_name, address, phone, email, website, logo_path)

    # ==================== User Management ====================
    
    @staticmethod
    def get_all_users():
        """Récupérer tous les utilisateurs"""
        return Settings.get_all_users()

    @staticmethod
    def create_user(username, email, password, role='vendeur'):
        """Créer un utilisateur"""
        return Settings.create_user(username, email, password, role)

    @staticmethod
    def update_user(user_id, username=None, email=None, role=None, is_active=None):
        """Mettre à jour un utilisateur"""
        return Settings.update_user(user_id, username, email, role, is_active)

    @staticmethod
    def reset_password(user_id, new_password):
        """Réinitialiser le mot de passe"""
        return Settings.reset_password(user_id, new_password)

    @staticmethod
    def deactivate_user(user_id):
        """Désactiver un utilisateur"""
        return Settings.deactivate_user(user_id)

    @staticmethod
    def delete_user(user_id):
        """Supprimer un utilisateur"""
        return Settings.delete_user(user_id)

    # ==================== General Settings ====================
    
    @staticmethod
    def get_general_settings():
        """Récupérer les paramètres généraux"""
        return Settings.get_general_settings()

    @staticmethod
    def update_general_settings(currency='XOF', tva=18, invoice_prefix='FAC', date_format='DD/MM/YYYY', timezone='Europe/Paris'):
        """Mettre à jour les paramètres généraux"""
        return Settings.update_general_settings(currency, tva, invoice_prefix, date_format, timezone)

    @staticmethod
    def get_setting(key):
        """Récupérer un paramètre spécifique"""
        return Settings.get_setting(key)
