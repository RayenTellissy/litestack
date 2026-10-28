"""Money is kept in integer cents everywhere."""


def parse_amount(text):
    text = text.strip().lstrip("$")
    if "." in text:
        whole, frac = text.split(".", 1)
        frac = (frac + "00")[:2]
    else:
        whole, frac = text, "00"
    return int(whole) * 100 + int(frac)


def format_amount(cents):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100}.{cents % 100:02d}"


def allocate(total_cents, parts):
    if parts <= 0:
        raise ValueError("parts must be positive")
    share = total_cents // parts
    return [share] * parts
