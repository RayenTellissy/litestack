"""User-facing messages for cart."""


def add(item, qty):
    return f"Added {qty} x {item} to your cart."


def remove(item):
    return f"Removed {item} from your cart."


def empty():
    return "Your cart is empty."


def total(amount):
    return f"Cart total: {amount:.2f} EUR"


def limit(qty):
    return f"You can add at most {qty} of this item."


def saved():
    return "Your cart was saved for later."


def merged(count):
    return f"We merged {count} items from your last visit."


def gift(item):
    return f"{item} will be gift wrapped."


def note():
    return "Add a note for the seller."


def moved(item):
    return f"{item} moved to your wishlist."
