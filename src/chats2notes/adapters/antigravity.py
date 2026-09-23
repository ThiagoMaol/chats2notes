"""Antigravity CLI log adapter."""

from pathlib import Path
from typing import Iterator, List, Optional

from chats2notes.adapters.base import BaseAdapter
from chats2notes.models import SessionSummary, Turn


class AntigravityAdapter(BaseAdapter):
    """Adapter for Antigravity CLI brain transcript files."""

    def __init__(self, default_brain_dir: Optional[Path] = None):
        self.default_brain_dir = default_brain_dir or (Path.home() / ".gemini" / "antigravity-cli" / "brain")

    def discover_sessions(self, base_paths: Optional[List[Path]] = None) -> List[SessionSummary]:
        """Discovers sessions across one or more brain paths, supporting multi-user home directories."""
        raise NotImplementedError("AntigravityAdapter.discover_sessions not implemented yet")

    def extract_new_turns(self, session: SessionSummary, since_step_index: int = 0) -> Iterator[Turn]:
        """Reads transcript_full.jsonl incrementally, yielding new Turn objects."""
        raise NotImplementedError("AntigravityAdapter.extract_new_turns not implemented yet")
