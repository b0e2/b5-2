"""Tests for metadata-only merge commits."""

import unittest
from contextlib import redirect_stdout
from io import StringIO

from main import CommandError, run_command
from mini_git import MiniGitError, Repository


class MergeCommitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repository()
        self.repo.init("Alice")

    def test_two_parents_and_graph_queries(self) -> None:
        root = self.repo.commit("root")
        self.repo.branch("feature")
        main_head = self.repo.commit("main change")
        self.repo.switch("feature")
        feature_head = self.repo.commit("feature change")
        self.repo.switch("main")
        merged = self.repo.merge("feature")

        self.assertEqual(merged.parents, (main_head.hash, feature_head.hash))
        self.assertEqual(self.repo.branches["main"], merged.hash)
        self.assertEqual(self.repo.branches["feature"], feature_head.hash)
        self.assertEqual({commit.hash for commit in self.repo.ancestors(merged.hash)},
                         {root.hash, main_head.hash, feature_head.hash})
        self.assertEqual(self.repo.path(main_head.hash, feature_head.hash),
                         [main_head.hash, root.hash, feature_head.hash])
        self.assertEqual(self.repo.path(feature_head.hash, merged.hash),
                         [feature_head.hash, merged.hash])
        order = {commit.hash: i for i, commit in enumerate(self.repo.log())}
        self.assertLess(order[main_head.hash], order[merged.hash])
        self.assertLess(order[feature_head.hash], order[merged.hash])
        self.assertEqual([commit.hash for commit in self.repo.search_keyword("merge")], [merged.hash])

    def test_invalid_targets_leave_state_unchanged(self) -> None:
        with self.assertRaisesRegex(MiniGitError, "Unknown branch"):
            self.repo.merge("missing")
        with self.assertRaisesRegex(MiniGitError, "itself"):
            self.repo.merge("main")
        self.repo.branch("feature")
        with self.assertRaisesRegex(MiniGitError, "empty branch"):
            self.repo.merge("feature")
        root = self.repo.commit("root")
        with self.assertRaisesRegex(MiniGitError, "empty branch"):
            self.repo.merge("feature")
        self.repo.switch("feature")
        self.repo.commit("feature root")
        self.repo.switch("main")
        self.repo.branch("same")
        with self.assertRaisesRegex(MiniGitError, "same HEAD"):
            self.repo.merge("same")
        self.assertEqual(self.repo.branches["main"], root.hash)
        self.assertEqual(len(self.repo.commits), 2)

    def test_cli_merge_and_arguments(self) -> None:
        self.repo.commit("root")
        self.repo.branch("feature")
        self.repo.commit("main")
        self.repo.switch("feature")
        self.repo.commit("feature")
        self.repo.switch("main")
        output = StringIO()
        with redirect_stdout(output):
            run_command("merge feature", self.repo)
        self.assertIn("Merge branch 'feature' into main", output.getvalue())
        with self.assertRaisesRegex(CommandError, "Invalid args"):
            run_command("merge", self.repo)
        with self.assertRaisesRegex(CommandError, "Invalid args"):
            run_command("merge feature extra", self.repo)


if __name__ == "__main__":
    unittest.main()
