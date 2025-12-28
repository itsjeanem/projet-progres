from database.connection import get_connection
from datetime import datetime


class Client:

    @staticmethod
    def create(nom, prenom, telephone=None, email=None, adresse=None, ville=None, code_postal=None):
        """Créer un nouveau client"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion à la base de données"

        cursor = conn.cursor()
        sql = """
        INSERT INTO clients (nom, prenom, telephone, email, adresse, ville, code_postal)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(sql, (nom, prenom, telephone, email, adresse, ville, code_postal))
            conn.commit()
            return True, "Client créé avec succès"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_by_id(client_id):
        """Récupérer un client par ID"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        sql = "SELECT * FROM clients WHERE id = %s"
        cursor.execute(sql, (client_id,))
        client = cursor.fetchone()
        conn.close()

        return client

    @staticmethod
    def get_all():
        """Récupérer tous les clients"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = "SELECT * FROM clients ORDER BY nom, prenom"
        cursor.execute(sql)
        clients = cursor.fetchall()
        conn.close()

        return clients

    @staticmethod
    def update(client_id, nom, prenom, telephone=None, email=None, adresse=None, ville=None, code_postal=None):
        """Modifier un client"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion à la base de données"

        cursor = conn.cursor()
        sql = """
        UPDATE clients 
        SET nom = %s, prenom = %s, telephone = %s, email = %s, 
            adresse = %s, ville = %s, code_postal = %s
        WHERE id = %s
        """

        try:
            cursor.execute(sql, (nom, prenom, telephone, email, adresse, ville, code_postal, client_id))
            conn.commit()
            return True, "Client modifié avec succès"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def delete(client_id):
        """Supprimer un client (vérifier les ventes associées)"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion à la base de données"

        cursor = conn.cursor()

        # Vérifier les ventes associées
        check_sql = "SELECT COUNT(*) as count FROM ventes WHERE client_id = %s"
        cursor.execute(check_sql, (client_id,))
        result = cursor.fetchone()

        if result and result['count'] > 0:
            conn.close()
            return False, f"Impossible de supprimer : {result['count']} vente(s) associée(s)"

        # Supprimer le client
        delete_sql = "DELETE FROM clients WHERE id = %s"

        try:
            cursor.execute(delete_sql, (client_id,))
            conn.commit()
            return True, "Client supprimé avec succès"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def search(search_term):
        """Recherche multicritère (nom, prénom, téléphone, email)"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT * FROM clients 
        WHERE nom LIKE %s OR prenom LIKE %s OR telephone LIKE %s OR email LIKE %s
        ORDER BY nom, prenom
        """

        search_pattern = f"%{search_term}%"

        try:
            cursor.execute(sql, (search_pattern, search_pattern, search_pattern, search_pattern))
            clients = cursor.fetchall()
        except Exception as e:
            print(f"Erreur recherche : {e}")
            clients = []
        finally:
            conn.close()

        return clients

    @staticmethod
    def get_purchase_history(client_id):
        """Récupérer l'historique des achats d'un client"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT v.id, v.numero_facture, v.date_vente, v.montant_total, v.statut
        FROM ventes v
        WHERE v.client_id = %s
        ORDER BY v.date_vente DESC
        """

        try:
            cursor.execute(sql, (client_id,))
            history = cursor.fetchall()
        except Exception as e:
            print(f"Erreur historique : {e}")
            history = []
        finally:
            conn.close()

        return history

    @staticmethod
    def get_statistics(client_id):
        """Récupérer les statistiques d'un client"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        sql = """
        SELECT 
            COUNT(id) as nombre_achats,
            SUM(montant_total) as ca_total,
            MAX(date_vente) as derniere_visite,
            AVG(montant_total) as montant_moyen
        FROM ventes
        WHERE client_id = %s
        """

        try:
            cursor.execute(sql, (client_id,))
            stats = cursor.fetchone()
        except Exception as e:
            print(f"Erreur statistiques : {e}")
            stats = None
        finally:
            conn.close()

        return stats
