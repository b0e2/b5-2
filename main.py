"""Command-line interface for Mini Git."""

import shlex

from mini_git import Commit, MiniGitError, Repository


def format_commit(commit: Commit) -> str:
    """Show a commit's ID, author, time, and message."""
    timestamp = commit.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return f"commit {commit.hash} ({commit.author}, {timestamp})\n{commit.message}"


class CommandError(Exception):
    """An error that can be shown to the user."""


def run_command(line: str, repository: Repository | None = None) -> bool:
    """Parse one command; return False to leave the REPL."""
    if repository is None:
        repository = Repository()
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        raise CommandError("Invalid args") from exc
    if not parts:
        return True

    command, *args = parts
    command = command.upper()
    if command in ("EXIT", "QUIT"):
        if args:
            raise CommandError("Invalid args")
        return False
    if command == "INIT" and len(args) == 1:
        repository.init(args[0])
        print(f"Initialized repository.\nCurrent branch: main\nCurrent user: {repository.current_user}")
        return True
    if command == "BRANCH" and len(args) == 1:
        repository.branch(args[0])
        print(f"Created branch: {args[0]}")
        return True
    if command == "SWITCH" and len(args) == 1:
        repository.switch(args[0])
        print(f"Switched to branch: {args[0]}")
        return True
    if command == "COMMIT" and len(args) == 1:
        commit = repository.commit(args[0])
        print(f"[{repository.current_branch} {commit.hash}] {commit.message}")
        return True
    if command == "LOG" and not args:
        commits = repository.log()
        print("\n".join(format_commit(commit) for commit in commits) or "No commits")
        return True
    if command == "ANCESTORS" and len(args) == 1:
        commits = repository.ancestors(args[0])
        print("\n".join(format_commit(commit) for commit in commits) or "No ancestors")
        return True
    if command == "PATH" and len(args) == 2:
        route = repository.path(args[0], args[1])
        print("Path: " + " -> ".join(route) if route is not None else "No path")
        return True
    if command in {"INIT", "BRANCH", "SWITCH", "COMMIT", "LOG", "ANCESTORS", "PATH"}:
        raise CommandError("Invalid args")
    raise CommandError(f"Unknown command: {parts[0]}")


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


if __name__ == "__main__":
    main()
