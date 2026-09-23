"""Testes unitários e de integração para o segmentador de transcripts em pares."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from chats2notes.segmenter import TranscriptSegmenter


class TestTranscriptSegmenter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.raw_dir = Path(self.test_dir) / "raw"
        self.segments_dir = Path(self.test_dir) / "segments"
        self.raw_dir.mkdir(parents=True)
        self.segments_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_sample_raw(self, user: str, session_id: str, lines: list) -> Path:
        session_dir = self.raw_dir / user / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        transcript_file = session_dir / "transcript_full.jsonl"
        with open(transcript_file, "w", encoding="utf-8") as f:
            for item in lines:
                if isinstance(item, str):
                    f.write(item + "\n")
                else:
                    f.write(json.dumps(item) + "\n")
        return transcript_file

    # SPECSFY: US-001 US-002 US-003 FR-001 FR-002 FR-003 FR-004 FR-005 FR-006 NFR-001 NFR-002 NFR-003 AC-001
    def test_segment_complete_session(self):
        """AC-001: Segmentação com sucesso de sessão completa com Markdown e auditoria JSON."""
        lines = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "Olá, preciso criar uma rota",
                "created_at": "2026-09-23T10:00:00Z",
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "thinking": "Pensando na rota...",
                "tool_calls": [{"tool": "view_file", "args": {"path": "routes.py"}}],
                "content": "",
                "created_at": "2026-09-23T10:00:05Z",
            },
            {
                "step_index": 2,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Aqui está a rota criada com sucesso.",
                "created_at": "2026-09-23T10:00:10Z",
            },
            {
                "step_index": 3,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "Agora adicione o middleware",
                "created_at": "2026-09-23T10:05:00Z",
            },
            {
                "step_index": 4,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Middleware adicionado.",
                "created_at": "2026-09-23T10:05:05Z",
            },
        ]
        self._create_sample_raw("user_a", "sess_123", lines)

        segmenter = TranscriptSegmenter(raw_dir=self.raw_dir, segments_dir=self.segments_dir)
        stats = segmenter.segment_all()

        self.assertEqual(stats["sessions_processed"], 1)
        self.assertEqual(stats["turns_generated"], 2)

        session_out = self.segments_dir / "user_a" / "sess_123"
        md_0001 = session_out / "0001.md"
        audit_0001 = session_out / "0001.audit.json"
        md_0002 = session_out / "0002.md"

        self.assertTrue(md_0001.exists())
        self.assertTrue(audit_0001.exists())
        self.assertTrue(md_0002.exists())

        # Verifica conteúdo do Markdown limpo 0001.md
        content_0001 = md_0001.read_text(encoding="utf-8")
        self.assertIn("session_id: sess_123", content_0001)
        self.assertIn("turn: 1", content_0001)
        self.assertIn("Olá, preciso criar uma rota", content_0001)
        self.assertIn("Aqui está a rota criada com sucesso.", content_0001)
        self.assertNotIn("Pensando na rota...", content_0001)
        self.assertNotIn("view_file", content_0001)

        # Verifica arquivo de auditoria 0001.audit.json
        audit_data = json.loads(audit_0001.read_text(encoding="utf-8"))
        self.assertEqual(audit_data["session_id"], "sess_123")
        self.assertEqual(audit_data["turn"], 1)
        self.assertIn("Pensando na rota...", audit_data.get("thinking", []))
        self.assertEqual(audit_data["tool_calls"][0]["tool"], "view_file")
        self.assertNotIn("Aqui está a rota criada com sucesso.", json.dumps(audit_data))

    # SPECSFY: US-001 US-002 US-003 FR-001 FR-002 FR-003 FR-005 FR-006 NFR-002 NFR-003 AC-002
    def test_ignore_incomplete_turn(self):
        """AC-002: Turno em andamento/incompleto é ignorado até finalização."""
        lines = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "Turno finalizado",
                "created_at": "2026-09-23T10:00:00Z",
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Resposta concluída",
                "created_at": "2026-09-23T10:00:05Z",
            },
            {
                "step_index": 2,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "Mensagem ainda sendo processada pelo modelo...",
                "created_at": "2026-09-23T10:05:00Z",
            },
        ]
        self._create_sample_raw("user_a", "sess_live", lines)

        segmenter = TranscriptSegmenter(raw_dir=self.raw_dir, segments_dir=self.segments_dir)
        stats = segmenter.segment_all()

        self.assertEqual(stats["turns_generated"], 1)
        session_out = self.segments_dir / "user_a" / "sess_live"
        self.assertTrue((session_out / "0001.md").exists())
        self.assertFalse((session_out / "0002.md").exists())

    # SPECSFY: US-001 US-002 US-003 FR-001 FR-002 FR-003 FR-004 FR-005 FR-006 NFR-001 NFR-002 NFR-003 AC-003
    def test_consistent_regeneration(self):
        """AC-003: Regeneração consistente da sessão a partir do raw atualizado."""
        lines_initial = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "Pergunta inicial",
                "created_at": "2026-09-23T10:00:00Z",
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Resposta inicial",
                "created_at": "2026-09-23T10:00:05Z",
            },
        ]
        raw_file = self._create_sample_raw("user_a", "sess_grow", lines_initial)

        segmenter = TranscriptSegmenter(raw_dir=self.raw_dir, segments_dir=self.segments_dir)
        segmenter.segment_all()

        session_out = self.segments_dir / "user_a" / "sess_grow"
        self.assertTrue((session_out / "0001.md").exists())
        self.assertFalse((session_out / "0002.md").exists())

        # Raw cresce com um novo turno completo
        lines_extra = [
            {
                "step_index": 2,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "Pergunta seguinte",
                "created_at": "2026-09-23T10:05:00Z",
            },
            {
                "step_index": 3,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Resposta seguinte",
                "created_at": "2026-09-23T10:05:10Z",
            },
        ]
        with open(raw_file, "a", encoding="utf-8") as f:
            for item in lines_extra:
                f.write(json.dumps(item) + "\n")

        # Reprocessa
        stats = segmenter.segment_all()
        self.assertEqual(stats["turns_generated"], 2)
        self.assertTrue((session_out / "0001.md").exists())
        self.assertTrue((session_out / "0002.md").exists())

    # SPECSFY: US-002 FR-001 FR-003 NFR-003 AC-005
    def test_corrupted_jsonl_resilience(self):
        """AC-005: Resiliência a linhas JSONL malformadas no raw."""
        lines = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "Turno 1",
                "created_at": "2026-09-23T10:00:00Z",
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Resposta 1",
                "created_at": "2026-09-23T10:00:05Z",
            },
            "{CORRUPTED_JSON_LINE!@#$%^&*()}",
            {
                "step_index": 2,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "Turno 2",
                "created_at": "2026-09-23T10:05:00Z",
            },
            {
                "step_index": 3,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Resposta 2",
                "created_at": "2026-09-23T10:05:05Z",
            },
        ]
        self._create_sample_raw("user_a", "sess_corrupt", lines)

        segmenter = TranscriptSegmenter(raw_dir=self.raw_dir, segments_dir=self.segments_dir)
        stats = segmenter.segment_all()

        self.assertEqual(stats["turns_generated"], 2)
        session_out = self.segments_dir / "user_a" / "sess_corrupt"
        self.assertTrue((session_out / "0001.md").exists())
        self.assertTrue((session_out / "0002.md").exists())
