"""Public API for the Mini Git package."""

from mini_git.algorithms.diff import compare_files, diff_lines
from mini_git.algorithms.sorting import insertion_sort, merge_sort
from mini_git.core.models import Commit, MiniGitError
from mini_git.core.repository import Repository


__all__ = [
    "Commit",
    "MiniGitError",
    "Repository",
    "compare_files",
    "diff_lines",
    "insertion_sort",
    "merge_sort",
]
