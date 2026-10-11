"""Tests for the alternate sort and benchmark output."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import benchmark_sort
from mini_git import insertion_sort, merge_sort


class SortBenchmarkTests(unittest.TestCase):
    def test_algorithms_are_stable_and_preserve_input(self) -> None:
        items = [(2, "first"), (1, "a"), (2, "second"), (1, "b")]
        expected = [(1, "a"), (1, "b"), (2, "first"), (2, "second")]
        for algorithm in (merge_sort, insertion_sort):
            self.assertEqual(algorithm(items, lambda item: item[0]), expected)
            self.assertEqual(algorithm([], lambda item: item), [])
            self.assertEqual(algorithm([4, 3, 2, 1], lambda item: item), [1, 2, 3, 4])
        self.assertEqual(items, [(2, "first"), (1, "a"), (2, "second"), (1, "b")])

    def test_benchmark_reports_same_sizes_and_complexities(self) -> None:
        output = StringIO()
        with patch.object(benchmark_sort, "SIZES", (10, 20)), \
                patch.object(benchmark_sort, "REPEATS", 2), redirect_stdout(output):
            benchmark_sort.main()
        text = output.getvalue()
        self.assertIn("seed=42, repetitions=2", text)
        self.assertIn("  10", text)
        self.assertIn("  20", text)
        self.assertIn("O(n log n)", text)
        self.assertIn("O(n²)", text)


if __name__ == "__main__":
    unittest.main()
