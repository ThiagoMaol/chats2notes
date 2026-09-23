"""State management for chats2notes checkpoints."""

from pathlib import Path
from typing import Dict, Optional, Tuple


class StateManager:
    """Manages incremental checkpoints persisted to disk atomically."""

    def __init__(self, state_file: Path):
        self.state_file = Path(state_file)
        self._state: Dict[str, int] = {}

    def get_checkpoint(self, host_user: str, session_id: str) -> int:
        """Returns the last processed step_index for the given session and user."""
        raise NotImplementedError("StateManager.get_checkpoint not implemented yet")

    def update_checkpoint(self, host_user: str, session_id: str, step_index: int) -> None:
        """Updates the checkpoint in memory."""
        raise NotImplementedError("StateManager.update_checkpoint not implemented yet")

    def save(self) -> None:
        """Persists the state to disk atomically using temporary file replace."""
        raise NotImplementedError("StateManager.save not implemented yet")

    def load(self) -> None:
        """Loads state from disk if it exists."""
        raise NotImplementedError("StateManager.load not implemented yet")
