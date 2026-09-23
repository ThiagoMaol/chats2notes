"""Storage management for formatting and writing Markdown notes."""

import json
import re
import unicodedata
from pathlib import Path
from typing import Optional, Union

from chats2notes.models import Turn


class MarkdownStorage:
    """Formats conversation turns into markdown notes for SilverBullet and Obsidian."""

    def __init__(self, output_dir: Union[str, Path], format_mode: str = "silverbullet"):
        self.output_dir = Path(output_dir)
        self.format_mode = format_mode

    def _safe_yaml_value(self, val: str) -> str:
        """Safely formats a string value for YAML frontmatter."""
        if not val:
            return '""'
        # If value has quotes, colons, newlines or special symbols, quote it as JSON string
        if any(c in val for c in [":", '"', "'", "\n", "#", "@", "`", "[", "]", "{", "}"]):
            return json.dumps(val, ensure_ascii=False)
        return val

    def _generate_title(self, prompt: str) -> str:
        """Derives a concise title from the user's prompt."""
        first_line = prompt.strip().split("\n")[0].strip()
        first_line = re.sub(r"^[#\s\-\*]+", "", first_line)
        if len(first_line) > 80:
            first_line = first_line[:77] + "..."
        return first_line or "Conversa sem título"

    def _slugify(self, text: str) -> str:
        """Converts text into a clean filesystem-friendly slug."""
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^\w\s-]", "", text.lower())
        text = re.sub(r"[-\s]+", "-", text).strip("-")
        return text[:50] or "nota"

    def format_note(self, turn: Turn) -> str:
        """Generates markdown string with frontmatter and structured body."""
        title = self._generate_title(turn.user_prompt)
        safe_title = self._safe_yaml_value(title)
        safe_agent = self._safe_yaml_value(turn.agent)
        safe_user = self._safe_yaml_value(turn.host_user)
        safe_workspace = self._safe_yaml_value(turn.workspace)
        safe_session = self._safe_yaml_value(turn.session_id)
        created_str = turn.created_at or "2026-09-23 00:00:00"

        tags = turn.tags or ["ai-notes", "antigravity"]
        tags_str = ", ".join(tags)

        frontmatter = [
            "---",
            f"name: {safe_title}",
            f"created: {created_str}",
            f"tags: [{tags_str}]",
            f"agent: {safe_agent}",
            f"host_user: {safe_user}",
            f"workspace: {safe_workspace}",
            f"session: {safe_session}",
            'category: "Engenharia de Software"',
            "---",
            "",
            f"# {title}",
            "",
            "## Prompt",
            "",
            turn.user_prompt.strip(),
            "",
            "## Resposta",
            "",
            turn.assistant_response.strip(),
            "",
        ]
        return "\n".join(frontmatter)

    def write_note(self, turn: Turn) -> Path:
        """Formats and writes the note to the output directory."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        slug = self._slugify(self._generate_title(turn.user_prompt))

        date_prefix = "2026-09-23"
        if turn.created_at:
            match = re.match(r"^(\d{4}-\d{2}-\d{2})", turn.created_at)
            if match:
                date_prefix = match.group(1)

        filename = f"{date_prefix}-{slug}.md"
        target_path = self.output_dir / filename

        # Avoid overwriting distinct turns with the same slug
        counter = 1
        while target_path.exists():
            filename = f"{date_prefix}-{slug}-{turn.step_index or counter}.md"
            target_path = self.output_dir / filename
            counter += 1

        content = self.format_note(turn)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        return target_path
