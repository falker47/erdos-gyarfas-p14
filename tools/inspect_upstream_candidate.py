#!/usr/bin/env python3
"""Freeze and independently inspect surprising tiny upstream outcomes.

The upstream process is treated as untrusted.  Its raw byte streams are
persisted before this module starts any graph parsing or predicate work.  Exit
100 inspection runs in a separate Python process with a parent-enforced,
cross-platform timeout.  These records are engineering diagnostics only and
never accept a counterexample or establish a mathematical result.
"""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Sequence

from jsonschema import FormatChecker
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VERIFIER_ROOT = REPOSITORY_ROOT / "verifier"
if str(VERIFIER_ROOT) not in sys.path:
    sys.path.insert(0, str(VERIFIER_ROOT))

from egverify.graph import Graph, GraphFormatError  # noqa: E402
from egverify.predicates import (  # noqa: E402
    find_exact_cycle,
    find_induced_path,
    minimum_degree,
    relevant_power_of_two_lengths,
)

try:
    from ._common import (  # type: ignore[import-not-found]
        load_upstream_provenance,
        repository_state,
        sha256_file,
    )
except ImportError:  # pragma: no cover - direct script execution
    from _common import load_upstream_provenance, repository_state, sha256_file


RECORD_SCHEMA_VERSION = "1.0"
OUTCOME_ARTIFACT_KIND = "surprising_process_outcome"
INSPECTION_ARTIFACT_KIND = "surprising_process_outcome_inspection"
CLASSIFICATION = "EMPIRICAL_OBSERVATION"
DEFAULT_LOG_PREFIX_BYTES = 16384
RECORD_SCHEMA_PATH = REPOSITORY_ROOT / "schemas" / "surprising-process-outcome.schema.json"

_TERMINATION_REASONS = frozenset({"exited", "signal", "timeout", "spawn-error"})
_UPSTREAM_INTEGER_TOKEN = r"[+-]?\d+"
_UPSTREAM_ADJACENCY_LINE = re.compile(
    rf"(?P<label>{_UPSTREAM_INTEGER_TOKEN}): "
    rf"(?P<neighbors>(?:{_UPSTREAM_INTEGER_TOKEN} )*)\Z"
)
_CANONICAL_VERTEX_LABEL = re.compile(r"(?:0|[1-9]\d*)\Z")


class UpstreamAdjacencyFormatError(ValueError):
    """A deterministic interface-adapter error for upstream graph text."""

    def __init__(self, code: str, location: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.location = location
        self.message = message

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "location": self.location,
            "message": self.message,
        }


class CandidateInspectionError(ValueError):
    """A stable error at the frozen-outcome inspection boundary."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True, slots=True)
class CapturedProcessOutcome:
    termination_reason: str
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    launcher_error: str | None = None


@dataclass(frozen=True, slots=True)
class InvocationIdentity:
    command: tuple[str, ...]
    executable_path: str
    executable_sha256: str | None
    project_commit: str | None
    project_revision: str
    upstream_commit: str | None
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FrozenOutcomeArtifacts:
    record_path: Path
    stdout_path: Path
    stderr_path: Path
    inspection_path: Path
    record: dict[str, Any]
    record_sha256: str


def _stable_json_bytes(value: Any) -> bytes:
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


def _write_json_exclusive(path: Path, value: Any) -> None:
    data = _stable_json_bytes(value)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()


def _write_bytes_exclusive(path: Path, value: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(value)
        stream.flush()


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise CandidateInspectionError(
                "duplicate_json_key", f"duplicate JSON key {key!r}"
            )
        value[key] = item
    return value


def _reject_nonfinite_json_constant(value: str) -> None:
    raise CandidateInspectionError(
        "nonfinite_json_number", f"non-finite JSON number {value!r} is forbidden"
    )


def _validate_record_schema(value: dict[str, Any]) -> None:
    """Validate a final artifact against the repository schema before writing."""

    try:
        schema = json.loads(
            RECORD_SCHEMA_PATH.read_bytes(),
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_nonfinite_json_constant,
        )
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
    except CandidateInspectionError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, SchemaError) as exc:
        raise CandidateInspectionError(
            "artifact_schema_unavailable",
            f"surprising-outcome schema could not be loaded: {type(exc).__name__}: {exc}",
        ) from exc
    if errors:
        error = errors[0]
        location = "$" + "".join(f"[{part!r}]" for part in error.absolute_path)
        raise CandidateInspectionError(
            "artifact_schema_validation_error",
            f"{location}: {error.message}",
        )


def _validate_process_outcome(outcome: CapturedProcessOutcome) -> None:
    reason = outcome.termination_reason
    code = outcome.exit_code
    is_integer = isinstance(code, int) and not isinstance(code, bool)
    if reason not in _TERMINATION_REASONS:
        raise ValueError(f"unsupported termination reason: {reason!r}")
    if reason == "exited" and (not is_integer or code < 0):
        raise ValueError("an exited outcome requires a nonnegative exit code")
    if reason == "signal" and (not is_integer or code >= 0):
        raise ValueError("a signal outcome requires a negative exit code")
    if reason in {"timeout", "spawn-error"} and code is not None:
        raise ValueError(f"a {reason} outcome requires a null exit code")
    if reason == "spawn-error" and not outcome.launcher_error:
        raise ValueError("a spawn-error outcome requires launcher_error")
    if reason != "spawn-error" and outcome.launcher_error is not None:
        raise ValueError("launcher_error is valid only for spawn-error")


def is_ordinary_completion(outcome: CapturedProcessOutcome) -> bool:
    _validate_process_outcome(outcome)
    return outcome.termination_reason == "exited" and outcome.exit_code == 0


def collect_invocation_identity(command: Sequence[str]) -> InvocationIdentity:
    """Collect stable process identity before invoking the upstream program."""

    if not command or not all(isinstance(item, str) for item in command):
        raise ValueError("command must be a nonempty sequence of strings")
    executable = Path(command[0]).resolve()
    limitations: list[str] = []
    executable_sha256: str | None
    if executable.is_file():
        executable_sha256 = sha256_file(executable)
    else:
        executable_sha256 = None
        limitations.append(
            "Executable SHA-256 is unavailable because the command path is not a file."
        )

    try:
        project_commit, _status, project_revision = repository_state()
    except (OSError, ValueError) as exc:
        project_commit = None
        project_revision = "unavailable"
        limitations.append(
            "Project revision is unavailable: "
            f"{type(exc).__name__}: {exc}"
        )

    try:
        provenance = load_upstream_provenance()
        raw_upstream_commit = provenance.get("resolved_commit")
        upstream_commit = (
            raw_upstream_commit if isinstance(raw_upstream_commit, str) else None
        )
        if upstream_commit is None:
            limitations.append(
                "Upstream commit is unavailable in the recorded provenance."
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        upstream_commit = None
        limitations.append(
            "Upstream commit is unavailable: "
            f"{type(exc).__name__}: {exc}"
        )

    return InvocationIdentity(
        command=tuple(command),
        executable_path=executable.as_posix(),
        executable_sha256=executable_sha256,
        project_commit=project_commit,
        project_revision=project_revision,
        upstream_commit=upstream_commit,
        limitations=tuple(limitations),
    )


def _artifact_paths(directory: Path, k: int) -> tuple[Path, Path, Path, Path]:
    stem = f"tiny-k{k}-surprising-outcome"
    return (
        directory / f"{stem}.json",
        directory / f"{stem}.stdout.bin",
        directory / f"{stem}.stderr.bin",
        directory / f"{stem}.inspection.json",
    )


def freeze_surprising_process_outcome(
    *,
    artifact_directory: Path,
    k: int,
    outcome: CapturedProcessOutcome,
    identity: InvocationIdentity,
    upstream_timeout_seconds: float,
    inspection_timeout_seconds: float,
) -> FrozenOutcomeArtifacts:
    """Persist raw streams and an immutable outcome record before inspection."""

    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    _validate_process_outcome(outcome)
    if is_ordinary_completion(outcome):
        raise ValueError("ordinary completion must not create a surprising artifact")
    for name, value in (
        ("upstream_timeout_seconds", upstream_timeout_seconds),
        ("inspection_timeout_seconds", inspection_timeout_seconds),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or value <= 0
        ):
            raise ValueError(f"{name} must be positive")

    artifact_directory.mkdir(parents=True, exist_ok=True)
    record_path, stdout_path, stderr_path, inspection_path = _artifact_paths(
        artifact_directory, k
    )
    for path in (record_path, stdout_path, stderr_path, inspection_path):
        if path.exists() or path.is_symlink():
            raise FileExistsError(f"refusing to overwrite frozen artifact: {path}")

    # These are the first writes after the upstream process returns.  Hashes
    # are deliberately recomputed from the closed files rather than buffers.
    _write_bytes_exclusive(stdout_path, outcome.stdout)
    _write_bytes_exclusive(stderr_path, outcome.stderr)
    stdout_size = stdout_path.stat().st_size
    stderr_size = stderr_path.stat().st_size
    stdout_sha256 = sha256_file(stdout_path)
    stderr_sha256 = sha256_file(stderr_path)

    limitations = [
        *identity.limitations,
        "This record is an EMPIRICAL_OBSERVATION, not a reproduction, certificate, proof, or accepted counterexample.",
        "Independent inspection is a bounded diagnostic and cannot accept a mathematical claim in this task.",
        "A candidate passing every recorded predicate remains surprising and requires a separate review task.",
    ]
    initial_inspection_status = (
        "not_started"
        if outcome.termination_reason == "exited" and outcome.exit_code == 100
        else "not_applicable"
    )
    record: dict[str, Any] = {
        "schema_version": RECORD_SCHEMA_VERSION,
        "artifact_kind": OUTCOME_ARTIFACT_KIND,
        "classification": CLASSIFICATION,
        "k": k,
        "command": list(identity.command),
        "executable_path": identity.executable_path,
        "executable_sha256": identity.executable_sha256,
        "project_commit": identity.project_commit,
        "project_revision": identity.project_revision,
        "upstream_commit": identity.upstream_commit,
        "termination_reason": outcome.termination_reason,
        "exit_code": outcome.exit_code,
        "launcher_error": outcome.launcher_error,
        "upstream_timeout_seconds": upstream_timeout_seconds,
        "stdout": {
            "path": stdout_path.name,
            "byte_length": stdout_size,
            "sha256": stdout_sha256,
        },
        "stderr": {
            "path": stderr_path.name,
            "byte_length": stderr_size,
            "sha256": stderr_sha256,
        },
        "inspection_initial_status": initial_inspection_status,
        "inspection_artifact_path": inspection_path.name,
        "inspection_timeout_seconds": inspection_timeout_seconds,
        "limitations": limitations,
    }
    _validate_record_schema(record)
    _write_json_exclusive(record_path, record)
    record_sha256 = sha256_file(record_path)
    return FrozenOutcomeArtifacts(
        record_path=record_path,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        inspection_path=inspection_path,
        record=record,
        record_sha256=record_sha256,
    )


def parse_upstream_adjacency_list(output: str) -> Graph:
    """Parse only the upstream ``print_graph`` adjacency-list interface."""

    if not output:
        raise UpstreamAdjacencyFormatError(
            "empty_output", "$", "candidate adjacency output is empty"
        )
    if not output.endswith("\n"):
        raise UpstreamAdjacencyFormatError(
            "missing_final_newline",
            "$",
            "candidate adjacency output must end with LF",
        )

    lines = output[:-1].split("\n")
    if any(not line for line in lines):
        raise UpstreamAdjacencyFormatError(
            "blank_line", "$", "candidate adjacency output contains a blank line"
        )

    declarations: dict[str, tuple[str, ...]] = {}
    for line_number, line in enumerate(lines, start=1):
        location = f"line {line_number}"
        match = _UPSTREAM_ADJACENCY_LINE.fullmatch(line)
        if match is None:
            raise UpstreamAdjacencyFormatError(
                "malformed_line",
                location,
                "expected '<vertex>: <neighbor> ... ' with ASCII decimal labels",
            )
        label = match.group("label")
        neighbors = tuple(match.group("neighbors").split())
        for token in (label, *neighbors):
            if _CANONICAL_VERTEX_LABEL.fullmatch(token) is None:
                raise UpstreamAdjacencyFormatError(
                    "noncanonical_vertex_label",
                    location,
                    f"vertex label {token!r} is not canonical unsigned decimal",
                )
        if label in declarations:
            raise UpstreamAdjacencyFormatError(
                "duplicate_vertex_declaration",
                location,
                f"vertex {label} is declared more than once",
            )
        if len(set(neighbors)) != len(neighbors):
            raise UpstreamAdjacencyFormatError(
                "duplicate_neighbor",
                location,
                f"vertex {label} declares a neighbor more than once",
            )
        if label in neighbors:
            raise UpstreamAdjacencyFormatError(
                "loop",
                location,
                f"vertex {label} declares itself as a neighbor",
            )
        declarations[label] = neighbors

    expected_labels = {str(vertex) for vertex in range(len(declarations))}
    actual_labels = set(declarations)
    if actual_labels != expected_labels:
        raise UpstreamAdjacencyFormatError(
            "noncanonical_vertex_labels",
            "$",
            "declared labels must be exactly 0 through n-1; "
            f"expected={sorted(expected_labels, key=lambda item: (len(item), item))!r}, "
            f"actual={sorted(actual_labels, key=lambda item: (len(item), item))!r}",
        )

    for label, neighbors in declarations.items():
        for neighbor in neighbors:
            if neighbor not in declarations:
                raise UpstreamAdjacencyFormatError(
                    "undeclared_endpoint",
                    f"vertex {label}",
                    f"neighbor {neighbor} has no vertex declaration",
                )
            if label not in declarations[neighbor]:
                raise UpstreamAdjacencyFormatError(
                    "asymmetric_adjacency",
                    f"vertex {label}",
                    f"adjacency {label}-{neighbor} is not declared symmetrically",
                )

    edges = [
        (int(label), int(neighbor))
        for label, neighbors in declarations.items()
        for neighbor in neighbors
        if int(label) < int(neighbor)
    ]
    try:
        return Graph(range(len(declarations)), edges)
    except GraphFormatError as exc:  # defensive trust-boundary conversion
        raise UpstreamAdjacencyFormatError(
            "graph_construction_failure", exc.location, exc.message
        ) from exc


def inspect_candidate_bytes(output: bytes, k: int) -> dict[str, Any]:
    """Inspect frozen candidate bytes without accepting any result."""

    try:
        text = output.decode("utf-8")
    except UnicodeDecodeError as exc:
        return {
            "parse_succeeded": False,
            "parse_error": {
                "code": "invalid_utf8",
                "location": f"byte {exc.start}",
                "message": "candidate adjacency output is not UTF-8",
            },
            "canonical_graph_serialization": None,
            "canonical_graph_sha256": None,
            "checks": None,
            "all_candidate_predicates_passed": None,
        }
    try:
        graph = parse_upstream_adjacency_list(text)
    except UpstreamAdjacencyFormatError as exc:
        return {
            "parse_succeeded": False,
            "parse_error": exc.as_dict(),
            "canonical_graph_serialization": None,
            "canonical_graph_sha256": None,
            "checks": None,
            "all_candidate_predicates_passed": None,
        }

    observed_minimum_degree = minimum_degree(graph)
    induced_path = find_induced_path(graph, k)
    cycle_checks: list[dict[str, Any]] = []
    for length in relevant_power_of_two_lengths(len(graph.vertices)):
        witness = find_exact_cycle(graph, length)
        cycle_checks.append(
            {
                "length": length,
                "passed": witness is None,
                "witness": None if witness is None else list(witness),
            }
        )
    checks: dict[str, Any] = {
        "simple_graph_construction": {"passed": True},
        "minimum_degree_at_least_3": {
            "observed": observed_minimum_degree,
            "passed": observed_minimum_degree >= 3,
        },
        f"p{k}_free": {
            "passed": induced_path is None,
            f"witness_induced_p{k}": (
                None if induced_path is None else list(induced_path)
            ),
        },
        "no_relevant_power_of_two_cycles": {
            "passed": all(check["passed"] for check in cycle_checks),
            "per_length": cycle_checks,
        },
    }
    return {
        "parse_succeeded": True,
        "parse_error": None,
        "canonical_graph_serialization": graph.canonical_bytes().decode("utf-8"),
        "canonical_graph_sha256": graph.canonical_sha256(),
        "checks": checks,
        "all_candidate_predicates_passed": all(
            bool(check["passed"]) for check in checks.values()
        ),
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise CandidateInspectionError(
            "invalid_record_path", "outcome record must be a regular non-symlink file"
        )
    try:
        value = json.loads(
            path.read_bytes(),
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_nonfinite_json_constant,
        )
    except UnicodeDecodeError as exc:
        raise CandidateInspectionError(
            "invalid_record_utf8", "outcome record is not UTF-8"
        ) from exc
    except json.JSONDecodeError as exc:
        raise CandidateInspectionError(
            "invalid_record_json", f"outcome record is not valid JSON: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise CandidateInspectionError(
            "invalid_record_type", "outcome record must be a JSON object"
        )
    return value


def _read_frozen_stream(
    record_path: Path, name: str, metadata: Any
) -> tuple[bytes, dict[str, Any]]:
    if not isinstance(metadata, dict):
        raise CandidateInspectionError(
            "invalid_stream_metadata", f"{name} metadata must be an object"
        )
    path_value = metadata.get("path")
    expected_size = metadata.get("byte_length")
    expected_sha256 = metadata.get("sha256")
    if (
        not isinstance(path_value, str)
        or not path_value
        or Path(path_value).name != path_value
    ):
        raise CandidateInspectionError(
            "invalid_stream_path", f"{name} path must be an artifact-relative basename"
        )
    if isinstance(expected_size, bool) or not isinstance(expected_size, int):
        raise CandidateInspectionError(
            "invalid_stream_size", f"{name} byte_length must be an integer"
        )
    if not isinstance(expected_sha256, str):
        raise CandidateInspectionError(
            "invalid_stream_hash", f"{name} sha256 must be a string"
        )
    stream_path = record_path.parent / path_value
    if stream_path.is_symlink() or not stream_path.is_file():
        raise CandidateInspectionError(
            "invalid_stream_file", f"{name} must be a regular non-symlink file"
        )
    data = stream_path.read_bytes()
    observed_sha256 = hashlib.sha256(data).hexdigest()
    if len(data) != expected_size or observed_sha256 != expected_sha256:
        raise CandidateInspectionError(
            "stream_integrity_mismatch",
            f"{name} does not match its frozen size and SHA-256",
        )
    return data, {
        "path": path_value,
        "byte_length": len(data),
        "sha256": observed_sha256,
    }


def inspect_frozen_outcome(record_path: Path) -> dict[str, Any]:
    """Read verified frozen streams and return a completed inspection record."""

    record = _load_json_object(record_path)
    if record.get("artifact_kind") != OUTCOME_ARTIFACT_KIND:
        raise CandidateInspectionError(
            "invalid_artifact_kind", "input is not a surprising outcome record"
        )
    k = record.get("k")
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise CandidateInspectionError("invalid_k", "outcome record k is invalid")
    if record.get("termination_reason") != "exited" or record.get("exit_code") != 100:
        raise CandidateInspectionError(
            "invalid_source_outcome", "candidate inspection requires exact exit 100"
        )
    stdout, stdout_metadata = _read_frozen_stream(
        record_path, "stdout", record.get("stdout")
    )
    _stderr, stderr_metadata = _read_frozen_stream(
        record_path, "stderr", record.get("stderr")
    )
    result = inspect_candidate_bytes(stdout, k)
    return {
        "schema_version": RECORD_SCHEMA_VERSION,
        "artifact_kind": INSPECTION_ARTIFACT_KIND,
        "classification": CLASSIFICATION,
        "source_outcome_path": record_path.name,
        "source_outcome_sha256": sha256_file(record_path),
        "source_outcome_preserved": True,
        "k": k,
        "status": "completed",
        "source_streams": {
            "stdout": stdout_metadata,
            "stderr": stderr_metadata,
        },
        "source_streams_preserved": True,
        "result": result,
        "error": None,
        "inspector_process": None,
        "limitations": [
            "This bounded inspection does not accept a counterexample or establish a mathematical result.",
            "A candidate passing every predicate remains surprising and requires a separate review task.",
        ],
    }


def _captured_stream(value: bytes) -> dict[str, Any]:
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "byte_length": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
    }


def _source_outcome_preserved(frozen: FrozenOutcomeArtifacts) -> bool:
    try:
        return (
            not frozen.record_path.is_symlink()
            and frozen.record_path.is_file()
            and sha256_file(frozen.record_path) == frozen.record_sha256
        )
    except OSError:
        return False


def _source_streams_preserved(frozen: FrozenOutcomeArtifacts) -> bool:
    for name, path in (("stdout", frozen.stdout_path), ("stderr", frozen.stderr_path)):
        metadata = frozen.record[name]
        try:
            if path.is_symlink() or not path.is_file():
                return False
            if path.stat().st_size != metadata["byte_length"]:
                return False
            if sha256_file(path) != metadata["sha256"]:
                return False
        except OSError:
            return False
    return True


def _inspection_error_payload(
    *,
    code: str,
    message: str,
    inspector_exit_code: int | None,
    inspector_stdout: bytes,
    inspector_stderr: bytes,
) -> dict[str, Any]:
    return {
        "status": "error",
        "result": None,
        "error": {"code": code, "message": message},
        "inspector_process": {
            "exit_code": inspector_exit_code,
            "stdout": _captured_stream(inspector_stdout),
            "stderr": _captured_stream(inspector_stderr),
        },
        "limitations": [
            "The independent inspection did not complete; the original frozen streams remain the primary diagnostic evidence.",
            "No counterexample, reproduction, certification, or mathematical result is accepted.",
        ],
    }


def _inspection_timeout_payload(
    inspector_exit_code: int | None,
    inspector_stdout: bytes,
    inspector_stderr: bytes,
) -> dict[str, Any]:
    payload = _inspection_error_payload(
        code="inspection_timeout",
        message="independent candidate inspection exceeded its autonomous timeout",
        inspector_exit_code=inspector_exit_code,
        inspector_stdout=inspector_stdout,
        inspector_stderr=inspector_stderr,
    )
    payload["status"] = "timeout"
    return payload


def _decode_inspector_protocol(stdout: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            stdout.decode("utf-8"),
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_nonfinite_json_constant,
        )
    except CandidateInspectionError:
        raise
    except UnicodeDecodeError as exc:
        raise CandidateInspectionError(
            "invalid_inspector_utf8", "inspector stdout is not UTF-8"
        ) from exc
    except json.JSONDecodeError as exc:
        raise CandidateInspectionError(
            "incomplete_inspector_output",
            f"inspector stdout is not one complete JSON value: {exc.msg}",
        ) from exc
    if not isinstance(value, dict):
        raise CandidateInspectionError(
            "invalid_inspector_output", "inspector output must be a JSON object"
        )
    if value.get("status") not in {"completed", "error"}:
        raise CandidateInspectionError(
            "invalid_inspector_status", "inspector status must be completed or error"
        )
    limitations = value.get("limitations")
    if (
        not isinstance(limitations, list)
        or not limitations
        or any(not isinstance(item, str) or not item for item in limitations)
    ):
        raise CandidateInspectionError(
            "incomplete_inspector_output",
            "inspector limitations must be a nonempty array of nonempty strings",
        )
    status = value["status"]
    if status == "completed":
        if (
            not isinstance(value.get("result"), dict)
            or "error" not in value
            or value["error"] is not None
            or value.get("inspector_process") is not None
        ):
            raise CandidateInspectionError(
                "incomplete_inspector_output",
                "completed inspector output requires a result and null error/process",
            )
        return {
            "status": "completed",
            "result": value["result"],
            "error": None,
            "inspector_process": None,
        }

    error = value.get("error")
    if (
        "result" not in value
        or value["result"] is not None
        or not isinstance(error, dict)
        or not isinstance(error.get("code"), str)
        or not error["code"]
        or not isinstance(error.get("message"), str)
        or not error["message"]
        or set(error) - {"code", "location", "message"}
    ):
        raise CandidateInspectionError(
            "incomplete_inspector_output",
            "error inspector output requires null result and a complete error object",
        )
    if "location" in error and (
        not isinstance(error["location"], str) or not error["location"]
    ):
        raise CandidateInspectionError(
            "incomplete_inspector_output",
            "inspector error location must be a nonempty string when present",
        )
    return {
        "status": "error",
        "result": None,
        "error": error,
        "inspector_process": None,
    }


def _bind_inspection_envelope(
    frozen: FrozenOutcomeArtifacts,
    body: dict[str, Any],
    *,
    timeout_seconds: float,
    source_outcome_preserved: bool,
    source_streams_preserved: bool,
) -> dict[str, Any]:
    if body["status"] == "completed":
        limitations = [
            "This bounded inspection does not accept a counterexample or establish a mathematical result.",
            "A candidate passing every predicate remains surprising and requires a separate review task.",
        ]
    else:
        limitations = [
            "The independent inspection did not complete successfully; the original frozen streams remain the primary diagnostic evidence.",
            "No counterexample, reproduction, certification, or mathematical result is accepted.",
        ]
    return {
        "schema_version": RECORD_SCHEMA_VERSION,
        "artifact_kind": INSPECTION_ARTIFACT_KIND,
        "classification": CLASSIFICATION,
        "source_outcome_path": frozen.record_path.name,
        "source_outcome_sha256": frozen.record_sha256,
        "source_outcome_preserved": source_outcome_preserved,
        "k": frozen.record["k"],
        "status": body["status"],
        "inspection_timeout_seconds": timeout_seconds,
        "source_streams": {
            "stdout": frozen.record["stdout"],
            "stderr": frozen.record["stderr"],
        },
        "source_streams_preserved": source_streams_preserved,
        "result": body["result"],
        "error": body["error"],
        "inspector_process": body["inspector_process"],
        "limitations": limitations,
    }


def _inspector_environment(
    overrides: dict[str, str] | None = None,
) -> dict[str, str]:
    environment = os.environ.copy()
    existing = environment.get("PYTHONPATH")
    verifier = str(VERIFIER_ROOT)
    environment["PYTHONPATH"] = (
        verifier if not existing else verifier + os.pathsep + existing
    )
    if overrides:
        environment.update(overrides)
    return environment


def run_bounded_candidate_inspection(
    frozen: FrozenOutcomeArtifacts,
    *,
    timeout_seconds: float,
    inspector_command: Sequence[str] | None = None,
    environment_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run and reap a direct inspector child, then write one final JSON record."""

    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, (int, float))
        or not math.isfinite(float(timeout_seconds))
        or timeout_seconds <= 0
    ):
        raise ValueError("timeout_seconds must be positive")
    if frozen.inspection_path.exists() or frozen.inspection_path.is_symlink():
        raise FileExistsError(
            f"refusing to overwrite inspection artifact: {frozen.inspection_path}"
        )
    command = list(inspector_command) if inspector_command is not None else [
        sys.executable,
        str(Path(__file__).resolve()),
        "--outcome-record",
        str(frozen.record_path.resolve()),
    ]
    if not command or not all(isinstance(item, str) for item in command):
        raise ValueError("inspector command must be a nonempty sequence of strings")

    inspector_stdout = b""
    inspector_stderr = b""
    inspector_exit_code: int | None = None
    try:
        with subprocess.Popen(
            command,
            cwd=REPOSITORY_ROOT,
            env=_inspector_environment(environment_overrides),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            try:
                inspector_stdout, inspector_stderr = process.communicate(
                    timeout=timeout_seconds
                )
            except subprocess.TimeoutExpired:
                process.kill()
                inspector_stdout, inspector_stderr = process.communicate()
                inspector_exit_code = process.returncode
                body = _inspection_timeout_payload(
                    inspector_exit_code, inspector_stdout, inspector_stderr
                )
            else:
                inspector_exit_code = process.returncode
                try:
                    protocol = _decode_inspector_protocol(inspector_stdout)
                except CandidateInspectionError as exc:
                    body = _inspection_error_payload(
                        code=exc.code,
                        message=exc.message,
                        inspector_exit_code=process.returncode,
                        inspector_stdout=inspector_stdout,
                        inspector_stderr=inspector_stderr,
                    )
                else:
                    if (
                        process.returncode == 0
                        and protocol.get("status") == "completed"
                        and not inspector_stderr
                    ):
                        body = protocol
                    elif (
                        process.returncode != 0
                        and protocol.get("status") == "error"
                    ):
                        body = protocol
                        body["inspector_process"] = {
                            "exit_code": process.returncode,
                            "stdout": _captured_stream(inspector_stdout),
                            "stderr": _captured_stream(inspector_stderr),
                        }
                    else:
                        body = _inspection_error_payload(
                            code="inspector_protocol_mismatch",
                            message=(
                                "inspector exit status, stderr, and JSON status are inconsistent"
                            ),
                            inspector_exit_code=process.returncode,
                            inspector_stdout=inspector_stdout,
                            inspector_stderr=inspector_stderr,
                        )
    except OSError as exc:
        body = _inspection_error_payload(
            code="inspector_spawn_error",
            message=f"{type(exc).__name__}: {exc}",
            inspector_exit_code=None,
            inspector_stdout=b"",
            inspector_stderr=b"",
        )

    source_outcome_preserved = _source_outcome_preserved(frozen)
    source_streams_preserved = _source_streams_preserved(frozen)
    if body["status"] == "completed" and not (
        source_outcome_preserved and source_streams_preserved
    ):
        body = _inspection_error_payload(
            code="source_integrity_mismatch",
            message="inspector completed after a frozen source artifact changed",
            inspector_exit_code=inspector_exit_code,
            inspector_stdout=inspector_stdout,
            inspector_stderr=inspector_stderr,
        )
    payload = _bind_inspection_envelope(
        frozen,
        body,
        timeout_seconds=timeout_seconds,
        source_outcome_preserved=source_outcome_preserved,
        source_streams_preserved=source_streams_preserved,
    )
    try:
        _validate_record_schema(payload)
    except CandidateInspectionError as exc:
        body = _inspection_error_payload(
            code="invalid_inspector_record",
            message=f"{exc.code}: {exc.message}",
            inspector_exit_code=inspector_exit_code,
            inspector_stdout=inspector_stdout,
            inspector_stderr=inspector_stderr,
        )
        payload = _bind_inspection_envelope(
            frozen,
            body,
            timeout_seconds=timeout_seconds,
            source_outcome_preserved=source_outcome_preserved,
            source_streams_preserved=source_streams_preserved,
        )
        _validate_record_schema(payload)
    _write_json_exclusive(frozen.inspection_path, payload)
    return payload


def _bounded_stream_diagnostic(
    path: Path, metadata: dict[str, Any], prefix_limit: int
) -> dict[str, Any]:
    if (
        isinstance(prefix_limit, bool)
        or not isinstance(prefix_limit, int)
        or prefix_limit < 0
    ):
        raise ValueError("prefix_limit must be a nonnegative integer")
    with path.open("rb") as stream:
        prefix = stream.read(prefix_limit)
    return {
        "path": path.as_posix(),
        "byte_length": metadata["byte_length"],
        "sha256": metadata["sha256"],
        "prefix_limit_bytes": prefix_limit,
        "prefix_base64": base64.b64encode(prefix).decode("ascii"),
        "prefix_utf8_with_replacement": prefix.decode("utf-8", errors="replace"),
        "truncated": metadata["byte_length"] > prefix_limit,
    }


def format_surprising_failure(
    outcome: CapturedProcessOutcome,
    frozen: FrozenOutcomeArtifacts,
    inspection: dict[str, Any] | None,
    *,
    prefix_limit: int = DEFAULT_LOG_PREFIX_BYTES,
) -> str:
    """Return bounded diagnostics beginning with the original process failure."""

    first_line = (
        "tiny upstream invocation did not complete ordinarily: "
        f"termination_reason={outcome.termination_reason} "
        f"exit_code={outcome.exit_code}"
    )
    disposition = "nonordinary upstream outcome frozen before inspection"
    if inspection is not None:
        status = inspection.get("status")
        result = inspection.get("result")
        if status == "timeout":
            disposition = "independent exit-100 inspection timed out"
        elif status == "error":
            disposition = "independent exit-100 inspection ended in error"
        elif isinstance(result, dict) and result.get("parse_succeeded") is False:
            disposition = "independent exit-100 inspection completed with parse failure"
        elif (
            isinstance(result, dict)
            and result.get("all_candidate_predicates_passed") is True
        ):
            disposition = (
                "all independent predicates passed; surprising result frozen for a separate task"
            )
        else:
            disposition = (
                "independent exit-100 inspection completed with at least one failed predicate"
            )
    summary = {
        "disposition": disposition,
        "outcome_record_path": frozen.record_path.as_posix(),
        "outcome_record_sha256": sha256_file(frozen.record_path),
        "stdout": _bounded_stream_diagnostic(
            frozen.stdout_path, frozen.record["stdout"], prefix_limit
        ),
        "stderr": _bounded_stream_diagnostic(
            frozen.stderr_path, frozen.record["stderr"], prefix_limit
        ),
        "inspection": (
            None
            if inspection is None
            else {
                "path": frozen.inspection_path.as_posix(),
                "sha256": sha256_file(frozen.inspection_path),
                "status": inspection.get("status"),
                "parse_succeeded": (
                    inspection.get("result", {}).get("parse_succeeded")
                    if isinstance(inspection.get("result"), dict)
                    else None
                ),
                "all_candidate_predicates_passed": (
                    inspection.get("result", {}).get(
                        "all_candidate_predicates_passed"
                    )
                    if isinstance(inspection.get("result"), dict)
                    else None
                ),
                "error": inspection.get("error"),
            }
        ),
    }
    return first_line + "\n" + json.dumps(
        summary, ensure_ascii=True, indent=2, sort_keys=True
    )


def _format_preservation_stage_error(
    outcome: CapturedProcessOutcome,
    *,
    stage: str,
    error: Exception,
    frozen: FrozenOutcomeArtifacts | None = None,
) -> str:
    summary: dict[str, Any] = {
        "disposition": f"{stage} error; original upstream failure remains authoritative",
        "error": {
            "type": type(error).__name__,
            "message": str(error),
        },
    }
    if frozen is not None:
        summary["outcome_record_path"] = frozen.record_path.as_posix()
        summary["stdout_path"] = frozen.stdout_path.as_posix()
        summary["stderr_path"] = frozen.stderr_path.as_posix()
    return (
        "tiny upstream invocation did not complete ordinarily: "
        f"termination_reason={outcome.termination_reason} "
        f"exit_code={outcome.exit_code}\n"
        + json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True)
    )


def ordinary_completion_failure(
    *,
    outcome: CapturedProcessOutcome,
    k: int,
    identity: InvocationIdentity,
    artifact_directory: Path,
    upstream_timeout_seconds: float,
    inspection_timeout_seconds: float,
    inspector_command: Sequence[str] | None = None,
    inspector_environment_overrides: dict[str, str] | None = None,
) -> str | None:
    """Enforce exact ordinary completion and preserve every other outcome."""

    if is_ordinary_completion(outcome):
        return None
    try:
        frozen = freeze_surprising_process_outcome(
            artifact_directory=artifact_directory,
            k=k,
            outcome=outcome,
            identity=identity,
            upstream_timeout_seconds=upstream_timeout_seconds,
            inspection_timeout_seconds=inspection_timeout_seconds,
        )
    except Exception as exc:  # secondary preservation failure must not mask upstream
        return _format_preservation_stage_error(
            outcome, stage="freeze", error=exc
        )
    inspection: dict[str, Any] | None = None
    if outcome.termination_reason == "exited" and outcome.exit_code == 100:
        try:
            inspection = run_bounded_candidate_inspection(
                frozen,
                timeout_seconds=inspection_timeout_seconds,
                inspector_command=inspector_command,
                environment_overrides=inspector_environment_overrides,
            )
        except Exception as exc:  # secondary inspection failure must not mask upstream
            return _format_preservation_stage_error(
                outcome,
                stage="inspection orchestration",
                error=exc,
                frozen=frozen,
            )
    try:
        return format_surprising_failure(outcome, frozen, inspection)
    except Exception as exc:  # preserve the primary upstream failure at all costs
        return _format_preservation_stage_error(
            outcome,
            stage="diagnostic formatting",
            error=exc,
            frozen=frozen,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcome-record", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = inspect_frozen_outcome(args.outcome_record.resolve())
    except CandidateInspectionError as exc:
        payload = {
            "schema_version": RECORD_SCHEMA_VERSION,
            "artifact_kind": INSPECTION_ARTIFACT_KIND,
            "classification": CLASSIFICATION,
            "status": "error",
            "result": None,
            "error": {"code": exc.code, "message": exc.message},
            "limitations": [
                "The frozen input could not be independently inspected.",
                "No counterexample or mathematical result is accepted.",
            ],
        }
        exit_code = 1
    except (OSError, KeyError, TypeError, ValueError, RecursionError) as exc:
        payload = {
            "schema_version": RECORD_SCHEMA_VERSION,
            "artifact_kind": INSPECTION_ARTIFACT_KIND,
            "classification": CLASSIFICATION,
            "status": "error",
            "result": None,
            "error": {
                "code": "inspection_exception",
                "message": f"{type(exc).__name__}: {exc}",
            },
            "limitations": [
                "The independent inspection ended in an error.",
                "No counterexample or mathematical result is accepted.",
            ],
        }
        exit_code = 1
    else:
        exit_code = 0
    print(json.dumps(payload, allow_nan=False, ensure_ascii=True, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
