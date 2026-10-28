import unittest

from tabsplit.money import allocate, format_amount, parse_amount


class ParseAmountTest(unittest.TestCase):
    def test_dollars_and_cents(self):
        self.assertEqual(parse_amount("12.34"), 1234)

    def test_whole_dollars(self):
        self.assertEqual(parse_amount("$7"), 700)

    def test_one_decimal(self):
        self.assertEqual(parse_amount("0.5"), 50)


class FormatAmountTest(unittest.TestCase):
    def test_pads_cents(self):
        self.assertEqual(format_amount(1205), "$12.05")

    def test_negative(self):
        self.assertEqual(format_amount(-50), "-$0.50")


class AllocateTest(unittest.TestCase):
    def test_even_split(self):
        self.assertEqual(allocate(9000, 3), [3000, 3000, 3000])

    def test_remainder_cents_are_kept(self):
        self.assertEqual(allocate(10000, 3), [3334, 3333, 3333])

    def test_rejects_zero_parts(self):
        with self.assertRaises(ValueError):
            allocate(100, 0)


if __name__ == "__main__":
    unittest.main()
