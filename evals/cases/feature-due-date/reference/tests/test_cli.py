import os
import subprocess
import sys
import tempfile
import unittest


class CliTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, TASKS_FILE=os.path.join(self.dir.name, "tasks.json"))

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "tasks", *args],
            capture_output=True, text=True, env=self.env,
        )

    def test_add_then_list(self):
        self.run_cli("add", "Buy milk", "--tag", "home")
        self.run_cli("add", "File taxes")
        out = self.run_cli("list").stdout
        self.assertEqual(out, "[ ] 1 Buy milk #home\n[ ] 2 File taxes\n")

    def test_done_hides_task_unless_all(self):
        self.run_cli("add", "Buy milk")
        self.run_cli("done", "1")
        self.assertEqual(self.run_cli("list").stdout, "No tasks.\n")
        self.assertEqual(self.run_cli("list", "--all").stdout, "[x] 1 Buy milk\n")

    def test_list_by_tag(self):
        self.run_cli("add", "Buy milk", "--tag", "home")
        self.run_cli("add", "Ship release", "--tag", "work")
        self.assertEqual(self.run_cli("list", "--tag", "work").stdout, "[ ] 2 Ship release #work\n")

    def test_due_date_prints_after_tags(self):
        self.run_cli("add", "Buy milk", "--tag", "home", "--due", "2026-11-01")
        self.assertEqual(self.run_cli("list").stdout, "[ ] 1 Buy milk #home due 2026-11-01\n")

    def test_overdue_lists_open_tasks_due_before_today(self):
        self.run_cli("add", "Renew passport", "--due", "2000-01-01")
        self.run_cli("add", "Plan trip", "--due", "2999-12-31")
        self.assertEqual(self.run_cli("list", "--overdue").stdout, "[ ] 1 Renew passport due 2000-01-01\n")

    def test_invalid_due_date_stores_nothing(self):
        result = self.run_cli("add", "Buy milk", "--due", "2026-02-30")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.run_cli("list").stdout, "No tasks.\n")

    def test_done_unknown_id(self):
        result = self.run_cli("done", "9")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "No task 9.\n")


if __name__ == "__main__":
    unittest.main()
