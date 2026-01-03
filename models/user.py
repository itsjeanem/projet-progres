import bcrypt
from database.connection import get_connection


class User:

    @staticmethod
    def create(username, password, email, role="vendeur"):
        """Create new user"""
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
        """Get user by username"""
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
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE id = %s AND is_active = TRUE"
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()
        conn.close()

        return user

    @staticmethod
    def get_all(active_only=True):
        """Get all users"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        if active_only:
            sql = "SELECT id, username, email, role, is_active, created_at FROM users WHERE is_active = TRUE ORDER BY username"
        else:
            sql = "SELECT id, username, email, role, is_active, created_at FROM users ORDER BY username"
        cursor.execute(sql)
        users = cursor.fetchall()
        conn.close()

        return users

    @staticmethod
    def get_by_role(role):
        """Get all users with specific role"""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        sql = "SELECT id, username, email, role, is_active, created_at FROM users WHERE role = %s AND is_active = TRUE"
        cursor.execute(sql, (role,))
        users = cursor.fetchall()
        conn.close()

        return users

    @staticmethod
    def update(user_id, **kwargs):
        """Update user fields"""
        conn = get_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        
        allowed_fields = ['username', 'email', 'role', 'is_active']
        updates = []
        values = []

        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = %s")
                values.append(value)

        if not updates:
            return False

        values.append(user_id)
        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"

        try:
            cursor.execute(sql, values)
            conn.commit()
            return True
        except Exception as e:
            print("Erreur modification utilisateur :", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        """Soft delete user (deactivate)"""
        conn = get_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        sql = "UPDATE users SET is_active = FALSE WHERE id = %s"

        try:
            cursor.execute(sql, (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print("Erreur suppression utilisateur :", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8") if isinstance(password_hash, str) else password_hash
        )

    @staticmethod
    def change_password(user_id, new_password):
        """Change user password"""
        conn = get_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        password_hash = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        )

        sql = "UPDATE users SET password_hash = %s WHERE id = %s"

        try:
            cursor.execute(sql, (password_hash, user_id))
            conn.commit()
            return True
        except Exception as e:
            print("Erreur changement de mot de passe :", e)
            return False
        finally:
            conn.close()

