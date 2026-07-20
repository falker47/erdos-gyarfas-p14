#!/usr/bin/env python3
"""Generate fail-closed v2 evidence for inspector timeout-test stability.

The bounded plan is fixed: two collection preflights, then 25 focused pytest
runs and two full-suite runs.  Every child is bracketed by independently
recorded raw Git probes and a source fingerprint.  The runner is deliberately
serial, performs no retry, and preserves a canonical partial report on the
first child failure, interruption, or observed state change.
"""

from __future__ import annotations

import argparse
import base64
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys
import time
from typing import Any, Protocol


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "TASK-20260720__bind_stability_evidence_to_exact_worktree"
REPOSITORY = "falker47/erdos-gyarfas-p14"
BRANCH = "main"
REVIEW_BASE_COMMIT = "a7066e70b92d80be2d1772127f329c24222c1b41"
TASK_START_HEAD = "b1eb792a2a771485f37979cd932303f14ab52f56"
ARTIFACT_KIND = "inspector_timeout_stability_evidence"
CLASSIFICATION = "EMPIRICAL_OBSERVATION"
FINGERPRINT_KIND = "canonical_source_inventory_v2"
COLLECTION_DIGEST_KIND = "canonical_collection_node_ids_v1"
FOCUSED_TEST_PATH = "tests/unit/test_upstream_candidate_inspection.py"
DEFAULT_REPORT_PATH = REPOSITORY_ROOT / "ops" / TASK_ID / "STABILITY_EVIDENCE.json"
DEFAULT_BASETEMP_ROOT = f"build/{TASK_ID}-basetemps"
OWNER_MARKER_NAME = ".inspector-timeout-stability-owner.json"
TASK_STATUS_PATH = f"ops/{TASK_ID}/TASK_STATUS.md"
REPORT_RELATIVE_PATH = f"ops/{TASK_ID}/STABILITY_EVIDENCE.json"
REPORT_TEMPORARY_PATH = REPORT_RELATIVE_PATH + ".tmp"
TOOL_NAMES = ("EG_CMAKE", "EG_CXX", "EG_NINJA", "EG_MAKE")

# These files may change while the task dossier is finalized after the single
# real run.  REVIEW_STATE.yaml is intentionally absent: the full unit suite
# reads it, so it is an execution input and remains fingerprinted.
NON_EXECUTION_TASK_PATHS = tuple(
    sorted(
        {
            "CURRENT_STATUS.md",
            "research/NEXT_RESEARCH_STEPS.md",
            TASK_STATUS_PATH,
            f"ops/{TASK_ID}/TASK_LOG.md",
            f"ops/{TASK_ID}/EVIDENCE.md",
            REPORT_RELATIVE_PATH,
            REPORT_TEMPORARY_PATH,
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
    {"schemas/inspector-timeout-stability-evidence-v2.schema.json"}
)
ALLOWED_UNTRACKED = UNTRACKED_EXECUTION_INPUTS | frozenset(
    {
        TASK_STATUS_PATH,
        f"ops/{TASK_ID}/TASK_LOG.md",
        f"ops/{TASK_ID}/EVIDENCE.md",
        REPORT_RELATIVE_PATH,
    }
)

# Kept as a small compatibility/discovery surface for synthetic tests.  The
# actual inventory is closed dynamically from every tracked execution path
# plus the exact allowed untracked v2 schema.
SOURCE_PATHS = tuple(
    sorted(
        {
            "REVIEW_STATE.yaml",
            "pyproject.toml",
            "schemas/inspector-timeout-stability-evidence.schema.json",
            "schemas/inspector-timeout-stability-evidence-v2.schema.json",
            FOCUSED_TEST_PATH,
            "tests/unit/test_inspector_timeout_stability_evidence.py",
            "tools/inspect_upstream_candidate.py",
            "tools/run_inspector_timeout_stability.py",
            "tools/validate_schemas.py",
            "tools/verify_inspector_timeout_stability.py",
        }
    )
)

EXPECTED_PLAN = {
    "collection_preflight_runs": 2,
    "focused_runs": 25,
    "full_suite_runs": 2,
    "serial": True,
    "retries": 0,
    "stop_on_first_failure": True,
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
FORBIDDEN_INHERITED_CONTROLS = (
    "PYTEST_ADDOPTS",
    "PYTEST_PLUGINS",
    "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
    "PY_COLORS",
    "NO_COLOR",
    "FORCE_COLOR",
    "PYTHONPATH",
    "PYTHONWARNINGS",
    "PYTHONPYCACHEPREFIX",
    "EG_CANDIDATE_INSPECTION_TIMEOUT_SECONDS",
    "EG_SURPRISING_OUTCOME_DIR",
)
SAFE_CHILD_ENVIRONMENT_NAMES = frozenset(
    {
        "PATH",
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "PATHEXT",
        "TEMP",
        "TMP",
        "TMPDIR",
        "USERPROFILE",
        "APPDATA",
        "LOCALAPPDATA",
        "PROGRAMDATA",
        "PROGRAMFILES",
        "PROGRAMFILES(X86)",
        "PROGRAMW6432",
        "NUMBER_OF_PROCESSORS",
        "PROCESSOR_ARCHITECTURE",
        "PROCESSOR_IDENTIFIER",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "TZ",
    }
)

PORCELAIN_MODE_RE = re.compile(rb"^[0-7]{6}$")
PORCELAIN_OID_RE = re.compile(rb"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
PORCELAIN_XY_RE = re.compile(rb"^[.MADRCUT]{2}$")
PORCELAIN_UNMERGED_XY_RE = re.compile(rb"^(?:DD|AU|UD|UA|DU|AA|UU)$")
PORCELAIN_SUB_RE = re.compile(rb"^(?:N\.\.\.|S[.C][.M][.U])$")
PYTEST_SUMMARY_LINE_RE = re.compile(
    r"^(?P<body>.+) in [0-9]+(?:\.[0-9]+)?s(?: \([^\r\n]+\))?$"
)
PYTEST_COUNT_RE = re.compile(
    r"^(?P<count>[0-9]+) (?P<kind>passed|failed|error|errors|skipped|xfailed|xpassed)$"
)
COLLECTION_SUMMARY_RE = re.compile(
    r"^(?P<count>[0-9]+) tests? collected in [0-9]+(?:\.[0-9]+)?s$"
)


class RunnerError(RuntimeError):
    """A deterministic fail-closed runner error."""


class ProcessInterrupted(KeyboardInterrupt):
    """A child interruption carrying every stream captured after termination."""

    def __init__(self, *, returncode: int | None, stdout: bytes, stderr: bytes) -> None:
        super().__init__("pytest subprocess interrupted")
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class ProcessResult(Protocol):
    returncode: int
    stdout: bytes
    stderr: bytes


ProcessRunner = Callable[..., ProcessResult]
GitProbeProvider = Callable[
    [Path, str, dict[str, list[str]]], Mapping[str, ProcessResult]
]


@dataclass(frozen=True, slots=True)
class RunnerConfig:
    repository_root: Path
    report_path: Path
    basetemp_root: str
    tool_values: Mapping[str, str | None]
    python_executable: str = sys.executable
    git_executable: str | None = None


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


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


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _captured_stream(value: bytes) -> dict[str, Any]:
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "byte_length": len(value),
        "sha256": _sha256_bytes(value),
    }


def _safe_relative_path(value: str, label: str) -> str:
    if not value or "\\" in value or value.startswith("/"):
        raise RunnerError(f"{label} is not a canonical repository-relative path: {value!r}")
    if re.match(r"^[A-Za-z]:", value):
        raise RunnerError(f"{label} is absolute: {value!r}")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise RunnerError(f"{label} contains traversal or an empty component: {value!r}")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise RunnerError(f"{label} contains a control character")
    return value


def _is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    isjunction = getattr(os.path, "isjunction", None)
    return bool(isjunction and isjunction(path))


def _repository_file(root: Path, relative_path: str) -> Path:
    _safe_relative_path(relative_path, "source path")
    root_resolved = root.resolve()
    unresolved = root_resolved / Path(relative_path)
    current = root_resolved
    for part in Path(relative_path).parts:
        current = current / part
        if _is_link_like(current):
            raise RunnerError(f"source path contains a symlink or junction: {relative_path}")
    try:
        unresolved.resolve().relative_to(root_resolved)
    except ValueError as exc:
        raise RunnerError(f"source path escapes repository: {relative_path}") from exc
    if not unresolved.is_file():
        raise RunnerError(f"source is not a regular file: {relative_path}")
    return unresolved


def _resolve_executable(value: str | None, label: str) -> Path:
    if value is None or not value.strip():
        raise RunnerError(f"{label} executable is required")
    candidate = Path(value)
    if not candidate.is_absolute():
        resolved_value = shutil.which(value)
        if resolved_value is None:
            raise RunnerError(f"{label} executable cannot be resolved: {value!r}")
        candidate = Path(resolved_value)
    resolved = candidate.resolve()
    if _is_link_like(candidate) or not resolved.is_file():
        raise RunnerError(f"{label} executable is not a regular non-symlink file: {value!r}")
    return resolved


def _file_identity(value: str | None, label: str) -> dict[str, Any]:
    path = _resolve_executable(value, label)
    data = path.read_bytes()
    normalized = path.as_posix()
    return {
        "effective_value": normalized,
        "resolved_path": normalized,
        "readable": True,
        "byte_length": len(data),
        "sha256": _sha256_bytes(data),
        "limitation": None,
    }


def _source_inventory(
    root: Path,
    paths: list[str] | tuple[str, ...],
    tracked_paths: set[str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relative_path in sorted(paths):
        path = _repository_file(root, relative_path)
        data = path.read_bytes()
        records.append(
            {
                "path": relative_path,
                "byte_length": len(data),
                "sha256": _sha256_bytes(data),
                "origin": "tracked" if relative_path in tracked_paths else "untracked",
            }
        )
    return records


def _source_fingerprint(records: list[dict[str, Any]]) -> str:
    return _sha256_bytes(_canonical_json_bytes(records))


def _environment_record(
    config: RunnerConfig,
    *,
    python_identity: dict[str, Any],
    git_identity: dict[str, Any],
    tool_identities: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    processor = platform.processor().strip() or None
    machine_identifier = platform.node().strip() or None
    cpu_count = os.cpu_count()
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable": python_identity,
        "git_executable": git_identity,
        "operating_system": platform.platform(),
        "architecture": platform.machine() or "unknown",
        "machine_identifier": machine_identifier,
        "processor_identifier": processor,
        "cpu_count": cpu_count,
        "working_directory": config.repository_root.resolve().as_posix(),
        "tool_overrides": tool_identities,
        "limitations": list(ENVIRONMENT_LIMITATIONS),
    }


def _verify_inherited_environment() -> None:
    present = [name for name in FORBIDDEN_INHERITED_CONTROLS if os.environ.get(name)]
    if present:
        raise RunnerError(
            "refusing inherited execution-control environment variables: "
            + ", ".join(present)
        )


def _child_environment(overrides: Mapping[str, str]) -> dict[str, str]:
    environment = {
        name: value
        for name, value in os.environ.items()
        if name.upper() in SAFE_CHILD_ENVIRONMENT_NAMES
    }
    if not any(name.upper() == "PATH" for name in environment):
        raise RunnerError("PATH is required for the bounded pytest environment")
    environment.update(overrides)
    return environment


def _git_prefix(root: Path, git_path: str) -> list[str]:
    return [
        git_path,
        "-c",
        f"safe.directory={root.resolve().as_posix()}",
        "-c",
        "core.excludesFile=",
    ]


def _git_probe_commands(root: Path, git_path: str) -> dict[str, list[str]]:
    prefix = _git_prefix(root, git_path)
    return {
        "status": [
            *prefix,
            "status",
            "--porcelain=v2",
            "-z",
            "--untracked-files=all",
            "--no-renames",
        ],
        "tracked": [*prefix, "ls-files", "-z"],
        "untracked": [
            *prefix,
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        "ignored": [
            *prefix,
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "-z",
        ],
        "staged": [
            *prefix,
            "diff",
            "--cached",
            "--name-only",
            "-z",
            "--",
        ],
    }


def _default_git_probe_provider(
    root: Path,
    _label: str,
    commands: dict[str, list[str]],
) -> dict[str, subprocess.CompletedProcess[bytes]]:
    results: dict[str, subprocess.CompletedProcess[bytes]] = {}
    for name, argv in commands.items():
        results[name] = subprocess.run(
            argv,
            cwd=root,
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    return results


def _nul_records(raw: bytes, label: str) -> list[bytes]:
    if not raw:
        return []
    if not raw.endswith(b"\0"):
        raise RunnerError(f"{label} is not NUL terminated")
    records = raw[:-1].split(b"\0")
    if any(not record for record in records):
        raise RunnerError(f"{label} contains an empty NUL record")
    return records


def _decode_git_path(raw: bytes, label: str) -> str:
    try:
        value = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RunnerError(f"{label} is not UTF-8: {exc}") from exc
    if value.encode("utf-8") != raw:
        raise RunnerError(f"{label} does not round-trip through UTF-8")
    return _safe_relative_path(value, label)


def _parse_path_list(raw: bytes, label: str) -> list[str]:
    paths = [
        _decode_git_path(record, f"{label} path {index}")
        for index, record in enumerate(_nul_records(raw, label), start=1)
    ]
    if len(paths) != len(set(paths)):
        raise RunnerError(f"{label} contains a duplicate path")
    return paths


def _validate_status_metadata(parts: list[bytes], label: str) -> None:
    if not PORCELAIN_XY_RE.fullmatch(parts[1]):
        raise RunnerError(f"{label} has malformed XY state")
    if not PORCELAIN_SUB_RE.fullmatch(parts[2]):
        raise RunnerError(f"{label} has malformed submodule state")
    if not all(PORCELAIN_MODE_RE.fullmatch(value) for value in parts[3:6]):
        raise RunnerError(f"{label} has malformed file mode")
    if not all(PORCELAIN_OID_RE.fullmatch(value) for value in parts[6:8]):
        raise RunnerError(f"{label} has malformed object ID")


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
                raise RunnerError(f"{record_label} is malformed")
            _validate_status_metadata(parts, record_label)
            path = _decode_git_path(parts[8], f"{record_label} path")
            xy = parts[1].decode("ascii")
        elif record.startswith(b"2 "):
            parts = record.split(b" ", 9)
            if len(parts) != 10 or index + 1 >= len(records):
                raise RunnerError(f"{record_label} is a malformed rename/copy record")
            _validate_status_metadata(parts, record_label)
            score_match = re.fullmatch(rb"[RC]([0-9]{1,3})", parts[8])
            if score_match is None or int(score_match.group(1)) > 100:
                raise RunnerError(f"{record_label} has malformed rename/copy score")
            path = _decode_git_path(parts[9], f"{record_label} path")
            _decode_git_path(records[index + 1], f"{record_label} original path")
            xy = parts[1].decode("ascii")
            index += 1
        elif record.startswith(b"u "):
            parts = record.split(b" ", 10)
            if len(parts) != 11:
                raise RunnerError(f"{record_label} is a malformed unmerged record")
            if not PORCELAIN_UNMERGED_XY_RE.fullmatch(parts[1]):
                raise RunnerError(f"{record_label} has malformed unmerged XY state")
            if not PORCELAIN_SUB_RE.fullmatch(parts[2]):
                raise RunnerError(f"{record_label} has malformed unmerged submodule state")
            if not all(PORCELAIN_MODE_RE.fullmatch(value) for value in parts[3:7]):
                raise RunnerError(f"{record_label} has malformed unmerged file mode")
            if not all(PORCELAIN_OID_RE.fullmatch(value) for value in parts[7:10]):
                raise RunnerError(f"{record_label} has malformed unmerged object ID")
            path = _decode_git_path(parts[10], f"{record_label} path")
            xy = parts[1].decode("ascii")
        elif record.startswith(b"? "):
            untracked.append(_decode_git_path(record[2:], f"{record_label} path"))
            index += 1
            continue
        elif record.startswith(b"! "):
            ignored.append(_decode_git_path(record[2:], f"{record_label} path"))
            index += 1
            continue
        else:
            raise RunnerError(f"{record_label} has an unknown porcelain-v2 prefix")
        if path in tracked_states:
            raise RunnerError(f"{label} contains duplicate tracked path {path!r}")
        tracked_states[path] = (xy[0], xy[1])
        index += 1
    if len(untracked) != len(set(untracked)):
        raise RunnerError(f"{label} contains duplicate untracked records")
    if len(ignored) != len(set(ignored)):
        raise RunnerError(f"{label} contains duplicate ignored records")
    return {
        "tracked_states": tracked_states,
        "untracked": untracked,
        "ignored": ignored,
    }


def _ignored_path_is_neutralized(path: str) -> bool:
    return (
        path.startswith("build/pytest-")
        or "__pycache__" in path.split("/")
    )


def _ignored_path_is_fingerprinted(path: str) -> bool:
    return path.startswith("build/release/")


def _expected_basetemps(root_relative: str = DEFAULT_BASETEMP_ROOT) -> list[str]:
    return [
        f"{root_relative}/collection-focused",
        f"{root_relative}/collection-full-suite",
        *[
            f"{root_relative}/focused-{index:02d}"
            for index in range(1, 26)
        ],
        *[
            f"{root_relative}/full-suite-{index:02d}"
            for index in range(1, 3)
        ],
    ]


def _ignored_task_path_is_owned(path: str, root_relative: str) -> bool:
    if path == f"{root_relative}/{OWNER_MARKER_NAME}":
        return True
    return any(
        path.startswith(basetemp + "/")
        for basetemp in _expected_basetemps(root_relative)
    )


def _task_status_file(root: Path) -> dict[str, Any]:
    path = root / TASK_STATUS_PATH
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
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return {
            "path": TASK_STATUS_PATH,
            "exists": False,
            "kind": "missing",
            "symlink": False,
        }
    symlink = stat.S_ISLNK(mode) or _is_link_like(path)
    if symlink:
        kind = "other"
    elif stat.S_ISREG(mode):
        kind = "regular_file"
    elif stat.S_ISDIR(mode):
        kind = "directory"
    else:
        kind = "other"
    return {
        "path": TASK_STATUS_PATH,
        "exists": True,
        "kind": kind,
        "symlink": symlink,
    }


def _healthy_task_status() -> dict[str, Any]:
    return {
        "path": TASK_STATUS_PATH,
        "exists": True,
        "kind": "regular_file",
        "symlink": False,
    }


def _normalize_snapshot(
    *,
    raw: dict[str, bytes],
    root_relative: str,
) -> tuple[dict[str, Any], set[str]]:
    status = _parse_porcelain_v2(raw["status"], "Git status stdout")
    tracked = _parse_path_list(raw["tracked"], "Git tracked stdout")
    untracked = _parse_path_list(raw["untracked"], "Git untracked stdout")
    ignored = _parse_path_list(raw["ignored"], "Git ignored stdout")
    staged_probe = _parse_path_list(raw["staged"], "Git staged stdout")

    tracked_set = set(tracked)
    if tracked_set & set(untracked):
        raise RunnerError("tracked and untracked Git inventories overlap")
    if tracked_set & set(ignored):
        raise RunnerError("tracked and ignored Git inventories overlap")
    if set(untracked) & set(ignored):
        raise RunnerError("untracked and ignored Git inventories overlap")
    if not set(status["tracked_states"]) <= tracked_set:
        raise RunnerError("Git status names a path absent from tracked inventory")
    if set(status["untracked"]) != set(untracked):
        raise RunnerError("Git status and untracked probes disagree")
    if status["ignored"]:
        raise RunnerError("Git status unexpectedly emitted ignored records")
    staged_status = {
        path
        for path, (index_state, _worktree_state) in status["tracked_states"].items()
        if index_state != "."
    }
    if staged_status != set(staged_probe):
        raise RunnerError("Git status and staged probes disagree")

    tracked_deleted = sorted(
        path
        for path, (_index_state, worktree_state) in status["tracked_states"].items()
        if worktree_state == "D"
    )
    tracked_modified = [
        {
            "path": path,
            "index_status": index_state,
            "worktree_status": worktree_state,
        }
        for path, (index_state, worktree_state) in sorted(
            status["tracked_states"].items()
        )
        if worktree_state not in {".", "D"}
    ]
    modified_paths = {record["path"] for record in tracked_modified}
    tracked_clean = sorted(tracked_set - set(tracked_deleted) - modified_paths)
    ignored_task = sorted(
        path
        for path in ignored
        if path == root_relative or path.startswith(root_relative + "/")
    )
    ignored_other = sorted(set(ignored) - set(ignored_task))
    task_non_execution = sorted(
        (modified_paths | set(tracked_deleted) | set(untracked))
        & set(NON_EXECUTION_TASK_PATHS)
    )
    execution_inputs = sorted(
        (tracked_set - set(NON_EXECUTION_TASK_PATHS))
        | (set(untracked) & set(UNTRACKED_EXECUTION_INPUTS))
        | {path for path in ignored_other if _ignored_path_is_fingerprinted(path)}
    )
    staged_records = [
        {
            "path": path,
            "index_status": status["tracked_states"][path][0],
        }
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
        | {
            path
            for path in ignored_task
            if not _ignored_task_path_is_owned(path, root_relative)
        }
        | ({REPORT_TEMPORARY_PATH} & set(untracked))
        | ({REPORT_TEMPORARY_PATH} & set(ignored))
    )
    return (
        {
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
        },
        tracked_set,
    )


def _snapshot_execution_payload(
    parsed: dict[str, Any],
    source_fingerprint: str | None,
    task_status_file: dict[str, Any],
) -> dict[str, Any]:
    return {
        "execution_input_paths": parsed["execution_input_paths"],
        "ignored_other": parsed["ignored_other"],
        "source_fingerprint_sha256": source_fingerprint,
        "staged": parsed["staged"],
        "task_status_file": task_status_file,
        "tracked_deleted": parsed["tracked_deleted"],
        "tracked_modified": parsed["tracked_modified"],
        "untracked_execution_inputs": sorted(
            set(parsed["untracked"]) & set(UNTRACKED_EXECUTION_INPUTS)
        ),
        "unexpected_paths": parsed["unexpected_paths"],
    }


def _capture_snapshot(
    *,
    root: Path,
    root_relative: str,
    git_path: str,
    label: str,
    sequence: int,
    expected_source_fingerprint: str | None,
    expected_execution_state_sha256: str | None,
    utc_now: Callable[[], str],
    git_probe_provider: GitProbeProvider,
) -> tuple[dict[str, Any], list[dict[str, Any]] | None]:
    commands = _git_probe_commands(root, git_path)
    results = git_probe_provider(root, label, commands)
    if set(results) != set(commands):
        raise RunnerError("Git probe provider returned the wrong command set")
    command_records: dict[str, Any] = {}
    raw: dict[str, bytes] = {}
    guard_errors: list[str] = []
    for name in commands:
        result = results[name]
        stdout = bytes(result.stdout or b"")
        stderr = bytes(result.stderr or b"")
        command_records[name] = {
            "argv": commands[name],
            "exit_code": result.returncode,
            "stdout": _captured_stream(stdout),
            "stderr": _captured_stream(stderr),
        }
        if result.returncode != 0:
            guard_errors.append(f"Git {name} probe exited with {result.returncode}")
        if stderr:
            guard_errors.append(f"Git {name} probe emitted unexpected stderr")
        raw[name] = stdout

    task_status = _task_status_file(root)
    if not guard_errors:
        try:
            parsed, tracked_paths = _normalize_snapshot(
                raw=raw,
                root_relative=root_relative,
            )
        except RunnerError as exc:
            guard_errors.append(f"{type(exc).__name__}: {exc}")
    if guard_errors:
        return (
            {
                "sequence": sequence,
                "label": label,
                "captured_at_utc": utc_now(),
                "commands": command_records,
                "task_status_file": task_status,
                "parsed": None,
                "normalized_sha256": None,
                "execution_state_sha256": None,
                "source_fingerprint_sha256": None,
                "accepted": False,
                "diagnostic": "; ".join(guard_errors),
            },
            None,
        )

    source_records: list[dict[str, Any]] | None
    source_error: str | None = None
    try:
        source_records = _source_inventory(
            root,
            parsed["execution_input_paths"],
            tracked_paths,
        )
        observed_source_fingerprint: str | None = _source_fingerprint(source_records)
    except (OSError, RunnerError) as exc:
        source_records = None
        observed_source_fingerprint = None
        source_error = f"{type(exc).__name__}: {exc}"

    reasons: list[str] = []
    if parsed["unexpected_paths"]:
        reasons.append(
            "unexpected worktree paths: " + ", ".join(parsed["unexpected_paths"])
        )
    if task_status != _healthy_task_status():
        reasons.append("active task status is not an exact regular non-symlink file")
    if source_error is not None:
        reasons.append(source_error)
    if (
        expected_source_fingerprint is not None
        and observed_source_fingerprint != expected_source_fingerprint
    ):
        reasons.append("source fingerprint differs from frozen execution identity")
    execution_payload = _snapshot_execution_payload(
        parsed,
        observed_source_fingerprint,
        task_status,
    )
    execution_state_sha256 = _sha256_bytes(_canonical_json_bytes(execution_payload))
    if (
        expected_execution_state_sha256 is not None
        and execution_state_sha256 != expected_execution_state_sha256
    ):
        reasons.append("execution-state identity differs from the frozen preflight")
    accepted = not reasons
    diagnostic = "; ".join(reasons) if reasons else None
    snapshot = {
        "sequence": sequence,
        "label": label,
        "captured_at_utc": utc_now(),
        "commands": command_records,
        "task_status_file": task_status,
        "parsed": parsed,
        "normalized_sha256": _sha256_bytes(_canonical_json_bytes(parsed)),
        "execution_state_sha256": execution_state_sha256,
        "source_fingerprint_sha256": observed_source_fingerprint,
        "accepted": accepted,
        "diagnostic": diagnostic,
    }
    return snapshot, source_records


def _run_git_text(root: Path, git_path: str, arguments: list[str]) -> str:
    process = subprocess.run(
        [*_git_prefix(root, git_path), *arguments],
        cwd=root,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        diagnostic = process.stderr.decode("utf-8", errors="replace").strip()
        raise RunnerError(f"Git read failed for {arguments!r}: {diagnostic}")
    if process.stderr:
        raise RunnerError(f"Git read emitted unexpected stderr for {arguments!r}")
    try:
        return process.stdout.decode("utf-8", errors="strict").strip()
    except UnicodeDecodeError as exc:
        raise RunnerError(f"Git read is not UTF-8 for {arguments!r}: {exc}") from exc


def verify_git_preconditions(
    root: Path,
    git_path: str | None = None,
) -> None:
    selected_git = git_path or _resolve_executable(shutil.which("git"), "Git").as_posix()
    if _run_git_text(root, selected_git, ["rev-parse", "--show-toplevel"]).replace(
        "\\", "/"
    ) != root.resolve().as_posix():
        raise RunnerError("repository root does not match the intended checkout")
    if _run_git_text(root, selected_git, ["branch", "--show-current"]) != BRANCH:
        raise RunnerError(f"current branch must be {BRANCH}")
    if _run_git_text(root, selected_git, ["rev-parse", "HEAD"]) != TASK_START_HEAD:
        raise RunnerError(f"HEAD must be exact task-start commit {TASK_START_HEAD}")
    if (
        _run_git_text(
            root,
            selected_git,
            ["rev-parse", f"{REVIEW_BASE_COMMIT}^{{commit}}"],
        )
        != REVIEW_BASE_COMMIT
    ):
        raise RunnerError("accepted review base does not resolve")
    if (
        _run_git_text(
            root,
            selected_git,
            ["merge-base", REVIEW_BASE_COMMIT, TASK_START_HEAD],
        )
        != REVIEW_BASE_COMMIT
    ):
        raise RunnerError("accepted review base is not an ancestor of task-start HEAD")
    origin = _run_git_text(root, selected_git, ["remote", "get-url", "origin"])
    if origin not in {
        "https://github.com/falker47/erdos-gyarfas-p14",
        "https://github.com/falker47/erdos-gyarfas-p14.git",
        "git@github.com:falker47/erdos-gyarfas-p14.git",
    }:
        raise RunnerError(f"origin does not identify {REPOSITORY}: {origin!r}")
    if _run_git_text(root, selected_git, ["diff", "--cached", "--name-only", "--"]):
        raise RunnerError("index must be empty before evidence execution")


def _atomic_write_report(path: Path, report: dict[str, Any], *, initial: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if _is_link_like(path) or _is_link_like(temporary):
        raise RunnerError("report or temporary path is a symlink/junction")
    if initial and path.exists():
        raise FileExistsError(f"refusing to overwrite existing evidence report: {path}")
    if not initial and (not path.is_file() or _is_link_like(path)):
        raise RunnerError("existing evidence report is not a regular task-owned file")
    if temporary.exists():
        raise FileExistsError(f"report temporary path already exists: {temporary}")
    data = _canonical_json_bytes(report)
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        # Do not remove an uncertain temporary file here.  The last atomically
        # installed report remains the authoritative partial record.
        raise
    if temporary.exists() or _is_link_like(temporary):
        raise RunnerError("atomic report temporary path remains after replacement")


def _owner_marker_payload(root_relative: str) -> dict[str, str]:
    return {
        "artifact_kind": ARTIFACT_KIND,
        "task_id": TASK_ID,
        "basetemp_root": root_relative,
    }


def _path_identity(path: Path, label: str) -> dict[str, int]:
    if _is_link_like(path):
        raise RunnerError(f"{label} is link-like")
    metadata = path.stat(follow_symlinks=False)
    return {"device": int(metadata.st_dev), "inode": int(metadata.st_ino)}


def _prepare_basetemp_root(
    root: Path,
    root_relative: str,
) -> tuple[Path, Path, dict[str, dict[str, int]]]:
    _safe_relative_path(root_relative, "basetemp root")
    if root_relative != DEFAULT_BASETEMP_ROOT:
        raise RunnerError("basetemp root must equal the fixed task-owned path")
    root_resolved = root.resolve()
    parent = root_resolved
    for part in Path(root_relative).parent.parts:
        parent = parent / part
        if _is_link_like(parent):
            raise RunnerError("basetemp parent contains a symlink or junction")
    try:
        parent.resolve().relative_to(root_resolved)
    except ValueError as exc:
        raise RunnerError("basetemp parent escapes repository") from exc
    base = root_resolved / root_relative
    if base.exists() or _is_link_like(base):
        raise RunnerError(f"task-owned basetemp root already exists: {root_relative}")
    base.parent.mkdir(parents=True, exist_ok=True)
    base.mkdir()
    marker = base / OWNER_MARKER_NAME
    marker.write_bytes(_canonical_json_bytes(_owner_marker_payload(root_relative)))
    identities = {
        "root_identity": _path_identity(base, "basetemp root"),
        "owner_marker_identity": _path_identity(marker, "basetemp owner marker"),
    }
    return base, marker, identities


def _verify_owner_marker(
    marker: Path,
    root_relative: str,
    *,
    base: Path | None = None,
    expected_identities: dict[str, dict[str, int]] | None = None,
) -> None:
    if _is_link_like(marker) or not marker.is_file():
        raise RunnerError("task-owned basetemp owner marker is missing or unsafe")
    try:
        value = json.loads(marker.read_bytes().decode("utf-8", errors="strict"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RunnerError(f"basetemp owner marker cannot be verified: {exc}") from exc
    if value != _owner_marker_payload(root_relative):
        raise RunnerError("basetemp owner marker payload is wrong")
    if marker.read_bytes() != _canonical_json_bytes(value):
        raise RunnerError("basetemp owner marker is not canonical")
    if expected_identities is not None:
        if base is None:
            raise RunnerError("basetemp identity verification lacks root path")
        if _path_identity(base, "basetemp root") != expected_identities["root_identity"]:
            raise RunnerError("basetemp root identity changed")
        if (
            _path_identity(marker, "basetemp owner marker")
            != expected_identities["owner_marker_identity"]
        ):
            raise RunnerError("basetemp owner marker identity changed")


def _create_basetemp(
    root: Path,
    base: Path,
    marker: Path,
    root_relative: str,
    relative_path: str,
    expected_identities: dict[str, dict[str, int]],
) -> None:
    _verify_owner_marker(
        marker,
        root_relative,
        base=base,
        expected_identities=expected_identities,
    )
    expected_parent = base.resolve()
    path = root / relative_path
    if path.parent.resolve() != expected_parent:
        raise RunnerError(f"basetemp is outside task-owned root: {relative_path}")
    if path.exists() or _is_link_like(path):
        raise RunnerError(f"basetemp already exists or is unsafe: {relative_path}")
    path.mkdir()


def _cleanup_basetemps(
    *,
    root: Path,
    base: Path,
    marker: Path,
    root_relative: str,
    created: list[str],
    expected_identities: dict[str, dict[str, int]],
) -> dict[str, Any]:
    expected = _expected_basetemps(root_relative)
    removed: list[str] = []
    remaining: list[str] = []
    unexpected: list[str] = []
    diagnostic: str | None = None
    root_removed = False
    identity_verified = False
    try:
        current = root.resolve()
        for part in Path(root_relative).parts:
            current = current / part
            if _is_link_like(current):
                raise RunnerError("cleanup root has a link-like path component")
        try:
            base.resolve().relative_to(root.resolve())
        except ValueError as exc:
            raise RunnerError("cleanup root escapes repository") from exc
        if _is_link_like(base) or not base.is_dir():
            raise RunnerError("cleanup root is missing, replaced, or link-like")
        _verify_owner_marker(
            marker,
            root_relative,
            base=base,
            expected_identities=expected_identities,
        )
        identity_verified = True
        allowed_names = {Path(path).name for path in created} | {OWNER_MARKER_NAME}
        for child in base.iterdir():
            if child.name not in allowed_names:
                unexpected.append(f"{root_relative}/{child.name}")
        if unexpected:
            raise RunnerError("cleanup root contains unexpected top-level entries")
        for relative_path in created:
            path = root / relative_path
            if not path.exists() and not _is_link_like(path):
                remaining.append(relative_path)
                raise RunnerError(
                    f"cleanup child disappeared before positive removal: {relative_path}"
                )
            if _is_link_like(path) or not path.is_dir() or path.parent.resolve() != base.resolve():
                remaining.append(relative_path)
                raise RunnerError(f"cleanup child is unsafe: {relative_path}")
            shutil.rmtree(path)
            if path.exists() or _is_link_like(path):
                remaining.append(relative_path)
                raise RunnerError(f"cleanup child remains: {relative_path}")
            removed.append(relative_path)
        _verify_owner_marker(
            marker,
            root_relative,
            base=base,
            expected_identities=expected_identities,
        )
        marker.unlink()
        base.rmdir()
        root_removed = not base.exists() and not _is_link_like(base)
        if not root_removed:
            raise RunnerError("cleanup root remains after removal")
    except (OSError, RunnerError) as exc:
        diagnostic = f"{type(exc).__name__}: {exc}"
        for relative_path in created:
            path = root / relative_path
            if (path.exists() or _is_link_like(path)) and relative_path not in remaining:
                remaining.append(relative_path)
    completed = (
        diagnostic is None
        and not unexpected
        and not remaining
        and removed == created
        and root_removed
    )
    return {
        "root": root_relative,
        "owner_marker": f"{root_relative}/{OWNER_MARKER_NAME}",
        "expected": expected,
        "created": list(created),
        "removed": removed,
        "remaining": remaining,
        "unexpected": unexpected,
        "root_identity": expected_identities["root_identity"],
        "owner_marker_identity": expected_identities["owner_marker_identity"],
        "identity_verified": identity_verified,
        "root_removed": root_removed,
        "completed": completed,
        "diagnostic": diagnostic,
    }


def _unparsed_summary(diagnostic: str) -> dict[str, Any]:
    return {
        "parsed": False,
        "passed": None,
        "failed": None,
        "errors": None,
        "skipped": None,
        "xfailed": None,
        "xpassed": None,
        "diagnostic": diagnostic,
    }


def parse_pytest_summary(stdout: bytes) -> dict[str, Any]:
    try:
        text = stdout.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        return _unparsed_summary(f"pytest stdout is not UTF-8: {exc}")
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
        return _unparsed_summary(
            "expected exactly one parseable pytest summary line; "
            f"observed {len(candidates)}"
        )
    return {"parsed": True, **candidates[0], "diagnostic": None}


def parse_collection_stdout(stdout: bytes) -> tuple[list[str] | None, int | None, str | None]:
    try:
        text = stdout.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        return None, None, f"collection stdout is not UTF-8: {exc}"
    lines = text.splitlines()
    summaries: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        match = COLLECTION_SUMMARY_RE.fullmatch(line.strip())
        if match is not None:
            summaries.append((index, int(match.group("count"))))
    if len(summaries) != 1:
        return None, None, "expected exactly one collection summary"
    summary_index, reported_count = summaries[0]
    if any(line.strip() for line in lines[summary_index + 1 :]):
        return None, None, "unexpected output follows collection summary"
    node_ids = [line.strip() for line in lines[:summary_index] if line.strip()]
    if len(node_ids) != len(set(node_ids)):
        return None, None, "collection contains duplicate node IDs"
    if any(
        not node_id.startswith("tests/") or "::" not in node_id or "\x00" in node_id
        for node_id in node_ids
    ):
        return None, None, "collection contains a malformed node ID"
    if len(node_ids) != reported_count:
        return None, None, "collection node-ID count differs from pytest count"
    return node_ids, reported_count, None


def _collection_digest(focused: list[str], full: list[str]) -> str:
    return _sha256_bytes(
        _canonical_json_bytes(
            {"focused_node_ids": focused, "full_suite_node_ids": full}
        )
    )


def _default_process_runner(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[bytes]:
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = process.communicate()
    except KeyboardInterrupt as exc:
        try:
            process.kill()
        except OSError:
            pass
        stdout, stderr = process.communicate()
        raise ProcessInterrupted(
            returncode=process.returncode,
            stdout=stdout or b"",
            stderr=stderr or b"",
        ) from exc
    return subprocess.CompletedProcess(
        argv,
        process.returncode,
        stdout or b"",
        stderr or b"",
    )


def _collection_command(
    python_path: str,
    phase: str,
    basetemp: str,
) -> list[str]:
    argv = [
        python_path,
        "-m",
        "pytest",
        "-q",
        "--collect-only",
        "-p",
        "no:cacheprovider",
    ]
    if phase == "collect_focused":
        argv.append(FOCUSED_TEST_PATH)
    argv.extend(["--basetemp", basetemp])
    return argv


def _run_command(python_path: str, phase: str, basetemp: str) -> list[str]:
    argv = [python_path, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    if phase == "focused":
        argv.append(FOCUSED_TEST_PATH)
    argv.extend(["--basetemp", basetemp])
    return argv


def _process_plan() -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = [
        {
            "process_sequence": 1,
            "phase": "collect_focused",
            "phase_index": 1,
            "basetemp": f"{DEFAULT_BASETEMP_ROOT}/collection-focused",
            "collection": True,
        },
        {
            "process_sequence": 2,
            "phase": "collect_full_suite",
            "phase_index": 1,
            "basetemp": f"{DEFAULT_BASETEMP_ROOT}/collection-full-suite",
            "collection": True,
        },
    ]
    for index in range(1, 26):
        plan.append(
            {
                "process_sequence": index + 2,
                "sequence": index,
                "phase": "focused",
                "phase_index": index,
                "basetemp": f"{DEFAULT_BASETEMP_ROOT}/focused-{index:02d}",
                "collection": False,
            }
        )
    for index in range(1, 3):
        plan.append(
            {
                "process_sequence": 27 + index,
                "sequence": 25 + index,
                "phase": "full_suite",
                "phase_index": index,
                "basetemp": f"{DEFAULT_BASETEMP_ROOT}/full-suite-{index:02d}",
                "collection": False,
            }
        )
    return plan


def _summary(
    report: dict[str, Any],
    *,
    stop_reason: str,
    failure_detail: str | None,
) -> dict[str, Any]:
    runs = report["runs"]
    collection_records = report["collection_identity"]["records"]
    focused_pass_counts = [
        run["pytest_summary"]["passed"]
        for run in runs
        if run["phase"] == "focused"
        and run["status"] == "passed"
        and run["pytest_summary"]["passed"] is not None
    ]
    full_pass_counts = [
        run["pytest_summary"]["passed"]
        for run in runs
        if run["phase"] == "full_suite"
        and run["status"] == "passed"
        and run["pytest_summary"]["passed"] is not None
    ]
    return {
        "recorded_process_count": len(collection_records) + len(runs),
        "recorded_run_count": len(runs),
        "focused_run_count": sum(run["phase"] == "focused" for run in runs),
        "full_suite_run_count": sum(
            run["phase"] == "full_suite" for run in runs
        ),
        "successful_run_count": sum(run["status"] == "passed" for run in runs),
        "failed_run_count": sum(run["status"] == "failed" for run in runs),
        "retries": 0,
        "focused_pass_counts": focused_pass_counts,
        "full_suite_pass_counts": full_pass_counts,
        "stop_reason": stop_reason,
        "failure_detail": failure_detail,
    }


def _pending_cleanup(
    root_relative: str,
    created: list[str],
    identities: dict[str, dict[str, int]],
) -> dict[str, Any]:
    return {
        "root": root_relative,
        "owner_marker": f"{root_relative}/{OWNER_MARKER_NAME}",
        "expected": _expected_basetemps(root_relative),
        "created": list(created),
        "removed": [],
        "remaining": list(created),
        "unexpected": [],
        "root_identity": identities["root_identity"],
        "owner_marker_identity": identities["owner_marker_identity"],
        "identity_verified": False,
        "root_removed": False,
        "completed": False,
        "diagnostic": "cleanup pending",
    }


def _initial_report(
    *,
    config: RunnerConfig,
    execution_started_at: str,
    source_files: list[dict[str, Any]],
    source_fingerprint: str | None,
    worktree_identity: str | None,
    environment: dict[str, Any],
    first_snapshot: dict[str, Any],
    created: list[str],
    cleanup_identities: dict[str, dict[str, int]],
) -> dict[str, Any]:
    report = {
        "schema_version": "2.0",
        "artifact_kind": ARTIFACT_KIND,
        "classification": CLASSIFICATION,
        "task_id": TASK_ID,
        "repository": REPOSITORY,
        "review_base_commit": REVIEW_BASE_COMMIT,
        "task_start_head": TASK_START_HEAD,
        "execution_project_revision": {
            "state": "dirty",
            "fingerprint_kind": FINGERPRINT_KIND,
            "fingerprint_sha256": source_fingerprint,
            "fingerprint_scope": [record["path"] for record in source_files],
            "worktree_identity_sha256": worktree_identity,
        },
        "execution_started_at_utc": execution_started_at,
        "execution_finished_at_utc": None,
        "completed": False,
        "source_files": source_files,
        "non_execution_task_paths": list(NON_EXECUTION_TASK_PATHS),
        "environment": environment,
        "expected_plan": dict(EXPECTED_PLAN),
        "report_persistence": {
            "report_path": REPORT_RELATIVE_PATH,
            "temporary_path": REPORT_TEMPORARY_PATH,
            "initial_write_mode": "same_directory_temp_then_replace",
            "replacement_mode": "same_directory_temp_then_replace",
            "fsync_file": True,
            "atomic_replace": True,
            "temporary_absent_at_finish": False,
        },
        "collection_identity": {
            "status": "pending",
            "records": [],
            "focused_node_ids": [],
            "full_suite_node_ids": [],
            "focused_count": None,
            "full_suite_count": None,
            "digest_kind": COLLECTION_DIGEST_KIND,
            "digest_sha256": None,
            "diagnostic": None,
        },
        "worktree_snapshots": [first_snapshot],
        "runs": [],
        "summary": {},
        "cleanup": _pending_cleanup(
            config.basetemp_root,
            created,
            cleanup_identities,
        ),
        "limitations": list(ROOT_LIMITATIONS),
    }
    report["summary"] = _summary(
        report,
        stop_reason="in_progress",
        failure_detail=None,
    )
    return report


def _process_overrides(
    *,
    root: Path,
    basetemp: str,
    phase: str,
    tool_paths: dict[str, str],
) -> dict[str, str]:
    pycache = (root / basetemp / "pycache").resolve()
    try:
        pycache.relative_to((root / basetemp).resolve())
    except ValueError as exc:
        raise RunnerError("pycache prefix escapes its task-owned basetemp") from exc
    overrides = {
        "PYTHONPYCACHEPREFIX": pycache.as_posix(),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    }
    if phase in {"collect_full_suite", "full_suite"}:
        overrides.update(tool_paths)
    return overrides


def _record_diagnostic(
    *,
    phase: str,
    interrupted: bool,
    returncode: int | None,
    after_snapshot: dict[str, Any],
    parse_diagnostic: str | None,
    pytest_summary: dict[str, Any] | None,
    expected_count: int | None,
) -> tuple[str, str | None]:
    reasons: list[str] = []
    if interrupted:
        reasons.append("pytest subprocess interrupted")
    elif returncode != 0:
        reasons.append(f"pytest exited with code {returncode}")
    if not after_snapshot["accepted"]:
        reasons.append(after_snapshot["diagnostic"] or "post-process snapshot rejected")
    if parse_diagnostic is not None:
        reasons.append(parse_diagnostic)
    if pytest_summary is not None and pytest_summary["parsed"]:
        for outcome in ("failed", "errors", "skipped", "xfailed", "xpassed"):
            if pytest_summary[outcome] != 0:
                reasons.append(f"pytest reported {pytest_summary[outcome]} {outcome}")
        if (
            expected_count is not None
            and pytest_summary["passed"] != expected_count
        ):
            reasons.append(
                f"pass count {pytest_summary['passed']} differs from collection count {expected_count}"
            )
    if interrupted:
        return "interrupted", "; ".join(reasons)
    if reasons:
        return "failed", "; ".join(reasons)
    return "passed", None


def run_evidence(
    config: RunnerConfig,
    *,
    process_runner: ProcessRunner = _default_process_runner,
    utc_now: Callable[[], str] = _utc_now,
    monotonic_ns: Callable[[], int] = time.monotonic_ns,
    monotonic: Callable[[], float] | None = None,
    git_checker: Callable[..., None] = verify_git_preconditions,
    git_probe_provider: GitProbeProvider = _default_git_probe_provider,
    tracked_path_provider: Callable[[Path], tuple[str, ...]] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Execute the exact v2 plan once and return ``(exit_code, report)``.

    ``tracked_path_provider`` is accepted only as a source-compatible legacy
    keyword for callers of v1; v2 never trusts it and always consumes raw Git
    probes.  Synthetic tests inject ``git_probe_provider`` instead.
    """

    del tracked_path_provider
    root = config.repository_root.resolve()
    if config.basetemp_root != DEFAULT_BASETEMP_ROOT:
        raise RunnerError("the v2 basetemp root is fixed by the evidence format")
    expected_report = (root / REPORT_RELATIVE_PATH).resolve()
    if config.report_path.resolve() != expected_report:
        raise RunnerError("report path must equal the fixed task dossier path")
    if not root.is_dir() or _is_link_like(root):
        raise RunnerError("repository root is missing or link-like")
    if _task_status_file(root) != _healthy_task_status():
        raise RunnerError("active TASK_STATUS.md must exist as a regular non-symlink file")
    _verify_inherited_environment()

    python_identity = _file_identity(config.python_executable, "Python")
    git_value = config.git_executable or shutil.which("git")
    git_identity = _file_identity(git_value, "Git")
    python_path = python_identity["resolved_path"]
    git_path = git_identity["resolved_path"]
    if set(config.tool_values) != set(TOOL_NAMES):
        raise RunnerError("exactly the four required tool overrides must be supplied")
    tool_identities = {
        name: _file_identity(config.tool_values[name], name) for name in TOOL_NAMES
    }
    tool_paths = {
        name: tool_identities[name]["resolved_path"] for name in TOOL_NAMES
    }
    environment = _environment_record(
        config,
        python_identity=python_identity,
        git_identity=git_identity,
        tool_identities=tool_identities,
    )
    if git_checker is verify_git_preconditions:
        git_checker(root, git_path)
    else:
        git_checker(root)

    report_path = expected_report
    temporary_path = report_path.with_name(report_path.name + ".tmp")
    if report_path.exists() or _is_link_like(report_path):
        raise FileExistsError(f"evidence report already exists: {report_path}")
    if temporary_path.exists() or _is_link_like(temporary_path):
        raise FileExistsError(f"evidence report temporary already exists: {temporary_path}")

    base: Path | None = None
    marker: Path | None = None
    cleanup_identities: dict[str, dict[str, int]] | None = None
    created: list[str] = []
    report: dict[str, Any] | None = None
    stop_reason = "in_progress"
    failure_detail: str | None = None
    interrupted = False
    execution_started_at = utc_now()
    clock_ns = monotonic_ns
    if monotonic is not None:
        clock_ns = lambda: int(monotonic() * 1_000_000_000)

    try:
        base, marker, cleanup_identities = _prepare_basetemp_root(
            root,
            config.basetemp_root,
        )
        plan = _process_plan()
        first = plan[0]
        _create_basetemp(
            root,
            base,
            marker,
            config.basetemp_root,
            first["basetemp"],
            cleanup_identities,
        )
        created.append(first["basetemp"])
        first_snapshot, first_sources = _capture_snapshot(
            root=root,
            root_relative=config.basetemp_root,
            git_path=git_path,
            label=f"before:1:{first['phase']}",
            sequence=1,
            expected_source_fingerprint=None,
            expected_execution_state_sha256=None,
            utc_now=utc_now,
            git_probe_provider=git_probe_provider,
        )
        source_fingerprint = first_snapshot["source_fingerprint_sha256"]
        bootstrap_failed = first_sources is None or source_fingerprint is None
        report = _initial_report(
            config=config,
            execution_started_at=execution_started_at,
            source_files=first_sources or [],
            source_fingerprint=source_fingerprint,
            worktree_identity=(
                None
                if bootstrap_failed
                else first_snapshot["execution_state_sha256"]
            ),
            environment=environment,
            first_snapshot=first_snapshot,
            created=created,
            cleanup_identities=cleanup_identities,
        )
        if bootstrap_failed or not first_snapshot["accepted"]:
            stop_reason = "failure"
            failure_detail = first_snapshot["diagnostic"] or "source bootstrap failed"
            report["summary"] = _summary(
                report,
                stop_reason=stop_reason,
                failure_detail=failure_detail,
            )
        _atomic_write_report(report_path, report, initial=True)

        for plan_index, specification in enumerate(plan):
            if stop_reason != "in_progress":
                break
            process_sequence = specification["process_sequence"]
            phase = specification["phase"]
            basetemp = specification["basetemp"]
            if plan_index == 0:
                before_snapshot = first_snapshot
            else:
                _create_basetemp(
                    root,
                    base,
                    marker,
                    config.basetemp_root,
                    basetemp,
                    cleanup_identities,
                )
                created.append(basetemp)
                report["cleanup"] = _pending_cleanup(
                    config.basetemp_root,
                    created,
                    cleanup_identities,
                )
                before_snapshot, _records = _capture_snapshot(
                    root=root,
                    root_relative=config.basetemp_root,
                    git_path=git_path,
                    label=f"before:{process_sequence}:{phase}",
                    sequence=2 * process_sequence - 1,
                    expected_source_fingerprint=source_fingerprint,
                    expected_execution_state_sha256=report["execution_project_revision"][
                        "worktree_identity_sha256"
                    ],
                    utc_now=utc_now,
                    git_probe_provider=git_probe_provider,
                )
                report["worktree_snapshots"].append(before_snapshot)
                _atomic_write_report(report_path, report, initial=False)
            if not before_snapshot["accepted"]:
                stop_reason = "failure"
                failure_detail = before_snapshot["diagnostic"]
                report["summary"] = _summary(
                    report,
                    stop_reason=stop_reason,
                    failure_detail=failure_detail,
                )
                _atomic_write_report(report_path, report, initial=False)
                break

            overrides = _process_overrides(
                root=root,
                basetemp=basetemp,
                phase=phase,
                tool_paths=tool_paths,
            )
            child_environment = _child_environment(overrides)
            argv = (
                _collection_command(python_path, phase, basetemp)
                if specification["collection"]
                else _run_command(python_path, phase, basetemp)
            )
            started_at = utc_now()
            started_ns = clock_ns()
            child_interrupted = False
            child_diagnostic: str | None = None
            try:
                result = process_runner(argv, cwd=root, env=child_environment)
                returncode: int | None = result.returncode
                stdout = bytes(result.stdout or b"")
                stderr = bytes(result.stderr or b"")
            except ProcessInterrupted as exc:
                child_interrupted = True
                returncode = exc.returncode
                stdout = bytes(exc.stdout)
                stderr = bytes(exc.stderr)
            except (OSError, ValueError) as exc:
                returncode = None
                stdout = b""
                stderr = b""
                child_diagnostic = f"{type(exc).__name__}: {exc}"
            finished_ns = clock_ns()
            finished_at = utc_now()
            after_snapshot, _records = _capture_snapshot(
                root=root,
                root_relative=config.basetemp_root,
                git_path=git_path,
                label=f"after:{process_sequence}:{phase}",
                sequence=2 * process_sequence,
                expected_source_fingerprint=source_fingerprint,
                expected_execution_state_sha256=report["execution_project_revision"][
                    "worktree_identity_sha256"
                ],
                utc_now=utc_now,
                git_probe_provider=git_probe_provider,
            )
            report["worktree_snapshots"].append(after_snapshot)

            common = {
                "process_sequence": process_sequence,
                "phase": phase,
                "argv": argv,
                "working_directory": root.as_posix(),
                "basetemp_path": basetemp,
                "environment_overrides": overrides,
                "started_at_utc": started_at,
                "finished_at_utc": finished_at,
                "wall_time_ns": max(0, finished_ns - started_ns),
                "exit_code": returncode,
                "stdout": _captured_stream(stdout),
                "stderr": _captured_stream(stderr),
                "before_snapshot_sequence": 2 * process_sequence - 1,
                "after_snapshot_sequence": 2 * process_sequence,
            }
            if specification["collection"]:
                node_ids, collected_count, parse_diagnostic = parse_collection_stdout(
                    stdout
                )
                if child_diagnostic is not None:
                    parse_diagnostic = child_diagnostic
                status, diagnostic = _record_diagnostic(
                    phase=phase,
                    interrupted=child_interrupted,
                    returncode=returncode,
                    after_snapshot=after_snapshot,
                    parse_diagnostic=parse_diagnostic,
                    pytest_summary=None,
                    expected_count=None,
                )
                if status == "passed" and phase == "collect_full_suite":
                    focused = report["collection_identity"]["focused_node_ids"]
                    if node_ids is None:
                        raise RunnerError("passed full collection lacks node IDs")
                    filtered = [
                        node_id
                        for node_id in node_ids
                        if node_id.startswith(FOCUSED_TEST_PATH + "::")
                    ]
                    if filtered != focused:
                        status = "failed"
                        diagnostic = (
                            "focused collection is not the ordered focused subset "
                            "of the full collection"
                        )
                record = {
                    **common,
                    "node_ids": node_ids or [],
                    "collected_count": collected_count,
                    "status": status,
                    "diagnostic": diagnostic,
                }
                report["collection_identity"]["records"].append(record)
                if status == "passed" and phase == "collect_focused":
                    report["collection_identity"]["focused_node_ids"] = node_ids
                    report["collection_identity"]["focused_count"] = collected_count
                elif status == "passed":
                    report["collection_identity"]["full_suite_node_ids"] = node_ids
                    report["collection_identity"]["full_suite_count"] = collected_count
                    report["collection_identity"]["digest_sha256"] = _collection_digest(
                        report["collection_identity"]["focused_node_ids"],
                        report["collection_identity"]["full_suite_node_ids"],
                    )
                    report["collection_identity"]["status"] = "completed"
                else:
                    report["collection_identity"]["status"] = status
                    report["collection_identity"]["diagnostic"] = diagnostic
            else:
                pytest_summary = parse_pytest_summary(stdout)
                expected_count = (
                    report["collection_identity"]["focused_count"]
                    if phase == "focused"
                    else report["collection_identity"]["full_suite_count"]
                )
                parse_diagnostic = (
                    pytest_summary["diagnostic"]
                    if not pytest_summary["parsed"]
                    else child_diagnostic
                )
                status, diagnostic = _record_diagnostic(
                    phase=phase,
                    interrupted=child_interrupted,
                    returncode=returncode,
                    after_snapshot=after_snapshot,
                    parse_diagnostic=parse_diagnostic,
                    pytest_summary=pytest_summary,
                    expected_count=expected_count,
                )
                record = {
                    **common,
                    "sequence": specification["sequence"],
                    "phase_index": specification["phase_index"],
                    "pytest_summary": pytest_summary,
                    "expected_pass_count": expected_count,
                    "status": status,
                    "diagnostic": diagnostic,
                }
                report["runs"].append(record)

            if status != "passed":
                stop_reason = "interrupted" if status == "interrupted" else "failure"
                failure_detail = diagnostic
                interrupted = status == "interrupted"
            report["cleanup"] = _pending_cleanup(
                config.basetemp_root,
                created,
                cleanup_identities,
            )
            report["summary"] = _summary(
                report,
                stop_reason=stop_reason,
                failure_detail=failure_detail,
            )
            _atomic_write_report(report_path, report, initial=False)

        if stop_reason == "in_progress":
            if (
                report["collection_identity"]["status"] == "completed"
                and len(report["runs"]) == 27
                and all(run["status"] == "passed" for run in report["runs"])
            ):
                stop_reason = "completed"
            else:
                stop_reason = "failure"
                failure_detail = "process plan ended without the exact 2+25+2 passing prefix"
    except KeyboardInterrupt:
        interrupted = True
        stop_reason = "interrupted"
        failure_detail = "runner interrupted outside a captured pytest child"
    except (OSError, RunnerError, ValueError) as exc:
        stop_reason = "failure"
        failure_detail = f"{type(exc).__name__}: {exc}"
        if report is None:
            if (
                base is not None
                and marker is not None
                and cleanup_identities is not None
            ):
                _cleanup_basetemps(
                    root=root,
                    base=base,
                    marker=marker,
                    root_relative=config.basetemp_root,
                    created=created,
                    expected_identities=cleanup_identities,
                )
            raise

    if (
        report is None
        or base is None
        or marker is None
        or cleanup_identities is None
    ):
        raise RunnerError("runner reached finalization without initialized evidence")
    cleanup = _cleanup_basetemps(
        root=root,
        base=base,
        marker=marker,
        root_relative=config.basetemp_root,
        created=created,
        expected_identities=cleanup_identities,
    )
    report["cleanup"] = cleanup
    if not cleanup["completed"]:
        cleanup_detail = cleanup["diagnostic"] or "task-owned cleanup incomplete"
        if failure_detail:
            failure_detail += "; " + cleanup_detail
        else:
            failure_detail = cleanup_detail
        stop_reason = "interrupted" if interrupted else "failure"
    plan_passed = (
        stop_reason == "completed"
        and report["collection_identity"]["status"] == "completed"
        and len(report["runs"]) == 27
        and all(run["status"] == "passed" for run in report["runs"])
    )
    report["completed"] = bool(plan_passed and cleanup["completed"])
    if report["completed"]:
        stop_reason = "completed"
        failure_detail = None
    elif stop_reason == "completed":
        stop_reason = "failure"
        failure_detail = failure_detail or "evidence did not complete"
    report["execution_finished_at_utc"] = utc_now()
    report["report_persistence"]["temporary_absent_at_finish"] = not (
        temporary_path.exists() or _is_link_like(temporary_path)
    )
    report["summary"] = _summary(
        report,
        stop_reason=stop_reason,
        failure_detail=failure_detail,
    )
    _atomic_write_report(report_path, report, initial=False)
    return (0 if report["completed"] else 1), report


def _tool_argument(
    parser: argparse.ArgumentParser,
    name: str,
    option: str,
) -> None:
    parser.add_argument(
        option,
        dest=name.lower(),
        default=os.environ.get(name),
        help=f"effective {name} executable (defaults to the {name} environment value)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="fixed final/partial v2 evidence report path",
    )
    parser.add_argument(
        "--basetemp-root",
        default=DEFAULT_BASETEMP_ROOT,
        help="fixed repository-relative task-owned pytest basetemp root",
    )
    _tool_argument(parser, "EG_CMAKE", "--eg-cmake")
    _tool_argument(parser, "EG_CXX", "--eg-cxx")
    _tool_argument(parser, "EG_NINJA", "--eg-ninja")
    _tool_argument(parser, "EG_MAKE", "--eg-make")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report_path = args.report
    if not report_path.is_absolute():
        report_path = REPOSITORY_ROOT / report_path
    config = RunnerConfig(
        repository_root=REPOSITORY_ROOT,
        report_path=report_path,
        basetemp_root=args.basetemp_root,
        tool_values={name: getattr(args, name.lower()) for name in TOOL_NAMES},
    )
    try:
        exit_code, report = run_evidence(config)
    except (FileExistsError, RunnerError, OSError, ValueError) as exc:
        print(
            json.dumps(
                {"ok": False, "error": f"{type(exc).__name__}: {exc}"},
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "ok": exit_code == 0,
                "completed": report["completed"],
                "report": report_path.resolve().as_posix(),
                "recorded_run_count": report["summary"]["recorded_run_count"],
                "stop_reason": report["summary"]["stop_reason"],
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
