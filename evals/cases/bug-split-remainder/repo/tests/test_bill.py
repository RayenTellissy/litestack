import unittest

from tabsplit.bill import add_tip, receipt


class ReceiptTest(unittest.TestCase):
    def test_even_receipt(self):
        self.assertEqual(
            receipt(9000, ["alice", "bob", "carol"]),
            "alice: $30.00\nbob: $30.00\ncarol: $30.00\nTotal: $90.00",
        )

    def test_tip_rounds_to_cent(self):
        self.assertEqual(add_tip(8000, 15), 9200)


if __name__ == "__main__":
    unittest.main()
