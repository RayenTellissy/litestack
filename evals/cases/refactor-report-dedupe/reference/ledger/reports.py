from datetime import date

from .entries import Entry


def _summary(entries, key):
    groups = {}
    for entry in entries:
        groups.setdefault(key(entry.day), []).append(entry)
    if not groups:
        return "No entries."
    lines = []
    for group in sorted(groups):
        lines.append(f"== {group} ==")
        totals = {}
        for entry in groups[group]:
            totals[entry.category] = totals.get(entry.category, 0.0) + entry.amount
        rows = [(category, totals[category]) for category in sorted(totals)]
        rows.append(("total", sum(totals.values())))
        lines.extend(f"{label:<16}{amount:>10.2f}" for label, amount in rows)
    return "\n".join(lines)


def _iso_week(day):
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def daily_summary(entries):
    return _summary(entries, date.isoformat)


def weekly_summary(entries):
    return _summary(entries, _iso_week)


def monthly_summary(entries):
    return _summary(entries, lambda day: f"{day.year}-{day.month:02d}")


def parse_line(line):
    day, category, amount = line.split(",")
    return Entry(date.fromisoformat(day.strip()), category.strip(), float(amount))
