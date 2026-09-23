"""End-to-end integration tests for chats2notes CLI."""

import json
import tempfile
import unittest
from pathlib import Path

from chats2notes.cli import main


class TestCLIIntegration(unittest.TestCase):
    """Integration test suite executing CLI workflows end-to-end."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.brain_dir = self.base_dir / "user_a" / ".gemini" / "antigravity-cli" / "brain"
        self.notes_dir = self.base_dir / "vault_notes"
        self.state_file = self.base_dir / "state.json"

        # Create mock session
        session_logs = self.brain_dir / "session_e2e" / ".system_generated" / "logs"
        session_logs.mkdir(parents=True, exist_ok=True)
        transcript = session_logs / "transcript_full.jsonl"
        with open(transcript, "w", encoding="utf-8") as f:
            f.write(json.dumps({"step_index": 0, "type": "USER_INPUT", "content": "Pergunta E2E"}) + "\n")
            f.write(json.dumps({"step_index": 1, "type": "PLANNER_RESPONSE", "content": "Resposta E2E"}) + "\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-001 AC-002 AC-003 AC-004
    def test_cli_full_workflow(self):
        """Executes full extract followed by status and checks idempotence."""
        # 1. First extraction
        ret = main([
            "extract",
            "--brain-dir", str(self.brain_dir),
            "--output-dir", str(self.notes_dir),
            "--state-file", str(self.state_file),
            "--format", "silverbullet",
        ])
        self.assertEqual(ret, 0)
        self.assertTrue(self.notes_dir.exists())
        self.assertTrue(self.state_file.exists())

        notes = list(self.notes_dir.glob("*.md"))
        self.assertEqual(len(notes), 1)
        with open(notes[0], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Pergunta E2E", content)
        self.assertIn("Resposta E2E", content)

        # 2. Status inspection
        ret_status = main(["status", "--state-file", str(self.state_file)])
        self.assertEqual(ret_status, 0)

        # 3. Second extraction (incremental idempotence)
        ret_second = main([
            "extract",
            "--brain-dir", str(self.brain_dir),
            "--output-dir", str(self.notes_dir),
            "--state-file", str(self.state_file),
        ])
        self.assertEqual(ret_second, 0)
        notes_after = list(self.notes_dir.glob("*.md"))
        self.assertEqual(len(notes_after), 1)


if __name__ == "__main__":
    unittest.main()
