import unittest
import subprocess
import tempfile
import os
import sys

class TestTaskman(unittest.TestCase):
    def setUp(self):
        self.temp_store = tempfile.NamedTemporaryFile(delete=False)
        self.temp_store.close()
        self.env = os.environ.copy()
        self.env["TASKMAN_STORE"] = self.temp_store.name
        self.cli = [sys.executable, "taskman.py"]

    def tearDown(self):
        os.unlink(self.temp_store.name)

    def run_cli(self, *args):
        result = subprocess.run(
            self.cli + list(args),
            env=self.env,
            capture_output=True,
            text=True
        )
        return result

    def test_list_empty(self):
        res = self.run_cli("list")
        self.assertEqual(res.returncode, 0)
        self.assertIn("No tasks found.", res.stdout)

    def test_add_task(self):
        res = self.run_cli("add", "Buy milk")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Added task 1", res.stdout)

    def test_list_tasks(self):
        self.run_cli("add", "Buy milk")
        res = self.run_cli("list")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Buy milk", res.stdout)
        self.assertIn("pending", res.stdout)

    def test_add_multiple_tasks(self):
        self.run_cli("add", "Task A")
        self.run_cli("add", "Task B")
        res = self.run_cli("list")
        self.assertIn("Task A", res.stdout)
        self.assertIn("Task B", res.stdout)
        self.assertIn("1    ", res.stdout)
        self.assertIn("2    ", res.stdout)

    def test_done_task(self):
        self.run_cli("add", "Task A")
        res = self.run_cli("done", "1")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Task 1 marked as done.", res.stdout)
        
        res_list = self.run_cli("list")
        self.assertNotIn("Task A", res_list.stdout) # Should not show in default list

    def test_list_all_tasks(self):
        self.run_cli("add", "Task A")
        self.run_cli("done", "1")
        res = self.run_cli("list", "--all")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Task A", res.stdout)
        self.assertIn("done", res.stdout)

    def test_done_task_not_found(self):
        res = self.run_cli("done", "999")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Task 999 not found.", res.stderr)

    def test_rm_task(self):
        self.run_cli("add", "Task A")
        res = self.run_cli("rm", "1")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Task 1 removed.", res.stdout)
        
        res_list = self.run_cli("list", "--all")
        self.assertNotIn("Task A", res_list.stdout)

    def test_rm_task_not_found(self):
        res = self.run_cli("rm", "999")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Task 999 not found.", res.stderr)

    def test_stats_empty(self):
        res = self.run_cli("stats")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Total     : 0", res.stdout)
        self.assertIn("Pending   : 0", res.stdout)
        self.assertIn("Done      : 0", res.stdout)

    def test_stats_populated(self):
        self.run_cli("add", "Task A")
        self.run_cli("add", "Task B")
        self.run_cli("done", "1")
        res = self.run_cli("stats")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Total     : 2", res.stdout)
        self.assertIn("Pending   : 1", res.stdout)
        self.assertIn("Done      : 1", res.stdout)

if __name__ == "__main__":
    unittest.main()
