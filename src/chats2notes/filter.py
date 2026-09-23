"""Workspace filtering logic for chats2notes."""

import os
from pathlib import Path
from typing import List, Optional


class WorkspaceFilter:
    """Filters out sessions that belong to ignored workspaces or projects."""

    def __init__(self, ignored_workspaces: Optional[List[str]] = None, ignore_self: bool = True):
        self.ignored_workspaces = [str(w).rstrip("/\\") for w in (ignored_workspaces or []) if w]
        self.ignore_self = ignore_self

    def should_ignore(self, workspace: Optional[str]) -> bool:
        """Returns True if the workspace path should be ignored."""
        if not workspace:
            return False

        ws_str = str(workspace).strip()
        if not ws_str:
            return False

        # Default self-exclusion: chats2notes
        if self.ignore_self:
            ws_parts = [p.lower() for p in Path(ws_str).parts]
            if "chats2notes" in ws_parts or "chats2notes" in ws_str.lower():
                return True

        # Check configured ignored workspaces (matches directory and any subdirectories)
        ws_norm = os.path.normpath(ws_str)
        for pattern in self.ignored_workspaces:
            pat_norm = os.path.normpath(pattern)
            if ws_norm == pat_norm:
                return True
            if ws_norm.startswith(pat_norm + os.sep):
                return True

        return False
