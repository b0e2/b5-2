"""Tests for parent-first logs and graph searches."""

import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from io import StringIO

from main import run_command
from mini_git import Commit, MiniGitError, Repository


class GraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repository()
        self.repo.init("Alice")

    def test_log_covers_branches_and_parents_first(self) -> None:
        root = self.repo.commit("root")
        self.repo.branch("feature")
        main_child = self.repo.commit("main")
        self.repo.switch("feature")
        feature_child = self.repo.commit("feature")
        order = {commit.hash: i for i, commit in enumerate(self.repo.log())}
        self.assertEqual(len(order), 3)
        self.assertLess(order[root.hash], order[main_child.hash])
        self.assertLess(order[root.hash], order[feature_child.hash])
        self.assertEqual(self.repo.path(main_child.hash, feature_child.hash),
                         [main_child.hash, root.hash, feature_child.hash])
        self.assertEqual([c.hash for c in self.repo.ancestors(feature_child.hash)], [root.hash])

    def test_multiple_parents_and_deeper_lexicographic_tie(self) -> None:
        root = self.repo.commit("root")
        common = self.repo.commit("common")
        left = self.repo.commit("left")
        self.repo.branches["main"] = common.hash
        right = self.repo.commit("right")
        merged = self.repo._create_commit("merged", (left.hash, right.hash))
        self.assertEqual(self.repo.path(root.hash, merged.hash),
                         [root.hash, common.hash, left.hash, merged.hash])
        self.assertEqual({c.hash for c in self.repo.ancestors(merged.hash)},
                         {root.hash, common.hash, left.hash, right.hash})
        self.assertEqual(self.repo.ancestors(root.hash), [])
        self.assertEqual(self.repo.path(root.hash, root.hash), [root.hash])
        self.repo.commits = dict(reversed(list(self.repo.commits.items())))
        order = {c.hash: i for i, c in enumerate(self.repo.log())}
        for commit in self.repo.commits.values():
            for parent in commit.parents:
                self.assertLess(order[parent], order[commit.hash])

    def test_log_sort_keys_and_parent_order(self) -> None:
        first = self.repo.commit("first")
        second = self.repo.commit("second")
        third = self.repo.commit("third")
        base = datetime(2024, 1, 1)
        self.repo.commits[first.hash] = Commit(
            first.hash,
            first.message,
            "Zoe",
            base + timedelta(days=2),
            (),
        )
        self.repo.commits[second.hash] = Commit(
            second.hash,
            second.message,
            "Amy",
            base,
            (first.hash,),
        )
        self.repo.commits[third.hash] = Commit(
            third.hash,
            third.message,
            "Amy",
            base,
            (second.hash,),
        )
        self.assertEqual(
            [item.hash for item in self.repo.log("date")],
            [second.hash, third.hash, first.hash],
        )
        self.assertEqual(
            [item.hash for item in self.repo.log("author")],
            [second.hash, third.hash, first.hash],
        )
        self.assertEqual(
            [item.hash for item in self.repo.log()],
            [first.hash, second.hash, third.hash],
        )

    def test_no_path_and_unknown_hash(self) -> None:
        first = self.repo.commit("first root")
        other = self.repo._create_commit("other root", ())
        self.assertIsNone(self.repo.path(first.hash, other.hash))
        with self.assertRaisesRegex(MiniGitError, "Unknown commit: missing"):
            self.repo.path("missing", first.hash)
        with self.assertRaisesRegex(MiniGitError, "Unknown commit: missing"):
            self.repo.ancestors("missing")

    def test_merge_commit_graph_queries(self) -> None:
        root = self.repo.commit("root")
        self.repo.branch("feature")
        main_head = self.repo.commit("main change")
        self.repo.switch("feature")
        feature_head = self.repo.commit("feature change")
        self.repo.switch("main")
        merged = self.repo.merge("feature")

        self.assertEqual(merged.parents, (main_head.hash, feature_head.hash))
        self.assertEqual(
            {commit.hash for commit in self.repo.ancestors(merged.hash)},
            {root.hash, main_head.hash, feature_head.hash},
        )
        self.assertEqual(
            self.repo.path(main_head.hash, feature_head.hash),
            [main_head.hash, root.hash, feature_head.hash],
        )
        self.assertEqual(
            self.repo.path(feature_head.hash, merged.hash),
            [feature_head.hash, merged.hash],
        )
        order = {
            commit.hash: index
            for index, commit in enumerate(self.repo.log())
        }
        self.assertLess(order[main_head.hash], order[merged.hash])
        self.assertLess(order[feature_head.hash], order[merged.hash])

    def test_cli_outputs_and_argument_errors(self) -> None:
        root = self.repo.commit("root")
        child = self.repo.commit("child")
        output = StringIO()
        with redirect_stdout(output):
            run_command("log", self.repo)
            run_command(f"ancestors {child.hash}", self.repo)
            run_command(f"path {root.hash} {child.hash}", self.repo)
        self.assertIn(f"commit {root.hash} (Alice,", output.getvalue())
        self.assertIn(f"Path: {root.hash} -> {child.hash}", output.getvalue())
        from main import CommandError
        with self.assertRaisesRegex(CommandError, "Invalid args"):
            run_command("log extra", self.repo)


if __name__ == "__main__":
    unittest.main()
