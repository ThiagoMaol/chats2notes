"""Motor de curadoria e síntese de notas atômicas para SilverBullet e Obsidian.

Lê segmentos fatiados em vault/segments/, filtra ruídos operacionais, classifica em
FAQ ou Pair-Programming, diagrama notas em Markdown com YAML frontmatter limpo e
mantém manifesto de rastreamento com memória de descarte.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CANONICAL_TAGS = {
    "git",
    "github",
    "gitea",
    "n8n",
    "llm",
    "linux",
    "windows",
    "tmux",
    "python",
    "php",
    "lua",
    "html",
    "css",
    "javascript",
    "laravel",
    "astro",
    "script",
    "automação",
    "ia",
    "vídeo",
    "áudio",
    "texto",
    "tts",
    "stt",
    "chat",
    "specsfy",
    "mvpfy",
    "brandfy",
    "companify",
    "ssh",
    "debian",
    "docker",
    "sqlite",
    "postgres",
    "database",
}

SYNONYM_MAP = {
    "python3": "python",
    "py": "python",
    "bash": "linux",
    "shell": "linux",
    "sh": "linux",
    "automation": "automação",
    "automatizado": "automação",
    "postgresql": "postgres",
}

OPERATIONAL_NOISE_PATTERNS = [
    r"^(?:sim|s|yes|y|ok|beleza|blz|certo|fechado|valeu|obrigado|prossiga|prosseguir|continua|continuar|pode continuar|entendido|avançar|1|2|3|4|5|6)\.?$",
    r"^(?:sim|ok|prossiga)[,!.\s]+(?:pode continuar|vamos em frente|prosseguir|em frente)?\.?$",
]


@dataclass
class CuratedManifest:
    """Gerencia o arquivo de manifesto de curadoria (vault/.curated.json)."""

    base_dir: Path
    manifest_file: Optional[Path] = None
    manifest_path: Path = field(init=False)
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.base_dir = Path(self.base_dir)
        if self.manifest_file:
            self.manifest_path = Path(self.manifest_file)
        else:
            self.manifest_path = self.base_dir / ".curated.json"
        self.load()

    def load(self) -> None:
        if self.manifest_path.exists():
            try:
                self.data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception:
                self.data = {"sessions": {}, "notes": []}
        else:
            self.data = {"sessions": {}, "notes": []}

    def save(self) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def is_evaluated(self, session_id: str, segment_num: str) -> bool:
        session_entry = self.data.get("sessions", {}).get(session_id, {})
        return segment_num in session_entry.get("evaluated_segments", [])

    def is_discarded(self, session_id: str, segment_num: str) -> bool:
        session_entry = self.data.get("sessions", {}).get(session_id, {})
        return segment_num in session_entry.get("discarded_segments", [])

    def mark_evaluated(self, session_id: str, segment_num: str) -> None:
        sessions = self.data.setdefault("sessions", {})
        session_entry = sessions.setdefault(session_id, {"evaluated_segments": [], "discarded_segments": [], "notes": []})
        if segment_num not in session_entry["evaluated_segments"]:
            session_entry["evaluated_segments"].append(segment_num)
        self.save()

    def mark_discarded(self, session_id: str, segment_num: str, reason: str = "noise") -> None:
        sessions = self.data.setdefault("sessions", {})
        session_entry = sessions.setdefault(session_id, {"evaluated_segments": [], "discarded_segments": [], "notes": []})
        if segment_num not in session_entry["evaluated_segments"]:
            session_entry["evaluated_segments"].append(segment_num)
        if segment_num not in session_entry["discarded_segments"]:
            session_entry["discarded_segments"].append(segment_num)
        self.save()

    def record_note(self, session_id: str, segment_num: str, note_name: str) -> None:
        sessions = self.data.setdefault("sessions", {})
        session_entry = sessions.setdefault(session_id, {"evaluated_segments": [], "discarded_segments": [], "notes": []})
        if segment_num not in session_entry["evaluated_segments"]:
            session_entry["evaluated_segments"].append(segment_num)
        if note_name not in session_entry["notes"]:
            session_entry["notes"].append(note_name)
        notes_list = self.data.setdefault("notes", [])
        if note_name not in notes_list:
            notes_list.append(note_name)
        self.save()

    def clear(self) -> None:
        self.data = {"sessions": {}, "notes": []}
        self.save()


class TagTaxonomy:
    """Extrai e normaliza tags baseadas em vocabulário controlado extensível."""

    DISTRO_ECOSYSTEM = {"debian", "ubuntu", "arch", "alpine", "fedora"}

    @staticmethod
    def extract_tags(text: str, category: str) -> List[str]:
        found_tags: List[str] = [category]
        lower_text = text.lower()
        words = re.findall(r"\b[a-záàâãéèêíïóôõöúçñ0-9_-]+\b", lower_text)

        for word in words:
            normalized = SYNONYM_MAP.get(word, word)
            if normalized in CANONICAL_TAGS and normalized not in found_tags:
                found_tags.append(normalized)
            if normalized in TagTaxonomy.DISTRO_ECOSYSTEM and "linux" not in found_tags:
                found_tags.append("linux")

        return found_tags


class NoiseDetector:
    """Identifica mensagens operacionais e triviais que devem ser descartadas."""

    @staticmethod
    def is_noise(prompt_text: str, response_text: str) -> bool:
        cleaned_prompt = prompt_text.strip().lower()
        if not cleaned_prompt:
            return True
        for pattern in OPERATIONAL_NOISE_PATTERNS:
            if re.match(pattern, cleaned_prompt):
                return True
        return False


class QuestionSplitter:
    """Identifica e desdobra perguntas múltiplas e independentes no mesmo turno."""

    @staticmethod
    def split(prompt_text: str, response_text: str) -> List[Tuple[str, str]]:
        if NoteDiagrammer.is_pair_programming(prompt_text):
            return [(prompt_text.strip(), response_text.strip())]

        # Procura por divisões explícitas com '?'
        questions = [q.strip() + "?" for q in prompt_text.split("?") if q.strip()]
        if len(questions) <= 1:
            return [(prompt_text.strip(), response_text.strip())]

        # Tenta correlacionar respostas quando cada pergunta tem tópico identificável
        items: List[Tuple[str, str]] = []
        for q in questions:
            # Busca trechos relevantes na resposta
            lines = [l for l in response_text.splitlines() if l.strip()]
            q_lower = q.lower()
            matching_lines = []
            for line in lines:
                # Se a linha menciona termos centrais da pergunta
                keywords = [w for w in re.findall(r"\b\w{3,}\b", q_lower) if w not in {"como", "para", "qual", "onde", "uma", "com"}]
                if any(k in line.lower() for k in keywords):
                    matching_lines.append(line)
            matched_response = "\n".join(matching_lines) if matching_lines else response_text
            items.append((q, matched_response))

        if len(items) == len(questions):
            return items
        return [(prompt_text.strip(), response_text.strip())]


class NoteDiagrammer:
    """Formata o corpo e frontmatter de notas atômicas conforme o tipo."""

    @staticmethod
    def is_pair_programming(prompt_text: str) -> bool:
        lower = prompt_text.lower()
        has_framework = any(fw in lower for fw in ["specsfy", "mvpfy", "brandfy", "companify", "framework"])
        has_numbered = bool(re.search(r"\bpergunta\s+\d+\b", lower))
        has_options = bool(re.search(r"^\s*1\.\s+", prompt_text, re.MULTILINE))
        return (has_numbered and has_options) or (has_framework and has_options)

    @staticmethod
    def generate_faq_summary(response_text: str) -> str:
        """Gera resumo objetivo em tópicos para Dev Júnior sem prolixidade de IA."""
        lines = [line.strip() for line in response_text.splitlines() if line.strip()]
        sentences: List[str] = []
        for line in lines:
            # Dividir em frases limpas
            parts = re.split(r"(?<=[.!?])\s+", line)
            for part in parts:
                cleaned = part.strip()
                if cleaned and not any(p in cleaned.lower() for p in ["siga estes passos", "vamos", "entendido", "prosseguindo"]):
                    sentences.append(cleaned)

        bullets = []
        for s in sentences[:4]:
            bullet_text = s.rstrip(".")
            bullets.append(f"- {bullet_text}.")

        if not bullets:
            bullets = [f"- {response_text.strip()}"]

        return "\n".join(bullets)

    @staticmethod
    def render_faq_note(
        title: str,
        prompt: str,
        response: str,
        tags: List[str],
        project: Optional[str],
        created_at: str,
        chat_date: str,
        segment_ref: str,
        related_notes: List[str],
        source: str = "antigravity",
    ) -> str:
        summary_bullets = NoteDiagrammer.generate_faq_summary(response)
        tags_yaml = "\n".join(f"  - {t}" for t in tags)
        related_yaml = "\n".join(f"  - {r}" for r in related_notes) if related_notes else " []"
        project_yaml = f'"{project}"' if project else "null"

        frontmatter = f"""---
name: "{title}"
tags:
{tags_yaml}
project: {project_yaml}
created: "{created_at}"
chat_date: "{chat_date}"
segment_ref: "{segment_ref}"
related_notes:{related_yaml}
source: "{source}"
---"""

        body = f"""# {title}

## Resumo Direto
{summary_bullets}

---

## Diálogo Original
### Entrada
{prompt}

### Resposta
{response}
"""
        return f"{frontmatter}\n\n{body}"

    @staticmethod
    def render_pair_programming_note(
        title: str,
        prompt: str,
        response: str,
        tags: List[str],
        project: Optional[str],
        created_at: str,
        chat_date: str,
        segment_ref: str,
        related_notes: List[str],
        source: str = "antigravity",
    ) -> str:
        # Extrair a pergunta resumida sem alternativas
        first_line = prompt.splitlines()[0] if prompt.splitlines() else prompt
        question_cleaned = re.sub(r"^(?:Pergunta\s+\d+\.\s*)", "", first_line).strip()

        tags_yaml = "\n".join(f"  - {t}" for t in tags)
        related_yaml = "\n".join(f"  - {r}" for r in related_notes) if related_notes else " []"
        project_yaml = f'"{project}"' if project else "null"

        frontmatter = f"""---
name: "{title}"
tags:
{tags_yaml}
project: {project_yaml}
created: "{created_at}"
chat_date: "{chat_date}"
segment_ref: "{segment_ref}"
related_notes:{related_yaml}
source: "{source}"
---"""

        body = f"""# {title}

## Pergunta
{question_cleaned}

## Resposta Selecionada
{response.strip()}

---

## Alternativas Originais
{prompt.strip()}
"""
        return f"{frontmatter}\n\n{body}"


class CuratorEngine:
    """Motor orquestrador de curadoria e persistência de notas atômicas."""

    def __init__(
        self,
        segments_dir: Path | str,
        notes_dir: Path | str,
        manifest_file: Optional[Path | str] = None,
        project_name: Optional[str] = None,
        force: bool = False,
    ):
        self.segments_dir = Path(segments_dir)
        self.notes_dir = Path(notes_dir)
        self.project_name = project_name
        self.force = force
        if manifest_file:
            m_path = Path(manifest_file)
            self.manifest = CuratedManifest(base_dir=m_path.parent, manifest_file=m_path)
        else:
            base_dir = self.notes_dir.parent if self.notes_dir.parent.exists() else self.notes_dir
            self.manifest = CuratedManifest(base_dir=base_dir)

    def _resolve_note_path(self, title: str, segment_ref: str) -> Path:
        """Resolve colisão de nomes com sufixo (2), respeitando idempotência da mesma ref."""
        clean_title = re.sub(r'[\\/*?:"<>|\r\n]', "", title).strip()
        clean_title = re.sub(r"^[-–—!?)(\s]+", "", clean_title).strip()
        clean_title = re.sub(r"\s+", " ", clean_title)
        if len(clean_title) > 80:
            truncated = clean_title[:80]
            if " " in truncated:
                clean_title = truncated.rsplit(" ", 1)[0].strip()
            else:
                clean_title = truncated.strip()
        if not clean_title:
            clean_title = "Nota"

        candidate = self.notes_dir / f"{clean_title}.md"
        if not candidate.exists():
            return candidate

        # Se já existe com este nome exato, verifica se é do mesmo segmento
        try:
            existing_content = candidate.read_text(encoding="utf-8")
            if f'segment_ref: "{segment_ref}"' in existing_content:
                return candidate
        except Exception:
            pass

        # Colisão de título diferente: aplica (2), (3)...
        idx = 2
        while True:
            candidate = self.notes_dir / f"{clean_title} ({idx}).md"
            if not candidate.exists():
                return candidate
            try:
                existing_content = candidate.read_text(encoding="utf-8")
                if f'segment_ref: "{segment_ref}"' in existing_content:
                    return candidate
            except Exception:
                pass
            idx += 1

    @staticmethod
    def clean_prompt(raw_prompt: str) -> str:
        """Extrai o texto real do usuário, eliminando tags do sistema e metadados injetados."""
        prompt = raw_prompt.strip()
        user_req_match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", prompt, re.DOTALL)
        if user_req_match:
            prompt = user_req_match.group(1).strip()
        else:
            prompt = re.sub(r"<\/?USER_REQUEST>", "", prompt).strip()

        prompt = re.sub(r"<ADDITIONAL_METADATA>.*?(?:</ADDITIONAL_METADATA>|\Z)", "", prompt, flags=re.DOTALL).strip()
        prompt = re.sub(r"<SKILL>.*?(?:</SKILL>|\Z)", "", prompt, flags=re.DOTALL).strip()
        prompt = re.sub(r"ADDITIONAL_METADATA.*", "", prompt, flags=re.DOTALL).strip()
        return prompt.strip()

    def _parse_segment_file(self, segment_path: Path) -> Tuple[Dict[str, Any], str, str]:
        """Extrai frontmatter YAML básico e seções # Entrada e # Resposta."""
        content = segment_path.read_text(encoding="utf-8")
        meta: Dict[str, Any] = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip().strip('"').strip("'")
                body = parts[2]
            else:
                body = content
        else:
            body = content

        prompt_match = re.search(r"^#\s+Entrada\s*\n(.*?)(?=^#\s+Resposta|\Z)", body, re.DOTALL | re.MULTILINE)
        response_match = re.search(r"^#\s+Resposta\s*\n(.*)", body, re.DOTALL | re.MULTILINE)

        raw_prompt = prompt_match.group(1).strip() if prompt_match else ""
        prompt = self.clean_prompt(raw_prompt)
        response = response_match.group(1).strip() if response_match else ""
        return meta, prompt, response

    def process_all(self) -> List[Path]:
        """Processa todos os segmentos encontrados e retorna as notas geradas."""
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        if self.force:
            self.manifest.clear()

        created_notes: List[Path] = []

        # Encontrar todas as sessões sob segments_dir
        segment_files = sorted(self.segments_dir.glob("*/*/*.md"))
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        for seg_file in segment_files:
            session_id = seg_file.parent.name
            user = seg_file.parent.parent.name
            segment_num = seg_file.stem
            segment_ref = f"vault/segments/{user}/{session_id}/{seg_file.name}"

            if not self.force and self.manifest.is_evaluated(session_id, segment_num):
                continue

            meta, prompt, response = self._parse_segment_file(seg_file)
            chat_date = meta.get("timestamp", now_str)

            # 1. Filtragem de ruído operacional
            if NoiseDetector.is_noise(prompt, response):
                self.manifest.mark_discarded(session_id, segment_num, reason="noise")
                continue

            # 2. Desdobramento de perguntas múltiplas
            sub_pairs = QuestionSplitter.split(prompt, response)
            generated_names_in_turn: List[str] = []

            for q, a in sub_pairs:
                is_pp = NoteDiagrammer.is_pair_programming(q)

                if is_pp:
                    category = "pair-programming"
                    project = self.project_name or meta.get("project", "projeto")
                    framework = "specsfy"
                    num_match = re.search(r"\bpergunta\s+(\d+)\b", q.lower())
                    p_num = num_match.group(1) if num_match else segment_num
                    title = f"{project} - {framework} - Pergunta {p_num}"
                else:
                    category = "faq"
                    project = self.project_name
                    # Título a partir da primeira pergunta limpa ou primeira linha
                    clean_lines = [l.strip() for l in q.splitlines() if l.strip()]
                    first_line = clean_lines[0] if clean_lines else "Nota"
                    if "?" in first_line:
                        title = first_line.split("?")[0].strip()
                    else:
                        title = first_line

                    # Remover caracteres inválidos para título
                    title = re.sub(r'[\\/*?:"<>|\r\n]', " ", title).strip()
                    title = re.sub(r"^[-–—!?)(\s]+", "", title).strip()
                    title = re.sub(r"\s+", " ", title).strip()

                    # Truncar com segurança para caber em nome de arquivo (< 80 caracteres)
                    if len(title) > 80:
                        truncated = title[:80]
                        if " " in truncated:
                            title = truncated.rsplit(" ", 1)[0].strip()
                        else:
                            title = truncated.strip()

                    if not title:
                        title = f"Nota {segment_num}"
                    if title and title[0].islower():
                        title = title[0].upper() + title[1:]

                tags = TagTaxonomy.extract_tags(f"{q} {a}", category=category)
                note_path = self._resolve_note_path(title, segment_ref)
                generated_names_in_turn.append(note_path.name)

                # Renderizar nota
                if is_pp:
                    note_content = NoteDiagrammer.render_pair_programming_note(
                        title=note_path.stem,
                        prompt=q,
                        response=a,
                        tags=tags,
                        project=project,
                        created_at=now_str,
                        chat_date=chat_date,
                        segment_ref=segment_ref,
                        related_notes=[],
                    )
                else:
                    note_content = NoteDiagrammer.render_faq_note(
                        title=note_path.stem,
                        prompt=q,
                        response=a,
                        tags=tags,
                        project=project,
                        created_at=now_str,
                        chat_date=chat_date,
                        segment_ref=segment_ref,
                        related_notes=[],
                    )

                note_path.write_text(note_content, encoding="utf-8")
                self.manifest.record_note(session_id, segment_num, note_path.name)
                created_notes.append(note_path)

            # Se houve desdobramento múltiplo, atualizar related_notes entre elas
            if len(generated_names_in_turn) > 1:
                for name in generated_names_in_turn:
                    p = self.notes_dir / name
                    if p.exists():
                        other_notes = [f'"{n}"' for n in generated_names_in_turn if n != name]
                        content = p.read_text(encoding="utf-8")
                        content = re.sub(r"related_notes:\s*\[\]", f"related_notes:\n" + "\n".join(f"  - {o}" for o in other_notes), content)
                        p.write_text(content, encoding="utf-8")

        return created_notes
