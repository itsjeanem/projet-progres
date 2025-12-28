import re


class ClientValidator:

    @staticmethod
    def validate_name(name):
        """Valider le nom/prénom"""
        if not name or len(name.strip()) < 2:
            return False, "Le nom doit contenir au moins 2 caractères"
        if len(name) > 100:
            return False, "Le nom ne doit pas dépasser 100 caractères"
        return True, ""

    @staticmethod
    def validate_email(email):
        """Valider l'email"""
        if not email:
            return True, ""  # Email optionnel
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Email invalide"
        return True, ""

    @staticmethod
    def validate_phone(phone):
        """Valider le téléphone"""
        if not phone:
            return True, ""  # Téléphone optionnel
        
        # Accepter les formats : 0123456789, +33123456789, 01 23 45 67 89, etc.
        phone_clean = re.sub(r'[\s\-\+\(\)]', '', phone)
        if not re.match(r'^[0-9]{10,}$', phone_clean):
            return False, "Téléphone invalide"
        return True, ""

    @staticmethod
    def validate_postal_code(postal_code):
        """Valider le code postal"""
        if not postal_code:
            return True, ""  # Code postal optionnel
        
        if not re.match(r'^[0-9]{5}$', postal_code):
            return False, "Code postal invalide (5 chiffres attendus)"
        return True, ""

    @staticmethod
    def validate_client_form(nom, prenom, telephone=None, email=None, code_postal=None):
        """Valider l'ensemble du formulaire"""
        # Vérifier nom
        is_valid, error = ClientValidator.validate_name(nom)
        if not is_valid:
            return False, f"Nom : {error}"

        # Vérifier prénom
        is_valid, error = ClientValidator.validate_name(prenom)
        if not is_valid:
            return False, f"Prénom : {error}"

        # Vérifier email
        is_valid, error = ClientValidator.validate_email(email)
        if not is_valid:
            return False, f"Email : {error}"

        # Vérifier téléphone
        is_valid, error = ClientValidator.validate_phone(telephone)
        if not is_valid:
            return False, f"Téléphone : {error}"

        # Vérifier code postal
        is_valid, error = ClientValidator.validate_postal_code(code_postal)
        if not is_valid:
            return False, f"Code postal : {error}"

        return True, ""


class ProductValidator:

    @staticmethod
    def validate_product_name(name):
        """Valider le nom du produit"""
        if not name or len(name.strip()) < 2:
            return False, "Le nom doit contenir au moins 2 caractères"
        if len(name) > 200:
            return False, "Le nom ne doit pas dépasser 200 caractères"
        return True, ""

    @staticmethod
    def validate_price(price):
        """Valider un prix"""
        if price is None or price == '':
            return False, "Le prix est obligatoire"
        try:
            price = float(price)
            if price < 0:
                return False, "Le prix ne peut pas être négatif"
            return True, ""
        except ValueError:
            return False, "Format de prix invalide"

    @staticmethod
    def validate_stock(stock):
        """Valider une quantité de stock"""
        if stock is None or stock == '':
            stock = 0
        try:
            stock = int(stock)
            if stock < 0:
                return False, "Le stock ne peut pas être négatif"
            return True, ""
        except ValueError:
            return False, "Format de stock invalide"

    @staticmethod
    def validate_product_form(nom, prix_achat, prix_vente, stock_min, category_id):
        """Valider le formulaire produit"""
        # Vérifier nom
        is_valid, error = ProductValidator.validate_product_name(nom)
        if not is_valid:
            return False, f"Nom : {error}"

        # Vérifier prix achat
        is_valid, error = ProductValidator.validate_price(prix_achat)
        if not is_valid:
            return False, f"Prix achat : {error}"

        # Vérifier prix vente
        is_valid, error = ProductValidator.validate_price(prix_vente)
        if not is_valid:
            return False, f"Prix vente : {error}"

        # Vérifier stock minimum
        is_valid, error = ProductValidator.validate_stock(stock_min)
        if not is_valid:
            return False, f"Stock min : {error}"

        # Vérifier catégorie
        if not category_id or category_id <= 0:
            return False, "Catégorie obligatoire"

        # Vérifier que prix_vente > prix_achat
        try:
            pa = float(prix_achat)
            pv = float(prix_vente)
            if pv <= pa:
                return False, "Le prix de vente doit être supérieur au prix d'achat"
        except ValueError:
            return False, "Erreur conversion prix"

        return True, ""
