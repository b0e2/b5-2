"""Tests for the Mini Git REPL."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from main import CommandError, main, run_command


class CommandTests(unittest.TestCase):
    def test_exit_and_quit_ignore_case(self) -> None:
        self.assertFalse(run_command("ExIt"))
        self.assertFalse(run_command("QUIT"))
        self.assertTrue(run_command("  "))

    def test_quoted_input_and_invalid_arguments(self) -> None:
        with self.assertRaisesRegex(CommandError, "Unknown command: commit"):
            run_command('commit "Add login feature"')
        for text in ('commit "unfinished', "exit now", "quit extra"):
            with self.subTest(text=text), self.assertRaisesRegex(CommandError, "Invalid args"):
                run_command(text)

    def test_repl_recovers_from_errors_and_stops_on_eof(self) -> None:
        output = StringIO()
        with patch("builtins.input", side_effect=["unknown", "quit extra", EOFError]), redirect_stdout(output):
            main()
        self.assertIn("Unknown command: unknown", output.getvalue())
        self.assertIn("Invalid args", output.getvalue())


if __name__ == "__main__":
    unittest.main()
