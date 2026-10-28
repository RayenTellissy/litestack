"""User-facing messages for wishlist."""


def added(name):
    return f"{name} added to your wishlist."


def removed(name):
    return f"{name} removed from your wishlist."


def empty():
    return "Your wishlist is empty."


def shared():
    return "Wishlist link copied."


def price_drop(name, amount):
    return f"{name} dropped to {amount:.2f} EUR."


def full(count):
    return f"Your wishlist can hold {count} items."


def private():
    return "Your wishlist is private."


def public():
    return "Your wishlist is public."


def back(name):
    return f"{name} from your wishlist is back in stock."


def moved(name):
    return f"{name} moved to your cart."
