class Session:
    _current_user = None

    @classmethod
    def login(cls, user: dict):
        """Login user and store session"""
        cls._current_user = user

    @classmethod
    def logout(cls):
        """Logout and clear session"""
        cls._current_user = None

    @classmethod
    def get_user(cls):
        """Get current user"""
        return cls._current_user

    @classmethod
    def is_authenticated(cls):
        """Check if user is authenticated"""
        return cls._current_user is not None

    @classmethod
    def get_role(cls):
        """Get current user's role"""
        if cls._current_user:
            return cls._current_user.get('role')
        return None

    @classmethod
    def get_username(cls):
        """Get current username"""
        if cls._current_user:
            return cls._current_user.get('username')
        return None

    @classmethod
    def get_user_id(cls):
        """Get current user ID"""
        if cls._current_user:
            return cls._current_user.get('id')
        return None
