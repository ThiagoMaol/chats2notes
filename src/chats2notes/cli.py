"""Command-line interface entry point for chats2notes."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from chats2notes.adapters.antigravity import AntigravityAdapter
from chats2notes.curator import CuratorEngine
from chats2notes.filter import WorkspaceFilter
from chats2notes.models import ExtractionConfig
from chats2notes.segmenter import TranscriptSegmenter
from chats2notes.state import StateManager
from chats2notes.storage import MarkdownStorage
from chats2notes.sync import RawSynchronizer


def build_parser() -> argparse.ArgumentParser:
    """Builds the argument parser for CLI commands."""
    parser = argparse.ArgumentParser(
        prog="chats2notes",
        description="Incremental conversation extractor from local agent transcripts to markdown notes."
    )
    subparsers = parser.add_subparsers(dest="command")

    # sync subcommand (Stage 1: Raw Transcript Synchronization)
    sync_parser = subparsers.add_parser("sync", help="Synchronize raw agent transcripts to vault/raw")
    sync_parser.add_argument("--brain-dir", action="append", help="Directory of agent brains (can specify multiple)")
    sync_parser.add_argument("--raw-dir", "--inbox-dir", dest="raw_dir", default="./vault/raw", help="Destination directory for raw transcripts (default: ./vault/raw)")
    sync_parser.add_argument("--segments-dir", default="./vault/segments", help="Destination directory for segmented turns when --segment is used")
    sync_parser.add_argument("--segment", action="store_true", help="Automatically segment raw transcripts into pairs after sync")
    sync_parser.add_argument("--ignore-workspace", action="append", help="Workspace path to ignore (can specify multiple)")
    sync_parser.add_argument("--all-users", action="store_true", help="Scan multi-user directories in /home")

    # segment subcommand (Stage 2: Deterministic Pair Segmentation)
    segment_parser = subparsers.add_parser("segment", help="Segment raw transcripts into ordered turn pairs and audit files")
    segment_parser.add_argument("--raw-dir", default="./vault/raw", help="Source directory containing raw transcripts (default: ./vault/raw)")
    segment_parser.add_argument("--segments-dir", default="./vault/segments", help="Destination directory for segmented pairs (default: ./vault/segments)")
    segment_parser.add_argument("--session", help="Optional specific session ID to segment")

    # curate subcommand (Stage 4: Curadoria Inteligente & Notas Humanizadas)
    curate_parser = subparsers.add_parser("curate", help="Curate segmented pairs into atomic humanized markdown notes")
    curate_parser.add_argument("--segments-dir", default="./vault/segments", help="Source directory containing segmented pairs (default: ./vault/segments)")
    curate_parser.add_argument("--notes-dir", default="./vault/notas", help="Destination directory for atomic notes (default: ./vault/notas)")
    curate_parser.add_argument("--manifest-file", help="Path to curated manifest file (default: vault/.curated.json)")
    curate_parser.add_argument("--project", help="Optional project name tag")
    curate_parser.add_argument("--force", action="store_true", help="Reprocess all segments ignoring previously curated manifest")

    # extract subcommand (Stage 3: Incremental Markdown Generation)
    extract_parser = subparsers.add_parser("extract", help="Extract notes incrementally from agent logs")
    extract_parser.add_argument("--brain-dir", action="append", help="Directory of agent brains (can specify multiple)")
    extract_parser.add_argument("--output-dir", default="./notes", help="Destination directory for markdown notes")
    extract_parser.add_argument("--state-file", help="Path to state checkpoint file")
    extract_parser.add_argument("--format", choices=["silverbullet", "obsidian"], default="silverbullet", help="Output format mode")
    extract_parser.add_argument("--all-users", action="store_true", help="Scan multi-user directories in /home")

    # status subcommand
    status_parser = subparsers.add_parser("status", help="Show monitored sessions and checkpoints")
    status_parser.add_argument("--state-file", help="Path to state checkpoint file")

    return parser


def run_sync(args: argparse.Namespace) -> int:
    """Executes raw transcript synchronization to vault/raw."""
    raw_dir = Path(args.raw_dir).expanduser()

    brain_paths = None
    if args.brain_dir:
        brain_paths = [Path(p).expanduser() for p in args.brain_dir]

    adapter = AntigravityAdapter()
    sessions = adapter.discover_sessions(base_paths=brain_paths)

    ignored_workspaces = args.ignore_workspace if args.ignore_workspace else []
    ws_filter = WorkspaceFilter(ignored_workspaces=ignored_workspaces)
    synchronizer = RawSynchronizer(raw_dir=raw_dir)

    result = synchronizer.sync_all(sessions, workspace_filter=ws_filter)

    print(f"Sincronização concluída: {result.discovered} sessões avaliadas, "
          f"{result.synced} sincronizadas, {result.updated} atualizadas, "
          f"{result.skipped} inalteradas, {result.ignored} ignoradas por workspace.")

    if getattr(args, "segment", False):
        segments_dir = Path(getattr(args, "segments_dir", "./vault/segments")).expanduser()
        segmenter = TranscriptSegmenter(raw_dir=raw_dir, segments_dir=segments_dir)
        stats = segmenter.segment_all()
        print(f"Segmentação automática concluída: {stats['sessions_processed']} sessões processadas, "
              f"{stats['turns_generated']} pares gerados em '{segments_dir}'.")

    return 0


def run_segment(args: argparse.Namespace) -> int:
    """Executes deterministic pair segmentation from vault/raw to vault/segments."""
    raw_dir = Path(args.raw_dir).expanduser()
    segments_dir = Path(args.segments_dir).expanduser()

    segmenter = TranscriptSegmenter(raw_dir=raw_dir, segments_dir=segments_dir)
    stats = segmenter.segment_all(target_session=args.session)

    print(f"Segmentação concluída: {stats['sessions_processed']} sessões processadas, "
          f"{stats['turns_generated']} pares gerados em '{segments_dir}'.")
    return 0


def run_extract(args: argparse.Namespace) -> int:
    """Executes incremental extraction workflow."""
    output_dir = Path(args.output_dir).expanduser()
    state_file = Path(args.state_file).expanduser() if args.state_file else (Path.home() / ".chats2notes" / "state.json")

    state_mgr = StateManager(state_file)
    storage = MarkdownStorage(output_dir=output_dir, format_mode=args.format)

    brain_paths = None
    if args.brain_dir:
        brain_paths = [Path(p).expanduser() for p in args.brain_dir]

    adapter = AntigravityAdapter()
    sessions = adapter.discover_sessions(base_paths=brain_paths)

    total_extracted = 0
    print(f"Sessões descobertas: {len(sessions)}")

    for session in sessions:
        last_step = state_mgr.get_checkpoint(session.host_user, session.session_id)
        new_turns = list(adapter.extract_new_turns(session, since_step_index=last_step))
        if not new_turns:
            continue

        for turn in new_turns:
            note_path = storage.write_note(turn)
            total_extracted += 1
            state_mgr.update_checkpoint(session.host_user, session.session_id, turn.step_index)

    state_mgr.save()
    print(f"Extração concluída com sucesso! {total_extracted} novas notas salvas em '{output_dir}'.")
    return 0


def run_curate(args: argparse.Namespace) -> int:
    """Executes intelligent curation and note synthesis."""
    segments_dir = Path(args.segments_dir).expanduser()
    notes_dir = Path(args.notes_dir).expanduser()
    manifest_file = Path(args.manifest_file).expanduser() if getattr(args, "manifest_file", None) else None

    engine = CuratorEngine(
        segments_dir=segments_dir,
        notes_dir=notes_dir,
        manifest_file=manifest_file,
        project_name=args.project,
        force=args.force,
    )

    created_notes = engine.process_all()
    count = len(created_notes)

    print(f"Curadoria concluída: {count} novas notas salvas em '{notes_dir}'.")
    return 0


def run_status(args: argparse.Namespace) -> int:
    """Displays monitored sessions and current checkpoints."""
    state_file = Path(args.state_file).expanduser() if args.state_file else (Path.home() / ".chats2notes" / "state.json")
    if not state_file.exists():
        print(f"Nenhum arquivo de estado encontrado em '{state_file}'.")
        return 0

    state_mgr = StateManager(state_file)
    print(f"Arquivo de estado: {state_file}")
    print(f"Total de checkpoints registrados: {len(state_mgr._state)}")
    for key, step in sorted(state_mgr._state.items()):
        print(f"  - {key}: último step_index={step}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """CLI main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "sync":
        return run_sync(args)
    elif args.command == "segment":
        return run_segment(args)
    elif args.command == "curate":
        return run_curate(args)
    elif args.command == "extract":
        return run_extract(args)
    elif args.command == "status":
        return run_status(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
