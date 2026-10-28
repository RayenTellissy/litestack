from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    tags: List[str] = field(default_factory=list)
    due: Optional[date] = None

    def line(self):
        mark = "x" if self.done else " "
        tags = "".join(f" #{tag}" for tag in self.tags)
        due = f" due {self.due.isoformat()}" if self.due else ""
        return f"[{mark}] {self.id} {self.title}{tags}{due}"

    def overdue(self, today):
        return not self.done and self.due is not None and self.due < today
