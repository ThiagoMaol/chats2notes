"""Data models for chats2notes."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Turn:
    """Represents a single conversation turn between user and assistant."""
    session_id: str
    step_index: int
    created_at: str
    user_prompt: str
    assistant_response: str
    host_user: str = ""
    workspace: str = ""
    agent: str = "antigravity"
    tags: List[str] = field(default_factory=list)


@dataclass
class SessionSummary:
    """Summary of a discovered conversation session."""
    session_id: str
    host_user: str
    workspace: str
    transcript_path: Path
    last_step_index: int = 0
    updated_at: str = ""


@dataclass
class ExtractionConfig:
    """Configuration for an extraction run."""
    brain_dirs: List[Path] = field(default_factory=list)
    output_dir: Path = field(default_factory=lambda: Path.cwd() / "notes")
    state_file: Path = field(default_factory=lambda: Path.home() / ".chats2notes" / "state.json")
    format_mode: str = "silverbullet"
