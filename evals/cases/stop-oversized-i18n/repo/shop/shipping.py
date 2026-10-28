"""User-facing messages for shipping."""


def eta(days):
    return f"Arrives in {days} days."


def free():
    return "Shipping is free for this order."


def cost(amount):
    return f"Shipping costs {amount:.2f} EUR."


def tracking(code):
    return f"Track your parcel with code {code}."


def delayed():
    return "Your parcel is delayed. Sorry!"


def pickup(place):
    return f"Pick up your parcel at {place}."


def express():
    return "Express delivery selected."


def abroad(country):
    return f"We ship to {country} in 5 to 7 days."


def signature():
    return "A signature is needed on delivery."


def address():
    return "We could not verify this address."
