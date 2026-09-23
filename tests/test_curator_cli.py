import io
import sys
import tempfile
import unittest
from pathlib import Path

from chats2notes.cli import main


class TestCuratorCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.segments_dir = Path(self.temp_dir.name) / "segments"
        self.notes_dir = Path(self.temp_dir.name) / "notas"
        self.segments_dir.mkdir(parents=True)
        self.notes_dir.mkdir(parents=True)

        session_dir = self.segments_dir / "user_a" / "sess_cli"
        session_dir.mkdir(parents=True)
        (session_dir / "0001.md").write_text(
            """---
session_id: "sess_cli"
turn: 1
timestamp: "2026-09-23T15:00:00Z"
user: "user_a"
start_step: 0
end_step: 1
---

# Entrada
Como verificar portas abertas no Linux?

# Resposta
Utilize o comando `ss -tulpn` ou `netstat -tulpn`.
""",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cli_curate_incremental_and_force(self):
        # SPECSFY:AC-006
        """Deve processar segmentos via CLI, respeitar o manifesto em segunda execução e reprocessar com --force."""
        captured_output = io.StringIO()
        original_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            exit_code = main(
                [
                    "curate",
                    "--segments-dir",
                    str(self.segments_dir),
                    "--notes-dir",
                    str(self.notes_dir),
                ]
            )
        finally:
            sys.stdout = original_stdout

        self.assertEqual(exit_code, 0)
        self.assertIn("Curadoria concluída", captured_output.getvalue())

        note_file = self.notes_dir / "Como verificar portas abertas no Linux.md"
        self.assertTrue(note_file.exists())

        # Segunda execução sem --force: deve reportar 0 novas notas
        captured_output_2 = io.StringIO()
        try:
            sys.stdout = captured_output_2
            exit_code_2 = main(
                [
                    "curate",
                    "--segments-dir",
                    str(self.segments_dir),
                    "--notes-dir",
                    str(self.notes_dir),
                ]
            )
        finally:
            sys.stdout = original_stdout

        self.assertEqual(exit_code_2, 0)
        self.assertIn("0 novas notas", captured_output_2.getvalue())

        # Terceira execução COM --force: deve reprocessar a nota
        captured_output_3 = io.StringIO()
        try:
            sys.stdout = captured_output_3
            exit_code_3 = main(
                [
                    "curate",
                    "--segments-dir",
                    str(self.segments_dir),
                    "--notes-dir",
                    str(self.notes_dir),
                    "--force",
                ]
            )
        finally:
            sys.stdout = original_stdout

        self.assertEqual(exit_code_3, 0)
        self.assertIn("1 novas notas", captured_output_3.getvalue())


if __name__ == "__main__":
    unittest.main()
