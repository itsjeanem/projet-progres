class Session:
    _current_user = None

    @classmethod
    def login(cls, user: dict):
        cls._current_user = user

    @classmethod
    def logout(cls):
        cls._current_user = None

    @classmethod
    def get_user(cls):
        return cls._current_user

    @classmethod
    def is_authenticated(cls):
        return cls._current_user is not None
