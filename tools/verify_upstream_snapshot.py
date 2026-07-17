#!/usr/bin/env python3
"""Compare the preserved upstream snapshot with its per-file hash inventory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from _common import REPOSITORY_ROOT, file_hash_inventory


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def expected_inventory(provenance: dict[str, Any]) -> dict[str, str]:
    for key in ("file_sha256", "file_hashes", "snapshot_files"):
        value = provenance.get(key)
        if isinstance(value, dict):
            return {str(path): str(digest) for path, digest in value.items()}
        if isinstance(value, list):
            inventory: dict[str, str] = {}
            for record in value:
                if not isinstance(record, dict) or "path" not in record or "sha256" not in record:
                    raise ValueError(f"invalid record in provenance field {key}")
                inventory[str(record["path"])] = str(record["sha256"])
            return inventory
    raise ValueError(
        "provenance has no per-file inventory; expected file_sha256, file_hashes, or snapshot_files"
    )


def validate_expected(inventory: dict[str, str]) -> None:
    for relative_path, digest in inventory.items():
        path = Path(relative_path)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != relative_path:
            raise ValueError(f"unsafe or non-canonical inventory path: {relative_path}")
        if not SHA256_RE.fullmatch(digest):
            raise ValueError(f"invalid SHA-256 for {relative_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provenance",
        type=Path,
        default=Path("upstream/UPSTREAM_PROVENANCE.json"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    provenance_path = args.provenance
    if not provenance_path.is_absolute():
        provenance_path = REPOSITORY_ROOT / provenance_path
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        expected = expected_inventory(provenance)
        validate_expected(expected)
        snapshot_path = provenance["snapshot_path"]
        snapshot = REPOSITORY_ROOT / snapshot_path
        actual = file_hash_inventory(snapshot)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 2

    missing = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    changed = sorted(path for path in set(expected) & set(actual) if expected[path] != actual[path])
    result = {
        "added": added,
        "changed": changed,
        "expected_file_count": len(expected),
        "missing": missing,
        "observed_file_count": len(actual),
        "ok": not (missing or added or changed),
        "snapshot_path": snapshot_path,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
