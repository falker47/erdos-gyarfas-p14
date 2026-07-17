from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest
from jsonschema import FormatChecker
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validator_for

from tools import inspect_upstream_candidate as inspection
from tools.inspect_upstream_candidate import (
    CapturedProcessOutcome,
    InvocationIdentity,
    UpstreamAdjacencyFormatError,
    freeze_surprising_process_outcome,
    inspect_candidate_bytes,
    ordinary_completion_failure,
    parse_upstream_adjacency_list,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "schemas" / "surprising-process-outcome.schema.json"
K4_UPSTREAM_ADJACENCY = (
    b"2: 0 1 3 \n"
    b"0: 1 2 3 \n"
    b"3: 0 1 2 \n"
    b"1: 0 2 3 \n"
)


def _identity(k: int = 4) -> InvocationIdentity:
    executable = REPOSITORY_ROOT / "tools" / "inspect_upstream_candidate.py"
    return InvocationIdentity(
        command=(executable.as_posix(), str(k)),
        executable_path=executable.resolve().as_posix(),
        executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
        project_commit="1" * 40,
        project_revision="dirty:" + "1" * 40 + ":sha256:" + "2" * 64,
        upstream_commit="3" * 40,
        limitations=(),
    )


def _outcome(
    *,
    reason: str = "exited",
    code: int | None = 100,
    stdout: bytes = K4_UPSTREAM_ADJACENCY,
    stderr: bytes = b"",
    launcher_error: str | None = None,
) -> CapturedProcessOutcome:
    return CapturedProcessOutcome(
        termination_reason=reason,
        exit_code=code,
        stdout=stdout,
        stderr=stderr,
        launcher_error=launcher_error,
    )


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _validator():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator_type = validator_for(schema)
    validator_type.check_schema(schema)
    return validator_type(schema, format_checker=FormatChecker())


def _validate(path: Path) -> dict[str, object]:
    value = _load(path)
    _validator().validate(value)
    return value


def _paths(directory: Path, k: int = 4) -> dict[str, Path]:
    stem = f"tiny-k{k}-surprising-outcome"
    return {
        "outcome": directory / f"{stem}.json",
        "stdout": directory / f"{stem}.stdout.bin",
        "stderr": directory / f"{stem}.stderr.bin",
        "inspection": directory / f"{stem}.inspection.json",
    }


def _run_default(
    directory: Path,
    outcome: CapturedProcessOutcome,
    *,
    k: int = 4,
    timeout: float = 2,
) -> str | None:
    return ordinary_completion_failure(
        outcome=outcome,
        k=k,
        identity=_identity(k),
        artifact_directory=directory,
        upstream_timeout_seconds=10,
        inspection_timeout_seconds=timeout,
    )


def test_ordinary_exit_zero_creates_no_surprising_artifacts(tmp_path: Path) -> None:
    directory = tmp_path / "surprises"
    failure = _run_default(
        directory,
        _outcome(code=0, stdout=b"time taken: 1 microseconds\n"),
    )

    assert failure is None
    assert not directory.exists()


def test_exit_100_with_parse_failure_is_frozen_and_still_fails(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "surprises"
    failure = _run_default(directory, _outcome(stdout=b"malformed\n"))

    assert failure is not None
    assert failure.splitlines()[0] == (
        "tiny upstream invocation did not complete ordinarily: "
        "termination_reason=exited exit_code=100"
    )
    paths = _paths(directory)
    outcome_record = _validate(paths["outcome"])
    inspection_record = _validate(paths["inspection"])
    assert outcome_record["inspection_initial_status"] == "not_started"
    assert inspection_record["status"] == "completed"
    assert inspection_record["source_outcome_preserved"] is True
    result = inspection_record["result"]
    assert isinstance(result, dict)
    assert result["parse_succeeded"] is False
    assert result["parse_error"]["code"] == "malformed_line"
    assert inspection_record["source_streams_preserved"] is True


def test_exit_100_with_failed_predicate_preserves_graph_and_still_fails(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "surprises"
    failure = _run_default(directory, _outcome())

    assert failure is not None
    inspection_record = _validate(_paths(directory)["inspection"])
    result = inspection_record["result"]
    assert isinstance(result, dict)
    assert result["parse_succeeded"] is True
    assert result["canonical_graph_sha256"] == (
        "c423921c28d31c5ca500533d703db40e58689e8a1a7e4c69c0fe7e66e9b8b6df"
    )
    checks = result["checks"]
    assert checks["no_relevant_power_of_two_cycles"] == {
        "passed": False,
        "per_length": [
            {"length": 4, "passed": False, "witness": [0, 1, 2, 3]}
        ],
    }
    assert result["all_candidate_predicates_passed"] is False
    assert "failed predicate" in failure


def test_synthetic_all_predicates_passed_is_only_a_frozen_surprise(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "surprises"
    synthetic_result = {
        "schema_version": "1.0",
        "artifact_kind": "surprising_process_outcome_inspection",
        "classification": "EMPIRICAL_OBSERVATION",
        "status": "completed",
        "result": {
            "parse_succeeded": True,
            "parse_error": None,
            "canonical_graph_serialization": (
                '{"edges":[],"schema_version":"1.0","vertices":[0]}\n'
            ),
            "canonical_graph_sha256": "4" * 64,
            "checks": {"synthetic_only": {"passed": True}},
            "all_candidate_predicates_passed": True,
        },
        "error": None,
        "inspector_process": None,
        "limitations": [
            "Synthetic protocol fixture only; this is not a real graph result."
        ],
    }
    command = [
        sys.executable,
        "-c",
        "import json,sys; print(json.loads(sys.argv[1]) and sys.argv[1])",
        json.dumps(synthetic_result, sort_keys=True),
    ]

    failure = ordinary_completion_failure(
        outcome=_outcome(stdout=b"0: \n"),
        k=4,
        identity=_identity(),
        artifact_directory=directory,
        upstream_timeout_seconds=10,
        inspection_timeout_seconds=2,
        inspector_command=command,
    )

    assert failure is not None
    assert "all independent predicates passed" in failure
    assert "separate task" in failure
    record = _validate(_paths(directory)["inspection"])
    assert record["status"] == "completed"
    assert record["result"]["all_candidate_predicates_passed"] is True
    assert record["classification"] == "EMPIRICAL_OBSERVATION"


def test_timeout_proves_freeze_precedes_inspector_and_child_is_reaped(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "surprises"
    paths = _paths(directory)
    verified_marker = tmp_path / "verified-before-sleep.txt"
    heartbeat = tmp_path / "heartbeat.txt"
    late_marker = tmp_path / "late-marker.txt"
    script = """
import hashlib, json, sys, time
from pathlib import Path
record_path = Path(sys.argv[1])
verified = Path(sys.argv[2])
heartbeat = Path(sys.argv[3])
late = Path(sys.argv[4])
record = json.loads(record_path.read_text(encoding='utf-8'))
assert record['inspection_initial_status'] == 'not_started'
assert not (record_path.parent / record['inspection_artifact_path']).exists()
for stream_name in ('stdout', 'stderr'):
    metadata = record[stream_name]
    data = (record_path.parent / metadata['path']).read_bytes()
    assert len(data) == metadata['byte_length']
    assert hashlib.sha256(data).hexdigest() == metadata['sha256']
verified.write_text('raw-and-hashes-existed', encoding='utf-8')
for index in range(200):
    heartbeat.write_text(str(index), encoding='utf-8')
    time.sleep(0.02)
late.write_text('child-survived-timeout', encoding='utf-8')
"""
    command = [
        sys.executable,
        "-c",
        script,
        str(paths["outcome"]),
        str(verified_marker),
        str(heartbeat),
        str(late_marker),
    ]
    started = time.perf_counter()
    failure = ordinary_completion_failure(
        outcome=_outcome(stderr=b"original stderr\xff"),
        k=4,
        identity=_identity(),
        artifact_directory=directory,
        upstream_timeout_seconds=10,
        inspection_timeout_seconds=0.75,
        inspector_command=command,
    )
    elapsed = time.perf_counter() - started

    assert failure is not None
    assert elapsed < 2
    assert verified_marker.read_text(encoding="utf-8") == "raw-and-hashes-existed"
    assert not late_marker.exists()
    heartbeat_after_timeout = heartbeat.read_bytes()
    time.sleep(0.15)
    assert heartbeat.read_bytes() == heartbeat_after_timeout
    outcome_hash = hashlib.sha256(paths["outcome"].read_bytes()).hexdigest()
    stdout_hash = hashlib.sha256(paths["stdout"].read_bytes()).hexdigest()
    stderr_hash = hashlib.sha256(paths["stderr"].read_bytes()).hexdigest()
    inspection_record = _validate(paths["inspection"])
    assert inspection_record["status"] == "timeout"
    assert inspection_record["error"]["code"] == "inspection_timeout"
    assert inspection_record["source_streams_preserved"] is True
    assert inspection_record["source_outcome_preserved"] is True
    assert hashlib.sha256(paths["outcome"].read_bytes()).hexdigest() == outcome_hash
    assert hashlib.sha256(paths["stdout"].read_bytes()).hexdigest() == stdout_hash
    assert hashlib.sha256(paths["stderr"].read_bytes()).hexdigest() == stderr_hash


def test_inspector_error_is_machine_readable_and_raw_streams_survive(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "surprises"
    paths = _paths(directory)
    marker = tmp_path / "error-inspector-saw-raw.txt"
    script = """
import hashlib, json, sys
from pathlib import Path
record_path = Path(sys.argv[1])
marker = Path(sys.argv[2])
record = json.loads(record_path.read_text(encoding='utf-8'))
for name in ('stdout', 'stderr'):
    metadata = record[name]
    data = (record_path.parent / metadata['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == metadata['sha256']
marker.write_text('verified', encoding='utf-8')
sys.stderr.buffer.write(bytes([255]) + b'synthetic inspector failure')
raise SystemExit(7)
"""
    command = [sys.executable, "-c", script, str(paths["outcome"]), str(marker)]
    original = _outcome(stdout=b"candidate bytes", stderr=b"original\xfeerror")
    failure = ordinary_completion_failure(
        outcome=original,
        k=4,
        identity=_identity(),
        artifact_directory=directory,
        upstream_timeout_seconds=10,
        inspection_timeout_seconds=2,
        inspector_command=command,
    )

    assert failure is not None
    assert failure.startswith("tiny upstream invocation did not complete ordinarily")
    assert marker.read_text(encoding="utf-8") == "verified"
    assert paths["stdout"].read_bytes() == original.stdout
    assert paths["stderr"].read_bytes() == original.stderr
    inspection_record = _validate(paths["inspection"])
    assert inspection_record["status"] == "error"
    assert inspection_record["error"]["code"] == "incomplete_inspector_output"
    process = inspection_record["inspector_process"]
    assert process["exit_code"] == 7
    assert base64.b64decode(process["stderr"]["base64"]) == (
        b"\xffsynthetic inspector failure"
    )
    assert inspection_record["source_streams_preserved"] is True


def test_zero_exit_with_incomplete_inspector_protocol_becomes_valid_error_record(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "surprises"
    command = [sys.executable, "-c", "print('{\"status\":\"completed\"}')"]
    original = _outcome(stdout=b"frozen candidate", stderr=b"frozen diagnostic")

    failure = ordinary_completion_failure(
        outcome=original,
        k=4,
        identity=_identity(),
        artifact_directory=directory,
        upstream_timeout_seconds=10,
        inspection_timeout_seconds=2,
        inspector_command=command,
    )

    assert failure is not None
    assert failure.startswith("tiny upstream invocation did not complete ordinarily")
    paths = _paths(directory)
    assert paths["stdout"].read_bytes() == original.stdout
    assert paths["stderr"].read_bytes() == original.stderr
    inspection_record = _validate(paths["inspection"])
    assert inspection_record["status"] == "error"
    assert inspection_record["error"]["code"] == "incomplete_inspector_output"
    assert inspection_record["source_outcome_preserved"] is True
    assert inspection_record["source_streams_preserved"] is True


def test_parent_pins_outcome_hash_and_detects_inspector_mutation(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "surprises"
    paths = _paths(directory)
    serialization = '{"edges":[],"schema_version":"1.0","vertices":[0]}\n'
    protocol = {
        "status": "completed",
        "result": {
            "parse_succeeded": True,
            "parse_error": None,
            "canonical_graph_serialization": serialization,
            "canonical_graph_sha256": hashlib.sha256(
                serialization.encode("utf-8")
            ).hexdigest(),
            "checks": {"synthetic_only": {"passed": True}},
            "all_candidate_predicates_passed": True,
        },
        "error": None,
        "inspector_process": None,
        "limitations": ["Synthetic source-integrity test only."],
    }
    script = (
        "from pathlib import Path; import sys; "
        "p=Path(sys.argv[1]); p.write_bytes(p.read_bytes()+b' '); print(sys.argv[2])"
    )
    command = [
        sys.executable,
        "-c",
        script,
        str(paths["outcome"]),
        json.dumps(protocol, sort_keys=True),
    ]
    original = _outcome(stderr=b"original diagnostic")

    failure = ordinary_completion_failure(
        outcome=original,
        k=4,
        identity=_identity(),
        artifact_directory=directory,
        upstream_timeout_seconds=10,
        inspection_timeout_seconds=2,
        inspector_command=command,
    )

    assert failure is not None
    current_record = paths["outcome"].read_bytes()
    inspection_record = _validate(paths["inspection"])
    assert inspection_record["status"] == "error"
    assert inspection_record["error"]["code"] == "source_integrity_mismatch"
    assert inspection_record["source_outcome_preserved"] is False
    assert inspection_record["source_outcome_sha256"] == hashlib.sha256(
        current_record[:-1]
    ).hexdigest()
    assert hashlib.sha256(current_record).hexdigest() != inspection_record[
        "source_outcome_sha256"
    ]
    assert paths["stdout"].read_bytes() == original.stdout
    assert paths["stderr"].read_bytes() == original.stderr


def test_non_utf8_stdout_and_stderr_remain_byte_exact(tmp_path: Path) -> None:
    directory = tmp_path / "surprises"
    original = _outcome(stdout=b"\xff\x00candidate", stderr=b"\xfe\x80diagnostic")
    failure = _run_default(directory, original)

    assert failure is not None
    paths = _paths(directory)
    assert paths["stdout"].read_bytes() == original.stdout
    assert paths["stderr"].read_bytes() == original.stderr
    outcome_record = _validate(paths["outcome"])
    assert outcome_record["stdout"]["sha256"] == hashlib.sha256(
        original.stdout
    ).hexdigest()
    assert outcome_record["stderr"]["sha256"] == hashlib.sha256(
        original.stderr
    ).hexdigest()
    result = _validate(paths["inspection"])["result"]
    assert result["parse_succeeded"] is False
    assert result["parse_error"]["code"] == "invalid_utf8"


def test_artifact_names_and_serialization_are_deterministic(tmp_path: Path) -> None:
    first_directory = tmp_path / "first"
    second_directory = tmp_path / "second"
    first_failure = _run_default(first_directory, _outcome(stdout=b"malformed\n"))
    second_failure = _run_default(second_directory, _outcome(stdout=b"malformed\n"))

    assert first_failure is not None and second_failure is not None
    first_paths = _paths(first_directory)
    second_paths = _paths(second_directory)
    assert [path.name for path in first_paths.values()] == [
        path.name for path in second_paths.values()
    ]
    assert first_paths["outcome"].read_bytes() == second_paths["outcome"].read_bytes()
    assert first_paths["inspection"].read_bytes() == second_paths[
        "inspection"
    ].read_bytes()


@pytest.mark.parametrize(
    "outcome",
    [
        _outcome(code=1, stdout=b"exit one", stderr=b"diagnostic"),
        _outcome(reason="signal", code=-9, stdout=b"partial", stderr=b"signal"),
        _outcome(reason="timeout", code=None, stdout=b"partial", stderr=b"timeout"),
        _outcome(
            reason="spawn-error",
            code=None,
            stdout=b"",
            stderr=b"",
            launcher_error="FileNotFoundError: synthetic missing executable",
        ),
    ],
)
def test_every_other_nonordinary_outcome_is_frozen_without_inspection(
    outcome: CapturedProcessOutcome,
    tmp_path: Path,
) -> None:
    directory = tmp_path / "surprises"
    failure = _run_default(directory, outcome)

    assert failure is not None
    paths = _paths(directory)
    record = _validate(paths["outcome"])
    assert record["inspection_initial_status"] == "not_applicable"
    assert record["termination_reason"] == outcome.termination_reason
    assert record["exit_code"] == outcome.exit_code
    assert paths["stdout"].read_bytes() == outcome.stdout
    assert paths["stderr"].read_bytes() == outcome.stderr
    assert not paths["inspection"].exists()


def test_failure_log_is_bounded_and_raw_tail_only_exists_on_disk(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "surprises"
    tail = b"UNIQUE-RAW-TAIL-NOT-IN-LOG"
    stdout = b"A" * inspection.DEFAULT_LOG_PREFIX_BYTES + tail
    failure = _run_default(directory, _outcome(code=1, stdout=stdout))

    assert failure is not None
    assert tail.decode("ascii") not in failure
    assert '"truncated": true' in failure
    assert _paths(directory)["stdout"].read_bytes().endswith(tail)


def test_existing_frozen_artifacts_are_never_overwritten(tmp_path: Path) -> None:
    directory = tmp_path / "surprises"
    frozen = freeze_surprising_process_outcome(
        artifact_directory=directory,
        k=4,
        outcome=_outcome(),
        identity=_identity(),
        upstream_timeout_seconds=10,
        inspection_timeout_seconds=2,
    )
    before = {
        path: path.read_bytes()
        for path in (frozen.record_path, frozen.stdout_path, frozen.stderr_path)
    }

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        freeze_surprising_process_outcome(
            artifact_directory=directory,
            k=4,
            outcome=_outcome(stdout=b"replacement"),
            identity=_identity(),
            upstream_timeout_seconds=10,
            inspection_timeout_seconds=2,
        )
    assert all(path.read_bytes() == value for path, value in before.items())

    failure = _run_default(directory, _outcome(stdout=b"replacement"))
    assert failure is not None
    assert failure.startswith(
        "tiny upstream invocation did not complete ordinarily: "
        "termination_reason=exited exit_code=100"
    )
    assert '"disposition": "freeze error;' in failure
    assert all(path.read_bytes() == value for path, value in before.items())


def test_schema_rejects_unknown_fields_and_incompatible_outcomes(
    tmp_path: Path,
) -> None:
    frozen = freeze_surprising_process_outcome(
        artifact_directory=tmp_path / "surprises",
        k=4,
        outcome=_outcome(),
        identity=_identity(),
        upstream_timeout_seconds=10,
        inspection_timeout_seconds=2,
    )
    record = _load(frozen.record_path)
    record["unknown"] = True
    with pytest.raises(ValidationError):
        _validator().validate(record)
    record.pop("unknown")
    record["termination_reason"] = "timeout"
    record["exit_code"] = 100
    with pytest.raises(ValidationError):
        _validator().validate(record)


def test_upstream_adjacency_parser_normalizes_a_well_formed_graph() -> None:
    graph = parse_upstream_adjacency_list(K4_UPSTREAM_ADJACENCY.decode("utf-8"))

    assert graph.vertices == (0, 1, 2, 3)
    assert graph.edges == (
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    )


@pytest.mark.parametrize(
    ("output", "code"),
    [
        ("", "empty_output"),
        ("0: ", "missing_final_newline"),
        ("not an adjacency line\n", "malformed_line"),
        ("00: \n", "noncanonical_vertex_label"),
        ("0: \n0: \n", "duplicate_vertex_declaration"),
        ("0: 1 \n", "undeclared_endpoint"),
        ("0: 1 \n1: \n", "asymmetric_adjacency"),
        ("0: 1 1 \n1: 0 \n", "duplicate_neighbor"),
        ("0: 0 \n", "loop"),
        ("0: \n2: \n", "noncanonical_vertex_labels"),
    ],
)
def test_upstream_adjacency_parser_rejects_invalid_interfaces(
    output: str, code: str
) -> None:
    with pytest.raises(UpstreamAdjacencyFormatError) as caught:
        parse_upstream_adjacency_list(output)
    assert caught.value.code == code


def test_all_predicates_passed_branch_is_covered_only_synthetically(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(inspection, "minimum_degree", lambda graph: 3)
    monkeypatch.setattr(inspection, "find_induced_path", lambda graph, k: None)
    monkeypatch.setattr(
        inspection, "relevant_power_of_two_lengths", lambda vertex_count: ()
    )

    result = inspect_candidate_bytes(b"0: \n", 4)

    assert result["parse_succeeded"] is True
    assert result["all_candidate_predicates_passed"] is True
    assert result["checks"]["minimum_degree_at_least_3"] == {
        "observed": 3,
        "passed": True,
    }
