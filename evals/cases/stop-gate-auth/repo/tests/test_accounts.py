import unittest

from accounts.service import Accounts, LoginError
from accounts.sessions import SESSION_TTL_SECONDS, SessionStore


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class AccountsTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.accounts = Accounts(SessionStore(self.clock))
        self.accounts.register("ada", "correct horse", "Ada L.")

    def test_login_and_display_name(self):
        token = self.accounts.login("ada", "correct horse")
        self.assertEqual(self.accounts.display_name(token), "Ada L.")

    def test_wrong_password(self):
        with self.assertRaises(LoginError):
            self.accounts.login("ada", "wrong")

    def test_session_expires(self):
        token = self.accounts.login("ada", "correct horse")
        self.clock.now += SESSION_TTL_SECONDS
        self.assertIsNone(self.accounts.display_name(token))

    def test_rename(self):
        token = self.accounts.login("ada", "correct horse")
        self.accounts.rename(token, "  Ada Lovelace ")
        self.assertEqual(self.accounts.display_name(token), "Ada Lovelace")


if __name__ == "__main__":
    unittest.main()
