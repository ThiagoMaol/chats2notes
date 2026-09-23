"""Unit tests for InboxSynchronizer raw transcript synchronization."""

import json
import tempfile
import unittest
from pathlib import Path

from chats2notes.models import SessionSummary
from chats2notes.sync import InboxSynchronizer


class TestSync(unittest.TestCase):
    """Test suite for copying and updating raw transcripts into vault/inbox/."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.source_dir = self.base_path / "brain"
        self.inbox_dir = self.base_path / "vault" / "inbox"
        self.synchronizer = InboxSynchronizer(self.inbox_dir)

        # Create sample source session
        self.session_dir = self.source_dir / "sess_sync_01" / ".system_generated" / "logs"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.source_transcript = self.session_dir / "transcript_full.jsonl"
        with open(self.source_transcript, "w", encoding="utf-8") as f:
            f.write(json.dumps({"step_index": 0, "type": "USER_INPUT", "content": "Primeiro log"}) + "\n")

        self.session = SessionSummary(
            session_id="sess_sync_01",
            host_user="thiago",
            workspace="/tmp/proj",
            transcript_path=self.source_transcript,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    # SPECSFY: US-002 FR-004 FR-005 FR-006 NFR-002 AC-005
    def test_initial_sync(self):
        """Initial sync copies raw transcript into vault/inbox preserving contents."""
        synced = self.synchronizer.sync_session(self.session)
        self.assertTrue(synced)

        target_file = self.inbox_dir / "thiago" / "sess_sync_01" / "transcript_full.jsonl"
        self.assertTrue(target_file.exists())
        with open(target_file, "r", encoding="utf-8") as f:
            target_content = f.read()
        with open(self.source_transcript, "r", encoding="utf-8") as f:
            source_content = f.read()
        self.assertEqual(target_content, source_content)

    # SPECSFY: US-002 FR-004 FR-005 FR-006 NFR-002 AC-006
    def test_idempotent_sync(self):
        """Unchanged files are skipped and not re-copied."""
        self.synchronizer.sync_session(self.session)
        # Second run with same file
        synced_again = self.synchronizer.sync_session(self.session)
        self.assertFalse(synced_again)

    # SPECSFY: US-002 FR-004 FR-005 FR-006 NFR-002 AC-008
    def test_incremental_append_sync(self):
        """When source file gets new lines, target is updated with new contents."""
        self.synchronizer.sync_session(self.session)

        # Append new message
        with open(self.source_transcript, "a", encoding="utf-8") as f:
            f.write(json.dumps({"step_index": 1, "type": "PLANNER_RESPONSE", "content": "Resposta"}) + "\n")

        updated = self.synchronizer.sync_session(self.session)
        self.assertTrue(updated)

        target_file = self.inbox_dir / "thiago" / "sess_sync_01" / "transcript_full.jsonl"
        with open(target_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)


if __name__ == "__main__":
    unittest.main()
