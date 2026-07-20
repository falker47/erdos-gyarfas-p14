from __future__ import annotations

import base64
import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import pytest
from jsonschema import FormatChecker
from jsonschema.validators import validator_for

from tools import run_inspector_timeout_stability as runner
from tools import verify_inspector_timeout_stability as verifier


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_RELATIVE_PATH = (
    "schemas/inspector-timeout-stability-evidence.schema.json"
)
FIXED_TIMESTAMP = "2026-07-19T12:00:00.000000Z"
SECRET_ENVIRONMENT_NAME = "INSPECTOR_STABILITY_TEST_SECRET"


@dataclass(slots=True)
class Bundle:
    root: Path
    report_path: Path
    schema_path: Path
    config: runner.RunnerConfig
    calls: list[dict[str, Any]]
    tool_values: dict[str, str]
    sibling_sentinel: Path
    exit_code: int
    report: dict[str, Any]


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


def _load_report(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.write_bytes(_canonical_json_bytes(report))


def _schema_validator(schema_path: Path):
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator_type = validator_for(schema)
    validator_type.check_schema(schema)
    return validator_type(schema, format_checker=FormatChecker())


def _stream_bytes(stream: dict[str, Any]) -> bytes:
    value = base64.b64decode(stream["base64"], validate=True)
    assert len(value) == stream["byte_length"]
    assert hashlib.sha256(value).hexdigest() == stream["sha256"]
    return value


def _replace_run_stdout(run: dict[str, Any], stdout: bytes, passed: int) -> None:
    run["stdout"] = {
        "base64": base64.b64encode(stdout).decode("ascii"),
        "byte_length": len(stdout),
        "sha256": hashlib.sha256(stdout).hexdigest(),
    }
    run["pytest_summary"] = {
        "parsed": True,
        "passed": passed,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "diagnostic": None,
    }


def _create_repository(base: Path) -> tuple[Path, Path, dict[str, str], Path]:
    root = base / "repository"
    root.mkdir(parents=True)
    source_schema = PROJECT_ROOT / SCHEMA_RELATIVE_PATH
    for relative_path in runner.SOURCE_PATHS:
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative_path == SCHEMA_RELATIVE_PATH:
            destination.write_bytes(source_schema.read_bytes())
        else:
            destination.write_bytes(
                f"synthetic source fixture: {relative_path}\n".encode("utf-8")
            )

    executable_directory = root / "fixtures" / "executables"
    executable_directory.mkdir(parents=True)
    executable_paths = {
        "PYTHON": executable_directory / "python-fixture.exe",
        "EG_CMAKE": executable_directory / "cmake-fixture.exe",
        "EG_CXX": executable_directory / "cxx-fixture.exe",
        "EG_NINJA": executable_directory / "ninja-fixture.exe",
        "EG_MAKE": executable_directory / "make-fixture.exe",
    }
    for name, path in executable_paths.items():
        path.write_bytes(f"synthetic executable: {name}\n".encode("ascii"))
    tool_values = {
        name: executable_paths[name].resolve().as_posix()
        for name in runner.TOOL_NAMES
    }
    python_value = executable_paths["PYTHON"].resolve().as_posix()

    sibling_sentinel = root / "build" / "unrelated-output" / "keep.txt"
    sibling_sentinel.parent.mkdir(parents=True)
    sibling_sentinel.write_bytes(b"must survive task-owned cleanup\n")
    return root, root / SCHEMA_RELATIVE_PATH, tool_values, Path(python_value)


def _run_bundle(
    base: Path,
    *,
    failure_at: int | None = None,
    interrupt_at: int | None = None,
    full_pass_counts: tuple[int, int] = (299, 299),
    extra_tracked_sources: dict[str, bytes] | None = None,
) -> Bundle:
    root, schema_path, tool_values, python_path = _create_repository(base)
    for relative_path, data in (extra_tracked_sources or {}).items():
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    report_path = (
        root
        / "ops"
        / runner.TASK_ID
        / "STABILITY_EVIDENCE.json"
    )
    config = runner.RunnerConfig(
        repository_root=root,
        report_path=report_path,
        basetemp_root=runner.DEFAULT_BASETEMP_ROOT,
        tool_values=tool_values,
        python_executable=python_path.resolve().as_posix(),
    )
    calls: list[dict[str, Any]] = []
    in_process_runner = False

    def fake_process_runner(
        argv: list[str], *, cwd: Path, env: dict[str, str]
    ) -> SimpleNamespace:
        nonlocal in_process_runner
        assert not in_process_runner, "process attempts must be strictly serial"
        in_process_runner = True
        try:
            call_number = len(calls) + 1
            persisted = _load_report(report_path)
            phase = "focused" if runner.FOCUSED_TEST_PATH in argv else "full_suite"
            basetemp = argv[-1]
            basetemp_path = cwd / basetemp
            assert cwd == root.resolve()
            assert argv[-2] == "--basetemp"
            assert basetemp_path.is_dir()
            (basetemp_path / "pytest-owned.tmp").write_bytes(
                f"attempt {call_number}\n".encode("ascii")
            )
            if phase == "focused":
                passed = 31
            else:
                passed = full_pass_counts[call_number - 26]
            return_code = 0
            stdout = (
                f"synthetic attempt {call_number}\n"
                f"{passed} passed in 0.01s\n"
            ).encode("ascii")
            if failure_at == call_number:
                return_code = 1
                stdout = b"30 passed, 1 failed in 0.01s\n"
            stderr = f"synthetic stderr {call_number}\n".encode("ascii")
            calls.append(
                {
                    "argv": list(argv),
                    "basetemp": basetemp,
                    "phase": phase,
                    "persisted_run_count": len(persisted["runs"]),
                    "tool_environment": {
                        name: env.get(name) for name in runner.TOOL_NAMES
                    },
                    "secret": env.get(SECRET_ENVIRONMENT_NAME),
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": return_code,
                }
            )
            if interrupt_at == call_number:
                raise runner.ProcessInterrupted(
                    returncode=-9,
                    stdout=stdout,
                    stderr=stderr,
                )
            return SimpleNamespace(
                returncode=return_code,
                stdout=stdout,
                stderr=stderr,
            )
        finally:
            in_process_runner = False

    exit_code, report = runner.run_evidence(
        config,
        process_runner=fake_process_runner,
        utc_now=lambda: FIXED_TIMESTAMP,
        monotonic=lambda: 0.0,
        git_checker=lambda _root: None,
        tracked_path_provider=lambda _root: tuple(
            sorted((extra_tracked_sources or {}).keys())
        ),
    )
    return Bundle(
        root=root,
        report_path=report_path,
        schema_path=schema_path,
        config=config,
        calls=calls,
        tool_values=tool_values,
        sibling_sentinel=root / "build" / "unrelated-output" / "keep.txt",
        exit_code=exit_code,
        report=report,
    )


@pytest.fixture(scope="module")
def successful_bundle(tmp_path_factory: pytest.TempPathFactory) -> Bundle:
    return _run_bundle(tmp_path_factory.mktemp("inspector-stability-success"))


def _mutated_report(
    tmp_path: Path,
    bundle: Bundle,
    mutate: Callable[[dict[str, Any]], None],
) -> Path:
    report = copy.deepcopy(bundle.report)
    mutate(report)
    path = tmp_path / "mutated-report.json"
    _write_report(path, report)
    return path


def _verify_failure(
    path: Path,
    bundle: Bundle,
    match: str,
) -> None:
    with pytest.raises(verifier.EvidenceVerificationError, match=match):
        verifier.verify_report(
            path,
            repository_root=bundle.root,
            schema_path=bundle.schema_path,
            verify_git=False,
        )


def test_canonical_success_is_schema_valid_and_independently_verified(
    successful_bundle: Bundle,
) -> None:
    bundle = successful_bundle
    raw = bundle.report_path.read_bytes()
    assert bundle.exit_code == 0
    assert raw == _canonical_json_bytes(bundle.report)
    assert _load_report(bundle.report_path) == bundle.report
    _schema_validator(bundle.schema_path).validate(bundle.report)

    result = verifier.verify_report(
        bundle.report_path,
        repository_root=bundle.root,
        schema_path=bundle.schema_path,
        verify_git=False,
    )
    assert result["ok"] is True
    assert result["focused_runs"] == 25
    assert result["focused_passes_each"] == 31
    assert result["full_suite_runs"] == 2
    assert result["full_suite_passes_each"] == 299


def test_runner_is_serial_and_uses_exact_phase_sequence(
    successful_bundle: Bundle,
) -> None:
    bundle = successful_bundle
    runs = bundle.report["runs"]
    assert [run["sequence"] for run in runs] == list(range(1, 28))
    assert [run["phase"] for run in runs] == ["focused"] * 25 + [
        "full_suite"
    ] * 2
    assert [run["phase_index"] for run in runs] == list(range(1, 26)) + [1, 2]
    assert [call["persisted_run_count"] for call in bundle.calls] == list(
        range(27)
    )
    assert [call["phase"] for call in bundle.calls] == ["focused"] * 25 + [
        "full_suite"
    ] * 2
    for call in bundle.calls[:25]:
        assert call["tool_environment"] == {
            name: None for name in runner.TOOL_NAMES
        }
    for call in bundle.calls[25:]:
        assert call["tool_environment"] == bundle.tool_values


def test_stream_base64_lengths_and_hashes_agree(
    successful_bundle: Bundle,
) -> None:
    for run_record, call in zip(
        successful_bundle.report["runs"], successful_bundle.calls, strict=True
    ):
        assert _stream_bytes(run_record["stdout"]) == call["stdout"]
        assert _stream_bytes(run_record["stderr"]) == call["stderr"]


def test_cleanup_removes_only_fixed_task_owned_paths(
    successful_bundle: Bundle,
) -> None:
    bundle = successful_bundle
    cleanup = bundle.report["cleanup"]
    assert cleanup["root"] == runner.DEFAULT_BASETEMP_ROOT
    assert cleanup["expected"] == [run["basetemp_path"] for run in bundle.report["runs"]]
    assert cleanup["removed"] == cleanup["expected"]
    assert cleanup["remaining"] == []
    assert cleanup["completed"] is True
    assert not (bundle.root / runner.DEFAULT_BASETEMP_ROOT).exists()
    assert bundle.sibling_sentinel.read_bytes() == b"must survive task-owned cleanup\n"


def test_first_failure_preserves_partial_report_and_never_retries(
    tmp_path: Path,
) -> None:
    bundle = _run_bundle(tmp_path, failure_at=3)
    assert bundle.exit_code == 1
    assert len(bundle.calls) == 3
    assert [call["persisted_run_count"] for call in bundle.calls] == [0, 1, 2]
    assert bundle.report_path.read_bytes() == _canonical_json_bytes(bundle.report)
    _schema_validator(bundle.schema_path).validate(bundle.report)
    assert bundle.report["completed"] is False
    assert [run["status"] for run in bundle.report["runs"]] == [
        "passed",
        "passed",
        "failed",
    ]
    assert bundle.report["summary"]["recorded_run_count"] == 3
    assert bundle.report["summary"]["failed_run_count"] == 1
    assert bundle.report["summary"]["retries"] == 0
    assert bundle.report["summary"]["stop_reason"] == "failure"


def test_interruption_preserves_captured_streams_and_never_retries(
    tmp_path: Path,
) -> None:
    bundle = _run_bundle(tmp_path, interrupt_at=2)
    assert bundle.exit_code == 1
    assert len(bundle.calls) == 2
    assert [run["status"] for run in bundle.report["runs"]] == [
        "passed",
        "interrupted",
    ]
    interrupted = bundle.report["runs"][1]
    assert interrupted["exit_code"] == -9
    assert _stream_bytes(interrupted["stdout"]) == bundle.calls[1]["stdout"]
    assert _stream_bytes(interrupted["stderr"]) == bundle.calls[1]["stderr"]
    assert interrupted["pytest_summary"]["parsed"] is False
    assert bundle.report["completed"] is False
    assert bundle.report["summary"]["recorded_run_count"] == 2
    assert bundle.report["summary"]["retries"] == 0
    assert bundle.report["summary"]["stop_reason"] == "interrupted"
    _schema_validator(bundle.schema_path).validate(bundle.report)


def test_post_process_interruption_preserves_completed_attempt_streams(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = runner._current_source_fingerprint
    calls = 0

    def interrupt_first_post_process_inventory(
        root: Path, paths: tuple[str, ...]
    ) -> str:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt
        return original(root, paths)

    monkeypatch.setattr(
        runner,
        "_current_source_fingerprint",
        interrupt_first_post_process_inventory,
    )
    bundle = _run_bundle(tmp_path)
    assert bundle.exit_code == 1
    assert len(bundle.calls) == 1
    assert len(bundle.report["runs"]) == 1
    interrupted = bundle.report["runs"][0]
    assert interrupted["status"] == "interrupted"
    assert interrupted["exit_code"] == 0
    assert _stream_bytes(interrupted["stdout"]) == bundle.calls[0]["stdout"]
    assert _stream_bytes(interrupted["stderr"]) == bundle.calls[0]["stderr"]
    assert interrupted["pytest_summary"]["parsed"] is True
    assert bundle.report["summary"]["stop_reason"] == "interrupted"
    assert bundle.report["summary"]["failure_detail"] == (
        "runner interrupted after subprocess completion"
    )
    _schema_validator(bundle.schema_path).validate(bundle.report)
    assert bundle.report["cleanup"]["completed"] is True
    assert not (bundle.root / runner.DEFAULT_BASETEMP_ROOT).exists()
    _verify_failure(bundle.report_path, bundle, "report completed must be true")


def test_post_process_inventory_failure_records_null_source_fingerprint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = runner._current_source_fingerprint
    calls = 0

    def fail_first_post_process_inventory(
        root: Path, paths: tuple[str, ...]
    ) -> str:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise runner.RunnerError("synthetic post-run inventory failure")
        return original(root, paths)

    monkeypatch.setattr(
        runner,
        "_current_source_fingerprint",
        fail_first_post_process_inventory,
    )
    bundle = _run_bundle(tmp_path)
    assert bundle.exit_code == 1
    assert len(bundle.calls) == 1
    failed = bundle.report["runs"][0]
    assert failed["status"] == "failed"
    assert failed["exit_code"] == 0
    assert failed["source_fingerprint_after"] is None
    assert _stream_bytes(failed["stdout"]) == bundle.calls[0]["stdout"]
    assert _stream_bytes(failed["stderr"]) == bundle.calls[0]["stderr"]
    assert bundle.report["summary"]["failure_detail"] == (
        "source fingerprint could not be acquired after the run"
    )
    _schema_validator(bundle.schema_path).validate(bundle.report)


def test_existing_report_is_never_overwritten(
    successful_bundle: Bundle,
) -> None:
    bundle = successful_bundle
    before = bundle.report_path.read_bytes()
    attempted = False

    def forbidden_process_runner(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        nonlocal attempted
        attempted = True
        raise AssertionError("process runner must not be called")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        runner.run_evidence(
            bundle.config,
            process_runner=forbidden_process_runner,
            git_checker=lambda _root: None,
        )
    assert attempted is False
    assert bundle.report_path.read_bytes() == before


def test_tracked_source_inventory_failure_is_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure = SimpleNamespace(
        returncode=1,
        stdout=b"",
        stderr=b"synthetic git inventory failure",
    )
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *_args, **_kwargs: failure,
    )
    with pytest.raises(
        runner.RunnerError,
        match=(
            "cannot inventory tracked source files: "
            "synthetic git inventory failure"
        ),
    ):
        runner._git_tracked_paths(tmp_path)


def test_source_file_hash_mismatch_is_detected(
    successful_bundle: Bundle,
) -> None:
    bundle = successful_bundle
    source = bundle.root / "tools" / "inspect_upstream_candidate.py"
    original = source.read_bytes()
    try:
        source.write_bytes(original + b"changed after evidence\n")
        _verify_failure(
            bundle.report_path,
            bundle,
            "source byte length mismatch|source SHA-256 mismatch",
        )
    finally:
        source.write_bytes(original)


def test_extra_tracked_execution_source_is_pinned_and_mutation_is_rejected(
    tmp_path: Path,
) -> None:
    relative_path = "extra/tracked_execution_input.py"
    bundle = _run_bundle(
        tmp_path,
        extra_tracked_sources={relative_path: b"VALUE = 1\n"},
    )
    source_paths = [
        record["path"] for record in bundle.report["source_files"]
    ]
    assert relative_path in source_paths
    assert relative_path in bundle.report["execution_project_revision"][
        "fingerprint_scope"
    ]
    (bundle.root / relative_path).write_bytes(b"VALUE = 2\n")
    _verify_failure(bundle.report_path, bundle, "source SHA-256 mismatch")


@pytest.mark.parametrize("case", ["duplicate", "missing", "sequence"])
def test_duplicate_missing_and_malformed_runs_are_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
    case: str,
) -> None:
    expected = {
        "duplicate": "schema validation failed",
        "missing": "expected exactly 27 run records",
        "sequence": "run sequences must be exactly",
    }[case]

    def mutate(report: dict[str, Any]) -> None:
        if case == "duplicate":
            report["runs"][1] = copy.deepcopy(report["runs"][0])
        elif case == "missing":
            report["runs"].pop()
        else:
            report["runs"][0]["sequence"] = 2

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    _verify_failure(path, successful_bundle, expected)


def test_focused_count_mismatch_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def mutate(report: dict[str, Any]) -> None:
        _replace_run_stdout(
            report["runs"][0], b"30 passed in 0.01s\n", passed=30
        )

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    _verify_failure(path, successful_bundle, "focused pass count is 30")


def test_inconsistent_full_suite_counts_are_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def mutate(report: dict[str, Any]) -> None:
        _replace_run_stdout(
            report["runs"][26], b"300 passed in 0.01s\n", passed=300
        )

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    _verify_failure(path, successful_bundle, "full-suite pass counts are inconsistent")


def test_nonzero_exit_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    path = _mutated_report(
        tmp_path,
        successful_bundle,
        lambda report: report["runs"][0].update(
            {"exit_code": 1, "status": "failed"}
        ),
    )
    _verify_failure(path, successful_bundle, "exit code is nonzero")


def test_completed_false_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    path = _mutated_report(
        tmp_path,
        successful_bundle,
        lambda report: report.update({"completed": False}),
    )
    _verify_failure(path, successful_bundle, "report completed must be true")


def test_schema_rejects_nested_unknown_property(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def mutate(report: dict[str, Any]) -> None:
        report["runs"][0]["stdout"]["unknown"] = True

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    _verify_failure(path, successful_bundle, "schema validation failed")


def test_missing_root_limitations_are_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    path = _mutated_report(
        tmp_path,
        successful_bundle,
        lambda report: report.pop("limitations"),
    )
    _verify_failure(path, successful_bundle, "schema validation failed")


def test_noncanonical_base64_is_rejected_semantically(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def mutate(report: dict[str, Any]) -> None:
        report["runs"][0]["stdout"]["base64"] = "AB=="

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    _verify_failure(path, successful_bundle, "Base64 is not canonical")


@pytest.mark.parametrize("stream_name", ["stdout", "stderr"])
def test_stream_hash_mismatch_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
    stream_name: str,
) -> None:
    def mutate(report: dict[str, Any]) -> None:
        report["runs"][0][stream_name]["sha256"] = "0" * 64

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    _verify_failure(path, successful_bundle, "SHA-256 mismatch")


def test_arbitrary_process_environment_is_not_captured(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "test-secret-value-that-must-not-enter-the-report"
    monkeypatch.setenv(SECRET_ENVIRONMENT_NAME, secret)
    bundle = _run_bundle(tmp_path)
    assert all(call["secret"] is None for call in bundle.calls)
    assert secret.encode("utf-8") not in bundle.report_path.read_bytes()
    assert set(bundle.report["environment"]) == {
        "python_version",
        "python_implementation",
        "python_executable",
        "operating_system",
        "architecture",
        "machine_identifier",
        "processor_identifier",
        "cpu_count",
        "working_directory",
        "tool_overrides",
        "limitations",
    }


def test_default_process_runner_kills_drains_and_preserves_interrupted_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeProcess:
        def __init__(self) -> None:
            self.returncode = -9
            self.communicate_calls = 0
            self.killed = False

        def communicate(self) -> tuple[bytes, bytes]:
            self.communicate_calls += 1
            if self.communicate_calls == 1:
                raise KeyboardInterrupt
            return b"partial stdout\n", b"partial stderr\n"

        def kill(self) -> None:
            self.killed = True

    process = FakeProcess()

    def fake_popen(*_args: Any, **_kwargs: Any) -> FakeProcess:
        return process

    monkeypatch.setattr(runner.subprocess, "Popen", fake_popen)
    with pytest.raises(runner.ProcessInterrupted) as raised:
        runner._default_process_runner(
            ["python", "-m", "pytest"],
            cwd=tmp_path,
            env={"PATH": "synthetic"},
        )
    assert process.killed is True
    assert process.communicate_calls == 2
    assert raised.value.returncode == -9
    assert raised.value.stdout == b"partial stdout\n"
    assert raised.value.stderr == b"partial stderr\n"


def test_effective_and_resolved_tool_identity_mismatch_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def mutate(report: dict[str, Any]) -> None:
        report["environment"]["tool_overrides"]["EG_CMAKE"][
            "effective_value"
        ] = bundle_value = report["environment"]["tool_overrides"]["EG_CXX"][
            "effective_value"
        ]
        assert bundle_value

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    _verify_failure(path, successful_bundle, "effective value resolves to")


def test_same_host_environment_rehash_rejects_mutated_tool(
    tmp_path: Path,
) -> None:
    bundle = _run_bundle(tmp_path)
    result = verifier.verify_report(
        bundle.report_path,
        repository_root=bundle.root,
        schema_path=bundle.schema_path,
        verify_git=False,
        rehash_environment=True,
    )
    assert result["ok"] is True
    tool = Path(bundle.tool_values["EG_CMAKE"])
    changed = bytearray(tool.read_bytes())
    changed[0] ^= 1
    tool.write_bytes(changed)
    with pytest.raises(
        verifier.EvidenceVerificationError,
        match="EG_CMAKE SHA-256 does not match",
    ):
        verifier.verify_report(
            bundle.report_path,
            repository_root=bundle.root,
            schema_path=bundle.schema_path,
            verify_git=False,
            rehash_environment=True,
        )


def test_environment_trust_boundary_limitation_is_required(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def mutate(report: dict[str, Any]) -> None:
        report["environment"]["limitations"].pop(0)

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    _verify_failure(path, successful_bundle, "environment limitations omit")


def test_optional_machine_limitation_is_accepted(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def mutate(report: dict[str, Any]) -> None:
        report["environment"]["machine_identifier"] = None
        limitation = "Machine identifier is unavailable."
        if limitation not in report["environment"]["limitations"]:
            report["environment"]["limitations"].append(limitation)

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    result = verifier.verify_report(
        path,
        repository_root=successful_bundle.root,
        schema_path=successful_bundle.schema_path,
        verify_git=False,
    )
    assert result["ok"] is True


def test_completed_report_with_null_finish_has_precise_failure(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    path = _mutated_report(
        tmp_path,
        successful_bundle,
        lambda report: report.update({"execution_finished_at_utc": None}),
    )
    _verify_failure(path, successful_bundle, "must be a non-null UTC timestamp")


def test_cleanup_root_substitution_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def mutate(report: dict[str, Any]) -> None:
        report["cleanup"]["root"] = "build/not-task-owned"

    path = _mutated_report(tmp_path, successful_bundle, mutate)
    _verify_failure(path, successful_bundle, "cleanup root is not the fixed task-owned root")


def test_duplicate_json_key_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    raw = successful_bundle.report_path.read_bytes()
    field = b'  "schema_version": "1.0",\n'
    assert raw.count(field) == 1
    path = tmp_path / "duplicate-key.json"
    path.write_bytes(raw.replace(field, field + field, 1))
    _verify_failure(path, successful_bundle, "duplicate JSON key")


def test_noncanonical_json_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    path = tmp_path / "noncanonical.json"
    path.write_text(
        json.dumps(successful_bundle.report, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    _verify_failure(path, successful_bundle, "report is not canonical")
