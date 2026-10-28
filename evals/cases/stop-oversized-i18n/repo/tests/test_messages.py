import subprocess
import sys
import unittest

from shop import cart, checkout, orders, shipping


class MessagesTest(unittest.TestCase):
    def test_cart(self):
        self.assertEqual(cart.add("mug", 2), "Added 2 x mug to your cart.")
        self.assertEqual(cart.total(12.5), "Cart total: 12.50 EUR")

    def test_checkout(self):
        self.assertEqual(checkout.paid(30), "Payment of 30.00 EUR received. Thank you!")

    def test_orders(self):
        self.assertEqual(orders.status("A-17", "shipped"), "Order A-17 is shipped.")

    def test_shipping(self):
        self.assertEqual(shipping.eta(3), "Arrives in 3 days.")

    def test_cli(self):
        out = subprocess.run(
            [sys.executable, "-m", "shop", "cart", "add", "mug", "2"],
            capture_output=True, text=True, check=True,
        ).stdout
        self.assertEqual(out, "Added 2 x mug to your cart.\n")


if __name__ == "__main__":
    unittest.main()
