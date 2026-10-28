from .entries import Entry


def daily_summary(entries):
    groups = {}
    for entry in entries:
        key = entry.day.isoformat()
        groups.setdefault(key, []).append(entry)
    lines = []
    for key in sorted(groups):
        lines.append(f"== {key} ==")
        totals = {}
        for entry in groups[key]:
            totals[entry.category] = totals.get(entry.category, 0.0) + entry.amount
        for category in sorted(totals):
            lines.append(f"{category:<16}{totals[category]:>10.2f}")
        lines.append(f"{'total':<16}{sum(totals.values()):>10.2f}")
    if not lines:
        return "No entries."
    return "\n".join(lines)


def weekly_summary(entries):
    groups = {}
    for entry in entries:
        year, week, _ = entry.day.isocalendar()
        key = f"{year}-W{week:02d}"
        groups.setdefault(key, []).append(entry)
    lines = []
    for key in sorted(groups):
        lines.append(f"== {key} ==")
        totals = {}
        for entry in groups[key]:
            totals[entry.category] = totals.get(entry.category, 0.0) + entry.amount
        for category in sorted(totals):
            lines.append(f"{category:<16}{totals[category]:>10.2f}")
        lines.append(f"{'total':<16}{sum(totals.values()):>10.2f}")
    if not lines:
        return "No entries."
    return "\n".join(lines)


def monthly_summary(entries):
    groups = {}
    for entry in entries:
        key = f"{entry.day.year}-{entry.day.month:02d}"
        groups.setdefault(key, []).append(entry)
    lines = []
    for key in sorted(groups):
        lines.append(f"== {key} ==")
        totals = {}
        for entry in groups[key]:
            totals[entry.category] = totals.get(entry.category, 0.0) + entry.amount
        for category in sorted(totals):
            lines.append(f"{category:<16}{totals[category]:>10.2f}")
        lines.append(f"{'total':<16}{sum(totals.values()):>10.2f}")
    if not lines:
        return "No entries."
    return "\n".join(lines)


def parse_line(line):
    day, category, amount = line.split(",")
    from datetime import date
    return Entry(date.fromisoformat(day.strip()), category.strip(), float(amount))
