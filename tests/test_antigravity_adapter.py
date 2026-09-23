"""Unit tests for AntigravityAdapter log parsing and session discovery."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from chats2notes.adapters.antigravity import AntigravityAdapter
from chats2notes.models import SessionSummary


class TestAntigravityAdapter(unittest.TestCase):
    """Test suite for Antigravity transcript extraction and resilience."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.adapter = AntigravityAdapter()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_mock_session(self, user_name: str, session_id: str, lines: list) -> Path:
        """Helper to create realistic directory structure and transcript_full.jsonl."""
        session_dir = (
            self.base_path
            / user_name
            / ".gemini"
            / "antigravity-cli"
            / "brain"
            / session_id
            / ".system_generated"
            / "logs"
        )
        session_dir.mkdir(parents=True, exist_ok=True)
        transcript_file = session_dir / "transcript_full.jsonl"
        with open(transcript_file, "w", encoding="utf-8") as f:
            for item in lines:
                if isinstance(item, str):
                    f.write(item + "\n")
                else:
                    f.write(json.dumps(item) + "\n")
        return transcript_file

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-001
    def test_initial_extraction(self):
        """Extracts complete turn (prompt + response) from clean transcript."""
        lines = [
            {"step_index": 0, "type": "USER_INPUT", "content": "Como criar uma nota?"},
            {"step_index": 1, "type": "PLANNER_RESPONSE", "content": "Use Markdown com frontmatter."},
        ]
        log_path = self._create_mock_session("thiago", "sess_alpha", lines)
        session = SessionSummary(
            session_id="sess_alpha",
            host_user="thiago",
            workspace="/tmp/proj",
            transcript_path=log_path,
        )

        turns = list(self.adapter.extract_new_turns(session, since_step_index=0))
        self.assertEqual(len(turns), 1)
        self.assertEqual(turns[0].user_prompt, "Como criar uma nota?")
        self.assertEqual(turns[0].assistant_response, "Use Markdown com frontmatter.")
        self.assertEqual(turns[0].step_index, 1)

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-002
    def test_incremental_idempotence(self):
        """Only extracts turns with step_index > since_step_index."""
        lines = [
            {"step_index": 0, "type": "USER_INPUT", "content": "Turn 1 prompt"},
            {"step_index": 1, "type": "PLANNER_RESPONSE", "content": "Turn 1 response"},
            {"step_index": 2, "type": "USER_INPUT", "content": "Turn 2 prompt"},
            {"step_index": 3, "type": "PLANNER_RESPONSE", "content": "Turn 2 response"},
        ]
        log_path = self._create_mock_session("thiago", "sess_beta", lines)
        session = SessionSummary(
            session_id="sess_beta",
            host_user="thiago",
            workspace="/tmp/proj",
            transcript_path=log_path,
        )

        # After step 1, only step 3 should be returned
        new_turns = list(self.adapter.extract_new_turns(session, since_step_index=1))
        self.assertEqual(len(new_turns), 1)
        self.assertEqual(new_turns[0].step_index, 3)

        # After step 3, nothing should be returned
        empty_turns = list(self.adapter.extract_new_turns(session, since_step_index=3))
        self.assertEqual(len(empty_turns), 0)

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-003
    def test_multi_user_discovery(self):
        """Discovers sessions across multiple user home directories."""
        self._create_mock_session("alice", "sess_alice_1", [{"step_index": 0, "type": "USER_INPUT", "content": "oi"}])
        self._create_mock_session("bob", "sess_bob_1", [{"step_index": 0, "type": "USER_INPUT", "content": "ola"}])

        sessions = self.adapter.discover_sessions(base_paths=[self.base_path / "alice", self.base_path / "bob"])
        users_found = {s.host_user for s in sessions}
        self.assertIn("alice", users_found)
        self.assertIn("bob", users_found)

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-004
    def test_resilience_corrupted_jsonl(self):
        """Corrupted JSON line is skipped and remaining valid turns are extracted."""
        lines = [
            '{"step_index": 0, "type": "USER_INPUT", "content": "Turn 1"}',
            '{"INVALID_JSON_LINE_WITHOUT_BRACES',
            '{"step_index": 1, "type": "PLANNER_RESPONSE", "content": "Turn 1 answer"}',
        ]
        log_path = self._create_mock_session("thiago", "sess_corrupt", lines)
        session = SessionSummary(
            session_id="sess_corrupt",
            host_user="thiago",
            workspace="/tmp/proj",
            transcript_path=log_path,
        )

        turns = list(self.adapter.extract_new_turns(session, since_step_index=0))
        self.assertEqual(len(turns), 1)
        self.assertEqual(turns[0].assistant_response, "Turn 1 answer")


if __name__ == "__main__":
    unittest.main()
