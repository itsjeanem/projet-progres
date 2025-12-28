from models.client import Client


class ClientController:

    @staticmethod
    def create_client(nom, prenom, telephone=None, email=None, adresse=None, ville=None, code_postal=None):
        """Contrôleur pour créer un client"""
        return Client.create(nom, prenom, telephone, email, adresse, ville, code_postal)

    @staticmethod
    def get_all_clients():
        """Récupérer tous les clients"""
        return Client.get_all()

    @staticmethod
    def get_client(client_id):
        """Récupérer un client par ID"""
        return Client.get_by_id(client_id)

    @staticmethod
    def update_client(client_id, nom, prenom, telephone=None, email=None, adresse=None, ville=None, code_postal=None):
        """Contrôleur pour modifier un client"""
        return Client.update(client_id, nom, prenom, telephone, email, adresse, ville, code_postal)

    @staticmethod
    def delete_client(client_id):
        """Contrôleur pour supprimer un client"""
        return Client.delete(client_id)

    @staticmethod
    def search_clients(search_term):
        """Recherche de clients"""
        if not search_term or len(search_term.strip()) < 1:
            return Client.get_all()
        return Client.search(search_term)

    @staticmethod
    def get_client_history(client_id):
        """Récupérer l'historique des achats"""
        return Client.get_purchase_history(client_id)

    @staticmethod
    def get_client_stats(client_id):
        """Récupérer les statistiques d'un client"""
        return Client.get_statistics(client_id)
