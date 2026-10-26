"""Tests for the Mini Git REPL."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from main import CommandError, main, run_command
from mini_git import MiniGitError, Repository


class CommandTests(unittest.TestCase):
    def test_exit_and_quit_ignore_case(self) -> None:
        self.assertFalse(run_command("ExIt"))
        self.assertFalse(run_command("QUIT"))
        self.assertTrue(run_command("  "))

    def test_quoted_input_and_invalid_arguments(self) -> None:
        repository = Repository()
        output = StringIO()
        with redirect_stdout(output):
            run_command('init "Alice Bob"', repository)
            run_command('commit "Add login feature"', repository)
        self.assertIn("Alice Bob", output.getvalue())
        self.assertIn("Add login feature", output.getvalue())
        for text in ('commit "unfinished', "exit now", "quit extra", "branch x y"):
            with self.subTest(text=text), self.assertRaisesRegex(CommandError, "Invalid args"):
                run_command(text, repository)
        with self.assertRaisesRegex(MiniGitError, "Unknown branch: missing"):
            run_command("switch missing", repository)

    def test_argument_errors_precede_repository_errors(self) -> None:
        repository = Repository()
        with self.assertRaisesRegex(CommandError, "Invalid args"):
            run_command("commit", repository)
        with self.assertRaisesRegex(MiniGitError, "Repository not initialized"):
            run_command("commit message", repository)
        repository.init("Alice")
        with self.assertRaisesRegex(MiniGitError, "Invalid args"):
            run_command('search ""', repository)
        with self.assertRaisesRegex(CommandError, "Unknown command: HeLp"):
            run_command("HeLp", repository)

    def test_repl_recovers_from_errors_and_stops_on_eof(self) -> None:
        output = StringIO()
        with patch("builtins.input", side_effect=["unknown", "quit extra", EOFError]), redirect_stdout(output):
            main()
        self.assertIn("Unknown command: unknown", output.getvalue())
        self.assertIn("Invalid args", output.getvalue())


if __name__ == "__main__":
    unittest.main()
