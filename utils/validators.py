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


class SaleValidator:

    @staticmethod
    def validate_client_id(client_id):
        """Valider la sélection client"""
        if not client_id or client_id <= 0:
            return False, "Client obligatoire"
        return True, ""

    @staticmethod
    def validate_articles(articles):
        """Valider la liste des articles"""
        if not articles or len(articles) == 0:
            return False, "Au moins un article obligatoire"
        
        for article in articles:
            if 'produit_id' not in article or article['produit_id'] <= 0:
                return False, "Produit invalide"
            if 'quantite' not in article or article['quantite'] <= 0:
                return False, "Quantité doit être supérieure à 0"
            if 'prix_unitaire' not in article or article['prix_unitaire'] < 0:
                return False, "Prix unitaire invalide"
        
        return True, ""

    @staticmethod
    def validate_remise(remise, remise_type, montant_total):
        """Valider la remise"""
        try:
            remise = float(remise)
            if remise < 0:
                return False, "Remise ne peut pas être négative"
            
            if remise_type == 'pourcentage':
                if remise > 100:
                    return False, "Pourcentage ne peut pas dépasser 100%"
            else:  # montant
                if remise > montant_total:
                    return False, "Remise ne peut pas dépasser le montant total"
            
            return True, ""
        except ValueError:
            return False, "Format remise invalide"

    @staticmethod
    def validate_tva(tva):
        """Valider le TVA"""
        try:
            tva = float(tva)
            if tva < 0 or tva > 100:
                return False, "TVA doit être entre 0 et 100"
            return True, ""
        except ValueError:
            return False, "Format TVA invalide"

    @staticmethod
    def validate_paiement(montant_paye, montant_total):
        """Valider un paiement"""
        try:
            montant_paye = float(montant_paye)
            if montant_paye <= 0:
                return False, "Montant doit être supérieur à 0"
            if montant_paye > montant_total:
                return False, f"Montant supérieur au total ({montant_total} XOF)"
            return True, ""
        except ValueError:
            return False, "Format montant invalide"

    @staticmethod
    def validate_sale_form(client_id, articles, tva, remise, remise_type):
        """Valider l'ensemble du formulaire vente"""
        # Vérifier client
        is_valid, error = SaleValidator.validate_client_id(client_id)
        if not is_valid:
            return False, error

        # Vérifier articles
        is_valid, error = SaleValidator.validate_articles(articles)
        if not is_valid:
            return False, error

        # Vérifier TVA
        is_valid, error = SaleValidator.validate_tva(tva)
        if not is_valid:
            return False, error

        # Calculer montant total pour valider remise
        montant_ht = sum(art['quantite'] * art['prix_unitaire'] for art in articles)
        
        # Vérifier remise
        is_valid, error = SaleValidator.validate_remise(remise, remise_type, montant_ht)
        if not is_valid:
            return False, error

        return True, ""
