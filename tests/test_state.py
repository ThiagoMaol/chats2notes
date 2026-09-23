"""Unit tests for StateManager and checkpoint persistence."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from chats2notes.state import StateManager


class TestStateManager(unittest.TestCase):
    """Test suite for incremental checkpoint tracking and atomic persistence."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temp_dir.name) / "test_state.json"
        self.manager = StateManager(self.state_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-001
    def test_initial_checkpoint_empty(self):
        """When state file does not exist, get_checkpoint returns 0."""
        step = self.manager.get_checkpoint("user1", "session_abc")
        self.assertEqual(step, 0)

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-002
    def test_update_and_save_checkpoint(self):
        """Updates checkpoint and verifies persistence across reloads."""
        self.manager.update_checkpoint("user_dev", "sess_001", 7)
        self.manager.save()

        # Load in another manager instance
        new_manager = StateManager(self.state_file)
        new_manager.load()
        self.assertEqual(new_manager.get_checkpoint("user_dev", "sess_001"), 7)

    # SPECSFY: US-001 FR-001 FR-002 FR-003 NFR-001 AC-003
    def test_atomic_save_resilience(self):
        """Verifies state is saved atomically and file contains valid JSON."""
        self.manager.update_checkpoint("thiago", "sess_999", 42)
        self.manager.save()

        self.assertTrue(self.state_file.exists())
        with open(self.state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("thiago:sess_999", data)
        self.assertEqual(data["thiago:sess_999"], 42)


if __name__ == "__main__":
    unittest.main()
