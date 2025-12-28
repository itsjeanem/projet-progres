from models.product import Product
from models.category import Category


class ProductController:

    @staticmethod
    def create_product(category_id, nom, description, prix_achat, prix_vente, stock_min, stock_actuel=0):
        """Créer un produit"""
        return Product.create(category_id, nom, description, prix_achat, prix_vente, stock_min, stock_actuel)

    @staticmethod
    def get_all_products():
        """Récupérer tous les produits"""
        return Product.get_all()

    @staticmethod
    def get_product(product_id):
        """Récupérer un produit"""
        return Product.get_by_id(product_id)

    @staticmethod
    def update_product(product_id, category_id, nom, description, prix_achat, prix_vente, stock_min):
        """Modifier un produit"""
        return Product.update(product_id, category_id, nom, description, prix_achat, prix_vente, stock_min)

    @staticmethod
    def delete_product(product_id):
        """Supprimer un produit"""
        return Product.delete(product_id)

    @staticmethod
    def search_products(search_term):
        """Rechercher un produit"""
        if not search_term or len(search_term.strip()) < 1:
            return Product.get_all()
        return Product.search(search_term)

    @staticmethod
    def update_product_stock(product_id, quantite, type_mouvement, user_id, description=""):
        """Mettre à jour le stock"""
        return Product.update_stock(product_id, quantite, type_mouvement, user_id, description)

    @staticmethod
    def get_stock_movements(product_id):
        """Récupérer l'historique des mouvements"""
        return Product.get_stock_movements(product_id)

    @staticmethod
    def get_low_stock_products():
        """Récupérer les produits en rupture"""
        return Product.get_low_stock_products()

    @staticmethod
    def get_all_categories():
        """Récupérer toutes les catégories"""
        return Category.get_all()

    @staticmethod
    def calculate_margin(prix_achat, prix_vente):
        """Calculer la marge"""
        return Product.calculate_margin(prix_achat, prix_vente)

    @staticmethod
    def get_products_by_category(category_id):
        """Récupérer les produits d'une catégorie"""
        return Product.get_by_category(category_id)
