from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Entry:
    day: date
    category: str
    amount: float
