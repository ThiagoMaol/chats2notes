"""Testes de integração para a interface CLI do comando segment."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chats2notes.cli import main


class TestSegmenterCLI(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.raw_dir = Path(self.test_dir) / "raw"
        self.segments_dir = Path(self.test_dir) / "segments"
        self.raw_dir.mkdir(parents=True)
        self.segments_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_sample_session(self, user: str, session_id: str):
        session_dir = self.raw_dir / user / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        transcript = session_dir / "transcript_full.jsonl"
        lines = [
            {"step_index": 0, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "Olá"},
            {"step_index": 1, "source": "MODEL", "type": "PLANNER_RESPONSE", "content": "Olá, tudo bem?"},
        ]
        with open(transcript, "w", encoding="utf-8") as f:
            for l in lines:
                f.write(json.dumps(l) + "\n")

    # SPECSFY: US-001 US-003 FR-002 FR-004 FR-006 NFR-001 NFR-002 AC-004
    def test_cli_segment_specific_session(self):
        """AC-004: Segmentação seletiva por identificador de sessão via CLI."""
        self._create_sample_session("user_a", "sess_alpha")
        self._create_sample_session("user_a", "sess_beta")

        args = [
            "chats2notes",
            "segment",
            "--raw-dir",
            str(self.raw_dir),
            "--segments-dir",
            str(self.segments_dir),
            "--session",
            "sess_alpha",
        ]

        with patch("sys.argv", args):
            code = main()

        self.assertEqual(code, 0)
        self.assertTrue((self.segments_dir / "user_a" / "sess_alpha" / "0001.md").exists())
        self.assertFalse((self.segments_dir / "user_a" / "sess_beta" / "0001.md").exists())
