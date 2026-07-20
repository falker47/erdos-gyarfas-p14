#!/usr/bin/env python3
"""Independently verify inspector timeout stability evidence.

This verifier deliberately does not import the evidence runner.  It validates
the schema and then recomputes every semantic invariant needed to accept the
bounded 25-focused-plus-2-full-suite engineering-test record.
"""

from __future__ import annotations

import argparse
import base64
import binascii
from datetime import UTC, datetime
import hashlib
import json
import ntpath
import os
from pathlib import Path
import posixpath
import re
import subprocess
import sys
from typing import Any

from jsonschema import FormatChecker
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_PATH = (
    REPOSITORY_ROOT
    / "ops"
    / "TASK-20260719__make_inspector_stability_evidence_auditable"
    / "STABILITY_EVIDENCE.json"
)
SCHEMA_PATH = (
    REPOSITORY_ROOT
    / "schemas"
    / "inspector-timeout-stability-evidence.schema.json"
)

REPOSITORY = "falker47/erdos-gyarfas-p14"
TASK_ID = "TASK-20260719__make_inspector_stability_evidence_auditable"
REVIEW_BASE_COMMIT = "a7066e70b92d80be2d1772127f329c24222c1b41"
TASK_START_HEAD = "c71d66995ae6a36620a2aa8f938faf6d84fe1af7"
ARTIFACT_KIND = "inspector_timeout_stability_evidence"
CLASSIFICATION = "EMPIRICAL_OBSERVATION"
FINGERPRINT_KIND = "canonical_source_inventory_v1"
TOOL_NAMES = ("EG_CMAKE", "EG_CXX", "EG_NINJA", "EG_MAKE")
FOCUSED_TEST_PATH = "tests/unit/test_upstream_candidate_inspection.py"
BASETEMP_ROOT = (
    "build/TASK-20260719__make_inspector_stability_evidence_auditable-basetemps"
)
REQUIRED_SOURCE_PATHS = frozenset(
    {
        "pyproject.toml",
        "schemas/inspector-timeout-stability-evidence.schema.json",
        "tests/unit/test_inspector_timeout_stability_evidence.py",
        FOCUSED_TEST_PATH,
        "tools/inspect_upstream_candidate.py",
        "tools/run_inspector_timeout_stability.py",
        "tools/validate_schemas.py",
        "tools/verify_inspector_timeout_stability.py",
    }
)
MUTABLE_NON_EXECUTION_PATHS = frozenset(
    {
        "CURRENT_STATUS.md",
        "research/NEXT_RESEARCH_STEPS.md",
        f"ops/{TASK_ID}/TASK_STATUS.md",
        f"ops/{TASK_ID}/TASK_LOG.md",
        f"ops/{TASK_ID}/EVIDENCE.md",
        f"ops/{TASK_ID}/STABILITY_EVIDENCE.json",
    }
)
EXPECTED_LIMITATIONS = (
    "This is bounded V1 engineering-test evidence.",
    "This is not an upstream reproduction.",
    "This is not exhaustive-search evidence.",
    "This is not a certificate.",
    "This establishes no theorem, counterexample, or pruning result.",
    "RFU-TEST-001 remains open until independent review.",
)
EXPECTED_ENVIRONMENT_LIMITATIONS = (
    "The complete process environment is intentionally neither captured nor "
    "forwarded; the child receives a minimal non-credential allowlist, and "
    "preflight rejected known pytest and inspector-test control variables.",
    "On Windows, interruption terminates and drains the direct pytest process; "
    "descendant-process termination relies on pytest and operating-system "
    "teardown and is not independently attested.",
)
EXPECTED_PLAN = {
    "focused_runs": 25,
    "full_suite_runs": 2,
    "serial": True,
    "retries": 0,
    "stop_on_first_failure": True,
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
WINDOWS_ABSOLUTE_PATH_RE = re.compile(
    r"^(?:[A-Za-z]:[\\/]|[\\/]{2}[^\\/]+[\\/][^\\/]+)"
)
PYTEST_SUMMARY_LINE_RE = re.compile(
    r"^(?P<body>.+) in [0-9]+(?:\.[0-9]+)?s(?: \([^\r\n]+\))?$"
)
PYTEST_COUNT_RE = re.compile(
    r"^(?P<count>[0-9]+) (?P<kind>passed|failed|error|errors|skipped|xfailed|xpassed)$"
)


class EvidenceVerificationError(ValueError):
    """A deterministic evidence-verification failure."""


def _fail(message: str) -> None:
    raise EvidenceVerificationError(message)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _reject_nonfinite_json_constant(value: str) -> None:
    _fail(f"non-finite JSON constant {value!r} is forbidden")


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
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_nonfinite_json_constant,
        )
    except EvidenceVerificationError:
        raise
    except UnicodeDecodeError as exc:
        _fail(f"report is not UTF-8: {exc}")
    except json.JSONDecodeError as exc:
        _fail(f"report is not strict JSON: {exc.msg} at line {exc.lineno}")
    except OSError as exc:
        _fail(f"report cannot be read: {type(exc).__name__}: {exc}")
    if not isinstance(value, dict):
        _fail("report root must be a JSON object")
    return raw, value


def _schema_errors(value: dict[str, Any], schema_path: Path) -> list[str]:
    try:
        _raw, schema = _load_json_object(schema_path)
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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _repository_file(root: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if (
        not relative_path
        or candidate.is_absolute()
        or candidate.as_posix() != relative_path
        or ".." in candidate.parts
    ):
        _fail(f"unsafe or noncanonical repository path: {relative_path!r}")
    resolved_root = root.resolve()
    unresolved = resolved_root / candidate
    resolved = unresolved.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        _fail(f"repository path escapes the checkout: {relative_path!r}")
    if unresolved.is_symlink() or not unresolved.is_file():
        _fail(f"source file is not a regular file: {relative_path}")
    return unresolved


def _source_fingerprint(records: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(record["path"].encode("utf-8"))
        digest.update(b"\t")
        digest.update(str(record["byte_length"]).encode("ascii"))
        digest.update(b"\t")
        digest.update(record["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _verify_sources(
    report: dict[str, Any],
    root: Path,
    expected_paths: tuple[str, ...] | None,
) -> str:
    records = report["source_files"]
    paths = [record["path"] for record in records]
    if paths != sorted(paths):
        _fail("source_files must be ordered lexicographically by path")
    if len(paths) != len(set(paths)):
        _fail("source_files contains a duplicate path")
    missing_required = sorted(REQUIRED_SOURCE_PATHS - set(paths))
    if missing_required:
        _fail(f"source_files omits required paths: {missing_required!r}")
    if expected_paths is not None and paths != list(expected_paths):
        _fail(
            "source_files scope does not equal all tracked execution inputs "
            "plus the required task sources"
        )

    for record in records:
        path = _repository_file(root, record["path"])
        data = path.read_bytes()
        observed_size = len(data)
        observed_hash = _sha256_bytes(data)
        if observed_size != record["byte_length"]:
            _fail(
                f"source byte length mismatch for {record['path']}: "
                f"recorded={record['byte_length']} observed={observed_size}"
            )
        if observed_hash != record["sha256"]:
            _fail(
                f"source SHA-256 mismatch for {record['path']}: "
                f"recorded={record['sha256']} observed={observed_hash}"
            )

    revision = report["execution_project_revision"]
    if revision["state"] != "dirty":
        _fail("execution project revision must identify the dirty task state")
    if revision["fingerprint_kind"] != FINGERPRINT_KIND:
        _fail("unsupported execution project fingerprint kind")
    if revision["fingerprint_scope"] != paths:
        _fail("execution fingerprint scope must equal the ordered source inventory")
    observed_fingerprint = _source_fingerprint(records)
    if observed_fingerprint != revision["fingerprint_sha256"]:
        _fail(
            "execution source fingerprint mismatch: "
            f"recorded={revision['fingerprint_sha256']} "
            f"observed={observed_fingerprint}"
        )
    return observed_fingerprint


def _normalized_absolute_path(value: str, label: str) -> str:
    if "\x00" in value:
        _fail(f"{label} contains a null byte")
    if WINDOWS_ABSOLUTE_PATH_RE.match(value):
        if not ntpath.isabs(value):
            _fail(f"{label} is not an absolute path: {value!r}")
        return ntpath.normpath(value).replace("\\", "/")
    if not posixpath.isabs(value):
        _fail(f"{label} is not an absolute path: {value!r}")
    return posixpath.normpath(value)


def _verify_file_identity(
    identity: dict[str, Any], label: str, *, rehash: bool
) -> str:
    if not identity["readable"]:
        _fail(f"{label} was not recorded as readable")
    if identity["limitation"] is not None:
        _fail(f"{label} has an unexpected acquisition limitation")
    normalized_path = _normalized_absolute_path(
        identity["resolved_path"], f"{label} resolved_path"
    )
    if identity["effective_value"] != normalized_path:
        _fail(
            f"{label} effective value resolves to {identity['effective_value']!r}, "
            f"not normalized recorded path {normalized_path!r}"
        )
    if not rehash:
        return normalized_path

    path = Path(normalized_path)
    if path.is_symlink() or not path.is_file():
        _fail(f"{label} is no longer a regular readable file: {path}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        _fail(f"{label} cannot be read: {type(exc).__name__}: {exc}")
    if len(data) != identity["byte_length"]:
        _fail(f"{label} byte length does not match the recorded environment")
    if _sha256_bytes(data) != identity["sha256"]:
        _fail(f"{label} SHA-256 does not match the recorded environment")
    return normalized_path


def _verify_environment(
    report: dict[str, Any], root: Path, *, rehash_environment: bool
) -> str:
    environment = report["environment"]
    if tuple(
        environment["limitations"][: len(EXPECTED_ENVIRONMENT_LIMITATIONS)]
    ) != EXPECTED_ENVIRONMENT_LIMITATIONS:
        _fail(
            "environment limitations omit the exact child-environment and "
            "interruption trust boundary"
        )
    working_directory = _normalized_absolute_path(
        environment["working_directory"], "environment working_directory"
    )
    if rehash_environment and Path(working_directory).resolve() != root.resolve():
        _fail("environment working_directory is not the repository root")
    python_path = _verify_file_identity(
        environment["python_executable"],
        "Python executable",
        rehash=rehash_environment,
    )
    overrides = environment["tool_overrides"]
    if set(overrides) != set(TOOL_NAMES):
        _fail("environment tool_overrides must contain exactly the four required tools")
    for name in TOOL_NAMES:
        _verify_file_identity(overrides[name], name, rehash=rehash_environment)
    limitation_text = " ".join(environment["limitations"]).lower()
    for field, words in (
        ("machine_identifier", ("machine", "identifier")),
        ("processor_identifier", ("processor", "identifier")),
        ("cpu_count", ("cpu", "count")),
    ):
        if environment[field] is None and not all(word in limitation_text for word in words):
            _fail(f"environment limitations do not explain unavailable {field}")
    return python_path


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
    observed_hash = _sha256_bytes(decoded)
    if observed_hash != stream["sha256"]:
        _fail(
            f"{label} SHA-256 mismatch: recorded={stream['sha256']} "
            f"observed={observed_hash}"
        )
    return decoded


def _parse_pytest_summary(stdout: bytes, label: str) -> dict[str, Any]:
    try:
        text = stdout.decode("utf-8")
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
        parts = match.group("body").split(", ")
        valid = True
        seen: set[str] = set()
        for part in parts:
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
        _fail(
            f"{label} must contain exactly one independently parseable pytest "
            f"summary line, observed {len(candidates)}"
        )
    return {
        "parsed": True,
        **candidates[0],
        "diagnostic": None,
    }


def _parse_timestamp(value: str, label: str) -> datetime:
    if not isinstance(value, str):
        _fail(f"{label} must be a non-null UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        _fail(f"{label} is not an RFC 3339 timestamp: {exc}")
    if parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
        _fail(f"{label} is not UTC")
    return parsed


def _expected_argv(
    *, python_path: str, phase: str, basetemp_path: str
) -> list[str]:
    command = [python_path, "-m", "pytest", "-q"]
    if phase == "focused":
        command.append(FOCUSED_TEST_PATH)
    command.extend(["--basetemp", basetemp_path])
    return command


def _verify_runs(
    report: dict[str, Any], source_fingerprint: str, python_path: str, root: Path
) -> None:
    if report["expected_plan"] != EXPECTED_PLAN:
        _fail("expected_plan is not the exact required 25+2 serial no-retry plan")
    if report["completed"] is not True:
        _fail("report completed must be true")

    runs = report["runs"]
    if len(runs) != 27:
        _fail(f"expected exactly 27 run records, observed {len(runs)}")
    sequences = [run["sequence"] for run in runs]
    if sequences != list(range(1, 28)):
        _fail(f"run sequences must be exactly 1..27, observed {sequences!r}")
    expected_phases = ["focused"] * 25 + ["full_suite"] * 2
    phases = [run["phase"] for run in runs]
    if phases != expected_phases:
        _fail("runs must contain 25 focused records followed by 2 full-suite records")
    phase_indices = [run["phase_index"] for run in runs]
    if phase_indices != list(range(1, 26)) + [1, 2]:
        _fail("phase-local run indices are malformed")

    commands = [tuple(run["argv"]) for run in runs]
    if len(commands) != len(set(commands)):
        _fail("run records contain a duplicate command argument vector")
    basetemps = [run["basetemp_path"] for run in runs]
    if len(basetemps) != len(set(basetemps)):
        _fail("run records contain a duplicate basetemp path")
    expected_basetemps = [
        f"{BASETEMP_ROOT}/focused-{index:02d}" for index in range(1, 26)
    ] + [
        f"{BASETEMP_ROOT}/full-suite-{index:02d}" for index in range(1, 3)
    ]
    if basetemps != expected_basetemps:
        _fail("run basetemps do not use the deterministic task-owned naming plan")

    execution_started = _parse_timestamp(
        report["execution_started_at_utc"], "execution_started_at_utc"
    )
    execution_finished = _parse_timestamp(
        report["execution_finished_at_utc"], "execution_finished_at_utc"
    )
    if execution_finished < execution_started:
        _fail("execution finished before it started")
    previous_finish = execution_started
    focused_counts: list[int] = []
    full_counts: list[int] = []
    effective_tools = {
        name: report["environment"]["tool_overrides"][name]["effective_value"]
        for name in TOOL_NAMES
    }

    for index, run in enumerate(runs, start=1):
        label = f"run {index}"
        started = _parse_timestamp(run["started_at_utc"], f"{label} started_at_utc")
        finished = _parse_timestamp(
            run["finished_at_utc"], f"{label} finished_at_utc"
        )
        if started < previous_finish:
            _fail(f"{label} overlaps or precedes the prior serial run")
        if finished < started:
            _fail(f"{label} finished before it started")
        previous_finish = finished
        if run["wall_time_seconds"] < 0:
            _fail(f"{label} has a negative wall time")
        if run["source_fingerprint_before"] != source_fingerprint:
            _fail(f"{label} source fingerprint before execution is wrong")
        if run["source_fingerprint_after"] != source_fingerprint:
            _fail(f"{label} source fingerprint after execution is wrong")
        expected_argv = _expected_argv(
            python_path=python_path,
            phase=run["phase"],
            basetemp_path=run["basetemp_path"],
        )
        if run["argv"] != expected_argv:
            _fail(f"{label} command is not the exact required pytest invocation")
        expected_overrides = {} if run["phase"] == "focused" else effective_tools
        if run["environment_overrides"] != expected_overrides:
            _fail(f"{label} effective environment overrides are incorrect")
        stdout = _decode_stream(run["stdout"], f"{label} stdout")
        _decode_stream(run["stderr"], f"{label} stderr")
        if run["exit_code"] != 0:
            _fail(f"{label} exit code is nonzero: {run['exit_code']}")
        if run["status"] != "passed":
            _fail(f"{label} final status is not passed")
        parsed = run["pytest_summary"]
        if parsed["parsed"] is not True:
            _fail(f"{label} pytest summary was not parsed")
        independently_parsed = _parse_pytest_summary(stdout, label)
        if parsed != independently_parsed:
            _fail(f"{label} parsed pytest summary disagrees with embedded stdout")
        if parsed["diagnostic"] is not None:
            _fail(f"{label} successful pytest summary has a diagnostic")
        for outcome in ("failed", "errors", "skipped", "xfailed", "xpassed"):
            if parsed[outcome] != 0:
                _fail(f"{label} has non-passing pytest outcome {outcome}={parsed[outcome]}")
        if run["phase"] == "focused":
            if parsed["passed"] != 31:
                _fail(f"{label} focused pass count is {parsed['passed']}, expected 31")
            focused_counts.append(parsed["passed"])
        else:
            if parsed["passed"] < 299:
                _fail(
                    f"{label} full-suite pass count is {parsed['passed']}, expected at least 299"
                )
            full_counts.append(parsed["passed"])

    if previous_finish > execution_finished:
        _fail("execution finish timestamp precedes the final run finish")
    if len(full_counts) != 2 or full_counts[0] != full_counts[1]:
        _fail(f"full-suite pass counts are inconsistent: {full_counts!r}")

    summary = report["summary"]
    expected_summary = {
        "recorded_run_count": 27,
        "focused_run_count": 25,
        "full_suite_run_count": 2,
        "successful_run_count": 27,
        "failed_run_count": 0,
        "retries": 0,
        "focused_pass_counts": focused_counts,
        "full_suite_pass_counts": full_counts,
        "stop_reason": "completed",
        "failure_detail": None,
    }
    if summary != expected_summary:
        _fail("summary does not equal values recomputed from the 27 run records")

    cleanup = report["cleanup"]
    if cleanup["root"] != BASETEMP_ROOT:
        _fail(
            f"cleanup root is not the fixed task-owned root: {cleanup['root']!r}"
        )
    if cleanup["expected"] != basetemps:
        _fail("cleanup expected paths must equal run basetemps in sequence order")
    if cleanup["removed"] != basetemps:
        _fail("cleanup removed paths do not prove removal of every run basetemp")
    if cleanup["remaining"]:
        _fail(f"task-owned basetemps remain: {cleanup['remaining']!r}")
    if cleanup["completed"] is not True:
        _fail("task-owned basetemp cleanup is not complete")
    cleanup_root = (root / cleanup["root"]).resolve()
    for basetemp in basetemps:
        basetemp_path = (root / basetemp).resolve()
        if basetemp_path.parent != cleanup_root:
            _fail(f"run basetemp is outside the recorded task root: {basetemp}")
        if basetemp_path.exists() or basetemp_path.is_symlink():
            _fail(f"run basetemp still exists: {basetemp}")
    if cleanup_root.exists() or cleanup_root.is_symlink():
        _fail(f"task-owned basetemp root still exists: {cleanup_root}")


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
    return process.stdout.decode("utf-8", errors="strict").strip()


def _tracked_execution_source_paths(root: Path) -> tuple[str, ...]:
    command = [
        "git",
        "-c",
        f"safe.directory={root.resolve().as_posix()}",
        "ls-files",
        "-z",
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
        _fail(f"cannot inventory tracked source files: {diagnostic}")
    tracked: set[str] = set()
    for raw_path in process.stdout.split(b"\0"):
        if not raw_path:
            continue
        try:
            relative_path = os.fsdecode(raw_path).replace("\\", "/")
        except UnicodeError as exc:
            _fail(f"tracked path cannot be decoded: {exc}")
        candidate = Path(relative_path)
        if (
            candidate.is_absolute()
            or candidate.as_posix() != relative_path
            or ".." in candidate.parts
        ):
            _fail(f"Git returned an unsafe tracked path: {relative_path!r}")
        if relative_path in tracked:
            _fail(f"Git returned a duplicate tracked path: {relative_path!r}")
        tracked.add(relative_path)
    return tuple(
        sorted((tracked - MUTABLE_NON_EXECUTION_PATHS) | REQUIRED_SOURCE_PATHS)
    )


def _verify_git_checkout(root: Path) -> None:
    task_start = _run_git(root, ["rev-parse", f"{TASK_START_HEAD}^{{commit}}"])
    if task_start != TASK_START_HEAD:
        _fail("task-start HEAD does not resolve to the required commit")
    base = _run_git(root, ["rev-parse", f"{REVIEW_BASE_COMMIT}^{{commit}}"])
    if base != REVIEW_BASE_COMMIT:
        _fail("accepted review base does not resolve to the required commit")
    if _run_git(root, ["merge-base", REVIEW_BASE_COMMIT, TASK_START_HEAD]) != REVIEW_BASE_COMMIT:
        _fail("accepted review base is not an ancestor of task-start HEAD")
    current_head = _run_git(root, ["rev-parse", "HEAD"])
    if _run_git(root, ["merge-base", TASK_START_HEAD, current_head]) != TASK_START_HEAD:
        _fail(
            "current checkout HEAD is neither task-start HEAD nor its descendant: "
            f"{current_head}"
        )


def verify_report(
    report_path: Path = DEFAULT_REPORT_PATH,
    *,
    repository_root: Path = REPOSITORY_ROOT,
    schema_path: Path | None = None,
    verify_git: bool = True,
    rehash_environment: bool = False,
) -> dict[str, Any]:
    """Verify one report and return a compact independently recomputed result."""

    root = repository_root.resolve()
    selected_schema = (
        schema_path.resolve()
        if schema_path is not None
        else root / "schemas" / "inspector-timeout-stability-evidence.schema.json"
    )
    raw, report = _load_json_object(report_path)
    canonical = _canonical_json_bytes(report)
    if raw != canonical:
        _fail("report is not canonical sorted indented UTF-8 JSON with one final LF")
    errors = _schema_errors(report, selected_schema)
    if errors:
        _fail(f"schema validation failed: {errors[0]}")

    exact_fields = {
        "schema_version": "1.0",
        "artifact_kind": ARTIFACT_KIND,
        "classification": CLASSIFICATION,
        "task_id": TASK_ID,
        "repository": REPOSITORY,
        "review_base_commit": REVIEW_BASE_COMMIT,
        "task_start_head": TASK_START_HEAD,
    }
    for field, expected in exact_fields.items():
        if report[field] != expected:
            _fail(f"{field} mismatch: expected {expected!r}, observed {report[field]!r}")
    if tuple(report["limitations"]) != EXPECTED_LIMITATIONS:
        _fail("report limitations do not state the exact V1 and non-mathematical boundary")
    if verify_git:
        _verify_git_checkout(root)
    expected_source_paths = (
        _tracked_execution_source_paths(root) if verify_git else None
    )
    source_fingerprint = _verify_sources(
        report, root, expected_source_paths
    )
    python_path = _verify_environment(
        report, root, rehash_environment=rehash_environment
    )
    _verify_runs(report, source_fingerprint, python_path, root)

    full_counts = report["summary"]["full_suite_pass_counts"]
    return {
        "ok": True,
        "report": report_path.resolve().as_posix(),
        "report_byte_length": len(raw),
        "report_sha256": _sha256_bytes(raw),
        "source_fingerprint_sha256": source_fingerprint,
        "focused_runs": 25,
        "focused_passes_each": 31,
        "full_suite_runs": 2,
        "full_suite_passes_each": full_counts[0],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report",
        nargs="?",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="evidence report (defaults to the current task dossier)",
    )
    parser.add_argument(
        "--rehash-environment",
        action="store_true",
        help=(
            "require the recorded Python and tool paths to exist locally and "
            "match their recorded byte lengths and SHA-256 hashes"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report_path = args.report
    if not report_path.is_absolute():
        report_path = REPOSITORY_ROOT / report_path
    try:
        result = verify_report(
            report_path, rehash_environment=args.rehash_environment
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
