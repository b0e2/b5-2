"""Stable sorting algorithms implemented without standard sorting APIs."""

from typing import Callable, List, TypeVar


T = TypeVar("T")


def merge_sort(items: List[T], key: Callable[[T], object]) -> List[T]:
    """Return a stable sorted copy in O(n log n) time and O(n) space."""
    if len(items) < 2:
        return items[:]
    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    result: List[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def insertion_sort(items: List[T], key: Callable[[T], object]) -> List[T]:
    """Return a stable sorted copy in O(n²) average/worst time."""
    result = items[:]
    for i in range(1, len(result)):
        item = result[i]
        item_key = key(item)
        j = i - 1
        while j >= 0 and key(result[j]) > item_key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = item
    return result
