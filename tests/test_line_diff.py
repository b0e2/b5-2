"""Tests for local text-file line comparison."""

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from line_diff import compare_files, diff_lines
from main import CommandError, run_command
from mini_git import MiniGitError


class LineDiffTests(unittest.TestCase):
    def test_common_deleted_and_added_with_repeated_lines(self) -> None:
        self.assertEqual(
            diff_lines(["one", "same", "old", "same"], ["one", "same", "new", "same"]),
            [(" ", "one"), (" ", "same"), ("-", "old"), ("+", "new"), (" ", "same")],
        )
        self.assertEqual(diff_lines([], ["added"]), [("+", "added")])
        self.assertEqual(diff_lines(["removed"], []), [("-", "removed")])
        self.assertEqual(diff_lines([], []), [])

    def test_files_and_quoted_cli_paths(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            before = Path(folder) / "old notes.txt"
            after = Path(folder) / "new notes.txt"
            before.write_text("same\nold\n", encoding="utf-8")
            after.write_text("same\nnew\n", encoding="utf-8")
            self.assertEqual(compare_files(str(before), str(after)),
                             [(" ", "same"), ("-", "old"), ("+", "new")])
            output = StringIO()
            with redirect_stdout(output):
                run_command(f'diff "{before}" "{after}"')
            self.assertIn("  same\n- old\n+ new", output.getvalue())
            with self.assertRaisesRegex(MiniGitError, "Cannot read file"):
                compare_files(str(before), str(before) + ".missing")

    def test_invalid_cli_args(self) -> None:
        with self.assertRaisesRegex(CommandError, "Invalid args"):
            run_command("diff only-one")


if __name__ == "__main__":
    unittest.main()
