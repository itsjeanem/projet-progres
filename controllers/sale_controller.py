from models.sale import Sale


class SaleController:

    @staticmethod
    def create_sale(client_id, user_id, articles, tva=20, remise=0, remise_type='montant', notes=""):
        """Créer une vente"""
        return Sale.create(client_id, user_id, articles, tva, remise, remise_type, notes)

    @staticmethod
    def get_sale(vente_id):
        """Récupérer une vente"""
        return Sale.get_by_id(vente_id)

    @staticmethod
    def get_sale_by_numero(numero_facture):
        """Récupérer une vente par numéro"""
        return Sale.get_by_numero(numero_facture)

    @staticmethod
    def get_all_sales(limit=100, offset=0):
        """Récupérer toutes les ventes"""
        return Sale.get_all(limit, offset)

    @staticmethod
    def get_sale_details(vente_id):
        """Récupérer les détails d'une vente"""
        return Sale.get_details(vente_id)

    @staticmethod
    def update_sale_status(vente_id, statut):
        """Mettre à jour le statut"""
        return Sale.update_status(vente_id, statut)

    @staticmethod
    def record_payment(vente_id, montant_paye):
        """Enregistrer un paiement"""
        return Sale.record_payment(vente_id, montant_paye)

    @staticmethod
    def get_payment_history(vente_id):
        """Récupérer l'historique des paiements"""
        return Sale.get_payment_history(vente_id)

    @staticmethod
    def get_unpaid_sales():
        """Récupérer les ventes impayées"""
        return Sale.get_unpaid_sales()

    @staticmethod
    def search_sales(search_term, search_type='numero'):
        """Rechercher une vente"""
        return Sale.search(search_term, search_type)

    @staticmethod
    def delete_sale(vente_id):
        """Supprimer une vente"""
        return Sale.delete(vente_id)

    @staticmethod
    def get_sales_statistics():
        """Récupérer les statistiques"""
        return Sale.get_statistics()

    @staticmethod
    def generate_invoice_number():
        """Générer un numéro de facture"""
        return Sale.generate_invoice_number()

    @staticmethod
    def export_sale_to_pdf(vente_id, output_path, company_info=None):
        """Exporter une vente en PDF"""
        return Sale.export_to_pdf(vente_id, output_path, company_info)
