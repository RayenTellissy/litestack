import argparse

from .bill import add_tip, receipt
from .money import parse_amount


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tabsplit")
    parser.add_argument("amount")
    parser.add_argument("people", nargs="+")
    parser.add_argument("--tip", type=float, default=0)
    args = parser.parse_args(argv)
    total = add_tip(parse_amount(args.amount), args.tip)
    print(receipt(total, args.people))


if __name__ == "__main__":
    main()
