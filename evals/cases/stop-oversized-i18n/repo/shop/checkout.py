"""User-facing messages for checkout."""


def start():
    return "Starting checkout."


def address():
    return "Please enter a delivery address."


def paid(amount):
    return f"Payment of {amount:.2f} EUR received. Thank you!"


def failed():
    return "Payment failed. Please try another card."


def review(count):
    return f"Review your {count} items before paying."


def guest():
    return "You are checking out as a guest."


def terms():
    return "Please accept the terms of sale."


def billing():
    return "Billing address is the same as delivery."


def total(amount):
    return f"You will pay {amount:.2f} EUR."


def timeout():
    return "Your checkout session timed out."
