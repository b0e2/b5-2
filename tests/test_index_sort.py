"""Tests for indexed lookup and stable merge sorting."""

import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from io import StringIO

from main import CommandError, run_command
from mini_git import Commit, Repository, merge_sort


class IndexSortTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repository()
        self.repo.init("Alice Bob")

    def test_token_phrase_author_and_reset(self) -> None:
        first = self.repo.commit("Add login feature")
        self.repo.commit("login extra feature")
        third = self.repo.commit("Login feature!")
        self.assertEqual([c.hash for c in self.repo.search_keyword("LOGIN")],
                         [first.hash, "00000002", third.hash])
        self.assertEqual(self.repo.search_keyword("login feature"), [first])
        self.assertEqual(self.repo.search_keyword("feature!"), [third])
        self.assertEqual(len(self.repo.search_author("Alice Bob")), 3)
        self.assertEqual(self.repo.search_author("alice bob"), [])
        self.repo.init("New User")
        self.assertEqual(self.repo.search_keyword("login"), [])
        self.assertEqual(self.repo.search_author("Alice Bob"), [])

    def test_search_only_reads_index_candidates(self) -> None:
        expected = self.repo.commit("indexed word")

        class LookupOnly(dict):
            def values(self):
                raise AssertionError("scan of all commits")

            def items(self):
                raise AssertionError("scan of all commits")

            def __iter__(self):
                raise AssertionError("scan of all commits")

        self.repo.commits = LookupOnly(self.repo.commits)
        self.assertEqual(self.repo.search_keyword("indexed"), [expected])
        self.assertEqual(self.repo.search_author("Alice Bob"), [expected])

    def test_stable_sort_and_log_keys(self) -> None:
        pairs = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
        self.assertEqual(merge_sort(pairs, lambda pair: pair[0]),
                         [(1, "b"), (1, "d"), (2, "a"), (2, "c")])
        a = self.repo.commit("first")
        b = self.repo.commit("second")
        c = self.repo.commit("third")
        base = datetime(2024, 1, 1)
        self.repo.commits[a.hash] = Commit(a.hash, a.message, "Zoe", base + timedelta(days=2), ())
        self.repo.commits[b.hash] = Commit(b.hash, b.message, "Amy", base, (a.hash,))
        self.repo.commits[c.hash] = Commit(c.hash, c.message, "Amy", base, (b.hash,))
        self.assertEqual([item.hash for item in self.repo.log("date")], [b.hash, c.hash, a.hash])
        self.assertEqual([item.hash for item in self.repo.log("author")], [b.hash, c.hash, a.hash])
        self.assertEqual([item.hash for item in self.repo.log()], [a.hash, b.hash, c.hash])

    def test_cli_options_and_invalid_values(self) -> None:
        self.repo.commit("Login feature")
        output = StringIO()
        with redirect_stdout(output):
            run_command('search --author="Alice Bob"', self.repo)
            run_command('search login', self.repo)
            run_command('log --sort-by=author', self.repo)
            run_command('log --sort-by=date', self.repo)
        self.assertIn("Login feature", output.getvalue())
        for text in ("log --sort-by=message", "search --author=", "search --wrong=x"):
            with self.subTest(text=text), self.assertRaisesRegex(CommandError, "Invalid args"):
                run_command(text, self.repo)


if __name__ == "__main__":
    unittest.main()
