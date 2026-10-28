import unittest
from datetime import date

from ledger.entries import Entry
from ledger.reports import daily_summary, monthly_summary, parse_line, weekly_summary

ENTRIES = [
    Entry(date(2026, 3, 2), "food", 12.5),
    Entry(date(2026, 3, 2), "rent", 900.0),
    Entry(date(2026, 3, 3), "food", 7.25),
    Entry(date(2026, 3, 9), "travel", 40.0),
    Entry(date(2026, 4, 1), "food", 3.0),
]


class ReportsTest(unittest.TestCase):
    def test_daily(self):
        self.assertEqual(
            daily_summary(ENTRIES[:3]),
            "== 2026-03-02 ==\n"
            "food                 12.50\n"
            "rent                900.00\n"
            "total               912.50\n"
            "== 2026-03-03 ==\n"
            "food                  7.25\n"
            "total                 7.25",
        )

    def test_weekly(self):
        self.assertEqual(
            weekly_summary(ENTRIES[:4]),
            "== 2026-W10 ==\n"
            "food                 19.75\n"
            "rent                900.00\n"
            "total               919.75\n"
            "== 2026-W11 ==\n"
            "travel               40.00\n"
            "total                40.00",
        )

    def test_monthly(self):
        self.assertEqual(
            monthly_summary(ENTRIES),
            "== 2026-03 ==\n"
            "food                 19.75\n"
            "rent                900.00\n"
            "travel               40.00\n"
            "total               959.75\n"
            "== 2026-04 ==\n"
            "food                  3.00\n"
            "total                 3.00",
        )

    def test_empty(self):
        self.assertEqual(daily_summary([]), "No entries.")

    def test_parse_line(self):
        self.assertEqual(parse_line("2026-03-02, food, 12.5"), ENTRIES[0])


if __name__ == "__main__":
    unittest.main()
