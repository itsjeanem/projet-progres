from database.connection import get_connection
from datetime import datetime
import bcrypt


class Settings:

    # ==================== Company Configuration ====================
    
    @staticmethod
    def get_company_info():
        """Récupérer les informations entreprise"""
        conn = get_connection()
        if not conn:
            return {}

        cursor = conn.cursor()
        keys = ['company_name', 'company_address', 'company_phone', 'company_email', 'company_website', 'company_logo']
        
        try:
            result = {}
            for key in keys:
                sql = "SELECT valeur FROM parametres WHERE cle = %s"
                cursor.execute(sql, (key,))
                row = cursor.fetchone()
                result[key] = row['valeur'] if row else ""
            
            conn.close()
            return result
        except Exception as e:
            print(f"Erreur récupération infos : {e}")
            conn.close()
            return {}

    @staticmethod
    def update_company_info(company_name, address, phone, email, website, logo_path=None):
        """Mettre à jour les informations entreprise"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        
        try:
            updates = [
                ('company_name', company_name),
                ('company_address', address),
                ('company_phone', phone),
                ('company_email', email),
                ('company_website', website)
            ]
            
            if logo_path:
                updates.append(('company_logo', logo_path))
            
            for key, value in updates:
                # Vérifier si la clé existe
                check_sql = "SELECT id FROM parametres WHERE cle = %s"
                cursor.execute(check_sql, (key,))
                exists = cursor.fetchone()
                
                if exists:
                    update_sql = "UPDATE parametres SET valeur = %s WHERE cle = %s"
                    cursor.execute(update_sql, (value, key))
                else:
                    insert_sql = """
                    INSERT INTO parametres (cle, valeur, description)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(insert_sql, (key, value, f"Configuration {key}"))
            
            conn.commit()
            conn.close()
            return True, "Entreprise mise à jour"
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Erreur : {str(e)}"

    # ==================== User Management ====================
    
    @staticmethod
    def get_all_users():
        """Récupérer tous les utilisateurs"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT id, username, email, role, is_active, created_at
        FROM users
        ORDER BY created_at DESC
        """
        
        try:
            cursor.execute(sql)
            users = cursor.fetchall()
            conn.close()
            return users
        except Exception as e:
            print(f"Erreur utilisateurs : {e}")
            conn.close()
            return []

    @staticmethod
    def create_user(username, email, password, role='vendeur'):
        """Créer un nouvel utilisateur"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        
        try:
            # Vérifier l'unicité
            check_sql = "SELECT id FROM users WHERE username = %s OR email = %s"
            cursor.execute(check_sql, (username, email))
            if cursor.fetchone():
                conn.close()
                return False, "Utilisateur ou email déjà existant"
            
            # Hasher le mot de passe
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Créer l'utilisateur
            insert_sql = """
            INSERT INTO users (username, email, password_hash, role, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
            """
            cursor.execute(insert_sql, (username, email, password_hash, role))
            conn.commit()
            conn.close()
            return True, f"Utilisateur {username} créé"
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def update_user(user_id, username=None, email=None, role=None, is_active=None):
        """Mettre à jour un utilisateur"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if username is not None:
                updates.append("username = %s")
                params.append(username)
            if email is not None:
                updates.append("email = %s")
                params.append(email)
            if role is not None:
                updates.append("role = %s")
                params.append(role)
            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)
            
            if not updates:
                conn.close()
                return False, "Aucun champ à mettre à jour"
            
            params.append(user_id)
            update_sql = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(update_sql, params)
            conn.commit()
            conn.close()
            return True, "Utilisateur mis à jour"
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def reset_password(user_id, new_password):
        """Réinitialiser le mot de passe d'un utilisateur"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        
        try:
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            update_sql = "UPDATE users SET password_hash = %s WHERE id = %s"
            cursor.execute(update_sql, (password_hash, user_id))
            conn.commit()
            conn.close()
            return True, "Mot de passe réinitialisé"
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def deactivate_user(user_id):
        """Désactiver un utilisateur"""
        return Settings.update_user(user_id, is_active=False)

    @staticmethod
    def delete_user(user_id):
        """Supprimer un utilisateur"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        
        try:
            delete_sql = "DELETE FROM users WHERE id = %s"
            cursor.execute(delete_sql, (user_id,))
            conn.commit()
            conn.close()
            return True, "Utilisateur supprimé"
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Erreur : {str(e)}"

    # ==================== General Settings ====================
    
    @staticmethod
    def get_general_settings():
        """Récupérer les paramètres généraux"""
        conn = get_connection()
        if not conn:
            return {}

        cursor = conn.cursor()
        keys = ['currency', 'tva_default', 'invoice_prefix', 'date_format', 'timezone']
        
        try:
            result = {}
            for key in keys:
                sql = "SELECT valeur FROM parametres WHERE cle = %s"
                cursor.execute(sql, (key,))
                row = cursor.fetchone()
                result[key] = row['valeur'] if row else ""
            
            conn.close()
            return result
        except Exception as e:
            print(f"Erreur paramètres : {e}")
            conn.close()
            return {}

    @staticmethod
    def update_general_settings(currency='XOF', tva=20, invoice_prefix='FAC', date_format='DD/MM/YYYY', timezone='Europe/Paris'):
        """Mettre à jour les paramètres généraux"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        
        try:
            settings = [
                ('currency', currency),
                ('tva_default', str(tva)),
                ('invoice_prefix', invoice_prefix),
                ('date_format', date_format),
                ('timezone', timezone)
            ]
            
            for key, value in settings:
                check_sql = "SELECT id FROM parametres WHERE cle = %s"
                cursor.execute(check_sql, (key,))
                exists = cursor.fetchone()
                
                if exists:
                    update_sql = "UPDATE parametres SET valeur = %s WHERE cle = %s"
                    cursor.execute(update_sql, (value, key))
                else:
                    insert_sql = """
                    INSERT INTO parametres (cle, valeur, description)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(insert_sql, (key, value, f"Configuration {key}"))
            
            conn.commit()
            conn.close()
            return True, "Paramètres mis à jour"
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Erreur : {str(e)}"

    @staticmethod
    def get_setting(key):
        """Récupérer un paramètre spécifique"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        
        try:
            sql = "SELECT valeur FROM parametres WHERE cle = %s"
            cursor.execute(sql, (key,))
            row = cursor.fetchone()
            conn.close()
            return row['valeur'] if row else None
        except Exception as e:
            print(f"Erreur paramètre : {e}")
            conn.close()
            return None
