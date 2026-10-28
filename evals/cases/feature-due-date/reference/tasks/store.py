import json
import os
from dataclasses import asdict
from datetime import date

from .model import Task


def path():
    return os.environ.get("TASKS_FILE", "tasks.json")


def load():
    try:
        with open(path()) as f:
            return [decode(raw) for raw in json.load(f)]
    except FileNotFoundError:
        return []


def save(tasks):
    with open(path(), "w") as f:
        json.dump([encode(task) for task in tasks], f, indent=2)


def decode(raw):
    due = raw.get("due")
    return Task(**{**raw, "due": date.fromisoformat(due) if due else None})


def encode(task):
    return {**asdict(task), "due": task.due.isoformat() if task.due else None}
