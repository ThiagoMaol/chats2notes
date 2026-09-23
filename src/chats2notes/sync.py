"""Raw log synchronizer to vault/raw."""

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

from chats2notes.models import SessionSummary


@dataclass
class SyncResult:
    """Summary of a synchronization run."""
    discovered: int = 0
    synced: int = 0
    updated: int = 0
    skipped: int = 0
    ignored: int = 0


class RawSynchronizer:
    """Synchronizes exact raw transcripts to a local vault/raw directory."""

    def __init__(self, raw_dir: Optional[Path] = None, inbox_dir: Optional[Path] = None):
        target = raw_dir or inbox_dir or Path("./vault/raw")
        self.raw_dir = Path(target)
        self.inbox_dir = self.raw_dir  # alias for backward compatibility

    def sync_session(self, session: SessionSummary) -> bool:
        """Copies or updates the session raw files in vault/raw atomically."""
        if not session.transcript_path or not session.transcript_path.exists():
            return False

        user_slug = session.host_user or "default"
        dest_dir = self.raw_dir / user_slug / session.session_id
        dest_file = dest_dir / session.transcript_path.name

        src_stat = session.transcript_path.stat()

        # Idempotence check: if file already exists with same size, skip
        if dest_file.exists():
            dest_stat = dest_file.stat()
            if dest_stat.st_size == src_stat.st_size:
                return False

        # Prepare destination directory
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Atomic copy: write to temp file then replace
        tmp_file = dest_dir / f".{dest_file.name}.tmp"
        try:
            shutil.copy2(session.transcript_path, tmp_file)
            os.replace(tmp_file, dest_file)
        finally:
            if tmp_file.exists():
                try:
                    tmp_file.unlink()
                except OSError:
                    pass

        # Write metadata file alongside transcript
        info_file = dest_dir / "session_info.json"
        tmp_info = dest_dir / ".session_info.tmp"
        try:
            with open(tmp_info, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": session.session_id,
                    "host_user": session.host_user,
                    "workspace": session.workspace,
                    "updated_at": session.updated_at,
                    "file_size": src_stat.st_size,
                }, f, indent=2, ensure_ascii=False)
            os.replace(tmp_info, info_file)
        except Exception:
            if tmp_info.exists():
                try:
                    tmp_info.unlink()
                except OSError:
                    pass

        return True

    def sync_all(self, sessions: List[SessionSummary], workspace_filter: Optional[Any] = None) -> SyncResult:
        """Synchronizes all provided sessions applying optional workspace filter."""
        result = SyncResult(discovered=len(sessions))

        for session in sessions:
            if workspace_filter and workspace_filter.should_ignore(session.workspace):
                result.ignored += 1
                continue

            user_slug = session.host_user or "default"
            dest_file = self.raw_dir / user_slug / session.session_id / session.transcript_path.name
            already_existed = dest_file.exists()

            changed = self.sync_session(session)
            if changed:
                if already_existed:
                    result.updated += 1
                else:
                    result.synced += 1
            else:
                result.skipped += 1

        return result


# Compatibility alias
InboxSynchronizer = RawSynchronizer
