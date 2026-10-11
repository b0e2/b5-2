"""Tests for commit nodes and branch pointers."""

import unittest

from mini_git import MiniGitError, Repository


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repository()
        self.repo.init("Alice")

    def test_root_and_branch_commits(self) -> None:
        root = self.repo.commit("Initial commit")
        self.assertEqual(root.parents, ())
        self.assertEqual(root.author, "Alice")
        self.repo.branch("feature")
        main_child = self.repo.commit("Main change")
        self.repo.switch("feature")
        feature_child = self.repo.commit("Feature change")
        self.assertEqual(main_child.parents, (root.hash,))
        self.assertEqual(feature_child.parents, (root.hash,))
        self.assertNotEqual(main_child.hash, feature_child.hash)
        self.assertEqual(self.repo.branches["main"], main_child.hash)
        self.assertEqual(self.repo.branches["feature"], feature_child.hash)
        self.assertIs(self.repo.commits[root.hash], root)

    def test_empty_branch_and_reset_do_not_reuse_ids(self) -> None:
        self.repo.branch("feature")
        self.repo.switch("feature")
        root = self.repo.commit("A root")
        self.assertEqual(root.parents, ())
        self.repo.init("Bob")
        next_root = self.repo.commit("Another root")
        self.assertNotEqual(root.hash, next_root.hash)
        self.assertEqual(next_root.author, "Bob")
        self.assertNotIn(root.hash, self.repo.commits)
        self.assertEqual(self.repo.branches, {"main": next_root.hash})

    def test_errors_and_parent_validation(self) -> None:
        with self.assertRaisesRegex(MiniGitError, "Branch already exists: main"):
            self.repo.branch("main")
        with self.assertRaisesRegex(MiniGitError, "Unknown branch: missing"):
            self.repo.switch("missing")
        with self.assertRaisesRegex(MiniGitError, "Unknown commit: missing"):
            self.repo._create_commit("invalid", ("missing",))
        with self.assertRaisesRegex(MiniGitError, "Invalid args"):
            self.repo._create_commit("invalid", ("x", "x"))
        with self.assertRaisesRegex(MiniGitError, "Repository not initialized"):
            Repository().commit("invalid")


if __name__ == "__main__":
    unittest.main()
