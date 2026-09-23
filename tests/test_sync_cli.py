"""Integration tests for chats2notes sync CLI command."""

import json
import tempfile
import unittest
from pathlib import Path

from chats2notes.cli import main


class TestSyncCLI(unittest.TestCase):
    """Test suite for the 'chats2notes sync' command."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.brain_dir = self.base_dir / "user_x" / ".gemini" / "antigravity-cli" / "brain"
        self.inbox_dir = self.base_dir / "vault" / "inbox"

        # 1. Valid project session
        session_a = self.brain_dir / "sess_valid" / ".system_generated" / "logs"
        session_a.mkdir(parents=True, exist_ok=True)
        with open(session_a / "transcript_full.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"step_index": 0, "type": "USER_INPUT", "content": "Valid chat"}) + "\n")

        # 2. Ignored chats2notes session
        session_b = self.brain_dir / "sess_chats2notes" / ".system_generated" / "logs"
        session_b.mkdir(parents=True, exist_ok=True)
        with open(session_b / "transcript_full.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"step_index": 0, "type": "USER_INPUT", "content": "Curating notes in chats2notes", "Cwd": "/home/thiago/PROJETOS/chats2notes"}) + "\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    # SPECSFY: US-002 FR-004 FR-005 FR-006 NFR-002 AC-005
    def test_cli_sync_success(self):
        """Runs chats2notes sync and copies valid session transcripts into inbox."""
        ret = main([
            "sync",
            "--brain-dir", str(self.brain_dir),
            "--inbox-dir", str(self.inbox_dir),
        ])
        self.assertEqual(ret, 0)
        self.assertTrue((self.inbox_dir / "user_x" / "sess_valid" / "transcript_full.jsonl").exists())

    # SPECSFY: US-002 FR-004 FR-005 FR-006 NFR-002 AC-006
    def test_cli_sync_ignore_workspace(self):
        """Ignores sessions matching chats2notes or passed in --ignore-workspace."""
        ret = main([
            "sync",
            "--brain-dir", str(self.brain_dir),
            "--inbox-dir", str(self.inbox_dir),
            "--ignore-workspace", "/home/thiago/PROJETOS/chats2notes",
        ])
        self.assertEqual(ret, 0)
        # Valid should exist, ignored session should NOT exist
        self.assertTrue((self.inbox_dir / "user_x" / "sess_valid" / "transcript_full.jsonl").exists())
        self.assertFalse((self.inbox_dir / "user_x" / "sess_chats2notes").exists())

    # SPECSFY: US-002 FR-004 FR-005 FR-006 NFR-002 AC-007
    def test_cli_sync_idempotent(self):
        """Running sync twice is idempotent and does not fail."""
        main(["sync", "--brain-dir", str(self.brain_dir), "--inbox-dir", str(self.inbox_dir)])
        ret_second = main(["sync", "--brain-dir", str(self.brain_dir), "--inbox-dir", str(self.inbox_dir)])
        self.assertEqual(ret_second, 0)


if __name__ == "__main__":
    unittest.main()
