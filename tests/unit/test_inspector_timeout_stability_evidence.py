from __future__ import annotations

import base64
import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
from typing import Any, Callable

import pytest
from jsonschema import FormatChecker
from jsonschema.validators import validator_for

from tools import run_inspector_timeout_stability as runner
from tools import verify_inspector_timeout_stability as verifier


PROJECT_ROOT = Path(__file__).resolve().parents[2]
V2_SCHEMA_RELATIVE_PATH = (
    "schemas/inspector-timeout-stability-evidence-v2.schema.json"
)

FOCUSED_NODE_IDS = (
    "tests/unit/test_upstream_candidate_inspection.py::test_one",
    "tests/unit/test_upstream_candidate_inspection.py::test_two",
)
FULL_SUITE_NODE_IDS = (
    *FOCUSED_NODE_IDS,
    "tests/unit/test_graph.py::test_three",
    "tests/integration/test_verifier_cli.py::test_four",
)


class ScriptedClock:
    """Deterministic strictly increasing UTC and monotonic test clock."""

    def __init__(self) -> None:
        self._ticks = 0

    def utc_now(self) -> str:
        self._ticks += 1
        seconds, micros = divmod(self._ticks, 1_000_000)
        return f"2026-07-20T08:00:{seconds:02d}.{micros:06d}Z"

    def monotonic_ns(self) -> int:
        self._ticks += 1
        return self._ticks * 1_000


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


def _captured_stream(value: bytes) -> dict[str, Any]:
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "byte_length": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
    }


def _nul_paths(paths: tuple[str, ...] | list[str]) -> bytes:
    return b"".join(path.encode("utf-8") + b"\0" for path in paths)


def _porcelain_v2_ordinary(path: str, xy: str = ".M") -> bytes:
    zero = "0" * 40
    return (
        f"1 {xy} N... 100644 100644 100644 {zero} {zero} {path}"
    ).encode("utf-8") + b"\0"


def _porcelain_v2_unmerged(path: str, xy: str) -> bytes:
    zero = "0" * 40
    return (
        f"u {xy} N... 100644 100644 100644 100644 "
        f"{zero} {zero} {zero} {path}"
    ).encode("utf-8") + b"\0"


def _porcelain_v2_status(
    *,
    modified: tuple[str, ...] = (),
    deleted: tuple[str, ...] = (),
    staged: tuple[str, ...] = (),
    untracked: tuple[str, ...] = (),
) -> bytes:
    staged_set = set(staged)
    modified_set = set(modified)
    deleted_set = set(deleted)
    records = [
        _porcelain_v2_ordinary(path, "MM" if path in staged_set else ".M")
        for path in modified
    ]
    records.extend(
        _porcelain_v2_ordinary(path, "MD" if path in staged_set else ".D")
        for path in deleted
    )
    records.extend(
        _porcelain_v2_ordinary(path, "M.")
        for path in staged
        if path not in modified_set | deleted_set
    )
    records.extend(f"? {path}".encode("utf-8") + b"\0" for path in untracked)
    return b"".join(records)


@dataclass(slots=True)
class SyntheticGitState:
    tracked: tuple[str, ...]
    modified: tuple[str, ...] = ()
    deleted: tuple[str, ...] = ()
    staged: tuple[str, ...] = ()
    untracked: tuple[str, ...] = ()
    ignored: tuple[str, ...] = ()

    def status_stdout(self) -> bytes:
        return _porcelain_v2_status(
            modified=self.modified,
            deleted=self.deleted,
            staged=self.staged,
            untracked=self.untracked,
        )

    def tracked_stdout(self) -> bytes:
        return _nul_paths(self.tracked)

    def untracked_stdout(self) -> bytes:
        return _nul_paths(self.untracked)

    def ignored_stdout(self) -> bytes:
        return _nul_paths(self.ignored)

    def staged_stdout(self) -> bytes:
        return _nul_paths(self.staged)


def _collection_stdout(node_ids: tuple[str, ...]) -> bytes:
    noun = "test" if len(node_ids) == 1 else "tests"
    return (
        "\n".join(node_ids)
        + f"\n\n{len(node_ids)} {noun} collected in 0.01s\n"
    ).encode("utf-8")


class SyntheticProcessRunner:
    """In-process stand-in for two collections and all 27 stability attempts."""

    def __init__(
        self,
        *,
        report_path: Path,
        failure_at: int | None = None,
        interrupt_at: int | None = None,
        before_call: Callable[[int, list[str]], None] | None = None,
        after_call: Callable[[int, list[str]], None] | None = None,
    ) -> None:
        self.report_path = report_path
        self.failure_at = failure_at
        self.interrupt_at = interrupt_at
        self.before_call = before_call
        self.after_call = after_call
        self.calls: list[dict[str, Any]] = []
        self._in_call = False
        self._stability_calls = 0

    def __call__(
        self, argv: list[str], *, cwd: Path, env: dict[str, str]
    ) -> SimpleNamespace:
        assert not self._in_call, "pytest subprocesses must be strictly serial"
        self._in_call = True
        try:
            process_sequence = len(self.calls) + 1
            if self.before_call is not None:
                self.before_call(process_sequence, argv)
            assert self.report_path.is_file(), "initial report precedes every child"
            persisted = _load_report(self.report_path)
            is_collection = "--collect-only" in argv
            is_focused = runner.FOCUSED_TEST_PATH in argv
            phase = (
                "collect_focused"
                if is_collection and is_focused
                else "collect_full_suite"
                if is_collection
                else "focused"
                if is_focused
                else "full_suite"
            )
            basetemp = argv[argv.index("--basetemp") + 1]
            basetemp_path = cwd / basetemp
            assert basetemp_path.is_dir()
            (basetemp_path / "pytest-owned.tmp").write_bytes(
                f"synthetic process {process_sequence}\n".encode("ascii")
            )

            returncode = 0
            if is_collection:
                nodes = FOCUSED_NODE_IDS if is_focused else FULL_SUITE_NODE_IDS
                stdout = _collection_stdout(nodes)
                stability_sequence = None
            else:
                self._stability_calls += 1
                stability_sequence = self._stability_calls
                passed = len(FOCUSED_NODE_IDS if is_focused else FULL_SUITE_NODE_IDS)
                stdout = f"{passed} passed in 0.01s\n".encode("ascii")
                if self.failure_at == stability_sequence:
                    returncode = 1
                    stdout = (
                        f"{max(0, passed - 1)} passed, 1 failed in 0.01s\n"
                    ).encode("ascii")
            stderr = f"synthetic stderr {process_sequence}\n".encode("ascii")
            call = {
                "argv": list(argv),
                "cwd": cwd,
                "env": dict(env),
                "phase": phase,
                "persisted_collection_count": len(
                    persisted.get("collection_identity", {}).get("records", [])
                ),
                "persisted_run_count": len(persisted.get("runs", [])),
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
                "stability_sequence": stability_sequence,
            }
            self.calls.append(call)
            if self.after_call is not None:
                self.after_call(process_sequence, argv)
            if (
                stability_sequence is not None
                and self.interrupt_at == stability_sequence
            ):
                raise runner.ProcessInterrupted(
                    returncode=-9,
                    stdout=stdout,
                    stderr=stderr,
                )
            return SimpleNamespace(
                returncode=returncode,
                stdout=stdout,
                stderr=stderr,
            )
        finally:
            self._in_call = False


class SyntheticGitProbeProvider:
    """Raw-byte provider for every five-command worktree snapshot."""

    def __init__(
        self,
        state_provider: Callable[[], SyntheticGitState],
        on_label: Callable[[str], None] | None = None,
        failure_provider: Callable[[], tuple[str, str, int, bytes] | None]
        | None = None,
    ) -> None:
        self.state_provider = state_provider
        self.on_label = on_label
        self.failure_provider = failure_provider
        self.calls: list[dict[str, Any]] = []

    def __call__(
        self,
        root: Path,
        label: str,
        commands: dict[str, list[str]],
    ) -> dict[str, SimpleNamespace]:
        if self.on_label is not None:
            self.on_label(label)
        state = self.state_provider()
        assert set(commands) == {"status", "tracked", "untracked", "ignored", "staged"}
        payloads = {
            "status": state.status_stdout(),
            "tracked": state.tracked_stdout(),
            "untracked": state.untracked_stdout(),
            "ignored": state.ignored_stdout(),
            "staged": state.staged_stdout(),
        }
        self.calls.append(
            {
                "root": root.resolve(),
                "label": label,
                "commands": copy.deepcopy(commands),
                "payloads": payloads,
            }
        )
        failure = self.failure_provider() if self.failure_provider is not None else None
        results: dict[str, SimpleNamespace] = {}
        for name in commands:
            if failure is not None and (label, name) == failure[:2]:
                results[name] = SimpleNamespace(
                    returncode=failure[2],
                    stdout=payloads[name],
                    stderr=failure[3],
                )
            else:
                results[name] = SimpleNamespace(
                    returncode=0,
                    stdout=payloads[name],
                    stderr=b"",
                )
        return results


@dataclass(slots=True)
class V2Repository:
    root: Path
    schema_path: Path
    report_path: Path
    tracked_paths: tuple[str, ...]
    modified_paths: tuple[str, ...]
    base_untracked_paths: tuple[str, ...]
    ignored_paths: tuple[str, ...]
    tool_values: dict[str, str]
    python_path: str
    git_path: str
    sibling_sentinel: Path

    def state(
        self,
        *,
        extra_untracked: tuple[str, ...] = (),
        staged: tuple[str, ...] = (),
        ignored: tuple[str, ...] | None = None,
    ) -> SyntheticGitState:
        untracked = set(self.base_untracked_paths) | set(extra_untracked)
        if self.report_path.is_file():
            untracked.add(runner.REPORT_RELATIVE_PATH)
        return SyntheticGitState(
            tracked=self.tracked_paths,
            modified=self.modified_paths,
            staged=staged,
            untracked=tuple(sorted(untracked)),
            ignored=self.ignored_paths if ignored is None else tuple(sorted(ignored)),
        )


def _create_v2_repository(base: Path) -> V2Repository:
    root = base / "repository"
    root.mkdir(parents=True)
    tracked = (
        (set(runner.SOURCE_PATHS) - set(runner.UNTRACKED_EXECUTION_INPUTS))
        | set(runner.ALLOWED_TRACKED_MODIFIED)
        | {"tests/unit/synthetic_tracked_execution_input.py"}
    )
    for relative_path in sorted(tracked):
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(
            f"synthetic tracked source: {relative_path}\n".encode("utf-8")
        )

    schema_path = root / V2_SCHEMA_RELATIVE_PATH
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_bytes((PROJECT_ROOT / V2_SCHEMA_RELATIVE_PATH).read_bytes())
    dossier = root / "ops" / runner.TASK_ID
    dossier.mkdir(parents=True, exist_ok=True)
    for name in ("TASK_STATUS.md", "TASK_LOG.md", "EVIDENCE.md"):
        (dossier / name).write_bytes(f"synthetic {name}\n".encode("ascii"))

    ignored_paths = (
        "build/pytest-prior/current",
        "build/release/synthetic-build-input.txt",
        "tests/unit/__pycache__/synthetic.cpython.pyc",
    )
    for relative_path in ignored_paths:
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"neutralized ignored fixture\n")

    executable_directory = root / "fixtures" / "executables"
    executable_directory.mkdir(parents=True)
    executables = {
        "PYTHON": executable_directory / "python-fixture.exe",
        "GIT": executable_directory / "git-fixture.exe",
        "EG_CMAKE": executable_directory / "cmake-fixture.exe",
        "EG_CXX": executable_directory / "cxx-fixture.exe",
        "EG_NINJA": executable_directory / "ninja-fixture.exe",
        "EG_MAKE": executable_directory / "make-fixture.exe",
    }
    for name, path in executables.items():
        path.write_bytes(f"synthetic executable: {name}\n".encode("ascii"))
    sibling_sentinel = root / "build" / "unrelated-output" / "keep.txt"
    sibling_sentinel.parent.mkdir(parents=True, exist_ok=True)
    sibling_sentinel.write_bytes(b"must survive task-owned cleanup\n")
    report_path = root / runner.REPORT_RELATIVE_PATH
    return V2Repository(
        root=root,
        schema_path=schema_path,
        report_path=report_path,
        tracked_paths=tuple(sorted(tracked)),
        modified_paths=tuple(sorted(runner.ALLOWED_TRACKED_MODIFIED)),
        base_untracked_paths=tuple(
            sorted(set(runner.ALLOWED_UNTRACKED) - {runner.REPORT_RELATIVE_PATH})
        ),
        ignored_paths=ignored_paths,
        tool_values={
            name: executables[name].resolve().as_posix() for name in runner.TOOL_NAMES
        },
        python_path=executables["PYTHON"].resolve().as_posix(),
        git_path=executables["GIT"].resolve().as_posix(),
        sibling_sentinel=sibling_sentinel,
    )


@dataclass(slots=True)
class MutableGitInputs:
    extra_untracked: tuple[str, ...] = ()
    staged: tuple[str, ...] = ()
    ignored: tuple[str, ...] | None = None
    probe_failure: tuple[str, str, int, bytes] | None = None


@dataclass(slots=True)
class Bundle:
    repo: V2Repository
    config: runner.RunnerConfig
    process: SyntheticProcessRunner
    probes: SyntheticGitProbeProvider
    git_inputs: MutableGitInputs
    exit_code: int
    report: dict[str, Any]


ProbeHook = Callable[[str, V2Repository, MutableGitInputs], None]
ProcessHook = Callable[[int, list[str], V2Repository, MutableGitInputs], None]


def _execute_repository(
    repo: V2Repository,
    *,
    failure_at: int | None = None,
    interrupt_at: int | None = None,
    extra_untracked: tuple[str, ...] = (),
    staged: tuple[str, ...] = (),
    ignored: tuple[str, ...] | None = None,
    on_probe: ProbeHook | None = None,
    before_process: ProcessHook | None = None,
    after_process: ProcessHook | None = None,
) -> Bundle:
    git_inputs = MutableGitInputs(extra_untracked, staged, ignored)

    def probe_hook(label: str) -> None:
        if on_probe is not None:
            on_probe(label, repo, git_inputs)

    def before_hook(sequence: int, argv: list[str]) -> None:
        if before_process is not None:
            before_process(sequence, argv, repo, git_inputs)

    def after_hook(sequence: int, argv: list[str]) -> None:
        if after_process is not None:
            after_process(sequence, argv, repo, git_inputs)

    probes = SyntheticGitProbeProvider(
        lambda: repo.state(
            extra_untracked=git_inputs.extra_untracked,
            staged=git_inputs.staged,
            ignored=git_inputs.ignored,
        ),
        on_label=probe_hook,
        failure_provider=lambda: git_inputs.probe_failure,
    )
    process = SyntheticProcessRunner(
        report_path=repo.report_path,
        failure_at=failure_at,
        interrupt_at=interrupt_at,
        before_call=before_hook,
        after_call=after_hook,
    )
    config = runner.RunnerConfig(
        repository_root=repo.root,
        report_path=repo.report_path,
        basetemp_root=runner.DEFAULT_BASETEMP_ROOT,
        tool_values=repo.tool_values,
        python_executable=repo.python_path,
        git_executable=repo.git_path,
    )
    clock = ScriptedClock()
    exit_code, report = runner.run_evidence(
        config,
        process_runner=process,
        utc_now=clock.utc_now,
        monotonic_ns=clock.monotonic_ns,
        git_checker=lambda _root: None,
        git_probe_provider=probes,
    )
    assert report == _load_report(repo.report_path)
    return Bundle(repo, config, process, probes, git_inputs, exit_code, report)


def _run_bundle(base: Path, **kwargs: Any) -> Bundle:
    return _execute_repository(_create_v2_repository(base), **kwargs)


def _verify(
    bundle: Bundle,
    report_path: Path | None = None,
    *,
    allow_partial: bool = False,
    rehash_environment: bool = False,
) -> dict[str, Any]:
    return verifier.verify_report(
        report_path or bundle.repo.report_path,
        repository_root=bundle.repo.root,
        schema_path=bundle.repo.schema_path,
        verify_git=False,
        rehash_environment=rehash_environment,
        allow_partial=allow_partial,
    )


def _assert_schema_valid(bundle: Bundle, report: dict[str, Any] | None = None) -> None:
    errors = list(_schema_validator(bundle.repo.schema_path).iter_errors(report or bundle.report))
    assert not errors, errors[0].message if errors else ""


def _mutated_report(
    tmp_path: Path,
    successful_bundle: Bundle,
    mutator: Callable[[dict[str, Any]], None],
) -> Path:
    report = copy.deepcopy(successful_bundle.report)
    mutator(report)
    path = tmp_path / "mutated.json"
    _write_report(path, report)
    return path


def _assert_mutation_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
    mutator: Callable[[dict[str, Any]], None],
) -> None:
    path = _mutated_report(tmp_path, successful_bundle, mutator)
    with pytest.raises(verifier.EvidenceVerificationError):
        _verify(successful_bundle, path)


@pytest.fixture(scope="module")
def successful_bundle(tmp_path_factory: pytest.TempPathFactory) -> Bundle:
    return _run_bundle(tmp_path_factory.mktemp("v2-success"))


def test_valid_v2_bundle_is_canonical_schema_valid_and_independently_verified(
    successful_bundle: Bundle,
) -> None:
    bundle = successful_bundle
    assert bundle.exit_code == 0
    assert bundle.report["completed"] is True
    assert bundle.repo.report_path.read_bytes() == _canonical_json_bytes(bundle.report)
    _assert_schema_valid(bundle)
    result = _verify(bundle, rehash_environment=True)
    assert result["ok"] is True
    assert result["completed"] is True


def test_synthetic_runner_is_exactly_serial_2_plus_25_plus_2_with_zero_retry(
    successful_bundle: Bundle,
) -> None:
    bundle = successful_bundle
    calls = bundle.process.calls
    assert len(calls) == 29
    assert [call["phase"] for call in calls] == [
        "collect_focused",
        "collect_full_suite",
        *(["focused"] * 25),
        "full_suite",
        "full_suite",
    ]
    assert [call["stability_sequence"] for call in calls[2:]] == list(range(1, 28))
    assert len(bundle.probes.calls) == 58
    assert [call["label"] for call in bundle.probes.calls] == [
        label
        for process_sequence, phase in enumerate(
            [
                "collect_focused",
                "collect_full_suite",
                *(["focused"] * 25),
                "full_suite",
                "full_suite",
            ],
            start=1,
        )
        for label in (
            f"before:{process_sequence}:{phase}",
            f"after:{process_sequence}:{phase}",
        )
    ]
    assert calls[0]["persisted_collection_count"] == 0
    assert calls[1]["persisted_collection_count"] == 1
    assert calls[2]["persisted_collection_count"] == 2
    assert calls[2]["persisted_run_count"] == 0
    assert calls[-1]["persisted_run_count"] == 26
    assert bundle.report["summary"]["retries"] == 0
    assert len(bundle.report["collection_identity"]["records"]) == 2
    assert len(bundle.report["runs"]) == 27

    for call in calls:
        assert call["argv"][:4] == [
            bundle.repo.python_path,
            "-m",
            "pytest",
            "-q",
        ]
        plugin_index = call["argv"].index("-p")
        assert call["argv"][plugin_index : plugin_index + 2] == [
            "-p",
            "no:cacheprovider",
        ]
        assert call["env"]["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
        pycache = Path(call["env"]["PYTHONPYCACHEPREFIX"])
        basetemp = call["argv"][call["argv"].index("--basetemp") + 1]
        assert pycache == (bundle.repo.root / basetemp / "pycache").resolve()


def test_raw_streams_and_cleanup_are_complete_and_task_owned(
    successful_bundle: Bundle,
) -> None:
    bundle = successful_bundle
    records = [
        *bundle.report["collection_identity"]["records"],
        *bundle.report["runs"],
    ]
    for record in records:
        assert _stream_bytes(record["stdout"])
        assert _stream_bytes(record["stderr"])
    for snapshot in bundle.report["worktree_snapshots"]:
        for probe in snapshot["commands"].values():
            _stream_bytes(probe["stdout"])
            assert _stream_bytes(probe["stderr"]) == b""
    cleanup = bundle.report["cleanup"]
    assert cleanup["created"] == cleanup["expected"]
    assert cleanup["removed"] == cleanup["expected"]
    assert cleanup["remaining"] == []
    assert cleanup["unexpected"] == []
    assert cleanup["completed"] is True
    assert not (bundle.repo.root / runner.DEFAULT_BASETEMP_ROOT).exists()
    assert bundle.repo.sibling_sentinel.read_bytes() == b"must survive task-owned cleanup\n"


def test_first_failure_preserves_schema_valid_partial_report_without_retry(
    tmp_path: Path,
) -> None:
    bundle = _run_bundle(tmp_path, failure_at=3)
    assert bundle.exit_code == 1
    assert len(bundle.process.calls) == 5
    assert len(bundle.report["runs"]) == 3
    assert [run["status"] for run in bundle.report["runs"]] == [
        "passed",
        "passed",
        "failed",
    ]
    assert bundle.report["summary"]["retries"] == 0
    assert bundle.report["summary"]["stop_reason"] == "failure"
    _assert_schema_valid(bundle)
    assert _verify(bundle, allow_partial=True)["completed"] is False


def test_interruption_preserves_both_streams_and_never_retries(tmp_path: Path) -> None:
    bundle = _run_bundle(tmp_path, interrupt_at=2)
    assert bundle.exit_code == 1
    assert len(bundle.process.calls) == 4
    assert len(bundle.report["runs"]) == 2
    interrupted = bundle.report["runs"][-1]
    assert interrupted["status"] == "interrupted"
    assert interrupted["exit_code"] == -9
    assert _stream_bytes(interrupted["stdout"]) == bundle.process.calls[-1]["stdout"]
    assert _stream_bytes(interrupted["stderr"]) == bundle.process.calls[-1]["stderr"]
    assert bundle.report["summary"]["stop_reason"] == "interrupted"
    _assert_schema_valid(bundle)
    assert _verify(bundle, allow_partial=True)["completed"] is False


def test_source_mutation_in_before_guard_stops_before_next_pytest(tmp_path: Path) -> None:
    source = "tests/unit/synthetic_tracked_execution_input.py"

    def mutate(label: str, repo: V2Repository, _inputs: MutableGitInputs) -> None:
        if label == "before:3:focused":
            (repo.root / source).write_bytes(b"mutated before focused run\n")

    bundle = _run_bundle(tmp_path, on_probe=mutate)
    assert bundle.exit_code == 1
    assert len(bundle.process.calls) == 2
    assert len(bundle.report["runs"]) == 0
    terminal = bundle.report["worktree_snapshots"][-1]
    assert terminal["label"] == "before:3:focused"
    assert terminal["accepted"] is False
    assert "source fingerprint" in terminal["diagnostic"]
    _assert_schema_valid(bundle)
    _verify(bundle, allow_partial=True)


def test_source_mutation_during_run_preserves_attempt_and_stops(tmp_path: Path) -> None:
    source = "tests/unit/synthetic_tracked_execution_input.py"

    def mutate(
        sequence: int,
        _argv: list[str],
        repo: V2Repository,
        _inputs: MutableGitInputs,
    ) -> None:
        if sequence == 3:
            (repo.root / source).write_bytes(b"mutated during focused run\n")

    bundle = _run_bundle(tmp_path, after_process=mutate)
    assert bundle.exit_code == 1
    assert len(bundle.process.calls) == 3
    assert len(bundle.report["runs"]) == 1
    attempt = bundle.report["runs"][0]
    assert attempt["status"] == "failed"
    assert _stream_bytes(attempt["stdout"]) == bundle.process.calls[-1]["stdout"]
    assert _stream_bytes(attempt["stderr"]) == bundle.process.calls[-1]["stderr"]
    assert bundle.report["worktree_snapshots"][-1]["accepted"] is False
    _assert_schema_valid(bundle)
    _verify(bundle, allow_partial=True)


def test_post_child_git_guard_failure_preserves_raw_guard_and_child_streams(
    tmp_path: Path,
) -> None:
    git_stderr = b"synthetic post-child Git guard failure\n"

    def fail_guard(
        label: str,
        _repo: V2Repository,
        inputs: MutableGitInputs,
    ) -> None:
        if label == "after:3:focused":
            inputs.probe_failure = (label, "status", 7, git_stderr)

    bundle = _run_bundle(tmp_path, on_probe=fail_guard)
    assert bundle.exit_code == 1
    assert len(bundle.process.calls) == 3
    assert len(bundle.report["runs"]) == 1
    run = bundle.report["runs"][0]
    assert run["status"] == "failed"
    assert _stream_bytes(run["stdout"]) == bundle.process.calls[-1]["stdout"]
    assert _stream_bytes(run["stderr"]) == bundle.process.calls[-1]["stderr"]

    guard = bundle.report["worktree_snapshots"][-1]
    assert guard["label"] == "after:3:focused"
    assert guard["accepted"] is False
    assert guard["parsed"] is None
    assert guard["normalized_sha256"] is None
    assert guard["execution_state_sha256"] is None
    assert guard["source_fingerprint_sha256"] is None
    assert guard["commands"]["status"]["exit_code"] == 7
    assert _stream_bytes(guard["commands"]["status"]["stderr"]) == git_stderr
    assert "Git status probe exited with 7" in guard["diagnostic"]
    _assert_schema_valid(bundle)
    _verify(bundle, allow_partial=True)


def test_worktree_mutation_between_runs_is_a_rejected_orphan_guard(
    tmp_path: Path,
) -> None:
    def mutate(label: str, _repo: V2Repository, inputs: MutableGitInputs) -> None:
        if label == "before:4:focused":
            inputs.extra_untracked = ("pytest.ini",)

    bundle = _run_bundle(tmp_path, on_probe=mutate)
    assert bundle.exit_code == 1
    assert len(bundle.process.calls) == 3
    assert len(bundle.report["runs"]) == 1
    terminal = bundle.report["worktree_snapshots"][-1]
    assert terminal["label"] == "before:4:focused"
    assert terminal["accepted"] is False
    assert "pytest.ini" in terminal["parsed"]["unexpected_paths"]
    _assert_schema_valid(bundle)
    _verify(bundle, allow_partial=True)


def test_staged_path_is_rejected_before_any_pytest(tmp_path: Path) -> None:
    bundle = _run_bundle(tmp_path, staged=("pyproject.toml",))
    assert bundle.exit_code == 1
    assert bundle.process.calls == []
    terminal = bundle.report["worktree_snapshots"][0]
    assert terminal["accepted"] is False
    assert terminal["parsed"]["staged"] == [
        {"path": "pyproject.toml", "index_status": "M"}
    ]
    _assert_schema_valid(bundle)
    _verify(bundle, allow_partial=True)


@pytest.mark.parametrize(
    "unexpected",
    [
        "pytest.ini",
        "tests/conftest.py",
        "tests/unit/test_untracked_collection_input.py",
        "sitecustomize.py",
        "notes/arbitrary.txt",
    ],
)
def test_execution_affecting_or_arbitrary_untracked_path_fails_preflight(
    tmp_path: Path,
    unexpected: str,
) -> None:
    bundle = _run_bundle(tmp_path, extra_untracked=(unexpected,))
    assert bundle.exit_code == 1
    assert bundle.process.calls == []
    snapshot = bundle.report["worktree_snapshots"][0]
    assert unexpected in snapshot["parsed"]["untracked"]
    assert unexpected in snapshot["parsed"]["unexpected_paths"]
    _assert_schema_valid(bundle)
    _verify(bundle, allow_partial=True)


def test_allowed_dossier_and_report_paths_are_non_execution_artifacts(
    successful_bundle: Bundle,
) -> None:
    report = successful_bundle.report
    source_paths = [record["path"] for record in report["source_files"]]
    assert "REVIEW_STATE.yaml" in source_paths
    assert V2_SCHEMA_RELATIVE_PATH in source_paths
    assert "tests/unit/synthetic_tracked_execution_input.py" in source_paths
    assert next(
        record for record in report["source_files"]
        if record["path"] == V2_SCHEMA_RELATIVE_PATH
    )["origin"] == "untracked"
    release_source = next(
        record for record in report["source_files"]
        if record["path"] == "build/release/synthetic-build-input.txt"
    )
    assert release_source["origin"] == "untracked"
    assert "build/release/synthetic-build-input.txt" in report[
        "worktree_snapshots"
    ][0]["parsed"]["execution_input_paths"]
    for excluded in runner.NON_EXECUTION_TASK_PATHS:
        assert excluded not in source_paths

    first = report["worktree_snapshots"][0]["parsed"]
    later = report["worktree_snapshots"][1]["parsed"]
    for path in (
        "CURRENT_STATUS.md",
        "research/NEXT_RESEARCH_STEPS.md",
        runner.TASK_STATUS_PATH,
        f"ops/{runner.TASK_ID}/TASK_LOG.md",
        f"ops/{runner.TASK_ID}/EVIDENCE.md",
    ):
        assert path in first["task_owned_non_execution_paths"]
    assert runner.REPORT_RELATIVE_PATH not in first["untracked"]
    assert runner.REPORT_RELATIVE_PATH in later["task_owned_non_execution_paths"]
    healthy = {
        "path": runner.TASK_STATUS_PATH,
        "exists": True,
        "kind": "regular_file",
        "symlink": False,
    }
    assert all(
        snapshot["task_status_file"] == healthy
        for snapshot in report["worktree_snapshots"]
    )


def test_authorized_untracked_execution_source_cannot_be_omitted(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def omit(report: dict[str, Any]) -> None:
        report["source_files"] = [
            source
            for source in report["source_files"]
            if source["path"] != V2_SCHEMA_RELATIVE_PATH
        ]

    _assert_mutation_rejected(tmp_path, successful_bundle, omit)


def test_altered_raw_git_output_is_independently_reconstructed(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        probe = report["worktree_snapshots"][0]["commands"]["status"]["stdout"]
        raw = _stream_bytes(probe)
        probe.update(_captured_stream(raw.split(b"\0", 1)[1]))

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


def test_wrong_git_status_stream_hash_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        report["worktree_snapshots"][0]["commands"]["status"]["stdout"][
            "sha256"
        ] = "0" * 64

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


def test_unmerged_git_status_preserves_every_porcelain_xy_state() -> None:
    for xy in ("DD", "AU", "UD", "UA", "DU", "AA", "UU"):
        parsed = verifier._parse_porcelain_v2(
            _porcelain_v2_unmerged("conflicted.py", xy),
            f"synthetic {xy}",
        )
        assert parsed["tracked_states"] == {
            "conflicted.py": (xy[0], xy[1])
        }


@pytest.mark.parametrize("kind", ["duplicate", "malformed"])
def test_duplicate_or_malformed_nul_git_record_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
    kind: str,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        probe = report["worktree_snapshots"][0]["commands"]["untracked"]["stdout"]
        raw = _stream_bytes(probe)
        if kind == "duplicate":
            first = raw.split(b"\0", 1)[0] + b"\0"
            raw += first
        else:
            raw = raw[:-1]
        probe.update(_captured_stream(raw))

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


@pytest.mark.parametrize("path", ["../escape.py", "/absolute.py", "C:/absolute.py"])
def test_git_paths_reject_traversal_and_absolute_forms(
    tmp_path: Path,
    successful_bundle: Bundle,
    path: str,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        probe = report["worktree_snapshots"][0]["commands"]["untracked"]["stdout"]
        probe.update(_captured_stream(_stream_bytes(probe) + path.encode() + b"\0"))

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


def test_source_symlink_is_rejected_before_pytest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _create_v2_repository(tmp_path)
    target = repo.root / "pyproject.toml"
    original = runner._is_link_like
    monkeypatch.setattr(
        runner,
        "_is_link_like",
        lambda path: Path(path) == target or original(Path(path)),
    )
    bundle = _execute_repository(repo)
    assert bundle.exit_code == 1
    assert bundle.process.calls == []
    assert bundle.report["completed"] is False
    assert bundle.report["source_files"] == []
    revision = bundle.report["execution_project_revision"]
    assert revision["fingerprint_scope"] == []
    assert revision["fingerprint_sha256"] is None
    assert revision["worktree_identity_sha256"] is None
    assert len(bundle.report["worktree_snapshots"]) == 1
    snapshot = bundle.report["worktree_snapshots"][0]
    assert snapshot["accepted"] is False
    assert snapshot["source_fingerprint_sha256"] is None
    assert "symlink" in snapshot["diagnostic"]
    _assert_schema_valid(bundle)
    with pytest.raises(verifier.EvidenceVerificationError):
        _verify(bundle)
    _verify(bundle, allow_partial=True)


@pytest.mark.parametrize("mutation", ["missing", "directory", "symlink"])
def test_active_task_status_requires_exact_regular_non_symlink_shape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    repo = _create_v2_repository(tmp_path)
    status = repo.root / runner.TASK_STATUS_PATH
    if mutation == "missing":
        status.unlink()
    elif mutation == "directory":
        status.unlink()
        status.mkdir()
    else:
        original = runner._is_link_like
        monkeypatch.setattr(
            runner,
            "_is_link_like",
            lambda path: Path(path) == status or original(Path(path)),
        )
    with pytest.raises(runner.RunnerError, match="TASK_STATUS"):
        _execute_repository(repo)
    assert not repo.report_path.exists()


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "altered"])
def test_collection_node_id_missing_duplicate_or_altered_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
    mutation: str,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        collection = report["collection_identity"]
        if mutation == "missing":
            collection["records"][0]["node_ids"].pop()
        elif mutation == "duplicate":
            record = collection["records"][0]
            duplicate = (FOCUSED_NODE_IDS[0], FOCUSED_NODE_IDS[0])
            record["stdout"] = _captured_stream(_collection_stdout(duplicate))
        else:
            collection["full_suite_node_ids"][-1] = (
                "tests/integration/test_verifier_cli.py::test_altered"
            )

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


@pytest.mark.parametrize("phase", ["focused", "full_suite"])
def test_run_pass_count_must_equal_its_recorded_collection(
    tmp_path: Path,
    successful_bundle: Bundle,
    phase: str,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        run = next(item for item in report["runs"] if item["phase"] == phase)
        observed = run["expected_pass_count"] - 1
        run["stdout"] = _captured_stream(f"{observed} passed in 0.01s\n".encode())
        run["pytest_summary"]["passed"] = observed

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


def test_noncanonical_base64_is_rejected(tmp_path: Path, successful_bundle: Bundle) -> None:
    def alter(report: dict[str, Any]) -> None:
        stream = report["runs"][0]["stderr"]
        stream.update(
            {
                "base64": "Zh==",
                "byte_length": 1,
                "sha256": hashlib.sha256(b"f").hexdigest(),
            }
        )

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


def test_wrong_captured_stream_hash_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        report["runs"][0]["stdout"]["sha256"] = "f" * 64

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


def test_forged_summary_totals_are_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    _assert_mutation_rejected(
        tmp_path,
        successful_bundle,
        lambda report: report["summary"].__setitem__("successful_run_count", 26),
    )


def test_cleanup_root_substitution_is_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    _assert_mutation_rejected(
        tmp_path,
        successful_bundle,
        lambda report: report["cleanup"].__setitem__("root", "build/foreign-root"),
    )


def test_delete_recreate_cleanup_root_fails_identity_check_without_deleting_replacement(
    tmp_path: Path,
) -> None:
    replacement_sentinel = b"foreign replacement must survive cleanup\n"

    def replace_root(
        sequence: int,
        _argv: list[str],
        repo: V2Repository,
        _inputs: MutableGitInputs,
    ) -> None:
        if sequence != 3:
            return
        base = repo.root / runner.DEFAULT_BASETEMP_ROOT
        shutil.rmtree(base)
        base.mkdir()
        marker = base / runner.OWNER_MARKER_NAME
        marker.write_bytes(
            _canonical_json_bytes(
                {
                    "artifact_kind": runner.ARTIFACT_KIND,
                    "task_id": runner.TASK_ID,
                    "basetemp_root": runner.DEFAULT_BASETEMP_ROOT,
                }
            )
        )
        (base / "foreign-sentinel.txt").write_bytes(replacement_sentinel)

    bundle = _run_bundle(tmp_path, after_process=replace_root)
    base = bundle.repo.root / runner.DEFAULT_BASETEMP_ROOT
    try:
        assert bundle.exit_code == 1
        assert len(bundle.process.calls) == 3
        assert len(bundle.report["runs"]) == 1
        cleanup = bundle.report["cleanup"]
        assert cleanup["completed"] is False
        assert cleanup["identity_verified"] is False
        assert "identity changed" in cleanup["diagnostic"]
        assert base.is_dir()
        assert (base / "foreign-sentinel.txt").read_bytes() == replacement_sentinel
        _assert_schema_valid(bundle)
        _verify(bundle, allow_partial=True)
    finally:
        if base.is_dir():
            shutil.rmtree(base)


def test_environment_tool_identity_tampering_and_same_host_change_are_rejected(
    tmp_path: Path,
    successful_bundle: Bundle,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        report["environment"]["tool_overrides"]["EG_CMAKE"][
            "effective_value"
        ] = successful_bundle.repo.tool_values["EG_CXX"]

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)

    tool = Path(successful_bundle.repo.tool_values["EG_CMAKE"])
    original = tool.read_bytes()
    try:
        tool.write_bytes(b"same-host tool mutation\n")
        with pytest.raises(verifier.EvidenceVerificationError):
            _verify(successful_bundle, rehash_environment=True)
    finally:
        tool.write_bytes(original)


@pytest.mark.parametrize("control", ["cache_plugin", "plugin_autoload"])
def test_recorded_child_execution_controls_cannot_be_removed_or_changed(
    tmp_path: Path,
    successful_bundle: Bundle,
    control: str,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        run = report["runs"][0]
        if control == "cache_plugin":
            index = run["argv"].index("-p")
            del run["argv"][index : index + 2]
        else:
            run["environment_overrides"]["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "0"

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


def test_child_environment_does_not_capture_arbitrary_parent_secret(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("INSPECTOR_STABILITY_SYNTHETIC_SECRET", "do-not-copy")
    bundle = _run_bundle(tmp_path, failure_at=1)
    assert all(
        "INSPECTOR_STABILITY_SYNTHETIC_SECRET" not in call["env"]
        for call in bundle.process.calls
    )


def test_unsafe_ignored_path_is_rejected_before_pytest(tmp_path: Path) -> None:
    bundle = _run_bundle(
        tmp_path,
        ignored=("dist/uncontrolled-plugin.py",),
    )
    assert bundle.exit_code == 1
    assert bundle.process.calls == []
    snapshot = bundle.report["worktree_snapshots"][0]
    assert snapshot["accepted"] is False
    assert "dist/uncontrolled-plugin.py" in snapshot["parsed"]["unexpected_paths"]
    _assert_schema_valid(bundle)
    _verify(bundle, allow_partial=True)


def test_neutralized_ignored_path_set_is_frozen_across_all_processes(
    tmp_path: Path,
) -> None:
    def mutate(label: str, repo: V2Repository, inputs: MutableGitInputs) -> None:
        if label == "before:4:focused":
            inputs.ignored = (*repo.ignored_paths, "build/pytest-new/stale")

    bundle = _run_bundle(tmp_path, on_probe=mutate)
    assert bundle.exit_code == 1
    assert len(bundle.process.calls) == 3
    terminal = bundle.report["worktree_snapshots"][-1]
    assert terminal["parsed"]["unexpected_paths"] == []
    assert terminal["accepted"] is False
    assert "execution-state identity" in terminal["diagnostic"]
    _assert_schema_valid(bundle)
    _verify(bundle, allow_partial=True)


@pytest.mark.parametrize("location", ["root", "nested"])
def test_schema_rejects_unknown_properties_recursively(
    tmp_path: Path,
    successful_bundle: Bundle,
    location: str,
) -> None:
    def alter(report: dict[str, Any]) -> None:
        target = report if location == "root" else report["runs"][0]
        target["unknown_property"] = True

    _assert_mutation_rejected(tmp_path, successful_bundle, alter)


@pytest.mark.parametrize(
    "encoding",
    ["noncanonical", "duplicate_key", "nonfinite", "non_utf8"],
)
def test_strict_json_rejects_noncanonical_duplicate_nonfinite_and_non_utf8(
    tmp_path: Path,
    successful_bundle: Bundle,
    encoding: str,
) -> None:
    report = successful_bundle.report
    canonical = _canonical_json_bytes(report)
    if encoding == "noncanonical":
        raw = json.dumps(report, sort_keys=True).encode("utf-8")
    elif encoding == "duplicate_key":
        needle = (
            b'  "artifact_kind": "inspector_timeout_stability_evidence",\n'
        )
        raw = canonical.replace(needle, needle + needle, 1)
    elif encoding == "nonfinite":
        raw = b'{"value": NaN}\n'
    else:
        raw = canonical + b"\xff"
    path = tmp_path / f"{encoding}.json"
    path.write_bytes(raw)
    with pytest.raises(verifier.EvidenceVerificationError):
        _verify(successful_bundle, path)


def test_preexisting_report_is_never_overwritten(tmp_path: Path) -> None:
    repo = _create_v2_repository(tmp_path)
    original = b"preexisting evidence must survive\n"
    repo.report_path.write_bytes(original)
    with pytest.raises(FileExistsError):
        _execute_repository(repo)
    assert repo.report_path.read_bytes() == original
