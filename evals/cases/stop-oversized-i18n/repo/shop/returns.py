"""User-facing messages for returns."""


def opened(number):
    return f"Return opened for order {number}."


def label():
    return "Print the return label and attach it to the box."


def refunded(amount):
    return f"Refund of {amount:.2f} EUR issued."


def window(days):
    return f"Returns are accepted within {days} days."


def denied():
    return "This item cannot be returned."


def received(number):
    return f"We received your return for order {number}."


def inspect():
    return "Your return is being inspected."


def exchange(name):
    return f"We will send a new {name}."


def partial(amount):
    return f"Partial refund of {amount:.2f} EUR issued."


def late():
    return "This return arrived after the return window."
