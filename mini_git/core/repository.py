"""In-memory commit, branch, and search state."""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from mini_git.algorithms.graph import (
    collect_ancestors,
    parent_first,
    shortest_path,
)
from mini_git.algorithms.sorting import merge_sort
from mini_git.core.index import SearchIndex
from mini_git.core.models import Commit, MiniGitError


class Repository:
    """Store commits by ID and branches by their current HEAD."""

    def __init__(self) -> None:
        self.next_id = 1
        self.initialized = False
        self.commits: Dict[str, Commit] = {}
        self.branches: Dict[str, Optional[str]] = {}
        self.current_branch = ""
        self.current_user = ""
        self._index = SearchIndex()

    @property
    def keyword_index(self) -> Dict[str, Set[str]]:
        """Expose keyword postings for compatibility and inspection."""
        return self._index.keywords

    @property
    def author_index(self) -> Dict[str, Set[str]]:
        """Expose author postings for compatibility and inspection."""
        return self._index.authors

    def init(self, user_name: str) -> None:
        """Start a new repository without reusing an earlier session ID."""
        if not user_name:
            raise MiniGitError("Invalid args")
        self.commits.clear()
        self._index.clear()
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
            raise MiniGitError("Branch already exists: {}".format(name))
        self.branches[name] = self.branches[self.current_branch]

    def switch(self, name: str) -> None:
        """Point HEAD at an existing branch."""
        self._require_init()
        if name not in self.branches:
            raise MiniGitError("Unknown branch: {}".format(name))
        self.current_branch = name

    def _create_commit(self, message: str, parents: Tuple[str, ...]) -> Commit:
        """Add a node whose parents already exist, preserving the DAG."""
        self._require_init()
        if not message:
            raise MiniGitError("Invalid args")
        if len(parents) != len(set(parents)):
            raise MiniGitError("Invalid args")
        for parent in parents:
            if parent not in self.commits:
                raise MiniGitError("Unknown commit: {}".format(parent))

        commit_hash = "{:08x}".format(self.next_id)
        self.next_id += 1
        new_commit = Commit(
            commit_hash,
            message,
            self.current_user,
            datetime.now(),
            parents,
        )
        self.commits[commit_hash] = new_commit
        self.branches[self.current_branch] = commit_hash
        self._index.add(new_commit)
        return new_commit

    def commit(self, message: str) -> Commit:
        """Create a commit with the current HEAD as its only parent, if any."""
        self._require_init()
        head = self.branches[self.current_branch]
        parents = () if head is None else (head,)
        return self._create_commit(message, parents)

    def merge(self, branch_name: str) -> Commit:
        """Create a metadata-only commit with current and target HEADs as parents."""
        self._require_init()
        if branch_name not in self.branches:
            raise MiniGitError("Unknown branch: {}".format(branch_name))
        if branch_name == self.current_branch:
            raise MiniGitError("Cannot merge a branch into itself")
        current_head = self.branches[self.current_branch]
        target_head = self.branches[branch_name]
        if current_head is None or target_head is None:
            raise MiniGitError("Cannot merge an empty branch")
        if current_head == target_head:
            raise MiniGitError("Branches already share the same HEAD")
        return self._create_commit(
            "Merge branch '{}' into {}".format(
                branch_name,
                self.current_branch,
            ),
            (current_head, target_head),
        )

    def _get_commit(self, commit_hash: str) -> Commit:
        self._require_init()
        if commit_hash not in self.commits:
            raise MiniGitError("Unknown commit: {}".format(commit_hash))
        return self.commits[commit_hash]

    def log(self, sort_by: Optional[str] = None) -> List[Commit]:
        """List parents first, or sort by date/author using merge sort."""
        self._require_init()
        if sort_by == "date":
            return merge_sort(
                list(self.commits.values()),
                lambda commit: commit.timestamp,
            )
        if sort_by == "author":
            return merge_sort(
                list(self.commits.values()),
                lambda commit: commit.author,
            )
        if sort_by is not None:
            raise MiniGitError("Invalid args")
        return parent_first(self.commits)

    def ancestors(self, commit_hash: str) -> List[Commit]:
        """Return every ancestor once by following parent references."""
        return collect_ancestors(
            self.commits,
            self._get_commit(commit_hash),
        )

    def path(self, start: str, end: str) -> Optional[List[str]]:
        """Find an undirected shortest path with a lexicographic tie break."""
        self._get_commit(start)
        self._get_commit(end)
        return shortest_path(self.commits, start, end)

    def search_keyword(self, keyword: str) -> List[Commit]:
        """Find indexed token or contiguous phrase matches."""
        self._require_init()
        return self._index.search_keyword(keyword, self.commits)

    def search_author(self, author: str) -> List[Commit]:
        """Find commits whose author matches exactly."""
        self._require_init()
        return self._index.search_author(author, self.commits)
