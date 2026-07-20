#!/usr/bin/env python3
"""Independently verify inspector timeout stability evidence format v2.

The verifier intentionally does not import the evidence runner.  It validates
strict canonical JSON, reconstructs every Git snapshot from its raw NUL
streams, reconstructs pytest collection and run summaries from raw stdout,
and checks complete or (when explicitly requested) fail-closed partial plans.
"""

from __future__ import annotations

import argparse
import base64
import binascii
from datetime import UTC, datetime
import hashlib
import json
import math
import ntpath
import os
from pathlib import Path
import posixpath
import re
import stat
import subprocess
import sys
from typing import Any

from jsonschema import FormatChecker
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "TASK-20260720__bind_stability_evidence_to_exact_worktree"
REPOSITORY = "falker47/erdos-gyarfas-p14"
REVIEW_BASE_COMMIT = "a7066e70b92d80be2d1772127f329c24222c1b41"
TASK_START_HEAD = "b1eb792a2a771485f37979cd932303f14ab52f56"
ARTIFACT_KIND = "inspector_timeout_stability_evidence"
CLASSIFICATION = "EMPIRICAL_OBSERVATION"
FINGERPRINT_KIND = "canonical_source_inventory_v2"
COLLECTION_DIGEST_KIND = "canonical_collection_node_ids_v1"
DEFAULT_REPORT_PATH = REPOSITORY_ROOT / "ops" / TASK_ID / "STABILITY_EVIDENCE.json"
SCHEMA_PATH = (
    REPOSITORY_ROOT
    / "schemas"
    / "inspector-timeout-stability-evidence-v2.schema.json"
)
FOCUSED_TEST_PATH = "tests/unit/test_upstream_candidate_inspection.py"
BASETEMP_ROOT = f"build/{TASK_ID}-basetemps"
OWNER_MARKER_NAME = ".inspector-timeout-stability-owner.json"
REPORT_RELATIVE_PATH = f"ops/{TASK_ID}/STABILITY_EVIDENCE.json"
REPORT_TEMPORARY_PATH = REPORT_RELATIVE_PATH + ".tmp"
TASK_STATUS_PATH = f"ops/{TASK_ID}/TASK_STATUS.md"
TOOL_NAMES = ("EG_CMAKE", "EG_CXX", "EG_NINJA", "EG_MAKE")

NON_EXECUTION_TASK_PATHS = tuple(
    sorted(
        {
            "CURRENT_STATUS.md",
            REPORT_RELATIVE_PATH,
            REPORT_TEMPORARY_PATH,
            TASK_STATUS_PATH,
            f"ops/{TASK_ID}/TASK_LOG.md",
            f"ops/{TASK_ID}/EVIDENCE.md",
            "research/NEXT_RESEARCH_STEPS.md",
        }
    )
)
ALLOWED_TRACKED_MODIFIED = frozenset(
    {
        "CURRENT_STATUS.md",
        "REVIEW_STATE.yaml",
        "research/NEXT_RESEARCH_STEPS.md",
        "tests/unit/test_inspector_timeout_stability_evidence.py",
        "tools/run_inspector_timeout_stability.py",
        "tools/validate_schemas.py",
        "tools/verify_inspector_timeout_stability.py",
    }
)
UNTRACKED_EXECUTION_INPUTS = frozenset(
    {
        "schemas/inspector-timeout-stability-evidence-v2.schema.json",
    }
)
ALLOWED_UNTRACKED = UNTRACKED_EXECUTION_INPUTS | frozenset(
    {
        TASK_STATUS_PATH,
        f"ops/{TASK_ID}/TASK_LOG.md",
        f"ops/{TASK_ID}/EVIDENCE.md",
        REPORT_RELATIVE_PATH,
    }
)
EXPECTED_PLAN = {
    "collection_preflight_runs": 2,
    "focused_runs": 25,
    "full_suite_runs": 2,
    "serial": True,
    "retries": 0,
    "stop_on_first_failure": True,
}
EXPECTED_REPORT_PERSISTENCE = {
    "report_path": REPORT_RELATIVE_PATH,
    "temporary_path": REPORT_TEMPORARY_PATH,
    "initial_write_mode": "same_directory_temp_then_replace",
    "replacement_mode": "same_directory_temp_then_replace",
    "fsync_file": True,
    "atomic_replace": True,
}
ROOT_LIMITATIONS = [
    "This is bounded V1 engineering-test evidence classified EMPIRICAL_OBSERVATION.",
    "This is not an upstream reproduction.",
    "This is not exhaustive-search evidence or a certificate.",
    "This establishes no theorem, counterexample, pruning rule, or mathematical result.",
    "RFU-TEST-001 remains OPEN until a later independent review.",
    "RFU-ENV-001 remains OPEN and is outside this task.",
    "Pre/post snapshots cannot detect a mutation that is fully restored within one child.",
    "Old explicit-basetemp outputs and in-tree bytecode caches are path-bound but content-neutralized by the child controls.",
]
ENVIRONMENT_LIMITATIONS = [
    "Only a minimized allowlist of inherited child-environment names is retained.",
    "Credentials and the complete parent environment are deliberately not recorded.",
]

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
WINDOWS_ABSOLUTE_PATH_RE = re.compile(
    r"^(?:[A-Za-z]:[\\/]|[\\/]{2}[^\\/]+[\\/][^\\/]+)"
)
PORCELAIN_MODE_RE = re.compile(rb"^[0-7]{6}$")
PORCELAIN_OID_RE = re.compile(rb"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
PORCELAIN_XY_RE = re.compile(rb"^[.MADRCUT]{2}$")
PORCELAIN_UNMERGED_XY_RE = re.compile(rb"^(?:DD|AU|UD|UA|DU|AA|UU)$")
PORCELAIN_SUBMODULE_RE = re.compile(rb"^(?:N\.\.\.|S[.C][.M][.U])$")
PYTEST_SUMMARY_LINE_RE = re.compile(
    r"^(?P<body>.+) in [0-9]+(?:\.[0-9]+)?s(?: \([^\r\n]+\))?$"
)
PYTEST_COUNT_RE = re.compile(
    r"^(?P<count>[0-9]+) (?P<kind>passed|failed|error|errors|skipped|xfailed|xpassed)$"
)
COLLECTION_SUMMARY_RE = re.compile(
    r"^(?P<count>[0-9]+) tests? collected in [0-9]+(?:\.[0-9]+)?s$"
)


class EvidenceVerificationError(ValueError):
    """A deterministic evidence-verification failure."""


class SnapshotAcquisitionFailure(EvidenceVerificationError):
    """Raw Git probes cannot be normalized into a trustworthy snapshot."""


class SnapshotIntegrityFailure(EvidenceVerificationError):
    """Recorded Git command or captured-stream integrity is structurally false."""


def _fail(message: str) -> None:
    raise EvidenceVerificationError(message)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_json_constant(value: str) -> None:
    _fail(f"non-finite JSON constant {value!r} is forbidden")


def _finite_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        _fail(f"non-finite JSON number {value!r} is forbidden")
    return parsed


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _load_json_object(path: Path) -> tuple[bytes, dict[str, Any]]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        _fail(f"JSON file cannot be read: {type(exc).__name__}: {exc}")
    if raw.startswith(b"\xef\xbb\xbf"):
        _fail("JSON file has a forbidden UTF-8 BOM")
    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_nonfinite_json_constant,
            parse_float=_finite_json_float,
        )
    except EvidenceVerificationError:
        raise
    except UnicodeDecodeError as exc:
        _fail(f"JSON file is not strict UTF-8: {exc}")
    except json.JSONDecodeError as exc:
        _fail(f"JSON file is not strict JSON: {exc.msg} at line {exc.lineno}")
    if not isinstance(value, dict):
        _fail("JSON root must be an object")
    return raw, value


def _schema_errors(value: dict[str, Any], schema_path: Path) -> list[str]:
    try:
        _schema_raw, schema = _load_json_object(schema_path)
        validator_type = validator_for(schema)
        validator_type.check_schema(schema)
        validator = validator_type(schema, format_checker=FormatChecker())
        errors = sorted(
            validator.iter_errors(value),
            key=lambda error: (
                tuple(str(part) for part in error.absolute_path),
                error.message,
            ),
        )
    except EvidenceVerificationError:
        raise
    except SchemaError as exc:
        _fail(f"evidence schema is invalid: {exc.message}")
    return [
        "$"
        + "".join(f"[{part!r}]" for part in error.absolute_path)
        + f": {error.message}"
        for error in errors
    ]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_repository_path(value: str, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{label} is empty or not a string")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        _fail(f"{label} contains a control character")
    if (
        "\\" in value
        or value.startswith("/")
        or re.match(r"^[A-Za-z]:", value)
        or WINDOWS_ABSOLUTE_PATH_RE.match(value)
    ):
        _fail(f"{label} is absolute or uses a noncanonical separator: {value!r}")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        _fail(f"{label} contains an empty or traversal component: {value!r}")
    if Path(value).as_posix() != value:
        _fail(f"{label} is not a canonical repository path: {value!r}")
    return value


def _decode_git_path(value: bytes, label: str) -> str:
    try:
        decoded = value.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        _fail(f"{label} is not UTF-8: {exc}")
    if decoded.encode("utf-8") != value:
        _fail(f"{label} does not round-trip through UTF-8")
    return _safe_repository_path(decoded, label)


def _decode_stream(stream: dict[str, Any], label: str) -> bytes:
    encoded = stream["base64"]
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        _fail(f"{label} contains malformed Base64: {exc}")
    if base64.b64encode(decoded).decode("ascii") != encoded:
        _fail(f"{label} Base64 is not canonical")
    if len(decoded) != stream["byte_length"]:
        _fail(f"{label} byte length mismatch")
    observed = _sha256_bytes(decoded)
    if observed != stream["sha256"]:
        _fail(
            f"{label} SHA-256 mismatch: recorded={stream['sha256']} observed={observed}"
        )
    return decoded


def _nul_records(raw: bytes, label: str) -> list[bytes]:
    if not raw:
        return []
    if not raw.endswith(b"\0"):
        _fail(f"{label} is not NUL terminated")
    records = raw[:-1].split(b"\0")
    if any(not record for record in records):
        _fail(f"{label} contains an empty or duplicate NUL record")
    return records


def _parse_path_list(raw: bytes, label: str) -> list[str]:
    paths = [
        _decode_git_path(record, f"{label} path {index}")
        for index, record in enumerate(_nul_records(raw, label), start=1)
    ]
    if len(paths) != len(set(paths)):
        _fail(f"{label} contains a duplicate path")
    return paths


def _validate_status_metadata(parts: list[bytes], label: str) -> None:
    if not PORCELAIN_XY_RE.fullmatch(parts[1]):
        _fail(f"{label} has malformed XY state")
    if not PORCELAIN_SUBMODULE_RE.fullmatch(parts[2]):
        _fail(f"{label} has malformed submodule state")
    if not all(PORCELAIN_MODE_RE.fullmatch(value) for value in parts[3:6]):
        _fail(f"{label} has malformed file mode")
    if not all(PORCELAIN_OID_RE.fullmatch(value) for value in parts[6:8]):
        _fail(f"{label} has malformed object ID")


def _parse_porcelain_v2(raw: bytes, label: str) -> dict[str, Any]:
    records = _nul_records(raw, label)
    tracked_states: dict[str, tuple[str, str]] = {}
    untracked: list[str] = []
    ignored: list[str] = []
    index = 0
    while index < len(records):
        record = records[index]
        record_label = f"{label} record {index + 1}"
        if record.startswith(b"1 "):
            parts = record.split(b" ", 8)
            if len(parts) != 9 or parts[0] != b"1":
                _fail(f"{record_label} is a malformed ordinary record")
            _validate_status_metadata(parts, record_label)
            path = _decode_git_path(parts[8], f"{record_label} path")
            xy = parts[1].decode("ascii")
        elif record.startswith(b"2 "):
            parts = record.split(b" ", 9)
            if len(parts) != 10 or index + 1 >= len(records):
                _fail(f"{record_label} is a malformed rename/copy record")
            _validate_status_metadata(parts, record_label)
            if (
                not re.fullmatch(rb"[RC][0-9]{1,3}", parts[8])
                or int(parts[8][1:]) > 100
            ):
                _fail(f"{record_label} has malformed rename/copy score")
            path = _decode_git_path(parts[9], f"{record_label} path")
            _decode_git_path(records[index + 1], f"{record_label} original path")
            xy = parts[1].decode("ascii")
            index += 1
        elif record.startswith(b"u "):
            parts = record.split(b" ", 10)
            if len(parts) != 11:
                _fail(f"{record_label} is a malformed unmerged record")
            if (
                not PORCELAIN_UNMERGED_XY_RE.fullmatch(parts[1])
                or not PORCELAIN_SUBMODULE_RE.fullmatch(parts[2])
            ):
                _fail(f"{record_label} has malformed unmerged state metadata")
            if not all(PORCELAIN_MODE_RE.fullmatch(value) for value in parts[3:7]):
                _fail(f"{record_label} has malformed unmerged file mode")
            if not all(PORCELAIN_OID_RE.fullmatch(value) for value in parts[7:10]):
                _fail(f"{record_label} has malformed unmerged object ID")
            path = _decode_git_path(parts[10], f"{record_label} path")
            xy = parts[1].decode("ascii")
        elif record.startswith(b"? "):
            path = _decode_git_path(record[2:], f"{record_label} path")
            untracked.append(path)
            index += 1
            continue
        elif record.startswith(b"! "):
            path = _decode_git_path(record[2:], f"{record_label} path")
            ignored.append(path)
            index += 1
            continue
        else:
            _fail(f"{record_label} has an unknown porcelain-v2 prefix")
        if path in tracked_states:
            _fail(f"{label} contains duplicate tracked path {path!r}")
        tracked_states[path] = (xy[0], xy[1])
        index += 1
    if len(untracked) != len(set(untracked)):
        _fail(f"{label} contains duplicate untracked records")
    if len(ignored) != len(set(ignored)):
        _fail(f"{label} contains duplicate ignored records")
    return {
        "tracked_states": tracked_states,
        "untracked": untracked,
        "ignored": ignored,
    }


def _verify_probe(
    probe: dict[str, Any],
    label: str,
    expected_tail: list[str],
    *,
    git_path: str,
    working_directory: str,
    acquisition_failures: list[str],
) -> bytes:
    argv = probe["argv"]
    expected_argv = [
        git_path,
        "-c",
        f"safe.directory={working_directory}",
        "-c",
        "core.excludesFile=",
        *expected_tail,
    ]
    if argv != expected_argv:
        raise SnapshotIntegrityFailure(
            f"{label} command is not the exact required Git probe"
        )
    try:
        stdout = _decode_stream(probe["stdout"], f"{label} stdout")
        stderr = _decode_stream(probe["stderr"], f"{label} stderr")
    except EvidenceVerificationError as exc:
        raise SnapshotIntegrityFailure(str(exc)) from exc
    if probe["exit_code"] != 0:
        acquisition_failures.append(
            f"{label} Git probe exited with code {probe['exit_code']}"
        )
    if stderr:
        acquisition_failures.append(f"{label} Git probe has unexpected stderr")
    return stdout


def _snapshot_execution_payload(
    parsed: dict[str, Any],
    source_fingerprint: str | None,
    task_status_file: dict[str, Any],
) -> dict[str, Any]:
    untracked_execution_inputs = sorted(
        (set(parsed["untracked"]) & set(UNTRACKED_EXECUTION_INPUTS))
    )
    return {
        "execution_input_paths": parsed["execution_input_paths"],
        "ignored_other": parsed["ignored_other"],
        "source_fingerprint_sha256": source_fingerprint,
        "staged": parsed["staged"],
        "task_status_file": task_status_file,
        "tracked_deleted": parsed["tracked_deleted"],
        "tracked_modified": parsed["tracked_modified"],
        "untracked_execution_inputs": untracked_execution_inputs,
        "unexpected_paths": parsed["unexpected_paths"],
    }


def _ignored_path_is_neutralized(path: str) -> bool:
    return (
        path.startswith("build/pytest-")
        or "__pycache__" in path.split("/")
    )


def _ignored_path_is_fingerprinted(path: str) -> bool:
    return path.startswith("build/release/")


def _ignored_task_path_is_owned(path: str) -> bool:
    if path == f"{BASETEMP_ROOT}/{OWNER_MARKER_NAME}":
        return True
    return any(path.startswith(basetemp + "/") for basetemp in _expected_basetemps())


def _task_status_shape_is_consistent(record: dict[str, Any]) -> bool:
    if record["path"] != TASK_STATUS_PATH:
        return False
    if record["symlink"]:
        return record["exists"] is True and record["kind"] == "other"
    if record["kind"] == "missing":
        return record["exists"] is False
    return record["exists"] is True


def _is_link_like(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except OSError:
        return False
    attributes = getattr(metadata, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return stat.S_ISLNK(metadata.st_mode) or bool(attributes & reparse_flag)


def _live_task_status_file(root: Path) -> dict[str, Any]:
    current = root.resolve()
    for part in Path(TASK_STATUS_PATH).parts:
        current = current / part
        if _is_link_like(current):
            return {
                "path": TASK_STATUS_PATH,
                "exists": True,
                "kind": "other",
                "symlink": True,
            }
    if not current.exists():
        return {
            "path": TASK_STATUS_PATH,
            "exists": False,
            "kind": "missing",
            "symlink": False,
        }
    kind = "regular_file" if current.is_file() else "directory" if current.is_dir() else "other"
    return {
        "path": TASK_STATUS_PATH,
        "exists": True,
        "kind": kind,
        "symlink": False,
    }


def _reconstruct_snapshot_inner(
    snapshot: dict[str, Any],
    label: str,
    *,
    git_path: str,
    working_directory: str,
) -> dict[str, Any]:
    commands = snapshot["commands"]
    acquisition_failures: list[str] = []
    status_raw = _verify_probe(
        commands["status"],
        f"{label} status",
        ["status", "--porcelain=v2", "-z", "--untracked-files=all", "--no-renames"],
        git_path=git_path,
        working_directory=working_directory,
        acquisition_failures=acquisition_failures,
    )
    tracked_raw = _verify_probe(
        commands["tracked"], f"{label} tracked", ["ls-files", "-z"],
        git_path=git_path, working_directory=working_directory,
        acquisition_failures=acquisition_failures,
    )
    untracked_raw = _verify_probe(
        commands["untracked"],
        f"{label} untracked",
        ["ls-files", "--others", "--exclude-standard", "-z"],
        git_path=git_path,
        working_directory=working_directory,
        acquisition_failures=acquisition_failures,
    )
    ignored_raw = _verify_probe(
        commands["ignored"],
        f"{label} ignored",
        ["ls-files", "--others", "--ignored", "--exclude-standard", "-z"],
        git_path=git_path,
        working_directory=working_directory,
        acquisition_failures=acquisition_failures,
    )
    staged_raw = _verify_probe(
        commands["staged"],
        f"{label} staged",
        ["diff", "--cached", "--name-only", "-z", "--"],
        git_path=git_path,
        working_directory=working_directory,
        acquisition_failures=acquisition_failures,
    )
    if acquisition_failures:
        raise SnapshotAcquisitionFailure("; ".join(acquisition_failures))
    status = _parse_porcelain_v2(status_raw, f"{label} status stdout")
    tracked = _parse_path_list(tracked_raw, f"{label} tracked stdout")
    untracked = _parse_path_list(untracked_raw, f"{label} untracked stdout")
    ignored = _parse_path_list(ignored_raw, f"{label} ignored stdout")
    staged_probe = _parse_path_list(staged_raw, f"{label} staged stdout")

    tracked_set = set(tracked)
    if tracked_set & (set(untracked) | set(ignored)) or set(untracked) & set(ignored):
        _fail(f"{label} Git path inventories overlap")
    status_tracked = set(status["tracked_states"])
    if not status_tracked <= tracked_set:
        _fail(f"{label} status names a path absent from the tracked inventory")
    if set(status["untracked"]) != set(untracked):
        _fail(f"{label} status and untracked Git probes disagree")
    if status["ignored"]:
        _fail(f"{label} status probe unexpectedly emitted ignored records")
    staged_status = {
        path for path, (index_state, _worktree_state) in status["tracked_states"].items()
        if index_state != "."
    }
    if staged_status != set(staged_probe):
        _fail(f"{label} status and staged Git probes disagree")

    tracked_deleted = sorted(
        path for path, (_x, y) in status["tracked_states"].items() if y == "D"
    )
    tracked_modified = [
        {
            "path": path,
            "index_status": x,
            "worktree_status": y,
        }
        for path, (x, y) in sorted(status["tracked_states"].items())
        if y not in {".", "D"}
    ]
    modified_paths = {record["path"] for record in tracked_modified}
    tracked_clean = sorted(tracked_set - set(tracked_deleted) - modified_paths)
    ignored_task = sorted(
        path
        for path in ignored
        if path == BASETEMP_ROOT or path.startswith(BASETEMP_ROOT + "/")
    )
    ignored_other = sorted(set(ignored) - set(ignored_task))
    task_non_execution = sorted(
        (modified_paths | set(tracked_deleted) | set(untracked))
        & set(NON_EXECUTION_TASK_PATHS)
    )
    execution_inputs = sorted(
        (tracked_set - set(NON_EXECUTION_TASK_PATHS))
        | (set(untracked) & set(UNTRACKED_EXECUTION_INPUTS))
        | {path for path in ignored if _ignored_path_is_fingerprinted(path)}
    )
    staged_records = [
        {"path": path, "index_status": status["tracked_states"][path][0]}
        for path in sorted(staged_status)
    ]
    unexpected = sorted(
        staged_status
        | set(tracked_deleted)
        | (modified_paths - set(ALLOWED_TRACKED_MODIFIED))
        | (set(untracked) - set(ALLOWED_UNTRACKED))
        | {
            path
            for path in ignored_other
            if not _ignored_path_is_neutralized(path)
            and not _ignored_path_is_fingerprinted(path)
        }
        | {path for path in ignored_task if not _ignored_task_path_is_owned(path)}
        | ({REPORT_TEMPORARY_PATH} & set(untracked))
    )
    parsed = {
        "tracked_clean": tracked_clean,
        "tracked_modified": tracked_modified,
        "tracked_deleted": tracked_deleted,
        "staged": staged_records,
        "untracked": sorted(untracked),
        "ignored_task_basetemps": ignored_task,
        "ignored_other": ignored_other,
        "task_owned_non_execution_paths": task_non_execution,
        "execution_input_paths": execution_inputs,
        "unexpected_paths": unexpected,
    }
    return parsed


def _reconstruct_snapshot(
    snapshot: dict[str, Any],
    label: str,
    *,
    git_path: str,
    working_directory: str,
) -> dict[str, Any]:
    try:
        return _reconstruct_snapshot_inner(
            snapshot,
            label,
            git_path=git_path,
            working_directory=working_directory,
        )
    except (SnapshotIntegrityFailure, SnapshotAcquisitionFailure):
        raise
    except EvidenceVerificationError as exc:
        raise SnapshotAcquisitionFailure(
            f"{label} Git output normalization failed: {exc}"
        ) from exc


def _verify_snapshots(
    report: dict[str, Any],
    source_fingerprint: str | None,
    *,
    git_path: str,
    working_directory: str,
    same_host: bool,
) -> tuple[dict[int, dict[str, Any]], str | None, set[int]]:
    snapshots = report["worktree_snapshots"]
    if len(snapshots) > 58:
        _fail("worktree snapshot count exceeds two snapshots for each of 29 subprocesses")
    sequences = [snapshot["sequence"] for snapshot in snapshots]
    if sequences != list(range(1, len(snapshots) + 1)):
        _fail("worktree snapshot sequences are not a strict 1-based prefix")
    by_sequence: dict[int, dict[str, Any]] = {}
    acquisition_failures: set[int] = set()
    frozen_identity = report["execution_project_revision"][
        "worktree_identity_sha256"
    ]
    prior_capture: datetime | None = None
    expected_task_status = {
        "path": TASK_STATUS_PATH,
        "exists": True,
        "kind": "regular_file",
        "symlink": False,
    }
    for snapshot in snapshots:
        sequence = snapshot["sequence"]
        label = f"worktree snapshot {sequence}"
        captured = _parse_timestamp(
            snapshot["captured_at_utc"], f"{label} captured_at_utc"
        )
        if prior_capture is not None and captured < prior_capture:
            _fail(f"{label} capture timestamp precedes the prior snapshot")
        prior_capture = captured
        task_status_file = snapshot["task_status_file"]
        if not _task_status_shape_is_consistent(task_status_file):
            _fail(f"{label} task-status shape/type evidence is contradictory")
        try:
            parsed = _reconstruct_snapshot(
                snapshot,
                label,
                git_path=git_path,
                working_directory=working_directory,
            )
        except SnapshotAcquisitionFailure:
            if sequence == 1 and not (
                source_fingerprint is None and frozen_identity is None
            ):
                _fail("first Git snapshot failed before a source baseline was established")
            if any(
                snapshot[field] is not None
                for field in (
                    "parsed",
                    "normalized_sha256",
                    "execution_state_sha256",
                    "source_fingerprint_sha256",
                )
            ):
                _fail(f"{label} failed acquisition must have null normalized fields")
            if snapshot["accepted"] is not False or snapshot["diagnostic"] is None:
                _fail(f"{label} failed acquisition lacks fail-closed status")
            acquisition_failures.add(sequence)
            by_sequence[sequence] = snapshot
            continue
        if parsed != snapshot["parsed"]:
            _fail(f"{label} normalized records disagree with raw Git streams")
        normalized_digest = _sha256_bytes(_canonical_json_bytes(parsed))
        if normalized_digest != snapshot["normalized_sha256"]:
            _fail(f"{label} normalized SHA-256 is wrong")
        execution_digest = _sha256_bytes(
            _canonical_json_bytes(
                _snapshot_execution_payload(
                    parsed,
                    snapshot["source_fingerprint_sha256"],
                    snapshot["task_status_file"],
                )
            )
        )
        if execution_digest != snapshot["execution_state_sha256"]:
            _fail(f"{label} execution-state SHA-256 is wrong")
        if (
            sequence == 1
            and frozen_identity is not None
            and execution_digest != frozen_identity
        ):
            _fail("first snapshot does not establish the frozen worktree identity")
        if (
            sequence == 1
            and snapshot["source_fingerprint_sha256"] != source_fingerprint
        ):
            _fail("first snapshot does not establish the frozen source identity")
        expected_accepted = (
            source_fingerprint is not None
            and frozen_identity is not None
            and not parsed["unexpected_paths"]
            and snapshot["source_fingerprint_sha256"] == source_fingerprint
            and task_status_file == expected_task_status
            and execution_digest == frozen_identity
        )
        if snapshot["accepted"] is not expected_accepted:
            _fail(f"{label} accepted flag disagrees with reconstructed state")
        if snapshot["accepted"]:
            if snapshot["diagnostic"] is not None:
                _fail(f"{label} accepted snapshot has a diagnostic")
        elif snapshot["diagnostic"] is None:
            _fail(f"{label} rejected snapshot lacks a diagnostic")
        by_sequence[sequence] = snapshot
    if same_host and snapshots:
        if _live_task_status_file(Path(working_directory)) != snapshots[-1][
            "task_status_file"
        ]:
            _fail("live task-status file type differs from the final snapshot")
    return by_sequence, frozen_identity, acquisition_failures


def _source_fingerprint(records: list[dict[str, Any]]) -> str:
    return _sha256_bytes(_canonical_json_bytes(records))


def _repository_file(root: Path, relative_path: str) -> Path:
    _safe_repository_path(relative_path, "source path")
    unresolved = root.resolve() / Path(relative_path)
    current = root.resolve()
    for part in Path(relative_path).parts:
        current = current / part
        if _is_link_like(current):
            _fail(f"source path contains a symlink: {relative_path}")
    resolved = unresolved.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        _fail(f"source path escapes repository: {relative_path}")
    if _is_link_like(unresolved) or not unresolved.is_file():
        _fail(f"source is not a regular file: {relative_path}")
    return unresolved


def _verify_sources(
    report: dict[str, Any], root: Path, *, rehash: bool
) -> tuple[str | None, list[str]]:
    records = report["source_files"]
    paths = [record["path"] for record in records]
    if paths != sorted(paths):
        _fail("source_files must be ordered lexicographically by path")
    if len(paths) != len(set(paths)):
        _fail("source_files contains a duplicate path")
    for record in records:
        _safe_repository_path(record["path"], "source_files path")
        if not SHA256_RE.fullmatch(record["sha256"]):
            _fail(f"source has malformed SHA-256: {record['path']}")
        if rehash:
            path = _repository_file(root, record["path"])
            data = path.read_bytes()
            if len(data) != record["byte_length"]:
                _fail(f"source byte length mismatch for {record['path']}")
            if _sha256_bytes(data) != record["sha256"]:
                _fail(f"source SHA-256 mismatch for {record['path']}")
    revision = report["execution_project_revision"]
    if revision["fingerprint_kind"] != FINGERPRINT_KIND:
        _fail("unsupported source fingerprint kind")
    if revision["fingerprint_scope"] != paths:
        _fail("source fingerprint scope differs from source inventory")
    if not records:
        if (
            revision["fingerprint_sha256"] is not None
            or revision["worktree_identity_sha256"] is not None
        ):
            _fail("empty bootstrap source inventory has a fabricated identity")
        return None, paths
    fingerprint = _source_fingerprint(records)
    if revision["fingerprint_sha256"] != fingerprint:
        _fail("source fingerprint SHA-256 is wrong")
    if revision["worktree_identity_sha256"] is None:
        _fail("nonempty source inventory lacks a worktree identity")
    return fingerprint, paths


def _normalized_absolute_path(value: str, label: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        _fail(f"{label} is empty or contains NUL")
    if WINDOWS_ABSOLUTE_PATH_RE.match(value):
        if not ntpath.isabs(value):
            _fail(f"{label} is not absolute")
        return ntpath.normpath(value).replace("\\", "/")
    if not posixpath.isabs(value):
        _fail(f"{label} is not absolute")
    return posixpath.normpath(value)


def _verify_file_identity(
    identity: dict[str, Any], label: str, *, rehash: bool
) -> str:
    if identity["readable"] is not True or identity["limitation"] is not None:
        _fail(f"{label} is not recorded as an unqualified readable file")
    resolved = _normalized_absolute_path(identity["resolved_path"], f"{label} path")
    if _normalized_absolute_path(identity["effective_value"], f"{label} value") != resolved:
        _fail(f"{label} effective and resolved paths disagree")
    if rehash:
        path = Path(resolved)
        if _is_link_like(path) or not path.is_file():
            _fail(f"{label} is no longer a regular file")
        data = path.read_bytes()
        if len(data) != identity["byte_length"]:
            _fail(f"{label} byte length does not match")
        if _sha256_bytes(data) != identity["sha256"]:
            _fail(f"{label} SHA-256 does not match")
    return resolved


def _verify_environment(
    report: dict[str, Any], root: Path, *, rehash: bool
) -> tuple[str, str, dict[str, str], str]:
    environment = report["environment"]
    if environment["limitations"] != ENVIRONMENT_LIMITATIONS:
        _fail("environment limitations are not the exact minimized-environment boundary")
    working_directory = _normalized_absolute_path(
        environment["working_directory"], "environment working directory"
    )
    if rehash and Path(working_directory).resolve() != root.resolve():
        _fail("environment working directory is not this repository root")
    python_path = _verify_file_identity(
        environment["python_executable"], "Python executable", rehash=rehash
    )
    git_path = _verify_file_identity(
        environment["git_executable"], "Git executable", rehash=rehash
    )
    overrides: dict[str, str] = {}
    if set(environment["tool_overrides"]) != set(TOOL_NAMES):
        _fail("environment tool override keys are wrong")
    for name in TOOL_NAMES:
        overrides[name] = _verify_file_identity(
            environment["tool_overrides"][name], name, rehash=rehash
        )
    return python_path, git_path, overrides, working_directory


def _parse_timestamp(value: str, label: str) -> datetime:
    if not isinstance(value, str):
        _fail(f"{label} must be a UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        _fail(f"{label} is invalid: {exc}")
    if not value.endswith("Z") or parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
        _fail(f"{label} is not canonical UTC")
    return parsed


def _parse_collection_stdout(stdout: bytes, label: str) -> tuple[list[str], int]:
    try:
        text = stdout.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        _fail(f"{label} collection stdout is not UTF-8: {exc}")
    lines = text.splitlines()
    summary_positions: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        match = COLLECTION_SUMMARY_RE.fullmatch(line.strip())
        if match is not None:
            summary_positions.append((index, int(match.group("count"))))
    if len(summary_positions) != 1:
        _fail(f"{label} must contain exactly one collection summary")
    summary_index, reported_count = summary_positions[0]
    if any(line.strip() for line in lines[summary_index + 1 :]):
        _fail(f"{label} has unexpected output after collection summary")
    node_ids = [line.strip() for line in lines[:summary_index] if line.strip()]
    if len(node_ids) != len(set(node_ids)):
        _fail(f"{label} collection contains duplicate node IDs")
    for node_id in node_ids:
        if "\x00" in node_id or not node_id.startswith("tests/") or "::" not in node_id:
            _fail(f"{label} has malformed node ID {node_id!r}")
    if len(node_ids) != reported_count:
        _fail(
            f"{label} node-ID count {len(node_ids)} differs from pytest count {reported_count}"
        )
    return node_ids, reported_count


def _parse_pytest_summary(stdout: bytes, label: str) -> dict[str, Any]:
    try:
        text = stdout.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        _fail(f"{label} pytest stdout is not UTF-8: {exc}")
    candidates: list[dict[str, int]] = []
    for line in text.splitlines():
        match = PYTEST_SUMMARY_LINE_RE.fullmatch(line.strip())
        if match is None:
            continue
        counts = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "xpassed": 0,
        }
        seen: set[str] = set()
        valid = True
        for part in match.group("body").split(", "):
            count_match = PYTEST_COUNT_RE.fullmatch(part)
            if count_match is None:
                valid = False
                break
            kind = count_match.group("kind")
            normalized = "errors" if kind in {"error", "errors"} else kind
            if normalized in seen:
                valid = False
                break
            seen.add(normalized)
            counts[normalized] = int(count_match.group("count"))
        if valid and seen:
            candidates.append(counts)
    if len(candidates) != 1:
        _fail(f"{label} must contain exactly one parseable pytest summary")
    return {"parsed": True, **candidates[0], "diagnostic": None}


def _verify_process_common(
    record: dict[str, Any],
    label: str,
    snapshots: dict[int, dict[str, Any]],
    working_directory: str,
    previous_finish: datetime,
) -> datetime:
    if (
        _normalized_absolute_path(record["working_directory"], f"{label} cwd")
        != working_directory
    ):
        _fail(f"{label} working directory differs from the recorded environment")
    started = _parse_timestamp(record["started_at_utc"], f"{label} start")
    finished = _parse_timestamp(record["finished_at_utc"], f"{label} finish")
    if started < previous_finish:
        _fail(f"{label} overlaps or precedes the prior process")
    if finished < started:
        _fail(f"{label} finishes before it starts")
    if record["wall_time_ns"] < 0:
        _fail(f"{label} has negative wall time")
    before = record["before_snapshot_sequence"]
    after = record["after_snapshot_sequence"]
    expected_before = 2 * record["process_sequence"] - 1
    expected_after = 2 * record["process_sequence"]
    if before != expected_before or after != expected_after:
        _fail(f"{label} does not reference its exact before/after snapshot pair")
    if before not in snapshots or after not in snapshots:
        _fail(f"{label} references a missing before/after snapshot")
    expected_before_label = (
        f"before:{record['process_sequence']}:{record['phase']}"
    )
    expected_after_label = f"after:{record['process_sequence']}:{record['phase']}"
    if snapshots[before]["label"] != expected_before_label:
        _fail(f"{label} before snapshot label is wrong")
    if snapshots[after]["label"] != expected_after_label:
        _fail(f"{label} after snapshot label is wrong")
    before_time = _parse_timestamp(
        snapshots[before]["captured_at_utc"], f"{label} before snapshot time"
    )
    after_time = _parse_timestamp(
        snapshots[after]["captured_at_utc"], f"{label} after snapshot time"
    )
    if not (before_time <= started <= finished <= after_time):
        _fail(f"{label} timestamps are not bracketed by its snapshots")
    if not snapshots[before]["accepted"]:
        _fail(f"{label} was launched after a rejected worktree guard")
    if record["status"] == "passed":
        if record["exit_code"] != 0:
            _fail(f"{label} passed with nonzero exit code")
        if not snapshots[after]["accepted"]:
            _fail(f"{label} passed without accepted before/after snapshots")
        if record["diagnostic"] is not None:
            _fail(f"{label} passed with a diagnostic")
    else:
        if record["diagnostic"] is None:
            _fail(f"{label} non-passing record lacks a diagnostic")
    _decode_stream(record["stderr"], f"{label} stderr")
    return finished


def _collection_digest(focused: list[str], full: list[str]) -> str:
    return _sha256_bytes(
        _canonical_json_bytes(
            {"focused_node_ids": focused, "full_suite_node_ids": full}
        )
    )


def _expected_pycache_prefix(working_directory: str, basetemp: str) -> str:
    return posixpath.normpath(
        working_directory.rstrip("/") + "/" + basetemp + "/pycache"
    )


def _verify_collection(
    report: dict[str, Any],
    snapshots: dict[int, dict[str, Any]],
    python_path: str,
    tools: dict[str, str],
    working_directory: str,
    execution_started: datetime,
) -> tuple[int | None, int | None, datetime, int]:
    collection = report["collection_identity"]
    records = collection["records"]
    if len(records) > 2:
        _fail("collection has more than two preflight records")
    expected_phases = ["collect_focused", "collect_full_suite"]
    previous_finish = execution_started
    parsed_lists: list[list[str]] = []
    for index, record in enumerate(records):
        label = f"collection record {index + 1}"
        if record["process_sequence"] != index + 1:
            _fail(f"{label} process sequence is wrong")
        if record["phase"] != expected_phases[index]:
            _fail(f"{label} phase is wrong")
        previous_finish = _verify_process_common(
            record, label, snapshots, working_directory, previous_finish
        )
        stdout = _decode_stream(record["stdout"], f"{label} stdout")
        try:
            node_ids, count = _parse_collection_stdout(stdout, label)
        except EvidenceVerificationError:
            node_ids, count = None, None
        if node_ids is None:
            if record["node_ids"] or record["collected_count"] is not None:
                _fail(f"{label} claims collection data absent from raw stdout")
        elif record["node_ids"] != node_ids or record["collected_count"] != count:
            _fail(f"{label} embedded node IDs/count disagree with stdout")
        if record["status"] == "passed":
            if node_ids is None:
                _fail(f"{label} passed without a parseable collection identity")
            parsed_lists.append(node_ids)
        else:
            parsed_lists.append([])
        expected_basetemp = (
            f"{BASETEMP_ROOT}/collection-focused"
            if index == 0
            else f"{BASETEMP_ROOT}/collection-full-suite"
        )
        if record["basetemp_path"] != expected_basetemp:
            _fail(f"{label} basetemp is not task-owned and deterministic")
        expected_argv = [
            python_path,
            "-m",
            "pytest",
            "-q",
            "--collect-only",
            "-p",
            "no:cacheprovider",
        ]
        if index == 0:
            expected_argv.append(FOCUSED_TEST_PATH)
        expected_argv.extend(["--basetemp", expected_basetemp])
        if record["argv"] != expected_argv:
            _fail(f"{label} is not the exact pytest collection command")
        overrides = record["environment_overrides"]
        expected_overrides = {
            "PYTHONPYCACHEPREFIX": _expected_pycache_prefix(
                working_directory, expected_basetemp
            ),
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        }
        if index == 1:
            expected_overrides.update(tools)
        if overrides != expected_overrides:
            _fail(f"{label} environment overrides are not exact")

    passed_prefix = 0
    for index, record in enumerate(records):
        if record["status"] == "passed":
            if passed_prefix != index:
                _fail("collection records are not a passed prefix")
            passed_prefix += 1
        else:
            break
    if any(record["status"] == "passed" for record in records[passed_prefix + 1 :]):
        _fail("collection continued after a non-passing record")
    if any(
        record["status"] != "passed"
        for record in records[:-1]
    ):
        _fail("collection contains a process after its first non-passing record")

    focused_count: int | None = None
    full_count: int | None = None
    if len(records) >= 1 and records[0]["status"] == "passed":
        focused = parsed_lists[0]
        if collection["focused_node_ids"] != focused:
            _fail("focused collection identity differs from raw focused collection")
        if any(
            not node_id.startswith(FOCUSED_TEST_PATH + "::")
            for node_id in focused
        ):
            _fail("focused collection contains a node outside the focused test module")
        focused_count = len(focused)
        if collection["focused_count"] != focused_count:
            _fail("focused collection count is wrong")
    elif collection["focused_node_ids"] or collection["focused_count"] is not None:
        _fail("incomplete focused collection has nonempty aggregate identity")
    if len(records) == 2 and records[1]["status"] == "passed":
        full = parsed_lists[1]
        if collection["full_suite_node_ids"] != full:
            _fail("full collection identity differs from raw full collection")
        full_count = len(full)
        if collection["full_suite_count"] != full_count:
            _fail("full-suite collection count is wrong")
        filtered = [
            node_id
            for node_id in full
            if node_id.startswith(FOCUSED_TEST_PATH + "::")
        ]
        if filtered != collection["focused_node_ids"]:
            _fail("focused collection is not the ordered focused subset of full collection")
    elif collection["full_suite_node_ids"] or collection["full_suite_count"] is not None:
        _fail("incomplete full collection has nonempty aggregate identity")

    if focused_count is not None and full_count is not None:
        digest = _collection_digest(
            collection["focused_node_ids"], collection["full_suite_node_ids"]
        )
        if collection["digest_kind"] != COLLECTION_DIGEST_KIND:
            _fail("unsupported collection digest kind")
        if collection["digest_sha256"] != digest:
            _fail("collection digest SHA-256 is wrong")
        if collection["status"] != "completed" or collection["diagnostic"] is not None:
            _fail("complete collection identity has inconsistent status")
    else:
        if collection["digest_sha256"] is not None:
            _fail("partial collection has a digest")
        if collection["status"] == "completed":
            _fail("partial collection is marked completed")
        nonpassing = next(
            (record for record in records if record["status"] != "passed"),
            None,
        )
        if nonpassing is not None:
            if (
                collection["status"] != nonpassing["status"]
                or collection["diagnostic"] is None
            ):
                _fail("failed/interrupted collection aggregate is inconsistent")
        elif collection["status"] == "pending":
            if collection["diagnostic"] is not None:
                _fail("pending collection identity has a diagnostic")
        elif collection["diagnostic"] is None:
            _fail("terminal partial collection identity lacks a diagnostic")
    return focused_count, full_count, previous_finish, len(records)


def _verify_runs(
    report: dict[str, Any],
    snapshots: dict[int, dict[str, Any]],
    python_path: str,
    tools: dict[str, str],
    working_directory: str,
    focused_count: int | None,
    full_count: int | None,
    previous_finish: datetime,
    collection_records: int,
) -> tuple[datetime, list[int], list[int]]:
    runs = report["runs"]
    if runs and (focused_count is None or full_count is None):
        _fail("stability runs exist before collection identity completed")
    expected_phases = ["focused"] * 25 + ["full_suite"] * 2
    focused_passes: list[int] = []
    full_passes: list[int] = []
    nonpassing_seen = False
    for index, run in enumerate(runs):
        sequence = index + 1
        label = f"run {sequence}"
        if run["sequence"] != sequence:
            _fail("run records are not a strict 1-based prefix")
        if collection_records != 2 or run["process_sequence"] != 2 + sequence:
            _fail(f"{label} process sequence is wrong")
        expected_phase = expected_phases[index]
        expected_phase_index = sequence if expected_phase == "focused" else sequence - 25
        if run["phase"] != expected_phase or run["phase_index"] != expected_phase_index:
            _fail(f"{label} phase or phase index is wrong")
        if nonpassing_seen:
            _fail("run records continue after first non-passing attempt")
        previous_finish = _verify_process_common(
            run, label, snapshots, working_directory, previous_finish
        )
        stdout = _decode_stream(run["stdout"], f"{label} stdout")
        independently_parsed: dict[str, Any] | None
        try:
            independently_parsed = _parse_pytest_summary(stdout, label)
        except EvidenceVerificationError:
            independently_parsed = None
        if run["pytest_summary"]["parsed"]:
            if independently_parsed is None:
                _fail(f"{label} claims a parsed summary absent from stdout")
            if run["pytest_summary"] != independently_parsed:
                _fail(f"{label} embedded pytest summary disagrees with stdout")
        else:
            if independently_parsed is not None:
                _fail(f"{label} fails to record a parseable summary from stdout")
            unparsed = run["pytest_summary"]
            if any(
                unparsed[outcome] is not None
                for outcome in ("passed", "failed", "errors", "skipped", "xfailed", "xpassed")
            ) or unparsed["diagnostic"] is None:
                _fail(f"{label} malformed unparsed pytest summary")
        expected_count = focused_count if expected_phase == "focused" else full_count
        if run["expected_pass_count"] != expected_count:
            _fail(f"{label} expected pass count differs from collection identity")
        if run["status"] == "passed":
            if independently_parsed is None:
                _fail(f"{label} passed without a parseable pytest summary")
            for outcome in ("failed", "errors", "skipped", "xfailed", "xpassed"):
                if independently_parsed[outcome] != 0:
                    _fail(f"{label} has non-passing outcome {outcome}")
            if independently_parsed["passed"] != expected_count:
                _fail(
                    f"{label} pass count {independently_parsed['passed']} "
                    f"does not equal collection count {expected_count}"
                )
            target = focused_passes if expected_phase == "focused" else full_passes
            target.append(independently_parsed["passed"])
        else:
            nonpassing_seen = True
        expected_basetemp = (
            f"{BASETEMP_ROOT}/focused-{expected_phase_index:02d}"
            if expected_phase == "focused"
            else f"{BASETEMP_ROOT}/full-suite-{expected_phase_index:02d}"
        )
        if run["basetemp_path"] != expected_basetemp:
            _fail(f"{label} basetemp is wrong")
        expected_argv = [
            python_path,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
        ]
        if expected_phase == "focused":
            expected_argv.append(FOCUSED_TEST_PATH)
        expected_argv.extend(["--basetemp", expected_basetemp])
        if run["argv"] != expected_argv:
            _fail(f"{label} command is not the exact pytest command")
        overrides = run["environment_overrides"]
        expected_overrides = {
            "PYTHONPYCACHEPREFIX": _expected_pycache_prefix(
                working_directory, expected_basetemp
            ),
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        }
        if expected_phase == "full_suite":
            expected_overrides.update(tools)
        if overrides != expected_overrides:
            _fail(f"{label} environment overrides are not exact")
    return previous_finish, focused_passes, full_passes


def _verify_summary(
    report: dict[str, Any],
    collection_records: int,
    focused_passes: list[int],
    full_passes: list[int],
) -> None:
    runs = report["runs"]
    expected = {
        "recorded_process_count": collection_records + len(runs),
        "recorded_run_count": len(runs),
        "focused_run_count": sum(run["phase"] == "focused" for run in runs),
        "full_suite_run_count": sum(run["phase"] == "full_suite" for run in runs),
        "successful_run_count": sum(run["status"] == "passed" for run in runs),
        "failed_run_count": sum(run["status"] == "failed" for run in runs),
        "retries": 0,
        "focused_pass_counts": focused_passes,
        "full_suite_pass_counts": full_passes,
        "stop_reason": report["summary"]["stop_reason"],
        "failure_detail": report["summary"]["failure_detail"],
    }
    if report["summary"] != expected:
        _fail("summary totals do not equal independently recomputed records")
    if report["completed"]:
        if expected["stop_reason"] != "completed" or expected["failure_detail"] is not None:
            _fail("completed report has inconsistent stop reason")
    else:
        if expected["stop_reason"] == "completed":
            _fail("partial report has completed stop reason")
        nonpassing = [
            record
            for record in [
                *report["collection_identity"]["records"],
                *runs,
            ]
            if record["status"] != "passed"
        ]
        if nonpassing:
            required_reason = (
                "interrupted"
                if nonpassing[-1]["status"] == "interrupted"
                else "failure"
            )
            if expected["stop_reason"] != required_reason:
                _fail("partial summary stop reason disagrees with first failure")
        if expected["stop_reason"] == "in_progress":
            if expected["failure_detail"] is not None:
                _fail("in-progress summary has failure detail")
        elif expected["failure_detail"] is None:
            _fail("terminal partial summary lacks failure detail")


def _next_process_phase(recorded_process_count: int) -> str | None:
    if recorded_process_count == 0:
        return "collect_focused"
    if recorded_process_count == 1:
        return "collect_full_suite"
    run_index = recorded_process_count - 2
    if run_index < 25:
        return "focused"
    if run_index < 27:
        return "full_suite"
    return None


def _verify_snapshot_coverage(
    report: dict[str, Any],
    snapshots: dict[int, dict[str, Any]],
    acquisition_failures: set[int],
) -> None:
    process_records = [
        *report["collection_identity"]["records"],
        *report["runs"],
    ]
    recorded = len(process_records)
    expected_paired_count = 2 * recorded
    observed = len(snapshots)
    if acquisition_failures:
        if (
            len(acquisition_failures) != 1
            or next(iter(acquisition_failures)) != observed
            or report["completed"]
        ):
            _fail("Git acquisition failure is not the sole terminal partial snapshot")
        if report["summary"]["stop_reason"] not in {"failure", "interrupted"}:
            _fail("terminal Git acquisition failure lacks a fail-closed stop reason")
    if observed == expected_paired_count:
        return
    if observed != expected_paired_count + 1:
        _fail("snapshot count is not exact process bracketing plus one optional guard")
    if report["completed"] or recorded >= 29:
        _fail("completed/exhausted plan has an orphan worktree snapshot")
    if any(record["status"] != "passed" for record in process_records):
        _fail("orphan before-guard follows a non-passing process")
    phase = _next_process_phase(recorded)
    if phase is None:
        _fail("orphan before-guard has no next process in the fixed plan")
    orphan = snapshots[observed]
    expected_label = f"before:{recorded + 1}:{phase}"
    if orphan["label"] != expected_label:
        _fail("terminal orphan is not the exact next-process before-guard")
    if report["summary"]["stop_reason"] not in {"failure", "interrupted"}:
        _fail("orphan before-guard lacks a fail-closed stop reason")


def _verify_bootstrap_partial_shape(
    report: dict[str, Any], snapshots: dict[int, dict[str, Any]]
) -> None:
    collection = report["collection_identity"]
    if (
        report["completed"]
        or report["execution_finished_at_utc"] is None
        or list(snapshots) != [1]
    ):
        _fail("bootstrap failure is not an exact one-snapshot partial report")
    first = snapshots[1]
    if (
        first["label"] != "before:1:collect_focused"
        or first["accepted"] is not False
        or first["diagnostic"] is None
    ):
        _fail("bootstrap failure lacks the rejected first before-guard")
    if report["runs"] or collection["records"]:
        _fail("bootstrap failure contains a fabricated process record")
    if (
        collection["status"] != "pending"
        or collection["focused_node_ids"]
        or collection["full_suite_node_ids"]
        or collection["focused_count"] is not None
        or collection["full_suite_count"] is not None
        or collection["digest_sha256"] is not None
        or collection["diagnostic"] is not None
    ):
        _fail("bootstrap failure contains a fabricated collection identity")
    if (
        report["summary"]["stop_reason"] not in {"failure", "interrupted"}
        or report["summary"]["failure_detail"] is None
    ):
        _fail("bootstrap failure lacks a terminal fail-closed summary")


def _expected_basetemps() -> list[str]:
    return [
        f"{BASETEMP_ROOT}/collection-focused",
        f"{BASETEMP_ROOT}/collection-full-suite",
    ] + [
        f"{BASETEMP_ROOT}/focused-{index:02d}" for index in range(1, 26)
    ] + [
        f"{BASETEMP_ROOT}/full-suite-{index:02d}" for index in range(1, 3)
    ]


def _verify_cleanup(report: dict[str, Any], root: Path, *, same_host: bool) -> None:
    cleanup = report["cleanup"]
    expected = _expected_basetemps()
    if cleanup["root"] != BASETEMP_ROOT:
        _fail("cleanup root is not the fixed task-owned root")
    if cleanup["owner_marker"] != f"{BASETEMP_ROOT}/{OWNER_MARKER_NAME}":
        _fail("cleanup owner marker path is wrong")
    root_identity = cleanup["root_identity"]
    marker_identity = cleanup["owner_marker_identity"]
    if root_identity["device"] != marker_identity["device"]:
        _fail("cleanup root and owner marker were not on the same device")
    if root_identity == marker_identity:
        _fail("cleanup root and owner marker identities are not distinct")
    if cleanup["expected"] != expected:
        _fail("cleanup expected paths do not equal the 29-slot plan")
    for field in ("created", "removed", "remaining"):
        values = cleanup[field]
        if len(values) != len(set(values)) or any(value not in expected for value in values):
            _fail(f"cleanup {field} contains a duplicate or foreign path")
    if cleanup["created"] != expected[: len(cleanup["created"])]:
        _fail("cleanup created paths are not a strict serial-plan prefix")
    if not set(cleanup["removed"]) <= set(cleanup["created"]):
        _fail("cleanup claims removal of a basetemp that was never created")
    if not set(cleanup["remaining"]) <= set(cleanup["created"]):
        _fail("cleanup remaining paths include a basetemp that was never created")
    if set(cleanup["remaining"]) & set(cleanup["removed"]):
        _fail("cleanup path is both removed and remaining")
    if cleanup["completed"]:
        if cleanup["remaining"] or cleanup["unexpected"]:
            _fail("completed cleanup reports remaining or unexpected paths")
        if cleanup["removed"] != cleanup["created"]:
            _fail("completed cleanup did not remove every created basetemp")
        if (
            cleanup["identity_verified"] is not True
            or cleanup["root_removed"] is not True
            or cleanup["diagnostic"] is not None
        ):
            _fail("completed cleanup lacks clean root-removal evidence")
    elif cleanup["diagnostic"] is None and report["execution_finished_at_utc"] is not None:
        _fail("finished report has incomplete cleanup without a diagnostic")
    if report["completed"]:
        if cleanup["created"] != expected or cleanup["removed"] != expected:
            _fail("completed cleanup did not create and remove all 29 basetemps")
        if cleanup["remaining"] or cleanup["completed"] is not True:
            _fail("completed cleanup left task-owned basetemps")
    if same_host and cleanup["completed"]:
        cleanup_root = (root / BASETEMP_ROOT).resolve()
        if cleanup_root.exists() or cleanup_root.is_symlink():
            _fail("task-owned cleanup root still exists")


def _run_git(root: Path, arguments: list[str]) -> str:
    command = [
        "git",
        "-c",
        f"safe.directory={root.resolve().as_posix()}",
        *arguments,
    ]
    process = subprocess.run(
        command,
        cwd=root,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        diagnostic = process.stderr.decode("utf-8", errors="replace").strip()
        _fail(f"Git read failed for {arguments!r}: {diagnostic}")
    try:
        return process.stdout.decode("utf-8", errors="strict").strip()
    except UnicodeDecodeError as exc:
        _fail(f"Git output is not UTF-8: {exc}")


def _verify_git_checkout(root: Path) -> None:
    task_start = _run_git(root, ["rev-parse", f"{TASK_START_HEAD}^{{commit}}"])
    if task_start != TASK_START_HEAD:
        _fail("task-start HEAD does not resolve to the required commit")
    base = _run_git(root, ["rev-parse", f"{REVIEW_BASE_COMMIT}^{{commit}}"])
    if base != REVIEW_BASE_COMMIT:
        _fail("review base does not resolve to the required commit")
    if _run_git(root, ["merge-base", REVIEW_BASE_COMMIT, TASK_START_HEAD]) != REVIEW_BASE_COMMIT:
        _fail("review base is not an ancestor of task-start HEAD")
    current = _run_git(root, ["rev-parse", "HEAD"])
    if _run_git(root, ["merge-base", TASK_START_HEAD, current]) != TASK_START_HEAD:
        _fail("current HEAD is neither task-start HEAD nor its descendant")
    origin = _run_git(root, ["remote", "get-url", "origin"])
    if origin not in {
        "https://github.com/falker47/erdos-gyarfas-p14",
        "https://github.com/falker47/erdos-gyarfas-p14.git",
        "git@github.com:falker47/erdos-gyarfas-p14.git",
    }:
        _fail("current origin does not identify falker47/erdos-gyarfas-p14")


def verify_report(
    report_path: Path = DEFAULT_REPORT_PATH,
    *,
    repository_root: Path = REPOSITORY_ROOT,
    schema_path: Path | None = None,
    verify_git: bool = True,
    rehash_environment: bool = False,
    allow_partial: bool = False,
) -> dict[str, Any]:
    """Verify one v2 report without importing or invoking the runner."""

    root = repository_root.resolve()
    selected_schema = (schema_path or (root / "schemas" / SCHEMA_PATH.name)).resolve()
    raw, report = _load_json_object(report_path)
    if raw != _canonical_json_bytes(report):
        _fail("report is not canonical sorted indented UTF-8 JSON with one final LF")
    errors = _schema_errors(report, selected_schema)
    if errors:
        _fail(f"schema validation failed: {errors[0]}")
    exact = {
        "schema_version": "2.0",
        "artifact_kind": ARTIFACT_KIND,
        "classification": CLASSIFICATION,
        "task_id": TASK_ID,
        "repository": REPOSITORY,
        "review_base_commit": REVIEW_BASE_COMMIT,
        "task_start_head": TASK_START_HEAD,
    }
    for key, expected in exact.items():
        if report[key] != expected:
            _fail(f"{key} mismatch: expected {expected!r}, observed {report[key]!r}")
    if report["expected_plan"] != EXPECTED_PLAN:
        _fail("expected_plan is not the exact 2-collection plus 25+2 no-retry plan")
    persistence = report["report_persistence"]
    for key, expected in EXPECTED_REPORT_PERSISTENCE.items():
        if persistence[key] != expected:
            _fail("report persistence policy is not the required atomic policy")
    if report["completed"] and persistence["temporary_absent_at_finish"] is not True:
        _fail("completed report did not establish absence of its temporary file")
    if report["non_execution_task_paths"] != list(NON_EXECUTION_TASK_PATHS):
        _fail("non-execution task path policy is wrong")
    if report["limitations"] != ROOT_LIMITATIONS:
        _fail("claim-boundary limitations are not the exact v2 bounded-evidence list")
    if verify_git:
        _verify_git_checkout(root)

    source_fingerprint, source_paths = _verify_sources(
        report, root, rehash=rehash_environment
    )
    python_path, git_path, tools, working_directory = _verify_environment(
        report, root, rehash=rehash_environment
    )
    snapshots, worktree_identity, acquisition_failures = _verify_snapshots(
        report,
        source_fingerprint,
        git_path=git_path,
        working_directory=working_directory,
        same_host=rehash_environment,
    )
    if source_fingerprint is None:
        _verify_bootstrap_partial_shape(report, snapshots)
    elif snapshots:
        first_parsed = snapshots[min(snapshots)]["parsed"]
        execution_paths = first_parsed["execution_input_paths"]
        if source_paths != execution_paths:
            _fail("source inventory omits or adds an execution input from worktree snapshots")
        tracked_paths = (
            set(first_parsed["tracked_clean"])
            | {record["path"] for record in first_parsed["tracked_modified"]}
            | set(first_parsed["tracked_deleted"])
        )
        for source in report["source_files"]:
            expected_origin = "tracked" if source["path"] in tracked_paths else "untracked"
            if source["origin"] != expected_origin:
                _fail(f"source origin is wrong for {source['path']}")
    execution_started = _parse_timestamp(
        report["execution_started_at_utc"], "execution_started_at_utc"
    )
    focused_count, full_count, previous_finish, collection_records = _verify_collection(
        report,
        snapshots,
        python_path,
        tools,
        working_directory,
        execution_started,
    )
    previous_finish, focused_passes, full_passes = _verify_runs(
        report,
        snapshots,
        python_path,
        tools,
        working_directory,
        focused_count,
        full_count,
        previous_finish,
        collection_records,
    )
    _verify_summary(report, collection_records, focused_passes, full_passes)
    _verify_snapshot_coverage(report, snapshots, acquisition_failures)
    _verify_cleanup(report, root, same_host=rehash_environment)

    finished_value = report["execution_finished_at_utc"]
    if snapshots:
        first_snapshot_time = _parse_timestamp(
            snapshots[1]["captured_at_utc"], "first snapshot timestamp"
        )
        if first_snapshot_time < execution_started:
            _fail("first snapshot precedes execution start")
        last_snapshot_time = _parse_timestamp(
            snapshots[len(snapshots)]["captured_at_utc"],
            "last snapshot timestamp",
        )
    else:
        last_snapshot_time = execution_started
    if finished_value is not None and persistence["temporary_absent_at_finish"] is not True:
        _fail("finished report did not establish absence of its temporary file")
    if report["completed"]:
        if finished_value is None:
            _fail("completed report has no finish timestamp")
        execution_finished = _parse_timestamp(
            finished_value, "execution_finished_at_utc"
        )
        if execution_finished < max(previous_finish, last_snapshot_time):
            _fail("execution finish precedes final subprocess/snapshot")
        if report["collection_identity"]["status"] != "completed":
            _fail("completed report lacks complete collection identity")
        if len(report["runs"]) != 27 or any(
            run["status"] != "passed" for run in report["runs"]
        ):
            _fail("completed report does not contain exactly 27 passed runs")
        if len(snapshots) != 58:
            _fail("completed report does not contain exactly 58 worktree snapshots")
    else:
        if not allow_partial:
            _fail("report is a valid partial record but not completed evidence")
        if finished_value is not None:
            execution_finished = _parse_timestamp(
                finished_value, "execution_finished_at_utc"
            )
            if execution_finished < max(previous_finish, last_snapshot_time):
                _fail("partial execution finish precedes its recorded evidence")

    return {
        "ok": True,
        "completed": report["completed"],
        "evidence_success": report["completed"],
        "report": report_path.resolve().as_posix(),
        "report_byte_length": len(raw),
        "report_sha256": _sha256_bytes(raw),
        "source_fingerprint_sha256": source_fingerprint,
        "worktree_identity_sha256": worktree_identity,
        "collection_digest_sha256": report["collection_identity"]["digest_sha256"],
        "focused_count": focused_count,
        "full_suite_count": full_count,
        "recorded_runs": len(report["runs"]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report",
        nargs="?",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="v2 evidence report",
    )
    parser.add_argument(
        "--rehash-environment",
        action="store_true",
        help="rehash current source files, Python, Git, and the four tool files",
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="accept a semantically valid incomplete prefix as partial, never as success",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report_path = args.report
    if not report_path.is_absolute():
        report_path = REPOSITORY_ROOT / report_path
    try:
        result = verify_report(
            report_path,
            rehash_environment=args.rehash_environment,
            allow_partial=args.allow_partial,
        )
    except (EvidenceVerificationError, OSError, KeyError, TypeError, ValueError) as exc:
        print(
            json.dumps(
                {"ok": False, "error": f"{type(exc).__name__}: {exc}"},
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
