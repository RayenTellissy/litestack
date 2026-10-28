import os
import subprocess
import sys
import tempfile
import unittest


class SearchAcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, TASKS_FILE=os.path.join(self.dir.name, "tasks.json"))
        self.run_cli("add", "Buy milk", "--tag", "home")
        self.run_cli("add", "Ship release notes", "--tag", "work")
        self.run_cli("add", "buy stamps")
        self.run_cli("add", "Call plumber")
        self.run_cli("done", "4")

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "tasks", *args],
            capture_output=True, text=True, env=self.env, cwd=os.getcwd(),
        )

    def test_matches_ignore_case_in_list_format(self):
        result = self.run_cli("search", "BUY")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "[ ] 1 Buy milk #home\n[ ] 3 buy stamps\n")

    def test_substring_match(self):
        self.assertEqual(self.run_cli("search", "release").stdout, "[ ] 2 Ship release notes #work\n")

    def test_done_tasks_hidden_by_default(self):
        result = self.run_cli("search", "plumber")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "No matching tasks.\n")

    def test_all_includes_done_tasks(self):
        result = self.run_cli("search", "plumber", "--all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "[x] 4 Call plumber\n")

    def test_no_match(self):
        result = self.run_cli("search", "zebra")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "No matching tasks.\n")

    def test_existing_commands_unchanged(self):
        self.assertEqual(
            self.run_cli("list").stdout,
            "[ ] 1 Buy milk #home\n[ ] 2 Ship release notes #work\n[ ] 3 buy stamps\n",
        )


if __name__ == "__main__":
    unittest.main()
