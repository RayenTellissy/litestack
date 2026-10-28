"""User-facing messages for coupons."""


def applied(code):
    return f"Coupon {code} applied."


def expired(code):
    return f"Coupon {code} has expired."


def invalid(code):
    return f"Coupon {code} is not valid."


def saved(amount):
    return f"You saved {amount:.2f} EUR."


def one():
    return "Only one coupon per order."


def min(amount):
    return f"This coupon needs an order of at least {amount:.2f} EUR."


def removed(code):
    return f"Coupon {code} removed."


def first():
    return "This coupon is for first orders only."


def best(code):
    return f"We applied your best coupon, {code}."


def used(code):
    return f"Coupon {code} was already used."
