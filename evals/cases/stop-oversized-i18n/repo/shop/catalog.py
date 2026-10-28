"""User-facing messages for catalog."""


def found(count):
    return f"Found {count} products."


def none():
    return "No products match your search."


def price(name, amount):
    return f"{name} costs {amount:.2f} EUR."


def out(name):
    return f"{name} is out of stock."


def new(name):
    return f"New arrival: {name}!"


def sorted(field):
    return f"Sorted by {field}."


def page(page, pages):
    return f"Page {page} of {pages}."


def filter(name):
    return f"Filter {name} applied."


def cleared():
    return "All filters cleared."


def compare(count):
    return f"Comparing {count} products."
