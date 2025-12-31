from database.connection import get_connection
from datetime import datetime, timedelta


class Statistics:

    @staticmethod
    def get_ca_by_period(period='today'):
        """Récupérer le chiffre d'affaires par période
        
        period: 'today', 'week', 'month'
        """
        conn = get_connection()
        if not conn:
            return 0

        cursor = conn.cursor()
        
        if period == 'today':
            sql = "SELECT COALESCE(SUM(montant_total), 0) as ca FROM ventes WHERE DATE(date_vente) = CURDATE()"
        elif period == 'week':
            sql = """
            SELECT COALESCE(SUM(montant_total), 0) as ca FROM ventes 
            WHERE YEARWEEK(date_vente) = YEARWEEK(NOW())
            """
        elif period == 'month':
            sql = """
            SELECT COALESCE(SUM(montant_total), 0) as ca FROM ventes 
            WHERE YEAR(date_vente) = YEAR(NOW())
            AND MONTH(date_vente) = MONTH(NOW())
            """
        else:
            return 0
        
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            conn.close()
            return float(result['ca'] or 0)
        except Exception as e:
            print(f"Erreur CA : {e}")
            conn.close()
            return 0

    @staticmethod
    def get_sales_count(period='today'):
        """Récupérer le nombre de ventes par période"""
        conn = get_connection()
        if not conn:
            return 0

        cursor = conn.cursor()
        
        if period == 'today':
            sql = "SELECT COUNT(*) as count FROM ventes WHERE DATE(date_vente) = CURDATE()"
        elif period == 'week':
            sql = """
            SELECT COUNT(*) as count FROM ventes 
            WHERE YEARWEEK(date_vente) = YEARWEEK(NOW())
            """
        elif period == 'month':
            sql = """
            SELECT COUNT(*) as count FROM ventes 
            WHERE YEAR(date_vente) = YEAR(NOW())
            AND MONTH(date_vente) = MONTH(NOW())
            """
        else:
            return 0
        
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            conn.close()
            return result['count'] or 0
        except Exception as e:
            print(f"Erreur count : {e}")
            conn.close()
            return 0

    @staticmethod
    def get_top_products(limit=5):
        """Récupérer les top produits vendus du mois"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT p.nom, p.category_id, c.nom as categorie, SUM(vd.quantite) as quantite_vendue, 
               SUM(vd.sous_total) as ca
        FROM ventes_details vd
        JOIN produits p ON vd.produit_id = p.id
        LEFT JOIN categories c ON p.category_id = c.id
        JOIN ventes v ON vd.vente_id = v.id
        WHERE YEAR(v.date_vente) = YEAR(NOW())
        AND MONTH(v.date_vente) = MONTH(NOW())
        GROUP BY p.id, p.nom, c.nom
        ORDER BY quantite_vendue DESC
        LIMIT %s
        """
        
        try:
            cursor.execute(sql, (limit,))
            products = cursor.fetchall()
            conn.close()
            return products
        except Exception as e:
            print(f"Erreur top produits : {e}")
            conn.close()
            return []

    @staticmethod
    def get_top_clients(limit=5):
        """Récupérer les top clients du mois"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT CONCAT(c.nom, ' ', c.prenom) as client_nom, 
               COUNT(v.id) as nombre_achats,
               SUM(v.montant_total) as ca_total
        FROM ventes v
        JOIN clients c ON v.client_id = c.id
        WHERE YEAR(v.date_vente) = YEAR(NOW())
        AND MONTH(v.date_vente) = MONTH(NOW())
        GROUP BY c.id, c.nom, c.prenom
        ORDER BY ca_total DESC
        LIMIT %s
        """
        
        try:
            cursor.execute(sql, (limit,))
            clients = cursor.fetchall()
            conn.close()
            return clients
        except Exception as e:
            print(f"Erreur top clients : {e}")
            conn.close()
            return []

    @staticmethod
    def get_low_stock_products():
        """Récupérer les produits en rupture de stock critique"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT p.id, p.nom, c.nom as categorie, p.stock_actuel, p.stock_min, 
               p.prix_vente, (p.stock_min - p.stock_actuel) as deficit
        FROM produits p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.stock_actuel <= p.stock_min
        ORDER BY deficit DESC
        LIMIT 10
        """
        
        try:
            cursor.execute(sql)
            products = cursor.fetchall()
            conn.close()
            return products
        except Exception as e:
            print(f"Erreur stocks bas : {e}")
            conn.close()
            return []

    @staticmethod
    def get_ca_by_category(period='month'):
        """Récupérer le CA par catégorie"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        
        if period == 'today':
            date_filter = "DATE(v.date_vente) = CURDATE()"
        elif period == 'week':
            date_filter = "YEARWEEK(v.date_vente) = YEARWEEK(NOW())"
        elif period == 'month':
            date_filter = """YEAR(v.date_vente) = YEAR(NOW())
            AND MONTH(v.date_vente) = MONTH(NOW())"""
        else:
            return []
        
        sql = f"""
        SELECT c.nom as categorie, SUM(vd.sous_total) as ca, COUNT(vd.id) as nombre_articles
        FROM ventes_details vd
        JOIN produits p ON vd.produit_id = p.id
        LEFT JOIN categories c ON p.category_id = c.id
        JOIN ventes v ON vd.vente_id = v.id
        WHERE {date_filter}
        GROUP BY c.id, c.nom
        ORDER BY ca DESC
        """
        
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            print(f"Erreur CA catégorie : {e}")
            conn.close()
            return []

    @staticmethod
    def get_ca_evolution(days=30):
        """Récupérer l'évolution du CA sur les 30 derniers jours"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT DATE(date_vente) as date, SUM(montant_total) as ca, COUNT(*) as nombre_ventes
        FROM ventes
        WHERE date_vente >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY DATE(date_vente)
        ORDER BY date ASC
        """
        
        try:
            cursor.execute(sql, (days,))
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            print(f"Erreur évolution : {e}")
            conn.close()
            return []

    @staticmethod
    def get_payment_status():
        """Récupérer les statuts de paiement"""
        conn = get_connection()
        if not conn:
            return {}

        cursor = conn.cursor()
        sql = """
        SELECT 
            statut,
            COUNT(*) as nombre,
            SUM(montant_total) as montant
        FROM ventes
        WHERE DATE(date_vente) >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY statut
        """
        
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            conn.close()
            
            status_data = {}
            for row in results:
                status = row['statut']
                status_data[status] = {
                    'nombre': row['nombre'],
                    'montant': float(row['montant'] or 0)
                }
            
            return status_data
        except Exception as e:
            print(f"Erreur paiements : {e}")
            conn.close()
            return {}

    @staticmethod
    def get_dashboard_summary():
        """Récupérer un résumé complet pour le dashboard"""
        return {
            'ca_today': Statistics.get_ca_by_period('today'),
            'ca_week': Statistics.get_ca_by_period('week'),
            'ca_month': Statistics.get_ca_by_period('month'),
            'sales_today': Statistics.get_sales_count('today'),
            'sales_week': Statistics.get_sales_count('week'),
            'sales_month': Statistics.get_sales_count('month'),
            'top_products': Statistics.get_top_products(5),
            'top_clients': Statistics.get_top_clients(5),
            'low_stock': Statistics.get_low_stock_products(),
            'ca_by_category': Statistics.get_ca_by_category('month'),
            'ca_evolution': Statistics.get_ca_evolution(30),
            'payment_status': Statistics.get_payment_status()
        }
