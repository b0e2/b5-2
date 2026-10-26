"""Interactive input loop for Mini Git."""

from mini_git.cli.commands import CommandError, run_command
from mini_git.core.models import MiniGitError
from mini_git.core.repository import Repository


def main() -> None:
    """Keep accepting commands until the user exits or closes input."""
    repository = Repository()
    while True:
        try:
            line = input("mini-git> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        try:
            if not run_command(line, repository):
                break
        except (CommandError, MiniGitError) as exc:
            print(exc)
