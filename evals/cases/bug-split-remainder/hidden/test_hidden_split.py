import os
import subprocess
import sys
import unittest

from tabsplit.bill import add_tip, receipt, split_even
from tabsplit.money import allocate


class AllocateKeepsEveryCentTest(unittest.TestCase):
    def assertFair(self, total, parts):
        shares = allocate(total, parts)
        self.assertEqual(len(shares), parts, (total, parts))
        self.assertEqual(sum(shares), total, (total, parts, shares))
        self.assertLessEqual(max(shares) - min(shares), 1, (total, parts, shares))
        for share in shares:
            self.assertIsInstance(share, int)

    def test_remainders(self):
        for total, parts in [(10000, 3), (10, 4), (5, 7), (1, 2), (99999, 8), (0, 3), (7, 7), (9000, 3)]:
            self.assertFair(total, parts)

    def test_even_split_unchanged(self):
        self.assertEqual(allocate(9000, 3), [3000, 3000, 3000])

    def test_rejects_zero_parts(self):
        with self.assertRaises(ValueError):
            allocate(100, 0)


class CallersTest(unittest.TestCase):
    def test_split_even_keeps_total(self):
        shares = split_even(10000, ["a", "b", "c"])
        self.assertEqual(sum(shares.values()), 10000)

    def test_receipt_total_matches_input(self):
        self.assertTrue(receipt(10000, ["a", "b", "c"]).endswith("Total: $100.00"))

    def test_tip_split_keeps_total(self):
        total = add_tip(10001, 18)
        self.assertEqual(sum(split_even(total, ["a", "b", "c", "d"]).values()), total)

    def test_cli_total_matches_input(self):
        out = subprocess.run(
            [sys.executable, "-m", "tabsplit", "100.00", "alice", "bob", "carol"],
            capture_output=True, text=True, check=True, cwd=os.getcwd(),
        ).stdout
        self.assertIn("Total: $100.00", out)


if __name__ == "__main__":
    unittest.main()
