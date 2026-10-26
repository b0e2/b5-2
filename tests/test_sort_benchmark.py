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

    def test_benchmark_compares_identical_seeded_inputs(self) -> None:
        received = []

        def record_merge(items, key):
            received.append(("merge", items[:]))
            return merge_sort(items, key)

        def record_insertion(items, key):
            received.append(("insertion", items[:]))
            return insertion_sort(items, key)

        with patch.object(benchmark_sort, "SIZES", (10,)), \
                patch.object(benchmark_sort, "REPEATS", 1), \
                patch.object(benchmark_sort, "merge_sort", record_merge), \
                patch.object(benchmark_sort, "insertion_sort", record_insertion), \
                patch("benchmark_sort.perf_counter", side_effect=range(20)), \
                redirect_stdout(StringIO()):
            benchmark_sort.main()

        merge_inputs = [items for name, items in received if name == "merge"]
        insertion_inputs = [items for name, items in received if name == "insertion"]
        self.assertEqual(merge_inputs, insertion_inputs)


if __name__ == "__main__":
    unittest.main()
