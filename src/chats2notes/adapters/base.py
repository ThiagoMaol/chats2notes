"""Base adapter abstract class for chats2notes."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, List, Optional

from chats2notes.models import SessionSummary, Turn


class BaseAdapter(ABC):
    """Abstract base adapter for log format ingestion."""

    @abstractmethod
    def discover_sessions(self, base_paths: Optional[List[Path]] = None) -> List[SessionSummary]:
        """Discovers sessions across one or more base directories."""
        pass

    @abstractmethod
    def extract_new_turns(self, session: SessionSummary, since_step_index: int = 0) -> Iterator[Turn]:
        """Extracts turns from a session after the given step_index."""
        pass
