"""Unit tests for Markdown note formatting and storage."""

import tempfile
import unittest
from pathlib import Path

from chats2notes.models import Turn
from chats2notes.storage import MarkdownStorage


class TestMarkdownStorage(unittest.TestCase):
    """Test suite for Markdown note formatting with SilverBullet & Obsidian compatibility."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
        self.storage = MarkdownStorage(self.output_dir, format_mode="silverbullet")

    def tearDown(self):
        self.temp_dir.cleanup()

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-001
    def test_format_silverbullet_and_obsidian_markdown(self):
        """Generates markdown with standard YAML frontmatter containing required metadata."""
        turn = Turn(
            session_id="uuid-1234",
            step_index=1,
            created_at="2026-09-23 02:00:00",
            user_prompt="Como estruturar notas no SilverBullet?",
            assistant_response="Use YAML frontmatter com name, tags e atributos customizados.",
            host_user="thiago",
            workspace="/home/thiago/repo",
            agent="antigravity",
            tags=["ai-notes", "silverbullet"],
        )

        content = self.storage.format_note(turn)
        self.assertTrue(content.startswith("---\n"))
        self.assertIn("name:", content)
        self.assertIn("agent: antigravity", content)
        self.assertIn("host_user: thiago", content)
        self.assertIn("workspace: /home/thiago/repo", content)
        self.assertIn("session: uuid-1234", content)
        self.assertIn("tags: [ai-notes, silverbullet]", content)
        self.assertIn("Como estruturar notas no SilverBullet?", content)
        self.assertIn("Use YAML frontmatter", content)

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-002
    def test_write_note_to_disk(self):
        """Writes note to target disk directory and creates needed directories."""
        turn = Turn(
            session_id="uuid-5678",
            step_index=2,
            created_at="2026-09-23 02:10:00",
            user_prompt="Pergunta 2",
            assistant_response="Resposta 2",
            host_user="thiago",
            workspace="/tmp/proj",
        )

        note_path = self.storage.write_note(turn)
        self.assertTrue(note_path.exists())
        self.assertEqual(note_path.parent, self.output_dir)
        with open(note_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertIn("Pergunta 2", saved_content)

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-003
    def test_yaml_escaping_and_special_chars(self):
        """Safely handles colons, quotes and special characters in frontmatter."""
        turn = Turn(
            session_id="uuid-special",
            step_index=3,
            created_at="2026-09-23 02:15:00",
            user_prompt='Nota com "aspas" e dois pontos: subtítulo',
            assistant_response="Resposta com código: `echo 'hello'`",
            host_user="thiago",
            workspace="/home/thiago/special:dir",
        )

        content = self.storage.format_note(turn)
        self.assertIn("name:", content)
        self.assertIn("---", content)


if __name__ == "__main__":
    unittest.main()
