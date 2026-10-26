"""Parse, validate, execute, and print one Mini Git command."""

import shlex
from typing import Callable, Dict, List, Optional

from mini_git.algorithms.diff import compare_files
from mini_git.core.models import Commit
from mini_git.core.repository import Repository


class CommandError(Exception):
    """An input error that can be shown to the user."""


def format_commit(commit: Commit) -> str:
    """Show a commit's ID, author, time, and message."""
    timestamp = commit.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return "commit {} ({}, {})\n{}".format(
        commit.hash,
        commit.author,
        timestamp,
        commit.message,
    )


def _require_count(args: List[str], count: int) -> None:
    if len(args) != count:
        raise CommandError("Invalid args")


def _exit(args: List[str], repository: Repository) -> bool:
    _require_count(args, 0)
    return False


def _init(args: List[str], repository: Repository) -> bool:
    _require_count(args, 1)
    repository.init(args[0])
    print(
        "Initialized repository.\nCurrent branch: main\nCurrent user: {}".format(
            repository.current_user,
        )
    )
    return True


def _branch(args: List[str], repository: Repository) -> bool:
    _require_count(args, 1)
    repository.branch(args[0])
    print("Created branch: {}".format(args[0]))
    return True


def _switch(args: List[str], repository: Repository) -> bool:
    _require_count(args, 1)
    repository.switch(args[0])
    print("Switched to branch: {}".format(args[0]))
    return True


def _commit(args: List[str], repository: Repository) -> bool:
    _require_count(args, 1)
    commit = repository.commit(args[0])
    print("[{} {}] {}".format(
        repository.current_branch,
        commit.hash,
        commit.message,
    ))
    return True


def _merge(args: List[str], repository: Repository) -> bool:
    _require_count(args, 1)
    commit = repository.merge(args[0])
    print("[{} {}] {}".format(
        repository.current_branch,
        commit.hash,
        commit.message,
    ))
    return True


def _log(args: List[str], repository: Repository) -> bool:
    if not args:
        commits = repository.log()
    elif len(args) == 1 and args[0] in (
        "--sort-by=date",
        "--sort-by=author",
    ):
        commits = repository.log(args[0].split("=", 1)[1])
    else:
        raise CommandError("Invalid args")
    print("\n".join(format_commit(commit) for commit in commits) or "No commits")
    return True


def _ancestors(args: List[str], repository: Repository) -> bool:
    _require_count(args, 1)
    commits = repository.ancestors(args[0])
    print("\n".join(format_commit(commit) for commit in commits) or "No ancestors")
    return True


def _path(args: List[str], repository: Repository) -> bool:
    _require_count(args, 2)
    route = repository.path(args[0], args[1])
    print("Path: " + " -> ".join(route) if route is not None else "No path")
    return True


def _search(args: List[str], repository: Repository) -> bool:
    _require_count(args, 1)
    if args[0].startswith("--author="):
        author = args[0][len("--author="):]
        if not author:
            raise CommandError("Invalid args")
        commits = repository.search_author(author)
    elif args[0].startswith("--"):
        raise CommandError("Invalid args")
    else:
        commits = repository.search_keyword(args[0])
    print(
        "\n".join(
            "- {}: {}".format(commit.hash, commit.message)
            for commit in commits
        ) or "No commits found"
    )
    return True


def _diff(args: List[str], repository: Repository) -> bool:
    _require_count(args, 2)
    changes = compare_files(args[0], args[1])
    print(
        "\n".join("{} {}".format(kind, line) for kind, line in changes)
        or "No differences"
    )
    return True


CommandHandler = Callable[[List[str], Repository], bool]

COMMANDS: Dict[str, CommandHandler] = {
    "EXIT": _exit,
    "QUIT": _exit,
    "INIT": _init,
    "BRANCH": _branch,
    "SWITCH": _switch,
    "COMMIT": _commit,
    "MERGE": _merge,
    "LOG": _log,
    "ANCESTORS": _ancestors,
    "PATH": _path,
    "SEARCH": _search,
    "DIFF": _diff,
}


def run_command(
    line: str,
    repository: Optional[Repository] = None,
) -> bool:
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
    handler = COMMANDS.get(command.upper())
    if handler is None:
        raise CommandError("Unknown command: {}".format(command))
    return handler(args, repository)
