"""User-facing messages for inventory."""


def low(name, qty):
    return f"Only {qty} left of {name}."


def restock(name):
    return f"{name} is back in stock."


def reserved(name):
    return f"{name} is reserved for 15 minutes."


def released(name):
    return f"Your reservation for {name} ended."


def unknown(name):
    return f"We do not sell {name}."


def preorder(name):
    return f"{name} can be preordered."


def ships(name, days):
    return f"{name} ships in {days} days."


def limited(name):
    return f"{name} is a limited edition."


def discontinued(name):
    return f"{name} is discontinued."


def notify(name):
    return f"We will email you when {name} is back."
