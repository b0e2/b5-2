"""Line-by-line comparison for two local text files."""

from pathlib import Path

from mini_git import MiniGitError


def diff_lines(before: list[str], after: list[str]) -> list[tuple[str, str]]:
    """Use longest common subsequence to mark common, deleted, and added lines."""
    rows, columns = len(before), len(after)
    length = [[0] * (columns + 1) for _ in range(rows + 1)]
    for i in range(rows - 1, -1, -1):
        for j in range(columns - 1, -1, -1):
            if before[i] == after[j]:
                length[i][j] = length[i + 1][j + 1] + 1
            else:
                length[i][j] = max(length[i + 1][j], length[i][j + 1])

    result: list[tuple[str, str]] = []
    i = j = 0
    while i < rows or j < columns:
        if i < rows and j < columns and before[i] == after[j]:
            result.append((" ", before[i]))
            i += 1
            j += 1
        elif i < rows and (j == columns or length[i + 1][j] >= length[i][j + 1]):
            result.append(("-", before[i]))
            i += 1
        else:
            result.append(("+", after[j]))
            j += 1
    return result


def compare_files(before_path: str, after_path: str) -> list[tuple[str, str]]:
    """Read UTF-8 files and compare their lines."""
    def read_lines(file_path: str) -> list[str]:
        try:
            return Path(file_path).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            raise MiniGitError(f"Cannot read file: {file_path}") from exc

    return diff_lines(read_lines(before_path), read_lines(after_path))
