#!/usr/bin/env python3
"""Generate auditable serial evidence for inspector timeout-test stability.

The runner performs exactly 25 focused pytest executions followed by two
complete-suite executions.  It records complete byte streams after every
attempt, never retries, and owns only one explicitly marked basetemp tree.
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
TASK_ID = "TASK-20260719__make_inspector_stability_evidence_auditable"
REPOSITORY = "falker47/erdos-gyarfas-p14"
BRANCH = "main"
REVIEW_BASE_COMMIT = "a7066e70b92d80be2d1772127f329c24222c1b41"
TASK_START_HEAD = "c71d66995ae6a36620a2aa8f938faf6d84fe1af7"
ARTIFACT_KIND = "inspector_timeout_stability_evidence"
CLASSIFICATION = "EMPIRICAL_OBSERVATION"
FINGERPRINT_KIND = "canonical_source_inventory_v1"
FOCUSED_TEST_PATH = "tests/unit/test_upstream_candidate_inspection.py"
DEFAULT_REPORT_PATH = (
    REPOSITORY_ROOT / "ops" / TASK_ID / "STABILITY_EVIDENCE.json"
)
DEFAULT_BASETEMP_ROOT = f"build/{TASK_ID}-basetemps"
OWNER_MARKER_NAME = ".inspector-timeout-stability-owner.json"
TOOL_NAMES = ("EG_CMAKE", "EG_CXX", "EG_NINJA", "EG_MAKE")
FORBIDDEN_INHERITED_CONTROLS = (
    "PYTEST_ADDOPTS",
    "PYTEST_PLUGINS",
    "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
    "PY_COLORS",
    "NO_COLOR",
    "FORCE_COLOR",
    "PYTHONPATH",
    "PYTHONWARNINGS",
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
SOURCE_PATHS = tuple(
    sorted(
        (
            "pyproject.toml",
            "schemas/inspector-timeout-stability-evidence.schema.json",
            "tests/unit/test_inspector_timeout_stability_evidence.py",
            FOCUSED_TEST_PATH,
            "tools/inspect_upstream_candidate.py",
            "tools/run_inspector_timeout_stability.py",
            "tools/validate_schemas.py",
            "tools/verify_inspector_timeout_stability.py",
        )
    )
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
EXPECTED_PLAN = {
    "focused_runs": 25,
    "full_suite_runs": 2,
    "serial": True,
    "retries": 0,
    "stop_on_first_failure": True,
}
ROOT_LIMITATIONS = [
    "This is bounded V1 engineering-test evidence.",
    "This is not an upstream reproduction.",
    "This is not exhaustive-search evidence.",
    "This is not a certificate.",
    "This establishes no theorem, counterexample, or pruning result.",
    "RFU-TEST-001 remains open until independent review.",
]
PYTEST_SUMMARY_LINE_RE = re.compile(
    r"^(?P<body>.+) in [0-9]+(?:\.[0-9]+)?s(?: \([^\r\n]+\))?$"
)
PYTEST_COUNT_RE = re.compile(
    r"^(?P<count>[0-9]+) (?P<kind>passed|failed|error|errors|skipped|xfailed|xpassed)$"
)


class RunnerError(RuntimeError):
    """A deterministic runner configuration or preservation failure."""


class ProcessInterrupted(KeyboardInterrupt):
    """A terminated child process whose captured output must be preserved."""

    def __init__(
        self,
        *,
        returncode: int | None,
        stdout: bytes,
        stderr: bytes,
    ) -> None:
        super().__init__("runner interrupted during subprocess execution")
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class ProcessResult(Protocol):
    returncode: int
    stdout: bytes
    stderr: bytes


ProcessRunner = Callable[..., ProcessResult]


@dataclass(frozen=True, slots=True)
class RunnerConfig:
    repository_root: Path
    report_path: Path
    basetemp_root: str
    tool_values: Mapping[str, str]
    python_executable: str = sys.executable


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


def _write_initial_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(_canonical_json_bytes(report))
        stream.flush()


def _replace_report(path: Path, report: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise RunnerError(f"refusing to replace through existing temporary file: {temporary}")
    try:
        with temporary.open("xb") as stream:
            stream.write(_canonical_json_bytes(report))
            stream.flush()
        os.replace(temporary, path)
    finally:
        if temporary.exists() and temporary.is_file() and not temporary.is_symlink():
            temporary.unlink()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _repository_path(root: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if (
        not relative_path
        or candidate.is_absolute()
        or candidate.as_posix() != relative_path
        or ".." in candidate.parts
    ):
        raise RunnerError(f"unsafe or noncanonical repository path: {relative_path!r}")
    resolved_root = root.resolve()
    unresolved = resolved_root / candidate
    resolved = unresolved.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise RunnerError(f"repository path escapes the checkout: {relative_path}") from exc
    return unresolved


def _git_tracked_paths(root: Path) -> tuple[str, ...]:
    process = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.resolve().as_posix()}",
            "ls-files",
            "-z",
        ],
        cwd=root,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        diagnostic = process.stderr.decode("utf-8", errors="replace").strip()
        raise RunnerError(f"cannot inventory tracked source files: {diagnostic}")
    values: list[str] = []
    for raw_path in process.stdout.split(b"\0"):
        if not raw_path:
            continue
        try:
            value = os.fsdecode(raw_path).replace("\\", "/")
        except UnicodeError as exc:
            raise RunnerError(f"tracked path is not decodable: {exc}") from exc
        values.append(value)
    return tuple(values)


def _execution_source_paths(
    root: Path,
    tracked_paths: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    tracked = set(
        _git_tracked_paths(root) if tracked_paths is None else tracked_paths
    )
    selected = (tracked - MUTABLE_NON_EXECUTION_PATHS) | set(SOURCE_PATHS)
    return tuple(sorted(selected))


def _source_inventory(
    root: Path, paths: tuple[str, ...] | None = None
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    selected_paths = _execution_source_paths(root) if paths is None else paths
    for relative_path in selected_paths:
        path = _repository_path(root, relative_path)
        if path.is_symlink() or not path.is_file():
            raise RunnerError(f"required source is not a regular file: {relative_path}")
        data = path.read_bytes()
        records.append(
            {
                "path": relative_path,
                "byte_length": len(data),
                "sha256": _sha256_bytes(data),
            }
        )
    return records


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


def _current_source_fingerprint(root: Path, paths: tuple[str, ...]) -> str:
    return _source_fingerprint(_source_inventory(root, paths))


def _resolve_file(value: str, label: str) -> Path:
    if not value:
        raise RunnerError(f"{label} is required")
    candidate = Path(value)
    if not candidate.is_absolute():
        located = shutil.which(value)
        if located is None:
            raise RunnerError(f"{label} cannot be resolved: {value!r}")
        candidate = Path(located)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise RunnerError(
            f"{label} cannot be resolved: {type(exc).__name__}: {exc}"
        ) from exc
    if resolved.is_symlink() or not resolved.is_file():
        raise RunnerError(f"{label} is not a regular file: {resolved}")
    try:
        resolved.open("rb").close()
    except OSError as exc:
        raise RunnerError(f"{label} is not readable: {type(exc).__name__}: {exc}") from exc
    return resolved


def _file_identity(value: str, label: str) -> dict[str, Any]:
    path = _resolve_file(value, label)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise RunnerError(
            f"{label} cannot be read: {type(exc).__name__}: {exc}"
        ) from exc
    return {
        "effective_value": path.as_posix(),
        "resolved_path": path.as_posix(),
        "readable": True,
        "byte_length": len(data),
        "sha256": _sha256_bytes(data),
        "limitation": None,
    }


def _environment_record(config: RunnerConfig) -> dict[str, Any]:
    missing = [name for name in TOOL_NAMES if not config.tool_values.get(name)]
    if missing:
        raise RunnerError(
            "missing required complete-suite tool values: " + ", ".join(missing)
        )
    machine = platform.machine().strip() or None
    processor = platform.processor().strip() or None
    cpu_count = os.cpu_count()
    limitations: list[str] = [
        "The complete process environment is intentionally neither captured nor "
        "forwarded; the child receives a minimal non-credential allowlist, and "
        "preflight rejected known pytest and inspector-test control variables.",
        "On Windows, interruption terminates and drains the direct pytest process; "
        "descendant-process termination relies on pytest and operating-system "
        "teardown and is not independently attested.",
    ]
    if machine is None:
        limitations.append("Machine identifier is unavailable.")
    if processor is None:
        limitations.append("Processor identifier is unavailable.")
    if cpu_count is None:
        limitations.append("CPU count is unavailable.")
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable": _file_identity(
            config.python_executable, "Python executable"
        ),
        "operating_system": platform.platform(),
        "architecture": platform.architecture()[0],
        "machine_identifier": machine,
        "processor_identifier": processor,
        "cpu_count": cpu_count,
        "working_directory": config.repository_root.resolve().as_posix(),
        "tool_overrides": {
            name: _file_identity(config.tool_values[name], name) for name in TOOL_NAMES
        },
        "limitations": limitations,
    }


def _verify_inherited_environment() -> None:
    present = [
        name for name in FORBIDDEN_INHERITED_CONTROLS if os.environ.get(name)
    ]
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
        raise RunnerError(f"Git read failed for {arguments!r}: {diagnostic}")
    return process.stdout.decode("utf-8", errors="strict").strip()


def verify_git_preconditions(root: Path) -> None:
    if _run_git(root, ["rev-parse", "--show-toplevel"]).replace("\\", "/") != (
        root.resolve().as_posix()
    ):
        raise RunnerError("repository root does not match the intended checkout")
    if _run_git(root, ["branch", "--show-current"]) != BRANCH:
        raise RunnerError(f"current branch must be {BRANCH}")
    if _run_git(root, ["rev-parse", "HEAD"]) != TASK_START_HEAD:
        raise RunnerError(f"HEAD must be exact task-start commit {TASK_START_HEAD}")
    if _run_git(root, ["rev-parse", f"{REVIEW_BASE_COMMIT}^{{commit}}"] ) != REVIEW_BASE_COMMIT:
        raise RunnerError("accepted review base does not resolve to the required commit")
    if _run_git(root, ["merge-base", REVIEW_BASE_COMMIT, TASK_START_HEAD]) != REVIEW_BASE_COMMIT:
        raise RunnerError("accepted review base is not an ancestor of task-start HEAD")
    origin = _run_git(root, ["remote", "get-url", "origin"])
    if origin not in {
        "https://github.com/falker47/erdos-gyarfas-p14",
        "https://github.com/falker47/erdos-gyarfas-p14.git",
        "git@github.com:falker47/erdos-gyarfas-p14.git",
    }:
        raise RunnerError(f"origin does not identify {REPOSITORY}: {origin!r}")
    if _run_git(root, ["diff", "--cached", "--name-only"]):
        raise RunnerError("index must be empty before evidence execution")


def _captured_stream(value: bytes) -> dict[str, Any]:
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "byte_length": len(value),
        "sha256": _sha256_bytes(value),
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
        text = stdout.decode("utf-8")
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


def _default_process_runner(
    argv: list[str], *, cwd: Path, env: dict[str, str]
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


def _run_plan() -> list[tuple[str, int, str]]:
    return [
        ("focused", index, f"{DEFAULT_BASETEMP_ROOT}/focused-{index:02d}")
        for index in range(1, 26)
    ] + [
        ("full_suite", index, f"{DEFAULT_BASETEMP_ROOT}/full-suite-{index:02d}")
        for index in range(1, 3)
    ]


def _command(python_path: str, phase: str, basetemp: str) -> list[str]:
    argv = [python_path, "-m", "pytest", "-q"]
    if phase == "focused":
        argv.append(FOCUSED_TEST_PATH)
    argv.extend(["--basetemp", basetemp])
    return argv


def _attempt_passed(
    *,
    phase: str,
    summary: dict[str, Any],
    exit_code: int | None,
    source_before: str,
    source_after: str | None,
    expected_source_fingerprint: str,
    first_full_pass_count: int | None,
) -> tuple[bool, str | None]:
    if source_before != expected_source_fingerprint:
        return False, "source fingerprint before the run differs from execution identity"
    if source_after is None:
        return False, "source fingerprint could not be acquired after the run"
    if source_after != expected_source_fingerprint:
        return False, "source fingerprint after the run differs from execution identity"
    if exit_code != 0:
        return False, f"pytest exited with code {exit_code}"
    if not summary["parsed"]:
        return False, f"pytest summary was not parsed: {summary['diagnostic']}"
    for outcome in ("failed", "errors", "skipped", "xfailed", "xpassed"):
        if summary[outcome] != 0:
            return False, f"pytest reported {outcome}={summary[outcome]}"
    if phase == "focused" and summary["passed"] != 31:
        return False, f"focused run reported {summary['passed']} passes, expected 31"
    if phase == "full_suite":
        if summary["passed"] < 299:
            return False, f"full suite reported {summary['passed']} passes, expected >=299"
        if first_full_pass_count is not None and summary["passed"] != first_full_pass_count:
            return False, (
                "full-suite pass counts differ: "
                f"first={first_full_pass_count} current={summary['passed']}"
            )
    return True, None


def _summary(
    runs: list[dict[str, Any]], *, stop_reason: str, failure_detail: str | None
) -> dict[str, Any]:
    return {
        "recorded_run_count": len(runs),
        "focused_run_count": sum(run["phase"] == "focused" for run in runs),
        "full_suite_run_count": sum(run["phase"] == "full_suite" for run in runs),
        "successful_run_count": sum(run["status"] == "passed" for run in runs),
        "failed_run_count": sum(run["status"] != "passed" for run in runs),
        "retries": 0,
        "focused_pass_counts": [
            run["pytest_summary"]["passed"]
            for run in runs
            if run["phase"] == "focused" and run["pytest_summary"]["parsed"]
        ],
        "full_suite_pass_counts": [
            run["pytest_summary"]["passed"]
            for run in runs
            if run["phase"] == "full_suite" and run["pytest_summary"]["parsed"]
        ],
        "stop_reason": stop_reason,
        "failure_detail": failure_detail,
    }


def _owner_marker_payload(root_relative: str) -> dict[str, str]:
    return {
        "task_id": TASK_ID,
        "owner": "tools/run_inspector_timeout_stability.py",
        "basetemp_root": root_relative,
    }


def _prepare_basetemp_root(root: Path, root_relative: str) -> tuple[Path, Path]:
    if root_relative != DEFAULT_BASETEMP_ROOT:
        raise RunnerError(
            f"basetemp root must be the fixed task-owned path {DEFAULT_BASETEMP_ROOT}"
        )
    resolved = _repository_path(root, root_relative)
    build_root = (root.resolve() / "build").resolve()
    try:
        resolved.relative_to(build_root)
    except ValueError as exc:
        raise RunnerError("task basetemp root must be inside repository/build") from exc
    if resolved.exists() or resolved.is_symlink():
        raise FileExistsError(f"refusing to reuse existing basetemp root: {resolved}")
    resolved.mkdir(parents=True, exist_ok=False)
    marker = resolved / OWNER_MARKER_NAME
    marker.write_bytes(_canonical_json_bytes(_owner_marker_payload(root_relative)))
    return resolved, marker


def _verify_owner_marker(marker: Path, root_relative: str) -> None:
    if marker.is_symlink() or not marker.is_file():
        raise RunnerError("task basetemp owner marker is absent or unsafe")
    try:
        observed = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RunnerError(f"task basetemp owner marker is invalid: {exc}") from exc
    if observed != _owner_marker_payload(root_relative):
        raise RunnerError("task basetemp owner marker does not match this runner")


def _cleanup_basetemps(
    *,
    repository_root: Path,
    root_relative: str,
    expected: list[str],
    marker: Path,
) -> tuple[list[str], list[str], str | None]:
    root = _repository_path(repository_root, root_relative)
    removed: list[str] = []
    try:
        _verify_owner_marker(marker, root_relative)
        expected_names = {Path(path).name for path in expected}
        allowed_names = expected_names | {OWNER_MARKER_NAME}
        observed_names = {path.name for path in root.iterdir()}
        unexpected = sorted(observed_names - allowed_names)
        if unexpected:
            raise RunnerError(f"unexpected entries in task basetemp root: {unexpected!r}")
        for relative_path in expected:
            child = _repository_path(repository_root, relative_path)
            if child.parent != root:
                raise RunnerError(f"cleanup child is outside task basetemp root: {relative_path}")
            if child.is_symlink():
                raise RunnerError(f"refusing to remove symlink basetemp: {relative_path}")
            if not child.exists():
                continue
            if not child.is_dir():
                raise RunnerError(f"refusing to remove non-directory basetemp: {relative_path}")
            def handle_remove_error(function, path, _error_info) -> None:
                os.chmod(path, stat.S_IWRITE)
                function(path)

            shutil.rmtree(child, onerror=handle_remove_error)
            removed.append(relative_path)
        _verify_owner_marker(marker, root_relative)
        marker.unlink()
        root.rmdir()
    except (OSError, RunnerError) as exc:
        remaining = [
            relative_path
            for relative_path in expected
            if _repository_path(repository_root, relative_path).exists()
            or _repository_path(repository_root, relative_path).is_symlink()
        ]
        return removed, remaining, f"{type(exc).__name__}: {exc}"
    return removed, [], None


def _initial_report(
    *,
    config: RunnerConfig,
    source_files: list[dict[str, Any]],
    source_fingerprint: str,
    environment: dict[str, Any],
    started_at: str,
    expected_basetemps: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
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
        },
        "execution_started_at_utc": started_at,
        "execution_finished_at_utc": None,
        "completed": False,
        "source_files": source_files,
        "environment": environment,
        "expected_plan": EXPECTED_PLAN,
        "runs": [],
        "summary": _summary([], stop_reason="in_progress", failure_detail=None),
        "cleanup": {
            "root": config.basetemp_root,
            "expected": expected_basetemps,
            "removed": [],
            "remaining": [],
            "completed": False,
        },
        "limitations": ROOT_LIMITATIONS,
    }


def run_evidence(
    config: RunnerConfig,
    *,
    process_runner: ProcessRunner = _default_process_runner,
    utc_now: Callable[[], str] = _utc_now,
    monotonic: Callable[[], float] = time.monotonic,
    git_checker: Callable[[Path], None] = verify_git_preconditions,
    tracked_path_provider: Callable[[Path], tuple[str, ...]] = _git_tracked_paths,
) -> tuple[int, dict[str, Any]]:
    """Run the fixed plan once and return ``(exit_code, final_report)``."""

    root = config.repository_root.resolve()
    report_path = config.report_path.resolve()
    try:
        report_path.relative_to(root)
    except ValueError as exc:
        raise RunnerError("evidence report must be inside the repository") from exc
    if report_path.exists() or report_path.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing evidence report: {report_path}")
    report_temporary = report_path.with_name(report_path.name + ".tmp")
    if report_temporary.exists() or report_temporary.is_symlink():
        raise FileExistsError(
            "refusing to use an occupied evidence-report temporary path: "
            f"{report_temporary}"
        )
    git_checker(root)
    _verify_inherited_environment()
    execution_source_paths = _execution_source_paths(
        root, tracked_path_provider(root)
    )
    source_files = _source_inventory(root, execution_source_paths)
    source_fingerprint = _source_fingerprint(source_files)
    environment = _environment_record(config)
    python_path = environment["python_executable"]["resolved_path"]
    plan = _run_plan()
    expected_basetemps = [item[2] for item in plan]
    basetemp_root, marker = _prepare_basetemp_root(root, config.basetemp_root)
    report = _initial_report(
        config=config,
        source_files=source_files,
        source_fingerprint=source_fingerprint,
        environment=environment,
        started_at=utc_now(),
        expected_basetemps=expected_basetemps,
    )
    try:
        _write_initial_report(report_path, report)
    except Exception:
        _cleanup_basetemps(
            repository_root=root,
            root_relative=config.basetemp_root,
            expected=expected_basetemps,
            marker=marker,
        )
        raise

    exit_code = 0
    stop_reason = "completed"
    failure_detail: str | None = None
    first_full_pass_count: int | None = None
    try:
        for sequence, (phase, phase_index, basetemp) in enumerate(plan, start=1):
            child = _repository_path(root, basetemp)
            if child.exists() or child.is_symlink():
                raise RunnerError(f"refusing to reuse basetemp: {basetemp}")
            child.mkdir(parents=False, exist_ok=False)
            argv = _command(python_path, phase, basetemp)
            environment_overrides = (
                {}
                if phase == "focused"
                else {
                    name: environment["tool_overrides"][name]["effective_value"]
                    for name in TOOL_NAMES
                }
            )
            process_environment = _child_environment(environment_overrides)
            source_before = _current_source_fingerprint(root, execution_source_paths)
            started_at = utc_now()
            started_monotonic = monotonic()
            run_status = "failed"
            process: ProcessResult | None = None
            try:
                process = process_runner(argv, cwd=root, env=process_environment)
                process_exit_code: int | None = process.returncode
                stdout = bytes(process.stdout)
                stderr = bytes(process.stderr)
                summary = parse_pytest_summary(stdout)
                try:
                    source_after = _current_source_fingerprint(
                        root, execution_source_paths
                    )
                except (OSError, RunnerError):
                    source_after = None
                passed, attempt_failure = _attempt_passed(
                    phase=phase,
                    summary=summary,
                    exit_code=process_exit_code,
                    source_before=source_before,
                    source_after=source_after,
                    expected_source_fingerprint=source_fingerprint,
                    first_full_pass_count=first_full_pass_count,
                )
                run_status = "passed" if passed else "failed"
            except ProcessInterrupted as exc:
                process_exit_code = exc.returncode
                stdout = exc.stdout
                stderr = exc.stderr
                summary = _unparsed_summary("runner interrupted during subprocess execution")
                try:
                    source_after = _current_source_fingerprint(
                        root, execution_source_paths
                    )
                except (OSError, RunnerError):
                    source_after = None
                attempt_failure = "runner interrupted during subprocess execution"
                run_status = "interrupted"
            except KeyboardInterrupt:
                if process is None:
                    process_exit_code = None
                    stdout = b""
                    stderr = b""
                    summary = _unparsed_summary(
                        "runner interrupted during subprocess execution"
                    )
                    attempt_failure = (
                        "runner interrupted during subprocess execution"
                    )
                else:
                    process_exit_code = process.returncode
                    stdout = bytes(process.stdout)
                    stderr = bytes(process.stderr)
                    summary = parse_pytest_summary(stdout)
                    attempt_failure = (
                        "runner interrupted after subprocess completion"
                    )
                try:
                    source_after = _current_source_fingerprint(
                        root, execution_source_paths
                    )
                except (OSError, RunnerError):
                    source_after = None
                run_status = "interrupted"
            except OSError as exc:
                process_exit_code = None
                stdout = b""
                stderr = str(exc).encode("utf-8", errors="replace")
                summary = _unparsed_summary(
                    f"subprocess launch failed: {type(exc).__name__}: {exc}"
                )
                try:
                    source_after = _current_source_fingerprint(
                        root, execution_source_paths
                    )
                except (OSError, RunnerError):
                    source_after = None
                attempt_failure = summary["diagnostic"]
            finished_monotonic = monotonic()
            finished_at = utc_now()
            run = {
                "sequence": sequence,
                "phase": phase,
                "phase_index": phase_index,
                "argv": argv,
                "basetemp_path": basetemp,
                "environment_overrides": environment_overrides,
                "started_at_utc": started_at,
                "finished_at_utc": finished_at,
                "wall_time_seconds": round(
                    max(0.0, finished_monotonic - started_monotonic), 9
                ),
                "exit_code": process_exit_code,
                "stdout": _captured_stream(stdout),
                "stderr": _captured_stream(stderr),
                "pytest_summary": summary,
                "source_fingerprint_before": source_before,
                "source_fingerprint_after": source_after,
                "status": run_status,
            }
            report["runs"].append(run)
            if run_status == "passed" and phase == "full_suite" and first_full_pass_count is None:
                first_full_pass_count = summary["passed"]
            if run_status == "passed":
                report["summary"] = _summary(
                    report["runs"], stop_reason="in_progress", failure_detail=None
                )
                _replace_report(report_path, report)
                continue
            exit_code = 1
            stop_reason = "interrupted" if run_status == "interrupted" else "failure"
            failure_detail = attempt_failure
            report["summary"] = _summary(
                report["runs"],
                stop_reason=stop_reason,
                failure_detail=failure_detail,
            )
            _replace_report(report_path, report)
            break
    except KeyboardInterrupt:
        exit_code = 1
        stop_reason = "interrupted"
        failure_detail = "runner interrupted outside subprocess execution"
    except (OSError, RunnerError) as exc:
        exit_code = 1
        stop_reason = "failure"
        failure_detail = f"{type(exc).__name__}: {exc}"

    cleanup_interrupted = False
    try:
        removed, remaining, cleanup_error = _cleanup_basetemps(
            repository_root=root,
            root_relative=config.basetemp_root,
            expected=expected_basetemps,
            marker=marker,
        )
    except KeyboardInterrupt:
        cleanup_interrupted = True
        removed = []
        remaining = [
            path
            for path in expected_basetemps
            if _repository_path(root, path).exists()
            or _repository_path(root, path).is_symlink()
        ]
        cleanup_error = "KeyboardInterrupt: runner interrupted during cleanup"
    cleanup_complete = cleanup_error is None and not remaining
    if (
        cleanup_complete
        and len(report["runs"]) == len(plan)
        and removed != expected_basetemps
    ):
        cleanup_complete = False
        cleanup_error = (
            "cleanup did not positively remove every completed-plan basetemp"
        )
    if not cleanup_complete:
        exit_code = 1
        stop_reason = "interrupted" if cleanup_interrupted else "failure"
        cleanup_detail = cleanup_error or (
            "cleanup did not remove every expected task-owned basetemp"
        )
        failure_detail = (
            cleanup_detail
            if failure_detail is None
            else failure_detail + "; " + cleanup_detail
        )
    try:
        final_source_fingerprint = _current_source_fingerprint(
            root, execution_source_paths
        )
    except (OSError, RunnerError) as exc:
        final_source_fingerprint = None
        final_source_error = f"{type(exc).__name__}: {exc}"
    else:
        final_source_error = None
    if final_source_fingerprint != source_fingerprint:
        exit_code = 1
        stop_reason = "failure"
        source_detail = final_source_error or (
            "final source fingerprint differs from the execution identity"
        )
        failure_detail = (
            source_detail
            if failure_detail is None
            else failure_detail + "; " + source_detail
        )
    all_runs_passed = len(report["runs"]) == 27 and all(
        run["status"] == "passed" for run in report["runs"]
    )
    if not all_runs_passed and exit_code == 0:
        exit_code = 1
        stop_reason = "failure"
        failure_detail = "the fixed 27-run plan did not complete"
    completed = exit_code == 0 and all_runs_passed and cleanup_complete
    report["execution_finished_at_utc"] = utc_now()
    report["completed"] = completed
    report["summary"] = _summary(
        report["runs"],
        stop_reason="completed" if completed else stop_reason,
        failure_detail=None if completed else failure_detail,
    )
    report["cleanup"] = {
        "root": config.basetemp_root,
        "expected": expected_basetemps,
        "removed": removed,
        "remaining": remaining,
        "completed": cleanup_complete,
    }
    try:
        _replace_report(report_path, report)
    except KeyboardInterrupt:
        report["completed"] = False
        report["summary"] = _summary(
            report["runs"],
            stop_reason="interrupted",
            failure_detail="runner interrupted while finalizing the report",
        )
        _replace_report(report_path, report)
        return 1, report
    return exit_code, report


def _tool_argument(
    parser: argparse.ArgumentParser, name: str, option: str
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
        help="final/partial evidence report path",
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
        tool_values={
            name: getattr(args, name.lower()) for name in TOOL_NAMES
        },
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
