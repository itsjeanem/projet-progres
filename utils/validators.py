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
