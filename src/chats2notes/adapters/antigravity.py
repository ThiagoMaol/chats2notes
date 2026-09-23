"""Antigravity CLI log adapter."""

import getpass
import json
import os
import re
from pathlib import Path
from typing import Iterator, List, Optional

from chats2notes.adapters.base import BaseAdapter
from chats2notes.models import SessionSummary, Turn


class AntigravityAdapter(BaseAdapter):
    """Adapter for Antigravity CLI brain transcript files."""

    def __init__(self, default_brain_dir: Optional[Path] = None):
        self.default_brain_dir = default_brain_dir or (Path.home() / ".gemini" / "antigravity-cli" / "brain")

    def _extract_user_from_path(self, path: Path) -> str:
        """Heuristically extracts host_user from the file path."""
        parts = path.resolve().parts
        if "home" in parts:
            try:
                idx = parts.index("home")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
            except ValueError:
                pass
        for i, part in enumerate(parts):
            if part == ".gemini" and i > 0:
                return parts[i - 1]
        try:
            return getpass.getuser()
        except Exception:
            return "default"

    def _extract_workspace_from_transcript(self, transcript_path: Path) -> str:
        """Reads initial lines of transcript to extract active workspace/cwd if present."""
        if not transcript_path.exists():
            return ""
        try:
            with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
                for _ in range(50):
                    line = f.readline()
                    if not line:
                        break
                    if '"Cwd":' in line:
                        match = re.search(r'"Cwd"\s*:\s*"([^"]+)"', line)
                        if match:
                            return match.group(1)
                    if "workspace:" in line.lower() or "cwd:" in line.lower():
                        match = re.search(r'(?:workspace|cwd)\s*[:=]\s*([^\s,;"]+)', line, re.IGNORECASE)
                        if match:
                            return match.group(1)
        except Exception:
            pass
        return ""

    def discover_sessions(self, base_paths: Optional[List[Path]] = None) -> List[SessionSummary]:
        """Discovers sessions across one or more brain paths, supporting multi-user home directories."""
        roots = []
        if base_paths:
            for p in base_paths:
                p = Path(p)
                if p.exists():
                    roots.append(p)
        else:
            if self.default_brain_dir.exists():
                roots.append(self.default_brain_dir)
            # Check other users in /home if accessible
            home_dir = Path("/home")
            if home_dir.is_dir():
                try:
                    for user_entry in home_dir.iterdir():
                        if user_entry.is_dir():
                            user_brain = user_entry / ".gemini" / "antigravity-cli" / "brain"
                            if user_brain.is_dir() and os.access(user_brain, os.R_OK):
                                if user_brain not in roots:
                                    roots.append(user_brain)
                except (PermissionError, OSError):
                    pass

        summaries = []
        seen_sessions = set()

        for root in roots:
            # Look for transcript_full.jsonl or transcript.jsonl
            try:
                for candidate in root.glob("**/transcript_full.jsonl"):
                    if candidate.parent.name == "logs" and candidate.parent.parent.name == ".system_generated":
                        session_dir = candidate.parent.parent.parent
                    elif candidate.parent.name == ".system_generated":
                        session_dir = candidate.parent.parent
                    else:
                        session_dir = candidate.parent
                    session_id = session_dir.name
                    if (str(root), session_id) in seen_sessions:
                        continue
                    seen_sessions.add((str(root), session_id))

                    host_user = self._extract_user_from_path(candidate)
                    workspace = self._extract_workspace_from_transcript(candidate)
                    summaries.append(
                        SessionSummary(
                            session_id=session_id,
                            host_user=host_user,
                            workspace=workspace,
                            transcript_path=candidate,
                        )
                    )
            except (PermissionError, OSError):
                continue

        return summaries

    def _clean_user_prompt(self, raw_content: str) -> str:
        """Strips system wrappers like <USER_REQUEST>, <ADDITIONAL_METADATA>, etc."""
        if not raw_content:
            return ""
        # Check if inside <USER_REQUEST>
        match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", raw_content, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Otherwise remove system tags
        cleaned = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", raw_content, flags=re.DOTALL)
        cleaned = re.sub(r"<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>", "", cleaned, flags=re.DOTALL)
        cleaned = re.sub(r"<SYSTEM_INSTRUCTION>.*?</SYSTEM_INSTRUCTION>", "", cleaned, flags=re.DOTALL)
        return cleaned.strip()

    def extract_new_turns(self, session: SessionSummary, since_step_index: int = 0) -> Iterator[Turn]:
        """Reads transcript_full.jsonl incrementally, yielding new Turn objects."""
        transcript_path = session.transcript_path
        if not transcript_path or not transcript_path.exists():
            return

        current_prompt = ""
        current_prompt_time = ""
        last_response = ""
        last_step = 0
        last_response_time = ""

        try:
            with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except (json.JSONDecodeError, ValueError):
                        # Resilient parsing: skip corrupted lines
                        continue

                    step_index = record.get("step_index", 0)
                    step_type = record.get("type", "")
                    content = record.get("content", "")
                    created_at = record.get("created_at", "")

                    if step_type == "USER_INPUT":
                        # If we had a previous turn waiting to be emitted
                        if current_prompt and last_response and last_step > since_step_index:
                            yield Turn(
                                session_id=session.session_id,
                                step_index=last_step,
                                created_at=last_response_time or current_prompt_time,
                                user_prompt=current_prompt,
                                assistant_response=last_response,
                                host_user=session.host_user,
                                workspace=session.workspace,
                                agent="antigravity",
                                tags=["ai-notes", "antigravity"],
                            )
                            current_prompt = ""
                            last_response = ""

                        cleaned = self._clean_user_prompt(content)
                        if cleaned:
                            current_prompt = cleaned
                            current_prompt_time = created_at
                            last_response = ""

                    elif step_type == "PLANNER_RESPONSE":
                        if content:
                            last_response = content.strip()
                            last_step = step_index
                            last_response_time = created_at

            # Emit final pending turn at end of transcript
            if current_prompt and last_response and last_step > since_step_index:
                yield Turn(
                    session_id=session.session_id,
                    step_index=last_step,
                    created_at=last_response_time or current_prompt_time,
                    user_prompt=current_prompt,
                    assistant_response=last_response,
                    host_user=session.host_user,
                    workspace=session.workspace,
                    agent="antigravity",
                    tags=["ai-notes", "antigravity"],
                )
        except (OSError, IOError):
            return
