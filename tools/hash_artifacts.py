#!/usr/bin/env python3
"""Compute deterministic SHA-256 hashes for files or a directory tree."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _common import REPOSITORY_ROOT, file_hash_inventory, inventory_digest, sha256_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)

    files = subparsers.add_parser("files", help="hash one or more files")
    files.add_argument("paths", nargs="+", type=Path)

    tree = subparsers.add_parser("tree", help="hash every file under a directory")
    tree.add_argument("directory", type=Path)
    return parser


def under_root(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.operation == "files":
            resolved_paths = [
                path if path.is_absolute() else REPOSITORY_ROOT / path for path in args.paths
            ]
            result = {
                "algorithm": "sha256",
                "files": {
                    under_root(path): sha256_file(path)
                    for path in resolved_paths
                },
            }
        else:
            directory = args.directory if args.directory.is_absolute() else REPOSITORY_ROOT / args.directory
            inventory = file_hash_inventory(directory)
            result = {
                "algorithm": "sha256",
                "directory": under_root(directory),
                "file_count": len(inventory),
                "files": inventory,
                "inventory_sha256": inventory_digest(inventory),
            }
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1
    result["ok"] = True
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
