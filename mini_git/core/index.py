"""Inverted indexes for commit messages and authors."""

from typing import Dict, List, Set

from mini_git.algorithms.sorting import merge_sort
from mini_git.core.models import Commit, MiniGitError


class SearchIndex:
    """Map normalized tokens and exact authors to commit IDs."""

    def __init__(self) -> None:
        self.keywords: Dict[str, Set[str]] = {}
        self.authors: Dict[str, Set[str]] = {}

    def clear(self) -> None:
        """Remove every posting list."""
        self.keywords.clear()
        self.authors.clear()

    def add(self, commit: Commit) -> None:
        """Index one newly created commit."""
        for token in set(commit.message.lower().split()):
            self.keywords.setdefault(token, set()).add(commit.hash)
        self.authors.setdefault(commit.author, set()).add(commit.hash)

    @staticmethod
    def _contains_tokens(message: List[str], query: List[str]) -> bool:
        return any(
            message[index:index + len(query)] == query
            for index in range(len(message) - len(query) + 1)
        )

    def search_keyword(
        self,
        keyword: str,
        commits: Dict[str, Commit],
    ) -> List[Commit]:
        """Intersect token postings and retain contiguous phrase matches."""
        tokens = keyword.lower().split()
        if not tokens:
            raise MiniGitError("Invalid args")
        candidates = self.keywords.get(tokens[0], set()).copy()
        for token in tokens[1:]:
            candidates.intersection_update(self.keywords.get(token, set()))
        hashes = merge_sort(list(candidates), lambda value: int(value, 16))
        return [
            commits[commit_hash]
            for commit_hash in hashes
            if self._contains_tokens(
                commits[commit_hash].message.lower().split(),
                tokens,
            )
        ]

    def search_author(
        self,
        author: str,
        commits: Dict[str, Commit],
    ) -> List[Commit]:
        """Return an exact-author posting list in commit ID order."""
        if not author:
            raise MiniGitError("Invalid args")
        hashes = merge_sort(
            list(self.authors.get(author, set())),
            lambda value: int(value, 16),
        )
        return [commits[commit_hash] for commit_hash in hashes]
