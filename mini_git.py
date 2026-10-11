"""In-memory commit and branch model for Mini Git."""

from dataclasses import dataclass
from datetime import datetime


class MiniGitError(Exception):
    """A repository error that can be shown to the user."""


@dataclass(frozen=True)
class Commit:
    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple[str, ...]


class Repository:
    """Store commits by ID and branches by their current HEAD."""

    def __init__(self) -> None:
        self.next_id = 1
        self.initialized = False
        self.commits: dict[str, Commit] = {}
        self.branches: dict[str, str | None] = {}
        self.current_branch = ""
        self.current_user = ""

    def init(self, user_name: str) -> None:
        """Start a new repository without reusing an earlier session ID."""
        if not user_name:
            raise MiniGitError("Invalid args")
        self.commits.clear()
        self.branches = {"main": None}
        self.current_branch = "main"
        self.current_user = user_name
        self.initialized = True

    def _require_init(self) -> None:
        if not self.initialized:
            raise MiniGitError("Repository not initialized")

    def branch(self, name: str) -> None:
        """Copy the current HEAD pointer to a new branch."""
        self._require_init()
        if not name:
            raise MiniGitError("Invalid args")
        if name in self.branches:
            raise MiniGitError(f"Branch already exists: {name}")
        self.branches[name] = self.branches[self.current_branch]

    def switch(self, name: str) -> None:
        """Point HEAD at an existing branch."""
        self._require_init()
        if name not in self.branches:
            raise MiniGitError(f"Unknown branch: {name}")
        self.current_branch = name

    def _create_commit(self, message: str, parents: tuple[str, ...]) -> Commit:
        """Add a node whose parents already exist, preserving the DAG."""
        self._require_init()
        if not message:
            raise MiniGitError("Invalid args")
        if len(parents) != len(set(parents)):
            raise MiniGitError("Invalid args")
        for parent in parents:
            if parent not in self.commits:
                raise MiniGitError(f"Unknown commit: {parent}")
        commit_hash = f"{self.next_id:08x}"
        self.next_id += 1
        new_commit = Commit(commit_hash, message, self.current_user, datetime.now(), parents)
        self.commits[commit_hash] = new_commit
        self.branches[self.current_branch] = commit_hash
        return new_commit

    def commit(self, message: str) -> Commit:
        """Create a commit with the current HEAD as its only parent, if any."""
        self._require_init()
        head = self.branches[self.current_branch]
        parents = () if head is None else (head,)
        return self._create_commit(message, parents)
