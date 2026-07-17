from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from tools import run_benchmark as benchmark
from tools.run_benchmark import (
    normalize_accepted_outcomes,
    normalize_process_outcome,
    outcome_is_accepted,
)


def _outcome(reason: str, code: int | None) -> dict[str, object]:
    return {
        "termination_reason": reason,
        "exit_code": code,
    }


def test_exit_zero_is_accepted_but_exit_100_is_not() -> None:
    accepted = normalize_accepted_outcomes([_outcome("exited", 0)])

    assert outcome_is_accepted("exited", 0, accepted)
    assert not outcome_is_accepted("exited", 100, accepted)


@pytest.mark.parametrize(
    ("reason", "code"),
    [
        ("timeout", None),
        ("spawn-error", None),
        ("signal", -9),
    ],
)
def test_timeout_spawn_error_and_signal_pairs_match_exactly(
    reason: str, code: int | None
) -> None:
    accepted = normalize_accepted_outcomes([_outcome(reason, code)])

    assert outcome_is_accepted(reason, code, accepted)


@pytest.mark.parametrize(
    ("reason", "code"),
    [
        ("exited", 0),
        ("exited", 100),
        ("signal", -1),
        ("timeout", None),
        ("spawn-error", None),
    ],
)
def test_compatible_process_outcomes_normalize(
    reason: str, code: int | None
) -> None:
    assert normalize_process_outcome(reason, code) == _outcome(reason, code)


@pytest.mark.parametrize(
    ("reason", "code"),
    [
        ("exited", -1),
        ("exited", None),
        ("exited", True),
        ("signal", 0),
        ("signal", False),
        ("timeout", 0),
        ("spawn-error", -1),
        ("unknown", None),
    ],
)
def test_incompatible_process_outcomes_are_rejected(
    reason: object, code: object
) -> None:
    with pytest.raises(ValueError):
        normalize_process_outcome(reason, code)


@pytest.mark.parametrize(
    "value",
    [
        [],
        {},
        ["not-an-object"],
        [{"termination_reason": "exited"}],
        [{"exit_code": 0}],
        [
            {
                "termination_reason": "exited",
                "exit_code": 0,
                "extra": False,
            }
        ],
        [_outcome("exited", -1)],
        [_outcome("signal", 0)],
        [_outcome("timeout", 0)],
        [_outcome("spawn-error", 1)],
    ],
)
def test_malformed_accepted_outcome_collections_are_rejected(
    value: object,
) -> None:
    with pytest.raises(ValueError):
        normalize_accepted_outcomes(value)


def test_duplicate_accepted_pairs_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate accepted process outcome"):
        normalize_accepted_outcomes(
            [
                _outcome("exited", 0),
                _outcome("timeout", None),
                _outcome("exited", 0),
            ]
        )


def test_matching_does_not_admit_cartesian_product_pairs() -> None:
    accepted = normalize_accepted_outcomes(
        [
            _outcome("exited", 0),
            _outcome("signal", -9),
        ]
    )

    assert not outcome_is_accepted("exited", 100, accepted)
    with pytest.raises(ValueError):
        outcome_is_accepted("exited", -9, accepted)
    with pytest.raises(ValueError):
        outcome_is_accepted("signal", 0, accepted)


def test_boolean_exit_codes_do_not_equal_integer_codes() -> None:
    accepted = normalize_accepted_outcomes([_outcome("exited", 1)])

    with pytest.raises(ValueError):
        outcome_is_accepted("exited", True, accepted)


@pytest.mark.parametrize(
    ("synthetic_kind", "expected"),
    [
        ("timeout", (b"partial stdout", b"partial stderr", None, "timeout")),
        (
            "spawn-error",
            (b"", b"synthetic spawn failure", None, "spawn-error"),
        ),
        ("signal", (b"signal stdout", b"signal stderr", -9, "signal")),
    ],
)
def test_execute_maps_timeout_spawn_error_and_signal_outcomes(
    synthetic_kind: str,
    expected: tuple[bytes, bytes, int | None, str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def synthetic_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        if synthetic_kind == "timeout":
            raise subprocess.TimeoutExpired(
                cmd=["synthetic-child"],
                timeout=1,
                output=b"partial stdout",
                stderr=b"partial stderr",
            )
        if synthetic_kind == "spawn-error":
            raise OSError("synthetic spawn failure")
        return subprocess.CompletedProcess(
            args=["synthetic-child"],
            returncode=-9,
            stdout=b"signal stdout",
            stderr=b"signal stderr",
        )

    monkeypatch.setattr(benchmark.subprocess, "run", synthetic_run)
    monkeypatch.setattr(benchmark, "resource_snapshot", lambda: None)

    observed = benchmark.execute(
        ["synthetic-child"],
        tmp_path,
        {},
        1,
    )

    assert observed[:4] == expected
    assert observed[4] >= 0
    assert observed[5] is None
    assert observed[6] is None
    assert observed[7] == [
        "CPU time and peak memory collection are unavailable on this platform."
    ]


def test_accepted_outcome_serialization_is_deterministic() -> None:
    values = [
        _outcome("spawn-error", None),
        _outcome("exited", 100),
        _outcome("timeout", None),
        _outcome("signal", -9),
        _outcome("exited", 0),
    ]

    first = normalize_accepted_outcomes(values)
    second = normalize_accepted_outcomes(list(reversed(values)))
    assert first == second == [
        _outcome("exited", 0),
        _outcome("exited", 100),
        _outcome("signal", -9),
        _outcome("timeout", None),
        _outcome("spawn-error", None),
    ]
    assert json.dumps(first, separators=(",", ":"), sort_keys=True) == (
        '[{"exit_code":0,"termination_reason":"exited"},'
        '{"exit_code":100,"termination_reason":"exited"},'
        '{"exit_code":-9,"termination_reason":"signal"},'
        '{"exit_code":null,"termination_reason":"timeout"},'
        '{"exit_code":null,"termination_reason":"spawn-error"}]'
    )


def test_unaccepted_execution_preserves_valid_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repository_root = Path(__file__).resolve().parents[2]
    schema_text = (
        repository_root / "schemas" / "benchmark-result.schema.json"
    ).read_text(encoding="utf-8")

    case_path = tmp_path / "benchmarks" / "cases" / "synthetic.json"
    result_path = tmp_path / "benchmarks" / "results" / "unexpected.json"
    executable = tmp_path / "build" / "synthetic-child.exe"
    schema_path = tmp_path / "schemas" / "benchmark-result.schema.json"
    for directory in (
        case_path.parent,
        result_path.parent,
        executable.parent,
        schema_path.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    executable.write_bytes(b"synthetic executable identity\n")
    schema_path.write_text(schema_text, encoding="utf-8", newline="\n")
    case_path.write_text(
        json.dumps(
            {
                "accepted_outcomes": [_outcome("exited", 0)],
                "arguments": ["3"],
                "case_id": "synthetic-unexpected-exit",
                "description": "Synthetic unaccepted outcome artifact test.",
                "environment": {},
                "executable": "build/synthetic-child.exe",
                "k": 3,
                "limitations": ["Synthetic unit-test process outcome."],
                "schema_version": "1.0",
                "thread_count": 1,
                "timeout_seconds": 1,
                "working_directory": ".",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    def repository_relative(path: Path) -> str:
        return path.resolve().relative_to(tmp_path.resolve()).as_posix()

    monkeypatch.setattr(benchmark, "REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr(benchmark, "repository_relative", repository_relative)
    monkeypatch.setattr(
        benchmark,
        "load_upstream_provenance",
        lambda: {"resolved_commit": "0" * 40},
    )
    monkeypatch.setattr(
        benchmark,
        "repository_state",
        lambda: ("1" * 40, "clean", "1" * 40),
    )
    monkeypatch.setattr(
        benchmark,
        "cmake_compiler",
        lambda case: ("synthetic-compiler", ["-O2"], []),
    )
    monkeypatch.setattr(
        benchmark,
        "execute",
        lambda command, cwd, environment, timeout: (
            b"candidate output\n",
            b"child diagnostic\n",
            100,
            "exited",
            0.25,
            0.1,
            4096,
            [],
        ),
    )

    return_code = benchmark.main(
        [
            "benchmarks/cases/synthetic.json",
            "--output",
            "benchmarks/results/unexpected.json",
        ]
    )

    assert return_code == benchmark.UNACCEPTED_OUTCOME_EXIT_CODE
    stdout_path = result_path.with_suffix(".stdout.txt")
    stderr_path = result_path.with_suffix(".stderr.txt")
    assert stdout_path.read_bytes() == b"candidate output\n"
    assert stderr_path.read_bytes() == b"child diagnostic\n"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["accepted_outcomes"] == [_outcome("exited", 0)]
    assert result["termination_reason"] == "exited"
    assert result["exit_code"] == 100
    assert result["outcome_accepted"] is False
    assert result["classification"] == "EMPIRICAL_OBSERVATION"

    diagnostic = json.loads(capsys.readouterr().out)
    assert diagnostic["ok"] is False
    assert diagnostic["actual_outcome"] == _outcome("exited", 100)
    for name, path in {
        "result": result_path,
        "stdout": stdout_path,
        "stderr": stderr_path,
    }.items():
        assert diagnostic["artifacts"][name] == {
            "path": repository_relative(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }


def test_streams_are_frozen_before_outcome_matching(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repository_root = Path(__file__).resolve().parents[2]
    case_path = tmp_path / "benchmarks" / "cases" / "synthetic.json"
    result_path = tmp_path / "benchmarks" / "results" / "matcher-error.json"
    stdout_path = result_path.with_suffix(".stdout.txt")
    stderr_path = result_path.with_suffix(".stderr.txt")
    executable = tmp_path / "build" / "synthetic-child.exe"
    schema_path = tmp_path / "schemas" / "benchmark-result.schema.json"
    for directory in (
        case_path.parent,
        result_path.parent,
        executable.parent,
        schema_path.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    executable.write_bytes(b"synthetic executable identity\n")
    schema_path.write_bytes(
        (repository_root / "schemas" / "benchmark-result.schema.json").read_bytes()
    )
    case_path.write_text(
        json.dumps(
            {
                "accepted_outcomes": [_outcome("exited", 0)],
                "arguments": ["3"],
                "case_id": "synthetic-matcher-error",
                "description": "Prove streams precede outcome matching.",
                "environment": {},
                "executable": "build/synthetic-child.exe",
                "k": 3,
                "limitations": ["Synthetic unit-test process outcome."],
                "schema_version": "1.0",
                "thread_count": 1,
                "timeout_seconds": 1,
                "working_directory": ".",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    def repository_relative(path: Path) -> str:
        return path.resolve().relative_to(tmp_path.resolve()).as_posix()

    expected_stdout = b"unaccepted candidate output\xff"
    expected_stderr = b"upstream diagnostic\xfe"
    real_sha256_file = benchmark.sha256_file
    hashed_paths: list[Path] = []

    def tracked_sha256_file(path: Path) -> str:
        hashed_paths.append(path.resolve())
        return real_sha256_file(path)

    def fail_after_asserting_frozen(
        reason: object,
        code: object,
        accepted: object,
    ) -> bool:
        assert reason == "exited"
        assert code == 100
        assert stdout_path.read_bytes() == expected_stdout
        assert stderr_path.read_bytes() == expected_stderr
        assert stdout_path.resolve() in hashed_paths
        assert stderr_path.resolve() in hashed_paths
        raise ValueError("synthetic outcome matcher failure")

    monkeypatch.setattr(benchmark, "REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr(benchmark, "repository_relative", repository_relative)
    monkeypatch.setattr(benchmark, "sha256_file", tracked_sha256_file)
    monkeypatch.setattr(
        benchmark,
        "load_upstream_provenance",
        lambda: {"resolved_commit": "0" * 40},
    )
    monkeypatch.setattr(
        benchmark,
        "repository_state",
        lambda: ("1" * 40, "clean", "1" * 40),
    )
    monkeypatch.setattr(
        benchmark,
        "cmake_compiler",
        lambda case: ("synthetic-compiler", ["-O2"], []),
    )
    monkeypatch.setattr(
        benchmark,
        "execute",
        lambda command, cwd, environment, timeout: (
            expected_stdout,
            expected_stderr,
            100,
            "exited",
            0.25,
            0.1,
            4096,
            [],
        ),
    )
    monkeypatch.setattr(benchmark, "outcome_is_accepted", fail_after_asserting_frozen)

    return_code = benchmark.main(
        [
            "benchmarks/cases/synthetic.json",
            "--output",
            "benchmarks/results/matcher-error.json",
        ]
    )

    assert return_code == 1
    assert stdout_path.read_bytes() == expected_stdout
    assert stderr_path.read_bytes() == expected_stderr
    assert not result_path.exists()
    assert json.loads(capsys.readouterr().out) == {
        "error": "synthetic outcome matcher failure",
        "ok": False,
    }
