"""In-memory commit and branch model for Mini Git."""

from collections import deque
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

    def _get_commit(self, commit_hash: str) -> Commit:
        self._require_init()
        if commit_hash not in self.commits:
            raise MiniGitError(f"Unknown commit: {commit_hash}")
        return self.commits[commit_hash]

    def log(self) -> list[Commit]:
        """Topologically list all commits with every parent before its child."""
        self._require_init()
        children: dict[str, list[str]] = {h: [] for h in self.commits}
        indegree = {h: len(commit.parents) for h, commit in self.commits.items()}
        for commit in self.commits.values():
            for parent in commit.parents:
                children[parent].append(commit.hash)
        ready = deque(h for h in self.commits if indegree[h] == 0)
        result: list[Commit] = []
        while ready:
            current = ready.popleft()
            result.append(self.commits[current])
            for child in children[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
        return result

    def ancestors(self, commit_hash: str) -> list[Commit]:
        """Traverse parent links once per ancestor in O(V+E) time."""
        start = self._get_commit(commit_hash)
        pending = list(start.parents)
        seen: set[str] = set()
        result: list[Commit] = []
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            commit = self.commits[current]
            result.append(commit)
            pending.extend(commit.parents)
        return result

    def path(self, start: str, end: str) -> list[str] | None:
        """Find an undirected shortest path, breaking ties by hash sequence.

        Reverse BFS computes distances in O(V+E); greedy shortest steps
        then select the lexicographically first complete path.
        """
        self._get_commit(start)
        self._get_commit(end)
        neighbors: dict[str, set[str]] = {h: set() for h in self.commits}
        for commit in self.commits.values():
            for parent in commit.parents:
                neighbors[commit.hash].add(parent)
                neighbors[parent].add(commit.hash)
        distance = {end: 0}
        pending = deque([end])
        while pending:
            current = pending.popleft()
            for neighbor in neighbors[current]:
                if neighbor not in distance:
                    distance[neighbor] = distance[current] + 1
                    pending.append(neighbor)
        if start not in distance:
            return None
        route = [start]
        current = start
        while current != end:
            choices = (h for h in neighbors[current] if distance.get(h) == distance[current] - 1)
            current = min(choices)
            route.append(current)
        return route
