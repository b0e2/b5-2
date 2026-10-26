"""Executable entry point and compatibility imports for Mini Git."""

from mini_git.cli.commands import CommandError, format_commit, run_command
from mini_git.cli.repl import main


__all__ = ["CommandError", "format_commit", "main", "run_command"]


if __name__ == "__main__":
    main()
