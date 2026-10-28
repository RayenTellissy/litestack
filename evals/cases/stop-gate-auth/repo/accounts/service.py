from .passwords import hash_password, verify_password
from .sessions import SessionStore


class LoginError(Exception):
    pass


class Accounts:
    def __init__(self, sessions=None):
        self.sessions = sessions or SessionStore()
        self._users = {}
        self._display_names = {}

    def register(self, username, password, display_name=None):
        if username in self._users:
            raise ValueError(f"{username} already exists")
        self._users[username] = hash_password(password)
        self._display_names[username] = display_name or username

    def login(self, username, password):
        stored = self._users.get(username)
        if stored is None or not verify_password(password, stored):
            raise LoginError("wrong username or password")
        return self.sessions.create(username)

    def display_name(self, token):
        username = self.sessions.user_for(token)
        return None if username is None else self._display_names[username]

    def rename(self, token, display_name):
        username = self.sessions.user_for(token)
        if username is None:
            raise LoginError("not logged in")
        self._display_names[username] = display_name.strip()
