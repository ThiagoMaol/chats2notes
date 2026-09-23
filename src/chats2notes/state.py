"""State management for chats2notes checkpoints."""

import json
import os
from pathlib import Path
from typing import Dict, Union


class StateManager:
    """Manages incremental checkpoints persisted to disk atomically."""

    def __init__(self, state_file: Union[str, Path]):
        self.state_file = Path(state_file)
        self._state: Dict[str, int] = {}
        if self.state_file.exists():
            self.load()

    def _make_key(self, host_user: str, session_id: str) -> str:
        """Generates a composite key for the user and session."""
        user = (host_user or "default").strip()
        sess = session_id.strip()
        return f"{user}:{sess}"

    def get_checkpoint(self, host_user: str, session_id: str) -> int:
        """Returns the last processed step_index for the given session and user."""
        key = self._make_key(host_user, session_id)
        return self._state.get(key, 0)

    def update_checkpoint(self, host_user: str, session_id: str, step_index: int) -> None:
        """Updates the checkpoint in memory."""
        key = self._make_key(host_user, session_id)
        self._state[key] = max(self._state.get(key, 0), int(step_index))

    def save(self) -> None:
        """Persists the state to disk atomically using temporary file replace."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.state_file.with_name(f"{self.state_file.name}.tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_file, self.state_file)
        except Exception:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
            raise

    def load(self) -> None:
        """Loads state from disk if it exists."""
        if not self.state_file.exists():
            self._state = {}
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._state = {str(k): int(v) for k, v in data.items()}
                else:
                    self._state = {}
        except (json.JSONDecodeError, OSError):
            self._state = {}
