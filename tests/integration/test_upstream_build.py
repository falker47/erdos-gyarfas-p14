"""Bounded engineering integration checks for the preserved upstream source.

These tests exercise build routes and tiny process invocations. They neither
verify the upstream search invariant nor establish exhaustive coverage.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest

from egverify.graph import Graph, GraphFormatError
from egverify.predicates import (
    find_exact_cycle,
    find_induced_path,
    minimum_degree,
    relevant_power_of_two_lengths,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = REPOSITORY_ROOT / "third_party" / "erdos-gyarfas"
SMOKE_TIMEOUT_SECONDS = 10
BUILD_TIMEOUT_SECONDS = 90
TOOL_ENVIRONMENT = {
    "cmake": "EG_CMAKE",
    "g++": "EG_CXX",
    "make": "EG_MAKE",
    "ninja": "EG_NINJA",
}
_UPSTREAM_INTEGER_TOKEN = r"[+-]?\d+"
_UPSTREAM_ADJACENCY_LINE = re.compile(
    rf"(?P<label>{_UPSTREAM_INTEGER_TOKEN}): "
    rf"(?P<neighbors>(?:{_UPSTREAM_INTEGER_TOKEN} )*)\Z"
)
_CANONICAL_VERTEX_LABEL = re.compile(r"(?:0|[1-9]\d*)\Z")

pytestmark = pytest.mark.integration


def _required_program(name: str) -> str:
    override_name = TOOL_ENVIRONMENT[name]
    override = os.environ.get(override_name)
    if override:
        path = Path(override)
        if not path.is_file():
            pytest.fail(f"{override_name} does not name a file: {override}")
        return str(path)

    path = shutil.which(name)
    if path is None:
        pytest.skip(f"required integration tool is not on PATH: {name}")
    return path


def _subprocess_environment() -> dict[str, str]:
    environment = os.environ.copy()
    override_directories = [
        str(Path(value).parent)
        for key, value in environment.items()
        if key in TOOL_ENVIRONMENT.values()
    ]
    if override_directories:
        environment["PATH"] = os.pathsep.join(
            [*override_directories, environment.get("PATH", "")]
        )
    return environment


def _run(
    command: list[str],
    *,
    cwd: Path,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=_subprocess_environment(),
    )


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
            "graph_construction_failure",
            exc.location,
            exc.message,
        ) from exc


def inspect_exit_100_candidate(output: str | bytes, k: int) -> dict[str, object]:
    """Independently inspect surprising output without accepting any result."""

    if isinstance(output, bytes):
        try:
            output = output.decode("utf-8")
        except UnicodeDecodeError as exc:
            return {
                "diagnostic_kind": "surprising_exit_100_candidate",
                "parse_succeeded": False,
                "parse_error": {
                    "code": "invalid_utf8",
                    "location": f"byte {exc.start}",
                    "message": "candidate adjacency output is not UTF-8",
                },
            }
    try:
        graph = parse_upstream_adjacency_list(output)
    except UpstreamAdjacencyFormatError as exc:
        return {
            "diagnostic_kind": "surprising_exit_100_candidate",
            "parse_succeeded": False,
            "parse_error": exc.as_dict(),
        }

    observed_minimum_degree = minimum_degree(graph)
    induced_path = find_induced_path(graph, k)
    cycle_checks: list[dict[str, object]] = []
    for length in relevant_power_of_two_lengths(len(graph.vertices)):
        witness = find_exact_cycle(graph, length)
        cycle_checks.append(
            {
                "length": length,
                "passed": witness is None,
                "witness": None if witness is None else list(witness),
            }
        )

    checks: dict[str, object] = {
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
    all_predicates_passed = all(
        bool(check["passed"])
        for check in checks.values()
        if isinstance(check, dict)
    )
    return {
        "diagnostic_kind": "surprising_exit_100_candidate",
        "parse_succeeded": True,
        "canonical_graph_serialization": graph.canonical_bytes().decode("utf-8"),
        "canonical_graph_sha256": graph.canonical_sha256(),
        "checks": checks,
        "all_candidate_predicates_passed": all_predicates_passed,
    }


@dataclass(frozen=True, slots=True)
class CapturedProcessOutcome:
    termination_reason: str
    exit_code: int | None
    stdout: bytes
    stderr: bytes


def _captured_bytes(value: str | bytes | None) -> bytes:
    if value is None:
        return b""
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


def _stream_diagnostic(value: bytes) -> dict[str, object]:
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "byte_length": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "utf8_with_replacement": value.decode("utf-8", errors="replace"),
    }


def _run_tiny_invocation(command: list[str]) -> CapturedProcessOutcome:
    try:
        result = subprocess.run(
            command,
            cwd=REPOSITORY_ROOT,
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=SMOKE_TIMEOUT_SECONDS,
            env=_subprocess_environment(),
        )
    except subprocess.TimeoutExpired as exc:
        return CapturedProcessOutcome(
            termination_reason="timeout",
            exit_code=None,
            stdout=_captured_bytes(exc.stdout),
            stderr=_captured_bytes(exc.stderr),
        )
    except OSError as exc:
        return CapturedProcessOutcome(
            termination_reason="spawn-error",
            exit_code=None,
            stdout=b"",
            stderr=str(exc).encode("utf-8", errors="replace"),
        )
    return CapturedProcessOutcome(
        termination_reason="signal" if result.returncode < 0 else "exited",
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def _ordinary_completion_failure(
    outcome: CapturedProcessOutcome, k: int
) -> str | None:
    outcome_data: dict[str, object] = {
        "actual_outcome": {
            "termination_reason": outcome.termination_reason,
            "exit_code": outcome.exit_code,
        },
        "stdout": _stream_diagnostic(outcome.stdout),
        "stderr": _stream_diagnostic(outcome.stderr),
    }
    if outcome.termination_reason == "exited" and outcome.exit_code == 0:
        return None
    if outcome.termination_reason == "exited" and outcome.exit_code == 100:
        candidate = inspect_exit_100_candidate(outcome.stdout, k)
        outcome_data["candidate_diagnostic"] = candidate
        if candidate.get("all_candidate_predicates_passed") is True:
            consequence = (
                "independent predicates all passed; this is a surprising "
                "mathematical result requiring a separate freeze-and-verify task"
            )
        else:
            consequence = (
                "candidate parsing or at least one independent predicate failed; "
                "this is an upstream correctness failure"
            )
        return (
            "exit 100 is never ordinary tiny-case completion; "
            f"{consequence}\n"
            + json.dumps(outcome_data, ensure_ascii=True, indent=2, sort_keys=True)
        )
    return (
        "tiny upstream invocation did not complete ordinarily with exit 0\n"
        + json.dumps(outcome_data, ensure_ascii=True, indent=2, sort_keys=True)
    )


_K4_UPSTREAM_ADJACENCY = (
    "2: 0 1 3 \n"
    "0: 1 2 3 \n"
    "3: 0 1 2 \n"
    "1: 0 2 3 \n"
)


def test_upstream_adjacency_parser_normalizes_a_well_formed_graph() -> None:
    graph = parse_upstream_adjacency_list(_K4_UPSTREAM_ADJACENCY)

    assert graph.vertices == (0, 1, 2, 3)
    assert graph.edges == (
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    )
    assert graph.canonical_bytes() == (
        b'{"edges":[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],'
        b'"schema_version":"1.0","vertices":[0,1,2,3]}\n'
    )
    assert graph.canonical_sha256() == (
        "c423921c28d31c5ca500533d703db40e58689e8a1a7e4c69c0fe7e66e9b8b6df"
    )


@pytest.mark.parametrize(
    ("output", "code"),
    [
        ("", "empty_output"),
        ("0: ", "missing_final_newline"),
        ("not an adjacency line\n", "malformed_line"),
        ("00: \n", "noncanonical_vertex_label"),
    ],
)
def test_upstream_adjacency_parser_rejects_malformed_syntax(
    output: str, code: str
) -> None:
    with pytest.raises(UpstreamAdjacencyFormatError) as caught:
        parse_upstream_adjacency_list(output)
    assert caught.value.code == code


@pytest.mark.parametrize(
    ("output", "code"),
    [
        ("0: \n0: \n", "duplicate_vertex_declaration"),
        ("0: 1 \n", "undeclared_endpoint"),
        ("0: 1 \n1: \n", "asymmetric_adjacency"),
        ("0: 1 1 \n1: 0 \n", "duplicate_neighbor"),
        ("0: 0 \n", "loop"),
        ("0: \n2: \n", "noncanonical_vertex_labels"),
    ],
)
def test_upstream_adjacency_parser_rejects_invalid_graph_interfaces(
    output: str, code: str
) -> None:
    with pytest.raises(UpstreamAdjacencyFormatError) as caught:
        parse_upstream_adjacency_list(output)
    assert caught.value.code == code


def test_candidate_diagnostic_reports_a_failed_power_cycle_predicate() -> None:
    diagnostic = inspect_exit_100_candidate(_K4_UPSTREAM_ADJACENCY, 4)

    assert diagnostic["parse_succeeded"] is True
    assert diagnostic["all_candidate_predicates_passed"] is False
    checks = diagnostic["checks"]
    assert isinstance(checks, dict)
    assert checks["simple_graph_construction"] == {"passed": True}
    assert checks["minimum_degree_at_least_3"] == {
        "observed": 3,
        "passed": True,
    }
    assert checks["p4_free"] == {
        "passed": True,
        "witness_induced_p4": None,
    }
    assert checks["no_relevant_power_of_two_cycles"] == {
        "passed": False,
        "per_length": [
            {
                "length": 4,
                "passed": False,
                "witness": [0, 1, 2, 3],
            }
        ],
    }


def test_exit_100_never_counts_as_ordinary_completion() -> None:
    ordinary = CapturedProcessOutcome(
        "exited", 0, b"time taken: 1 microseconds\n", b""
    )
    surprising = CapturedProcessOutcome(
        "exited", 100, _K4_UPSTREAM_ADJACENCY.encode("utf-8"), b""
    )

    assert _ordinary_completion_failure(ordinary, 4) is None
    failure = _ordinary_completion_failure(surprising, 4)
    assert failure is not None
    assert "exit 100 is never ordinary tiny-case completion" in failure
    assert '"all_candidate_predicates_passed": false' in failure
    payload = json.loads(failure[failure.index("{") :])
    assert payload["stdout"]["base64"] == base64.b64encode(
        _K4_UPSTREAM_ADJACENCY.encode("utf-8")
    ).decode("ascii")
    assert payload["stdout"]["sha256"] == hashlib.sha256(
        _K4_UPSTREAM_ADJACENCY.encode("utf-8")
    ).hexdigest()


def _assert_completed_build(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, (
        f"command failed with exit {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


@pytest.fixture(scope="session")
def cmake_upstream_executable(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the CMake wrapper out of tree and return its executable."""

    cmake = _required_program("cmake")
    ninja = _required_program("ninja")
    cxx = _required_program("g++")
    build_dir = tmp_path_factory.mktemp("upstream-cmake-build")

    configure = _run(
        [
            cmake,
            "-S",
            str(REPOSITORY_ROOT),
            "-B",
            str(build_dir),
            "-G",
            "Ninja",
            f"-DCMAKE_MAKE_PROGRAM={Path(ninja).as_posix()}",
            f"-DCMAKE_CXX_COMPILER={Path(cxx).as_posix()}",
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        cwd=REPOSITORY_ROOT,
        timeout=BUILD_TIMEOUT_SECONDS,
    )
    _assert_completed_build(configure)

    build = _run(
        [cmake, "--build", str(build_dir), "--target", "eg-upstream-serial"],
        cwd=REPOSITORY_ROOT,
        timeout=BUILD_TIMEOUT_SECONDS,
    )
    _assert_completed_build(build)

    suffix = ".exe" if os.name == "nt" else ""
    executable = build_dir / "bin" / f"eg-upstream-serial{suffix}"
    assert executable.is_file()
    return executable


def test_original_makefile_builds_in_temporary_copy(tmp_path: Path) -> None:
    """Build with the unmodified Makefile without writing into the snapshot."""

    make = _required_program("make")
    _required_program("g++")
    copied_upstream = tmp_path / "erdos-gyarfas"
    shutil.copytree(UPSTREAM, copied_upstream)

    if os.name == "nt" and "msys" in make.lower():
        clean_command = [make, "PATH=/ucrt64/bin:/usr/bin", "clean"]
        build_command = [make, "PATH=/ucrt64/bin:/usr/bin"]
    else:
        clean_command = [make, "clean"]
        build_command = [make]

    clean = _run(clean_command, cwd=copied_upstream, timeout=BUILD_TIMEOUT_SECONDS)
    _assert_completed_build(clean)
    build = _run(build_command, cwd=copied_upstream, timeout=BUILD_TIMEOUT_SECONDS)
    _assert_completed_build(build)

    assert (copied_upstream / "out" / "a.out").is_file()
    assert not (UPSTREAM / "out").exists()


def test_cmake_wrapper_builds(cmake_upstream_executable: Path) -> None:
    assert cmake_upstream_executable.is_file()


@pytest.mark.parametrize("k", [3, 4])
def test_tiny_upstream_invocation_requires_ordinary_exit_zero(
    cmake_upstream_executable: Path,
    k: int,
) -> None:
    outcome = _run_tiny_invocation(
        [str(cmake_upstream_executable), str(k)]
    )

    failure = _ordinary_completion_failure(outcome, k)
    if failure is not None:
        pytest.fail(failure, pytrace=False)
    assert outcome.stdout.strip()
