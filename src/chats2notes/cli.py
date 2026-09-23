"""Command-line interface entry point for chats2notes."""

import argparse
import sys
from typing import List, Optional


def build_parser() -> argparse.ArgumentParser:
    """Builds the argument parser for CLI commands."""
    parser = argparse.ArgumentParser(
        prog="chats2notes",
        description="Incremental conversation extractor from local agent transcripts to markdown notes."
    )
    subparsers = parser.add_subparsers(dest="command")

    # extract subcommand
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


def main(args: Optional[List[str]] = None) -> int:
    """CLI main execution function."""
    parser = build_parser()
    parsed = parser.parse_args(args)
    if not parsed.command:
        parser.print_help()
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
