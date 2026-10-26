"""Core data types shared by Mini Git features."""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


class MiniGitError(Exception):
    """A repository error that can be shown to the user."""


@dataclass(frozen=True)
class Commit:
    """Immutable commit metadata and parent references."""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: Tuple[str, ...]
