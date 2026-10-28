import json
import os
import subprocess
import sys
import tempfile
import unittest


class DueDateAcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.file = os.path.join(self.dir.name, "tasks.json")
        self.env = dict(os.environ, TASKS_FILE=self.file)

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "tasks", *args],
            capture_output=True, text=True, env=self.env, cwd=os.getcwd(),
        )

    def test_due_date_prints_after_tags(self):
        result = self.run_cli("add", "Buy milk", "--tag", "home", "--due", "2026-11-01")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.run_cli("add", "File taxes", "--due", "2027-04-15")
        self.assertEqual(
            self.run_cli("list").stdout,
            "[ ] 1 Buy milk #home due 2026-11-01\n[ ] 2 File taxes due 2027-04-15\n",
        )

    def test_tasks_without_due_date_print_as_before(self):
        self.run_cli("add", "Buy milk", "--tag", "home")
        self.run_cli("add", "Call mom", "--due", "2026-11-01")
        self.assertEqual(self.run_cli("list").stdout, "[ ] 1 Buy milk #home\n[ ] 2 Call mom due 2026-11-01\n")

    def test_due_date_survives_later_saves(self):
        self.run_cli("add", "Buy milk", "--due", "2026-11-01")
        self.run_cli("add", "Call mom")
        self.run_cli("done", "2")
        self.assertEqual(self.run_cli("list", "--all").stdout, "[ ] 1 Buy milk due 2026-11-01\n[x] 2 Call mom\n")

    def test_file_from_before_the_change_still_loads(self):
        with open(self.file, "w") as f:
            json.dump([{"id": 1, "title": "Old task", "done": False, "tags": ["home"]}], f)
        self.assertEqual(self.run_cli("list").stdout, "[ ] 1 Old task #home\n")
        result = self.run_cli("add", "New task", "--due", "2026-11-01")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.run_cli("list").stdout, "[ ] 1 Old task #home\n[ ] 2 New task due 2026-11-01\n")

    def test_overdue_lists_only_open_tasks_due_before_today(self):
        self.run_cli("add", "Renew passport", "--due", "2000-01-01")
        self.run_cli("add", "Plan trip", "--due", "2999-12-31")
        self.run_cli("add", "No date")
        self.run_cli("add", "Pay old bill", "--due", "2000-01-01")
        self.run_cli("done", "4")
        result = self.run_cli("list", "--overdue")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "[ ] 1 Renew passport due 2000-01-01\n")

    def test_overdue_with_nothing_overdue(self):
        self.run_cli("add", "Plan trip", "--due", "2999-12-31")
        self.assertEqual(self.run_cli("list", "--overdue").stdout, "No tasks.\n")

    def test_invalid_date_is_rejected_and_nothing_stored(self):
        for value in ("2026-02-30", "tomorrow"):
            result = self.run_cli("add", "Buy milk", "--due", value)
            self.assertEqual(result.returncode, 2, value)
            self.assertIn(value, result.stderr)
        self.assertEqual(self.run_cli("list").stdout, "No tasks.\n")

    def test_existing_commands_unchanged(self):
        self.run_cli("add", "Buy milk", "--tag", "home")
        self.run_cli("add", "Ship release", "--tag", "work")
        self.run_cli("done", "1")
        self.assertEqual(self.run_cli("list").stdout, "[ ] 2 Ship release #work\n")
        self.assertEqual(self.run_cli("list", "--all", "--tag", "home").stdout, "[x] 1 Buy milk #home\n")


if __name__ == "__main__":
    unittest.main()
