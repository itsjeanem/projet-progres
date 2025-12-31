from models.statistics import Statistics


class StatisticsController:

    @staticmethod
    def get_ca_by_period(period='today'):
        """Récupérer le CA par période"""
        return Statistics.get_ca_by_period(period)

    @staticmethod
    def get_sales_count(period='today'):
        """Récupérer le nombre de ventes par période"""
        return Statistics.get_sales_count(period)

    @staticmethod
    def get_top_products(limit=5):
        """Récupérer les top produits"""
        return Statistics.get_top_products(limit)

    @staticmethod
    def get_top_clients(limit=5):
        """Récupérer les top clients"""
        return Statistics.get_top_clients(limit)

    @staticmethod
    def get_low_stock_products():
        """Récupérer les produits en rupture"""
        return Statistics.get_low_stock_products()

    @staticmethod
    def get_ca_by_category(period='month'):
        """Récupérer le CA par catégorie"""
        return Statistics.get_ca_by_category(period)

    @staticmethod
    def get_ca_evolution(days=30):
        """Récupérer l'évolution du CA"""
        return Statistics.get_ca_evolution(days)

    @staticmethod
    def get_payment_status():
        """Récupérer les statuts de paiement"""
        return Statistics.get_payment_status()

    @staticmethod
    def get_dashboard_summary():
        """Récupérer le résumé complet"""
        return Statistics.get_dashboard_summary()
