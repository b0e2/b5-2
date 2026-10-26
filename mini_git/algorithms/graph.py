"""Graph algorithms over immutable commit parent references."""

from collections import deque
from typing import Dict, List, Optional, Set

from mini_git.core.models import Commit


def parent_first(commits: Dict[str, Commit]) -> List[Commit]:
    """Return every commit after all of its parents in O(V+E) time."""
    children: Dict[str, List[str]] = {commit_hash: [] for commit_hash in commits}
    indegree = {
        commit_hash: len(commit.parents)
        for commit_hash, commit in commits.items()
    }
    for commit in commits.values():
        for parent in commit.parents:
            children[parent].append(commit.hash)

    ready = deque(
        commit_hash
        for commit_hash in commits
        if indegree[commit_hash] == 0
    )
    result: List[Commit] = []
    while ready:
        current = ready.popleft()
        result.append(commits[current])
        for child in children[current]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
    return result


def collect_ancestors(commits: Dict[str, Commit], start: Commit) -> List[Commit]:
    """Traverse each ancestor once by following parent references."""
    pending = list(start.parents)
    seen: Set[str] = set()
    result: List[Commit] = []
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        commit = commits[current]
        result.append(commit)
        pending.extend(commit.parents)
    return result


def shortest_path(
    commits: Dict[str, Commit],
    start: str,
    end: str,
) -> Optional[List[str]]:
    """Find an undirected shortest path with a lexicographic tie break."""
    neighbors: Dict[str, Set[str]] = {
        commit_hash: set()
        for commit_hash in commits
    }
    for commit in commits.values():
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
        choices = (
            commit_hash
            for commit_hash in neighbors[current]
            if distance.get(commit_hash) == distance[current] - 1
        )
        current = min(choices)
        route.append(current)
    return route
