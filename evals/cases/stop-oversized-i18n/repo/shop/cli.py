import argparse

from . import cart, catalog, checkout, coupons, inventory, orders, returns, reviews, shipping, wishlist

MODULES = {
    "cart": cart,
    "catalog": catalog,
    "checkout": checkout,
    "coupons": coupons,
    "inventory": inventory,
    "orders": orders,
    "returns": returns,
    "reviews": reviews,
    "shipping": shipping,
    "wishlist": wishlist,
}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="shop", description="Print a shop message.")
    parser.add_argument("area", choices=sorted(MODULES))
    parser.add_argument("message")
    parser.add_argument("args", nargs="*")
    ns = parser.parse_args(argv)
    fn = getattr(MODULES[ns.area], ns.message)
    values = [float(a) if a.replace(".", "", 1).isdigit() and "." in a else int(a) if a.isdigit() else a for a in ns.args]
    print(fn(*values))
    return 0
