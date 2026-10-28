import argparse
import sys

from . import store
from .model import Task


def cmd_add(args):
    tasks = store.load()
    next_id = max((task.id for task in tasks), default=0) + 1
    task = Task(id=next_id, title=args.title, tags=args.tag)
    tasks.append(task)
    store.save(tasks)
    print(f"Added {task.id}.")
    return 0


def cmd_list(args):
    tasks = [t for t in store.load() if args.all or not t.done]
    if args.tag:
        tasks = [t for t in tasks if args.tag in t.tags]
    if not tasks:
        print("No tasks.")
        return 0
    for task in tasks:
        print(task.line())
    return 0


def cmd_done(args):
    tasks = store.load()
    for task in tasks:
        if task.id == args.id:
            task.done = True
            store.save(tasks)
            print(f"Done {task.id}.")
            return 0
    print(f"No task {args.id}.", file=sys.stderr)
    return 1


def parser():
    p = argparse.ArgumentParser(prog="tasks")
    sub = p.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a task")
    add.add_argument("title")
    add.add_argument("--tag", action="append", default=[])
    add.set_defaults(run=cmd_add)

    ls = sub.add_parser("list", help="list open tasks")
    ls.add_argument("--tag")
    ls.add_argument("--all", action="store_true", help="include done tasks")
    ls.set_defaults(run=cmd_list)

    done = sub.add_parser("done", help="mark a task done")
    done.add_argument("id", type=int)
    done.set_defaults(run=cmd_done)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    return args.run(args)
