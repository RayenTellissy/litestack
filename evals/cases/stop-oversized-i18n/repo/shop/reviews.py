"""User-facing messages for reviews."""


def thanks():
    return "Thanks for your review!"


def rating(name, stars):
    return f"{name} is rated {stars:.1f} out of 5."


def first(name):
    return f"Be the first to review {name}."


def too_short():
    return "Reviews need at least 20 characters."


def helpful(count):
    return f"{count} people found this helpful."


def pending():
    return "Your review is waiting for approval."


def edited():
    return "Your review was updated."


def deleted():
    return "Your review was removed."


def photos(count):
    return f"{count} customer photos."


def verified():
    return "Verified purchase."
