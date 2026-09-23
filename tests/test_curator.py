import os
import tempfile
import unittest
from pathlib import Path

# Tentativa de importação da unidade a ser desenvolvida (RED esperado)
from chats2notes.curator import CuratorEngine, NoteDiagrammer, CuratedManifest


class TestCuratorEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.segments_dir = Path(self.temp_dir.name) / "segments"
        self.notes_dir = Path(self.temp_dir.name) / "notas"
        self.segments_dir.mkdir(parents=True)
        self.notes_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_curate_faq_atomic_note(self):
        # SPECSFY:AC-001
        """Deve converter um segmento geral em nota FAQ atômica com resposta enxuta e divisor."""
        session_dir = self.segments_dir / "user_a" / "sess_faq"
        session_dir.mkdir(parents=True)
        segment_file = session_dir / "0001.md"
        segment_file.write_text(
            """---
session_id: "sess_faq"
turn: 1
timestamp: "2026-09-23T10:00:00Z"
user: "user_a"
start_step: 0
end_step: 1
---

# Entrada
Como configurar o SSH no Debian 12 com chave pública?

# Resposta
Para configurar o SSH no Debian 12 com chave pública, siga estes passos. Primeiro gere a chave com ssh-keygen. Depois copie com ssh-copy-id. Por fim ajuste o arquivo /etc/ssh/sshd_config desabilitando PasswordAuthentication.
""",
            encoding="utf-8",
        )

        engine = CuratorEngine(segments_dir=self.segments_dir, notes_dir=self.notes_dir)
        notes = engine.process_all()

        self.assertEqual(len(notes), 1)
        expected_note = self.notes_dir / "Como configurar o SSH no Debian 12 com chave pública.md"
        self.assertTrue(expected_note.exists())

        content = expected_note.read_text(encoding="utf-8")
        # Validação do YAML frontmatter
        self.assertIn("tags:", content)
        self.assertIn("faq", content)
        self.assertIn("linux", content)
        self.assertIn('segment_ref: "vault/segments/user_a/sess_faq/0001.md"', content)
        self.assertIn('source: "antigravity"', content)

        # Validação da estrutura de corpo e divisor
        self.assertIn("## Resumo Direto", content)
        self.assertIn("---", content)
        self.assertIn("## Diálogo Original", content)
        self.assertIn("Como configurar o SSH no Debian 12 com chave pública?", content)

    def test_curate_pair_programming_note(self):
        # SPECSFY:AC-002
        """Deve converter pergunta numerada de framework em nota pair-programming estruturada."""
        session_dir = self.segments_dir / "user_a" / "sess_specsfy"
        session_dir.mkdir(parents=True)
        segment_file = session_dir / "0001.md"
        segment_file.write_text(
            """---
session_id: "sess_specsfy"
turn: 1
timestamp: "2026-09-23T11:00:00Z"
user: "user_a"
start_step: 0
end_step: 1
---

# Entrada
Pergunta 1. Qual o tipo de banco de dados do projeto?
1. PostgreSQL relacional
2. SQLite local
3. MySQL
4. Escrever outra resposta
5. Gere outras opções
6. Avançar

# Resposta
1. PostgreSQL relacional com extensão pgvector para embeddings.
""",
            encoding="utf-8",
        )

        engine = CuratorEngine(segments_dir=self.segments_dir, notes_dir=self.notes_dir, project_name="chats2notes")
        notes = engine.process_all()

        self.assertEqual(len(notes), 1)
        expected_note = self.notes_dir / "chats2notes - specsfy - Pergunta 1.md"
        self.assertTrue(expected_note.exists())

        content = expected_note.read_text(encoding="utf-8")
        self.assertIn("pair-programming", content)
        self.assertIn('project: "chats2notes"', content)
        self.assertIn("## Pergunta", content)
        self.assertIn("## Resposta Selecionada", content)
        self.assertIn("PostgreSQL relacional com extensão pgvector", content)
        self.assertIn("---", content)
        self.assertIn("## Alternativas Originais", content)

    def test_discard_operational_noise_turn(self):
        # SPECSFY:AC-003
        """Deve descartar mensagens triviais e operacionais gravando no manifesto."""
        session_dir = self.segments_dir / "user_a" / "sess_noise"
        session_dir.mkdir(parents=True)
        segment_file = session_dir / "0001.md"
        segment_file.write_text(
            """---
session_id: "sess_noise"
turn: 1
timestamp: "2026-09-23T12:00:00Z"
user: "user_a"
start_step: 0
end_step: 1
---

# Entrada
sim

# Resposta
Entendido. Prosseguindo com o próximo passo da especificação.
""",
            encoding="utf-8",
        )

        engine = CuratorEngine(segments_dir=self.segments_dir, notes_dir=self.notes_dir)
        notes = engine.process_all()

        self.assertEqual(len(notes), 0)
        # Nenhuma nota gerada
        self.assertEqual(len(list(self.notes_dir.glob("*.md"))), 0)

        # Manifesto registrou o descarte
        manifest = CuratedManifest(self.temp_dir.name)
        self.assertTrue(manifest.is_discarded("sess_noise", "0001"))

    def test_split_multiple_independent_questions(self):
        # SPECSFY:AC-004
        """Deve desdobrar perguntas múltiplas independentes em notas distintas com links mútuos."""
        session_dir = self.segments_dir / "user_a" / "sess_split"
        session_dir.mkdir(parents=True)
        segment_file = session_dir / "0001.md"
        segment_file.write_text(
            """---
session_id: "sess_split"
turn: 1
timestamp: "2026-09-23T13:00:00Z"
user: "user_a"
start_step: 0
end_step: 1
---

# Entrada
Como criar uma branch no git? E como rodar um container docker com porta exposta?

# Resposta
Para criar uma branch no git: `git switch -c nome-da-branch`.
Para rodar um container docker com porta: `docker run -p 8080:80 nginx`.
""",
            encoding="utf-8",
        )

        engine = CuratorEngine(segments_dir=self.segments_dir, notes_dir=self.notes_dir)
        notes = engine.process_all()

        self.assertEqual(len(notes), 2)
        note_files = list(self.notes_dir.glob("*.md"))
        self.assertEqual(len(note_files), 2)

        # Cada nota referencia a outra no frontmatter
        note1_content = note_files[0].read_text(encoding="utf-8")
        note2_content = note_files[1].read_text(encoding="utf-8")
        self.assertIn("related_notes:", note1_content)
        self.assertIn("related_notes:", note2_content)

    def test_disambiguate_note_name_collision(self):
        # SPECSFY:AC-005
        """Deve adicionar sufixo numérico quando existir colisão de nomes de notas idênticos."""
        # Criar nota preexistente
        existing_note = self.notes_dir / "Como listar branches no Git.md"
        existing_note.write_text("Conteúdo anterior", encoding="utf-8")

        session_dir = self.segments_dir / "user_a" / "sess_col"
        session_dir.mkdir(parents=True)
        segment_file = session_dir / "0001.md"
        segment_file.write_text(
            """---
session_id: "sess_col"
turn: 1
timestamp: "2026-09-23T14:00:00Z"
user: "user_a"
start_step: 0
end_step: 1
---

# Entrada
Como listar branches no Git?

# Resposta
Execute `git branch -a` para listar locais e remotas.
""",
            encoding="utf-8",
        )

        engine = CuratorEngine(segments_dir=self.segments_dir, notes_dir=self.notes_dir)
        notes = engine.process_all()

        self.assertEqual(len(notes), 1)
        expected_note = self.notes_dir / "Como listar branches no Git (2).md"
        self.assertTrue(expected_note.exists())
        self.assertEqual(existing_note.read_text(encoding="utf-8"), "Conteúdo anterior")


if __name__ == "__main__":
    unittest.main()
