import bcrypt
from database.connection import get_connection


class User:

    @staticmethod
    def create(username, password, email, role="vendeur"):
        conn = get_connection()
        if not conn:
            return False

        cursor = conn.cursor()

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        sql = """
        INSERT INTO users (username, password_hash, email, role)
        VALUES (%s, %s, %s, %s)
        """

        try:
            cursor.execute(sql, (username, password_hash, email, role))
            conn.commit()
            return True
        except Exception as e:
            print("Erreur création utilisateur :", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        conn.close()

        return user

    @staticmethod
    def verify_password(password, password_hash):
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8") if isinstance(password_hash, str) else password_hash
        )
