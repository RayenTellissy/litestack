import json
import os
from dataclasses import asdict

from .model import Task


def path():
    return os.environ.get("TASKS_FILE", "tasks.json")


def load():
    try:
        with open(path()) as f:
            return [Task(**raw) for raw in json.load(f)]
    except FileNotFoundError:
        return []


def save(tasks):
    with open(path(), "w") as f:
        json.dump([asdict(task) for task in tasks], f, indent=2)
