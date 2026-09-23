"""Storage management for formatting and writing Markdown notes."""

from pathlib import Path
from typing import Optional

from chats2notes.models import Turn


class MarkdownStorage:
    """Formats conversation turns into markdown notes for SilverBullet and Obsidian."""

    def __init__(self, output_dir: Path, format_mode: str = "silverbullet"):
        self.output_dir = Path(output_dir)
        self.format_mode = format_mode

    def format_note(self, turn: Turn) -> str:
        """Generates markdown string with frontmatter and structured body."""
        raise NotImplementedError("MarkdownStorage.format_note not implemented yet")

    def write_note(self, turn: Turn) -> Path:
        """Formats and writes the note to the output directory."""
        raise NotImplementedError("MarkdownStorage.write_note not implemented yet")
