"""Compare two locally implemented stable sorting algorithms."""

from random import Random
from time import perf_counter

from mini_git.algorithms.sorting import insertion_sort, merge_sort


SIZES = (100, 500, 1000, 2000)
REPEATS = 5


def measure(items, algorithm) -> float:
    """Return mean elapsed milliseconds; exclude input generation."""
    elapsed = 0.0
    for _ in range(REPEATS):
        start = perf_counter()
        algorithm(items, lambda value: value)
        elapsed += perf_counter() - start
    return elapsed * 1000 / REPEATS


def main() -> None:
    """Print per-size timings from identical seeded inputs."""
    random = Random(42)
    print(
        "seed=42, repetitions={}, milliseconds (lower is faster)".format(
            REPEATS,
        )
    )
    print("size  merge sort  insertion sort")
    for size in SIZES:
        items = [random.randrange(size // 4) for _ in range(size)]
        if merge_sort(items, lambda value: value) != insertion_sort(
            items,
            lambda value: value,
        ):
            raise AssertionError("Sorting algorithms disagree")
        merge_ms = measure(items, merge_sort)
        insertion_ms = measure(items, insertion_sort)
        print("{:4d}  {:10.3f}  {:14.3f}".format(
            size,
            merge_ms,
            insertion_ms,
        ))
    print(
        "merge: average/worst O(n log n), stable; "
        "insertion: average/worst O(n²), stable"
    )


if __name__ == "__main__":
    main()
