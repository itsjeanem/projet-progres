from models.user import User


class UserController:

    @staticmethod
    def login(username, password):
        if not username or not password:
            return None, "Champs obligatoires"

        user = User.get_by_username(username)

        if not user:
            return None, "Utilisateur introuvable"

        if not User.verify_password(password, user["password_hash"]):
            return None, "Mot de passe incorrect"

        return user, None
