from models.user import User
from utils.permissions import check_role


class UserController:

    @staticmethod
    def login(username, password):
        """Authenticate user with username and password"""
        if not username or not password:
            return None, "Champs obligatoires"

        user = User.get_by_username(username)

        if not user:
            return None, "Utilisateur introuvable"

        if not User.verify_password(password, user["password_hash"]):
            return None, "Mot de passe incorrect"

        return user, None

    @staticmethod
    def create_user(username, email, password, role="vendeur"):
        """Create new user - requires admin role"""
        if not check_role("admin"):
            return False, "Seuls les administrateurs peuvent créer des utilisateurs"
        
        if not username or not email or not password:
            return False, "Champs obligatoires"
        
        if not User.create(username, password, email, role):
            return False, "Erreur lors de la création de l'utilisateur"
        
        return True, None

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.get_by_id(user_id)

    @staticmethod
    def get_all_users():
        """Get all users - requires admin role"""
        if not check_role("admin"):
            return None, "Seuls les administrateurs peuvent voir la liste des utilisateurs"
        
        return User.get_all(), None

    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user - requires admin role"""
        if not check_role("admin"):
            return False, "Seuls les administrateurs peuvent modifier les utilisateurs"
        
        return User.update(user_id, **kwargs), None

    @staticmethod
    def delete_user(user_id):
        """Delete user - requires admin role"""
        if not check_role("admin"):
            return False, "Seuls les administrateurs peuvent supprimer les utilisateurs"
        
        return User.delete(user_id), None
