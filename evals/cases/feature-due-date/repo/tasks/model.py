from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    tags: List[str] = field(default_factory=list)

    def line(self):
        mark = "x" if self.done else " "
        tags = "".join(f" #{tag}" for tag in self.tags)
        return f"[{mark}] {self.id} {self.title}{tags}"
