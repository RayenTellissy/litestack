import json
import os
import random
import unittest
from datetime import date, timedelta

from ledger import reports
from ledger.entries import Entry

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden_reports.json")
CATEGORIES = ["food", "rent", "travel", "gifts", "a", "zz-misc"]


def scenarios():
    rng = random.Random(1234)
    out = {"empty": [], "single": [Entry(date(2026, 5, 17), "food", 0.1)]}
    out["year_boundary"] = [
        Entry(date(2025, 12, 28), "gifts", 50.0),
        Entry(date(2025, 12, 29), "gifts", 20.0),
        Entry(date(2026, 1, 1), "food", 9.99),
        Entry(date(2027, 1, 3), "travel", 300.0),
    ]
    out["refunds"] = [
        Entry(date(2026, 2, 3), "travel", 120.0),
        Entry(date(2026, 2, 3), "travel", -120.0),
        Entry(date(2026, 2, 4), "food", -4.5),
    ]
    for n in range(4):
        start = date(2025, 11, 1)
        out[f"random_{n}"] = [
            Entry(
                start + timedelta(days=rng.randrange(120)),
                rng.choice(CATEGORIES),
                round(rng.uniform(-50, 500), rng.choice([0, 1, 2])),
            )
            for _ in range(rng.randrange(5, 40))
        ]
    return out


def render_all():
    return {
        f"{name}/{kind}": getattr(reports, f"{kind}_summary")(list(entries))
        for name, entries in scenarios().items()
        for kind in ("daily", "weekly", "monthly")
    }


class GoldenReportsTest(unittest.TestCase):
    def test_outputs_match_recorded_baseline(self):
        with open(GOLDEN) as f:
            golden = json.load(f)
        actual = render_all()
        self.assertEqual(sorted(actual), sorted(golden))
        for key in golden:
            self.assertEqual(actual[key], golden[key], key)

    def test_parse_line_unchanged(self):
        self.assertEqual(reports.parse_line(" 2026-01-02 ,rent, -3 "), Entry(date(2026, 1, 2), "rent", -3.0))


if __name__ == "__main__":
    if os.environ.get("RECORD_GOLDEN"):
        with open(GOLDEN, "w") as f:
            json.dump(render_all(), f, indent=1, sort_keys=True)
    else:
        unittest.main()
