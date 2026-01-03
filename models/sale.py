from database.connection import get_connection
from datetime import datetime
import random
import string


class Sale:

    @staticmethod
    def generate_invoice_number():
        """Générer un numéro de facture unique"""
        conn = get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        # Numéro au format: YYYY/MMMM/NNNNNN
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        
        # Chercher le dernier numéro du mois
        sql = """
        SELECT numero_facture FROM ventes 
        WHERE numero_facture LIKE %s
        ORDER BY numero_facture DESC LIMIT 1
        """
        pattern = f"{year}/{month:02d}/%"
        cursor.execute(sql, (pattern,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            last_num = result[0].split('/')[-1]
            next_num = str(int(last_num) + 1).zfill(6)
        else:
            next_num = "000001"
        
        return f"{year}/{month:02d}/{next_num}"

    @staticmethod
    def create(client_id, user_id, articles, tva=20, remise=0, remise_type='montant', notes=""):
        """Créer une nouvelle vente
        
        articles = [
            {'produit_id': 1, 'quantite': 2, 'prix_unitaire': 100},
            ...
        ]
        """
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        
        try:
            # Générer numéro de facture
            numero_facture = Sale.generate_invoice_number()
            if not numero_facture:
                return False, "Erreur génération numéro facture"
            
            # Calculer le montant total
            montant_ht = sum(art['quantite'] * art['prix_unitaire'] for art in articles)
            
            # Appliquer remise
            if remise_type == 'pourcentage':
                montant_remise = montant_ht * (remise / 100)
            else:
                montant_remise = remise
            
            montant_ht = montant_ht - montant_remise
            montant_ttc = montant_ht * (1 + tva / 100)
            
            # Créer la vente
            vente_sql = """
            INSERT INTO ventes (numero_facture, client_id, user_id, montant_total, statut, notes)
            VALUES (%s, %s, %s, %s, 'en_cours', %s)
            """
            cursor.execute(vente_sql, (numero_facture, client_id, user_id, montant_ttc, notes))
            vente_id = cursor.lastrowid
            
            # Ajouter les articles
            detail_sql = """
            INSERT INTO ventes_details (vente_id, produit_id, quantite, prix_unitaire)
            VALUES (%s, %s, %s, %s)
            """
            
            for article in articles:
                cursor.execute(detail_sql, (
                    vente_id, 
                    article['produit_id'],
                    article['quantite'],
                    article['prix_unitaire']
                ))
            
            conn.commit()
            return True, f"Vente créée (Facture: {numero_facture})"
        
        except Exception as e:
            conn.rollback()
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_by_id(vente_id):
        """Récupérer une vente par ID"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        sql = "SELECT * FROM ventes WHERE id = %s"
        cursor.execute(sql, (vente_id,))
        vente = cursor.fetchone()
        conn.close()

        return vente

    @staticmethod
    def get_by_numero(numero_facture):
        """Récupérer une vente par numéro facture"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        sql = "SELECT * FROM ventes WHERE numero_facture = %s"
        cursor.execute(sql, (numero_facture,))
        vente = cursor.fetchone()
        conn.close()

        return vente

    @staticmethod
    def get_all(limit=100, offset=0):
        """Récupérer toutes les ventes"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT v.*, CONCAT(c.nom, ' ', c.prenom) as client_nom, u.username as vendeur
        FROM ventes v
        LEFT JOIN clients c ON v.client_id = c.id
        LEFT JOIN users u ON v.user_id = u.id
        ORDER BY v.date_vente DESC
        LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (limit, offset))
        ventes = cursor.fetchall()
        conn.close()

        return ventes

    @staticmethod
    def get_details(vente_id):
        """Récupérer les détails d'une vente"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT vd.*, p.nom as produit_nom
        FROM ventes_details vd
        LEFT JOIN produits p ON vd.produit_id = p.id
        WHERE vd.vente_id = %s
        """
        cursor.execute(sql, (vente_id,))
        details = cursor.fetchall()
        conn.close()

        return details

    @staticmethod
    def update_status(vente_id, statut):
        """Mettre à jour le statut d'une vente"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        sql = "UPDATE ventes SET statut = %s WHERE id = %s"

        try:
            cursor.execute(sql, (statut, vente_id))
            conn.commit()
            return True, f"Statut mis à jour : {statut}"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def record_payment(vente_id, montant_paye):
        """Enregistrer un paiement"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        
        try:
            # Récupérer la vente
            select_sql = "SELECT montant_total, montant_paye FROM ventes WHERE id = %s"
            cursor.execute(select_sql, (vente_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Vente non trouvée"
            
            # Convertir en float pour éviter les erreurs Decimal + float
            montant_total = float(result['montant_total'])
            montant_deja_paye = float(result['montant_paye'])
            montant_paye = float(montant_paye)
            
            nouveau_paiement = montant_deja_paye + montant_paye
            
            if nouveau_paiement > montant_total:
                conn.close()
                return False, f"Paiement supérieur au montant : {montant_total}"
            
            # Déterminer le nouveau statut
            if nouveau_paiement >= montant_total:
                statut = 'payee'
            elif nouveau_paiement > 0:
                statut = 'partielle'
            else:
                statut = 'en_cours'
            
            # Mettre à jour le paiement
            update_sql = """
            UPDATE ventes 
            SET montant_paye = %s, statut = %s
            WHERE id = %s
            """
            cursor.execute(update_sql, (nouveau_paiement, statut, vente_id))
            
            # Enregistrer dans l'historique des paiements
            payment_sql = """
            INSERT INTO paiements (vente_id, montant, date_paiement)
            VALUES (%s, %s, %s)
            """
            cursor.execute(payment_sql, (vente_id, montant_paye, datetime.now()))
            
            conn.commit()
            montant_restant = montant_total - nouveau_paiement
            return True, f"Paiement enregistré : {montant_paye:.2f}€ (Montant restant: {montant_restant:.2f}€)"
        
        except Exception as e:
            conn.rollback()
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_payment_history(vente_id):
        """Récupérer l'historique des paiements d'une vente"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT * FROM paiements
        WHERE vente_id = %s
        ORDER BY date_paiement DESC
        """
        
        try:
            cursor.execute(sql, (vente_id,))
            paiements = cursor.fetchall()
        except Exception as e:
            print(f"Erreur paiements : {e}")
            paiements = []
        finally:
            conn.close()

        return paiements

    @staticmethod
    def get_unpaid_sales():
        """Récupérer les ventes impayées"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT v.*, CONCAT(c.nom, ' ', c.prenom) as client_nom
        FROM ventes v
        LEFT JOIN clients c ON v.client_id = c.id
        WHERE v.statut IN ('en_cours', 'partielle')
        ORDER BY v.date_vente DESC
        """

        try:
            cursor.execute(sql)
            ventes = cursor.fetchall()
        except Exception as e:
            print(f"Erreur ventes impayées : {e}")
            ventes = []
        finally:
            conn.close()

        return ventes

    @staticmethod
    def search(search_term, search_type='numero'):
        """Rechercher une vente"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        
        if search_type == 'numero':
            sql = """
            SELECT v.*, CONCAT(c.nom, ' ', c.prenom) as client_nom
            FROM ventes v
            LEFT JOIN clients c ON v.client_id = c.id
            WHERE v.numero_facture LIKE %s
            ORDER BY v.date_vente DESC
            """
        elif search_type == 'client':
            sql = """
            SELECT v.*, CONCAT(c.nom, ' ', c.prenom) as client_nom
            FROM ventes v
            LEFT JOIN clients c ON v.client_id = c.id
            WHERE c.nom LIKE %s OR c.prenom LIKE %s
            ORDER BY v.date_vente DESC
            """
        else:
            return []
        
        try:
            if search_type == 'client':
                pattern = f"%{search_term}%"
                cursor.execute(sql, (pattern, pattern))
            else:
                pattern = f"%{search_term}%"
                cursor.execute(sql, (pattern,))
            
            ventes = cursor.fetchall()
        except Exception as e:
            print(f"Erreur recherche : {e}")
            ventes = []
        finally:
            conn.close()

        return ventes

    @staticmethod
    def delete(vente_id):
        """Supprimer une vente"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()

        try:
            # Supprimer les détails
            delete_details_sql = "DELETE FROM ventes_details WHERE vente_id = %s"
            cursor.execute(delete_details_sql, (vente_id,))
            
            # Supprimer les paiements
            delete_payments_sql = "DELETE FROM paiements WHERE vente_id = %s"
            cursor.execute(delete_payments_sql, (vente_id,))
            
            # Supprimer la vente
            delete_vente_sql = "DELETE FROM ventes WHERE id = %s"
            cursor.execute(delete_vente_sql, (vente_id,))
            
            conn.commit()
            return True, "Vente supprimée"
        except Exception as e:
            conn.rollback()
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_statistics():
        """Récupérer les statistiques des ventes"""
        conn = get_connection()
        if not conn:
            return {}

        cursor = conn.cursor()
        sql = """
        SELECT 
            COUNT(*) as total_ventes,
            SUM(montant_total) as ca_total,
            AVG(montant_total) as ticket_moyen,
            SUM(CASE WHEN statut = 'payee' THEN montant_total ELSE 0 END) as ca_paye,
            SUM(CASE WHEN statut IN ('en_cours', 'partielle') THEN (montant_total - montant_paye) ELSE 0 END) as montant_reste_total
        FROM ventes
        WHERE DATE(date_vente) = CURDATE()
        """

        try:
            cursor.execute(sql)
            stats = cursor.fetchone()
            conn.close()
            
            # Convertir tous les Decimal en float pour éviter les erreurs de type
            return {
                'total_ventes': int(stats['total_ventes'] or 0),
                'ca_total': float(stats['ca_total'] or 0),
                'ticket_moyen': float(stats['ticket_moyen'] or 0),
                'ca_paye': float(stats['ca_paye'] or 0),
                'montant_reste': float(stats['montant_reste_total'] or 0)
            }
        except Exception as e:
            print(f"Erreur statistiques : {e}")
            return {
                'total_ventes': 0,
                'ca_total': 0.0,
                'ticket_moyen': 0.0,
                'ca_paye': 0.0,
                'montant_reste': 0.0
            }
