"""End-to-end CLI sessions with real process input and output."""

import subprocess
import sys
import unittest
from pathlib import Path


MAIN = Path(__file__).resolve().parents[1] / "main.py"


def run_session(*commands: str) -> str:
    """Run a complete Mini Git session and return its output."""
    result = subprocess.run(
        [sys.executable, str(MAIN)],
        input="\n".join(commands) + "\n",
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


class CliFlowTests(unittest.TestCase):
    def test_branch_search_and_graph_session(self) -> None:
        output = run_session(
            'init "Alice Bob"',
            'commit "Initial commit"',
            'branch feature',
            'switch feature',
            'commit "Add login feature"',
            'switch main',
            'commit "Add payment feature"',
            'log',
            'path 00000002 00000003',
            'ancestors 00000002',
            'search "login feature"',
            'search --author="Alice Bob"',
            'log --sort-by=author',
            'log --sort-by=date',
            'quit',
        )
        self.assertIn("[main 00000001] Initial commit", output)
        self.assertIn("[feature 00000002] Add login feature", output)
        self.assertIn("Path: 00000002 -> 00000001 -> 00000003", output)
        self.assertIn("- 00000002: Add login feature", output)
        self.assertIn("commit 00000003 (Alice Bob,", output)
        first_log = output.index("commit 00000001 (Alice Bob,")
        child_log = output.index("commit 00000002 (Alice Bob,")
        self.assertLess(first_log, child_log)

    def test_errors_empty_state_and_recovery(self) -> None:
        output = run_session(
            'log',
            'init Alice',
            'log',
            'path unknown other',
            'search --author=',
            'log --sort-by=message',
            'commit "recovered"',
            'exit',
        )
        self.assertIn("Repository not initialized", output)
        self.assertIn("No commits", output)
        self.assertIn("Unknown commit: unknown", output)
        self.assertGreaterEqual(output.count("Invalid args"), 2)
        self.assertIn("[main 00000001] recovered", output)


if __name__ == "__main__":
    unittest.main()
