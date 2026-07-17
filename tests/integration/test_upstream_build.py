"""Bounded engineering integration checks for the preserved upstream source.

These tests exercise build routes and tiny process invocations. They neither
verify the upstream search invariant nor establish exhaustive coverage.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest


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
def test_tiny_upstream_invocation_terminates_and_captures_output(
    cmake_upstream_executable: Path,
    k: int,
) -> None:
    result = _run(
        [str(cmake_upstream_executable), str(k)],
        cwd=REPOSITORY_ROOT,
        timeout=SMOKE_TIMEOUT_SECONDS,
    )

    # Source inspection documents 0 for ordinary completion and 100 when the
    # program prints a candidate. Neither code is interpreted here as a proof.
    assert result.returncode in {0, 100}
    assert isinstance(result.stdout, str)
    assert isinstance(result.stderr, str)
    assert result.stdout.strip()
