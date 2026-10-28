#!/usr/bin/env python3
"""Fail when a skill or agent doc cites a principle that principles.md does not define.

A citation is a parenthesized list of principle names, such as
"(Model the domain, Design it as if it was always there)". Any parenthesized
text that starts with a capital letter and holds no code span counts as one.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "litestack"


def main():
    names = re.findall(r"^\*\*(.+?)\.\*\*", (SKILL / "principles.md").read_text(), re.M)
    name = "|".join(map(re.escape, names))
    citation = re.compile(rf"(?:{name})(?:, (?:{name}))*")
    checked, bad = 0, []
    for doc in sorted(SKILL.rglob("*.md")) + sorted((ROOT / "agents").glob("*.md")):
        for lineno, line in enumerate(doc.read_text().splitlines(), 1):
            for group in re.findall(r"\(([A-Z][^()`]*)\)", line):
                checked += 1
                if not citation.fullmatch(group):
                    bad.append(f"{doc.relative_to(ROOT)}:{lineno}: ({group}) is not a list of principles from principles.md")
    print("\n".join(bad) or f"{checked} citations match the {len(names)} principles in principles.md")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
