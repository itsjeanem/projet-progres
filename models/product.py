from database.connection import get_connection
from datetime import datetime


class Product:

    @staticmethod
    def create(category_id, nom, description, prix_achat, prix_vente, stock_min, stock_actuel=0):
        """Créer un nouveau produit"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        sql = """
        INSERT INTO produits (category_id, nom, description, prix_achat, prix_vente, stock_min, stock_actuel)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(sql, (category_id, nom, description, prix_achat, prix_vente, stock_min, stock_actuel))
            conn.commit()
            product_id = cursor.lastrowid
            
            # Enregistrer le mouvement de stock initial
            if stock_actuel > 0:
                Product.record_stock_movement(product_id, stock_actuel, "entree", None, "Création stock initial")
            
            return True, f"Produit créé avec succès"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_by_id(product_id):
        """Récupérer un produit par ID"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        sql = "SELECT * FROM produits WHERE id = %s"
        cursor.execute(sql, (product_id,))
        product = cursor.fetchone()
        conn.close()

        return product

    @staticmethod
    def get_all():
        """Récupérer tous les produits"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT p.*, c.nom as categorie
        FROM produits p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY c.nom, p.nom
        """
        cursor.execute(sql)
        products = cursor.fetchall()
        conn.close()

        return products

    @staticmethod
    def get_by_category(category_id):
        """Récupérer les produits d'une catégorie"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = "SELECT * FROM produits WHERE category_id = %s ORDER BY nom"
        cursor.execute(sql, (category_id,))
        products = cursor.fetchall()
        conn.close()

        return products

    @staticmethod
    def update(product_id, category_id, nom, description, prix_achat, prix_vente, stock_min):
        """Modifier un produit"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        sql = """
        UPDATE produits 
        SET category_id = %s, nom = %s, description = %s, 
            prix_achat = %s, prix_vente = %s, stock_min = %s
        WHERE id = %s
        """

        try:
            cursor.execute(sql, (category_id, nom, description, prix_achat, prix_vente, stock_min, product_id))
            conn.commit()
            return True, "Produit modifié"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def delete(product_id):
        """Supprimer un produit (vérifier les ventes)"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()

        # Vérifier les ventes associées
        check_sql = "SELECT COUNT(*) as count FROM ventes_details WHERE produit_id = %s"
        cursor.execute(check_sql, (product_id,))
        result = cursor.fetchone()

        if result and result['count'] > 0:
            conn.close()
            return False, f"Impossible : {result['count']} vente(s) associée(s)"

        # Supprimer le produit
        delete_sql = "DELETE FROM produits WHERE id = %s"

        try:
            cursor.execute(delete_sql, (product_id,))
            conn.commit()
            return True, "Produit supprimé"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def update_stock(product_id, quantite, type_mouvement, user_id, description=""):
        """Ajouter/Retirer du stock"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()

        # Récupérer le stock actuel
        select_sql = "SELECT stock_actuel FROM produits WHERE id = %s"
        cursor.execute(select_sql, (product_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return False, "Produit non trouvé"

        new_stock = result['stock_actuel'] + quantite

        if new_stock < 0:
            conn.close()
            return False, "Stock insuffisant"

        # Mettre à jour le stock
        update_sql = "UPDATE produits SET stock_actuel = %s WHERE id = %s"

        try:
            cursor.execute(update_sql, (new_stock, product_id))
            
            # Enregistrer le mouvement
            Product.record_stock_movement(product_id, quantite, type_mouvement, user_id, description)
            
            conn.commit()
            return True, f"Stock mis à jour ({quantite:+d})"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def record_stock_movement(product_id, quantite, type_mouvement, user_id, description=""):
        """Enregistrer un mouvement de stock"""
        conn = get_connection()
        if not conn:
            return

        cursor = conn.cursor()
        sql = """
        INSERT INTO mouvements_stock (produit_id, user_id, type, quantite, description, date_mouvement)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(sql, (product_id, user_id, type_mouvement, quantite, description, datetime.now()))
            conn.commit()
        except Exception as e:
            print(f"Erreur enregistrement mouvement : {e}")
        finally:
            conn.close()

    @staticmethod
    def get_stock_movements(product_id):
        """Récupérer l'historique des mouvements de stock"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT ms.*, u.username
        FROM mouvements_stock ms
        LEFT JOIN users u ON ms.user_id = u.id
        WHERE ms.produit_id = %s
        ORDER BY ms.date_mouvement DESC
        """

        try:
            cursor.execute(sql, (product_id,))
            movements = cursor.fetchall()
        except Exception as e:
            print(f"Erreur mouvements : {e}")
            movements = []
        finally:
            conn.close()

        return movements

    @staticmethod
    def get_low_stock_products():
        """Récupérer les produits en rupture de stock"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT p.*, c.nom as categorie
        FROM produits p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.stock_actuel <= p.stock_min
        ORDER BY p.stock_actuel ASC
        """

        try:
            cursor.execute(sql)
            products = cursor.fetchall()
        except Exception as e:
            print(f"Erreur stocks bas : {e}")
            products = []
        finally:
            conn.close()

        return products

    @staticmethod
    def calculate_margin(prix_achat, prix_vente):
        """Calculer la marge en pourcentage"""
        if prix_achat == 0:
            return 0
        return ((prix_vente - prix_achat) / prix_achat) * 100

    @staticmethod
    def search(search_term):
        """Rechercher un produit"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = """
        SELECT p.*, c.nom as categorie
        FROM produits p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.nom LIKE %s OR p.description LIKE %s
        ORDER BY p.nom
        """

        search_pattern = f"%{search_term}%"

        try:
            cursor.execute(sql, (search_pattern, search_pattern))
            products = cursor.fetchall()
        except Exception as e:
            print(f"Erreur recherche : {e}")
            products = []
        finally:
            conn.close()

        return products
