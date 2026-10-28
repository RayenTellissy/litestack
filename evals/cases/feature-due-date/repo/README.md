# tasks

A small command-line task list. Tasks live in a JSON file, `tasks.json` in the
current directory unless `TASKS_FILE` points elsewhere.

```
python3 -m tasks add "Buy milk" --tag home
python3 -m tasks list
python3 -m tasks list --tag home
python3 -m tasks done 1
python3 -m tasks list --all
```

Run the tests with `python3 -m unittest discover -s tests`.
