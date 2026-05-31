#!/usr/bin/env python3
"""
reorganize.py — Convert old flat story file layout to per-story folders.

Old structure (all files in a single source directory):
    <source_dir>/<story_name>.mp3
    <source_dir>/<story_name>.srt
    <source_dir>/<story_name>_原文.txt

New structure (one folder per story under the output directory):
    <output_dir>/<story_name>/audio.mp3
    <output_dir>/<story_name>/subtitles.srt
    <output_dir>/<story_name>/原文.txt

Usage:
    python reorganize.py <source_dir> [output_dir]

    source_dir   Directory containing the old flat files (.mp3, .srt, _原文.txt).
    output_dir   Where to create per-story folders (default: current directory).

Options:
    --dry-run    Preview moves without executing them.
    --move       Move files instead of copying (default is copy).

Examples:
    # Preview what would happen
    python reorganize.py 茶杯助手_openclaw_backup --dry-run

    # Copy files into per-story folders under current directory
    python reorganize.py 茶杯助手_openclaw_backup

    # Move files into per-story folders under a specific output path
    python reorganize.py 茶杯助手_openclaw_backup ./output --move
"""

import argparse
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path


# File type mapping: (suffix_to_strip, new_filename)
FILE_TYPES = {
    ".mp3": ("", "audio.mp3"),
    ".srt": ("", "subtitles.srt"),
}

# Special pattern: files ending with _原文.txt
TEXT_SUFFIX = "_原文.txt"
TEXT_NEW_NAME = "原文.txt"


def discover_stories(source_dir: Path) -> dict[str, dict[str, Path]]:
    """Scan source_dir and group files by story name.

    Returns a dict: story_name -> {"audio": Path, "subtitles": Path, "text": Path}
    """
    stories: dict[str, dict[str, Path]] = defaultdict(dict)

    for entry in sorted(source_dir.iterdir()):
        if not entry.is_file():
            continue

        name = entry.name

        # Check for _原文.txt pattern first (before generic .txt)
        if name.endswith(TEXT_SUFFIX):
            story_name = name[: -len(TEXT_SUFFIX)]
            stories[story_name]["text"] = entry
            continue

        # Check audio/subtitle extensions
        suffix = entry.suffix.lower()
        if suffix in FILE_TYPES:
            story_name = entry.stem
            label = "audio" if suffix == ".mp3" else "subtitles"
            stories[story_name][label] = entry

    return dict(stories)


def reorganize(
    source_dir: Path,
    output_dir: Path,
    dry_run: bool = False,
    move: bool = False,
) -> None:
    if not source_dir.is_dir():
        print(f"Error: source directory '{source_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    stories = discover_stories(source_dir)

    if not stories:
        print("No story files (.mp3, .srt, _原文.txt) found in source directory.")
        return

    action_verb = "Move" if move else "Copy"
    action_fn = shutil.move if move else shutil.copy2

    print(f"Found {len(stories)} story(ies) in '{source_dir}':\n")

    for story_name in sorted(stories):
        files = stories[story_name]
        story_dir = output_dir / story_name

        print(f"  📂 {story_name}/")

        if not dry_run:
            story_dir.mkdir(parents=True, exist_ok=True)

        mapping = [
            ("audio", "audio.mp3"),
            ("subtitles", "subtitles.srt"),
            ("text", TEXT_NEW_NAME),
        ]

        for label, new_name in mapping:
            if label in files:
                src = files[label]
                dst = story_dir / new_name
                print(f"    {action_verb}: {src.name} → {story_name}/{new_name}")
                if not dry_run:
                    action_fn(str(src), str(dst))
            else:
                print(f"    ⚠ Missing: {new_name} (no source file found)")

        print()

    if dry_run:
        print("(dry-run mode — no files were changed)")
    else:
        print(f"Done. {len(stories)} story folder(s) created under '{output_dir}'.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reorganize flat story files into per-story folders.",
    )
    parser.add_argument(
        "source_dir",
        help="Directory containing the old flat files (.mp3, .srt, _原文.txt).",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=".",
        help="Where to create per-story folders (default: current directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview moves without executing them.",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying (default is copy).",
    )

    args = parser.parse_args()

    reorganize(
        source_dir=Path(args.source_dir),
        output_dir=Path(args.output_dir),
        dry_run=args.dry_run,
        move=args.move,
    )


if __name__ == "__main__":
    main()
