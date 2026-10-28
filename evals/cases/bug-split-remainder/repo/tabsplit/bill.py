from .money import allocate, format_amount


def split_even(total_cents, people):
    return dict(zip(people, allocate(total_cents, len(people))))


def add_tip(subtotal_cents, tip_percent):
    return subtotal_cents + round(subtotal_cents * tip_percent / 100)


def receipt(total_cents, people):
    shares = split_even(total_cents, people)
    lines = [f"{name}: {format_amount(amount)}" for name, amount in shares.items()]
    lines.append(f"Total: {format_amount(sum(shares.values()))}")
    return "\n".join(lines)
