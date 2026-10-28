import secrets
import time

SESSION_TTL_SECONDS = 60 * 60


class SessionStore:
    def __init__(self, clock=time.time):
        self._clock = clock
        self._sessions = {}

    def create(self, username):
        token = secrets.token_urlsafe(32)
        self._sessions[token] = (username, self._clock() + SESSION_TTL_SECONDS)
        return token

    def user_for(self, token):
        entry = self._sessions.get(token)
        if entry is None:
            return None
        username, expires_at = entry
        if self._clock() >= expires_at:
            del self._sessions[token]
            return None
        return username

    def end(self, token):
        self._sessions.pop(token, None)
