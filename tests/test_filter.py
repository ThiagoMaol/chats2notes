"""Unit tests for WorkspaceFilter exclusion logic."""

import unittest
from chats2notes.filter import WorkspaceFilter


class TestFilter(unittest.TestCase):
    """Test suite for excluding chats2notes and customized workspaces."""

    # SPEC-0002: US-002 FR-004 FR-005 FR-006 NFR-002 AC-005
    def test_ignore_default_chats2notes(self):
        """Sessions whose workspace belongs to chats2notes are ignored by default."""
        flt = WorkspaceFilter()
        self.assertTrue(flt.should_ignore("/home/thiago/PROJETOS/ghub_thiago/chats2notes"))
        self.assertTrue(flt.should_ignore("/opt/apps/chats2notes/subfolder"))

    # SPEC-0002: US-002 FR-004 FR-005 FR-006 NFR-002 AC-007
    def test_ignore_custom_workspace(self):
        """Custom workspaces configured for exclusion are correctly rejected."""
        flt = WorkspaceFilter(ignored_workspaces=["/secret/project", "/tmp/admin"])
        self.assertTrue(flt.should_ignore("/secret/project"))
        self.assertTrue(flt.should_ignore("/secret/project/src"))
        self.assertTrue(flt.should_ignore("/tmp/admin"))

    # SPEC-0002: US-002 FR-004 FR-005 FR-006 NFR-002 AC-008
    def test_allow_regular_workspace(self):
        """Regular user workspaces not in the ignore list are allowed."""
        flt = WorkspaceFilter(ignored_workspaces=["/tmp/admin"])
        self.assertFalse(flt.should_ignore("/home/thiago/PROJETOS/meu-app"))
        self.assertFalse(flt.should_ignore("/var/www/ecommerce"))


if __name__ == "__main__":
    unittest.main()
