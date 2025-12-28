from database.connection import get_connection


class Category:

    @staticmethod
    def get_all():
        """Récupérer toutes les catégories"""
        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        sql = "SELECT * FROM categories ORDER BY nom"
        cursor.execute(sql)
        categories = cursor.fetchall()
        conn.close()

        return categories

    @staticmethod
    def get_by_id(category_id):
        """Récupérer une catégorie par ID"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        sql = "SELECT * FROM categories WHERE id = %s"
        cursor.execute(sql, (category_id,))
        category = cursor.fetchone()
        conn.close()

        return category

    @staticmethod
    def create(nom, description=None):
        """Créer une nouvelle catégorie"""
        conn = get_connection()
        if not conn:
            return False, "Erreur de connexion"

        cursor = conn.cursor()
        sql = "INSERT INTO categories (nom, description) VALUES (%s, %s)"

        try:
            cursor.execute(sql, (nom, description))
            conn.commit()
            return True, "Catégorie créée"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()
