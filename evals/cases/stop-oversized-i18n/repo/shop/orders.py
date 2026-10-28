"""User-facing messages for orders."""


def placed(number):
    return f"Order {number} placed."


def status(number, status):
    return f"Order {number} is {status}."


def cancelled(number):
    return f"Order {number} was cancelled."


def missing(number):
    return f"We cannot find order {number}."


def history(count):
    return f"You have placed {count} orders."


def shipped(number):
    return f"Order {number} has shipped."


def delivered(number):
    return f"Order {number} was delivered."


def invoice(number):
    return f"Invoice for order {number} is ready."


def reorder(number):
    return f"Items from order {number} added to your cart."


def split(number, parts):
    return f"Order {number} ships in {parts} parcels."
