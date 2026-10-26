"""Longest-common-subsequence line comparison."""

from pathlib import Path
from typing import List, Tuple

from mini_git.core.models import MiniGitError


LineChange = Tuple[str, str]


def diff_lines(before: List[str], after: List[str]) -> List[LineChange]:
    """Mark common, deleted, and added lines with LCS dynamic programming."""
    rows, columns = len(before), len(after)
    length = [[0] * (columns + 1) for _ in range(rows + 1)]
    for i in range(rows - 1, -1, -1):
        for j in range(columns - 1, -1, -1):
            if before[i] == after[j]:
                length[i][j] = length[i + 1][j + 1] + 1
            else:
                length[i][j] = max(length[i + 1][j], length[i][j + 1])

    result: List[LineChange] = []
    i = j = 0
    while i < rows or j < columns:
        if i < rows and j < columns and before[i] == after[j]:
            result.append((" ", before[i]))
            i += 1
            j += 1
        elif i < rows and (
            j == columns or length[i + 1][j] >= length[i][j + 1]
        ):
            result.append(("-", before[i]))
            i += 1
        else:
            result.append(("+", after[j]))
            j += 1
    return result


def compare_files(before_path: str, after_path: str) -> List[LineChange]:
    """Read UTF-8 files and compare their lines."""
    def read_lines(file_path: str) -> List[str]:
        try:
            return Path(file_path).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            raise MiniGitError("Cannot read file: {}".format(file_path)) from exc

    return diff_lines(read_lines(before_path), read_lines(after_path))
