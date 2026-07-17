#!/usr/bin/env python3
"""Validate one experiment manifest structurally and check artifact hashes."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from jsonschema.validators import validator_for

from _common import REPOSITORY_ROOT, sha256_file


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def safe_artifact_path(relative_path: str) -> Path:
    candidate = (REPOSITORY_ROOT / relative_path).resolve()
    try:
        candidate.relative_to(REPOSITORY_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"artifact path escapes repository: {relative_path}") from exc
    return candidate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = REPOSITORY_ROOT / manifest_path
    try:
        manifest_path.resolve().relative_to(REPOSITORY_ROOT.resolve())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        schema = json.loads(
            (REPOSITORY_ROOT / "schemas" / "experiment-manifest.schema.json").read_text(
                encoding="utf-8"
            )
        )
        validator_type = validator_for(schema)
        validator_type.check_schema(schema)
        validator_type(schema, format_checker=FormatChecker()).validate(manifest)

        artifacts = set(manifest["artifacts"])
        hashed_artifacts = set(manifest["artifact_sha256"])
        if artifacts != hashed_artifacts:
            missing_hash = sorted(artifacts - hashed_artifacts)
            unlisted_hash = sorted(hashed_artifacts - artifacts)
            raise ValueError(
                f"artifact/hash key mismatch; missing_hash={missing_hash}, unlisted_hash={unlisted_hash}"
            )
        for relative_path, expected_digest in manifest["artifact_sha256"].items():
            path = safe_artifact_path(relative_path)
            if not path.is_file():
                raise ValueError(f"artifact does not exist: {relative_path}")
            actual_digest = sha256_file(path)
            if actual_digest != expected_digest:
                raise ValueError(f"artifact SHA-256 mismatch: {relative_path}")
        artifact_digests = set(manifest["artifact_sha256"].values())
        for field in ("stdout_sha256", "stderr_sha256"):
            stream_digest = manifest[field]
            if stream_digest is not None and stream_digest not in artifact_digests:
                raise ValueError(f"{field} is not the digest of a listed artifact")

        if manifest["finished_at_utc"] is not None and manifest["started_at_utc"] is not None:
            if parse_timestamp(manifest["finished_at_utc"]) < parse_timestamp(
                manifest["started_at_utc"]
            ):
                raise ValueError("finished_at_utc precedes started_at_utc")
        if manifest["search_mode"] == "p14-power2" and manifest["k"] != 14:
            raise ValueError("p14-power2 mode requires k=14")
        if manifest["search_mode"] == "p13-c4c8" and manifest["k"] != 13:
            raise ValueError("p13-c4c8 mode requires k=13")
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        SchemaError,
        ValidationError,
    ) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1

    print(
        json.dumps(
            {
                "artifacts_verified": len(manifest["artifacts"]),
                "manifest": manifest_path.relative_to(REPOSITORY_ROOT).as_posix(),
                "ok": True,
                "semantic_checks": [
                    "artifact-set-equality",
                    "artifact-sha256",
                    "captured-stream-artifact-hashes",
                    "timestamp-order",
                    "search-mode-k-consistency",
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
