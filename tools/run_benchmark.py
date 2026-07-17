#!/usr/bin/env python3
"""Run one bounded engineering benchmark and emit a validated JSON result.

The runner executes exactly the argv array in a reviewed case definition; it
never invokes a shell. Results are performance/process observations only and
must not be used as evidence of search completeness or a mathematical claim.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from jsonschema.validators import validator_for

from _common import (
    REPOSITORY_ROOT,
    load_upstream_provenance,
    repository_relative,
    repository_state,
    sha256_file,
    write_json,
)

try:
    import resource
except ImportError:  # pragma: no cover - exercised on Windows
    resource = None


CASE_KEYS = {
    "schema_version",
    "case_id",
    "description",
    "executable",
    "arguments",
    "working_directory",
    "build_directory",
    "k",
    "timeout_seconds",
    "thread_count",
    "environment",
    "limitations",
}


def timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_case(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("benchmark case must be a JSON object")
    unknown = set(value) - CASE_KEYS
    if unknown:
        raise ValueError(f"unknown benchmark case fields: {sorted(unknown)}")
    required = CASE_KEYS - {"build_directory", "environment", "limitations"}
    missing = required - set(value)
    if missing:
        raise ValueError(f"missing benchmark case fields: {sorted(missing)}")
    if value["schema_version"] != "1.0":
        raise ValueError("unsupported benchmark case schema_version")
    if not isinstance(value["case_id"], str) or not value["case_id"]:
        raise ValueError("case_id must be a non-empty string")
    if not isinstance(value["description"], str) or not value["description"]:
        raise ValueError("description must be a non-empty string")
    if not isinstance(value["executable"], str) or not value["executable"]:
        raise ValueError("executable must be a non-empty repository-relative path")
    if not isinstance(value["arguments"], list) or not all(
        isinstance(item, str) for item in value["arguments"]
    ):
        raise ValueError("arguments must be an array of strings")
    if not isinstance(value["k"], int) or isinstance(value["k"], bool) or value["k"] < 1:
        raise ValueError("k must be a positive integer")
    if (
        isinstance(value["timeout_seconds"], bool)
        or not isinstance(value["timeout_seconds"], (int, float))
        or value["timeout_seconds"] <= 0
    ):
        raise ValueError("timeout_seconds must be positive")
    if (
        isinstance(value["thread_count"], bool)
        or not isinstance(value["thread_count"], int)
        or value["thread_count"] < 1
    ):
        raise ValueError("thread_count must be a positive integer")
    if not isinstance(value["working_directory"], str) or not value["working_directory"]:
        raise ValueError("working_directory must be a non-empty string")
    if "build_directory" in value and (
        not isinstance(value["build_directory"], str) or not value["build_directory"]
    ):
        raise ValueError("build_directory must be a non-empty string")
    environment = value.get("environment", {})
    if not isinstance(environment, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in environment.items()
    ):
        raise ValueError("environment must map strings to strings")
    limitations = value.get("limitations", [])
    if not isinstance(limitations, list) or not all(
        isinstance(item, str) and item for item in limitations
    ):
        raise ValueError("limitations must be an array of non-empty strings")
    return value


def repository_path(value: str, *, require_file: bool = False) -> Path:
    path = (REPOSITORY_ROOT / value).resolve()
    repository_relative(path)
    if require_file and not path.is_file():
        raise ValueError(f"file does not exist: {value}")
    return path


def executable_path(value: str) -> Path:
    path = repository_path(value)
    if os.name == "nt" and path.suffix.lower() != ".exe":
        path = path.with_suffix(".exe")
    if not path.is_file():
        raise ValueError(f"benchmark executable does not exist: {repository_relative(path)}")
    return path


def cmake_compiler(case: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    limitations: list[str] = []
    build_directory = case.get("build_directory")
    if not build_directory:
        return "unknown", [], ["Compiler and flags were not recoverable: no build_directory in case."]
    cache_path = repository_path(build_directory) / "CMakeCache.txt"
    if not cache_path.is_file():
        return "unknown", [], ["Compiler and flags were not recoverable: CMakeCache.txt is absent."]

    compile_commands_path = cache_path.parent / "compile_commands.json"
    if compile_commands_path.is_file():
        try:
            records = json.loads(compile_commands_path.read_text(encoding="utf-8"))
            record = next(
                item
                for item in records
                if isinstance(item, dict) and str(item.get("file", "")).replace("\\", "/").endswith("/src/main.cpp")
            )
            if isinstance(record.get("arguments"), list):
                command = [str(item) for item in record["arguments"]]
            else:
                command = shlex.split(str(record["command"]), posix=os.name != "nt")
            if not command:
                raise ValueError("empty compiler command")
            compiler = command[0]
            source = str(record["file"]).replace("\\", "/")
            flags: list[str] = []
            skip_next = False
            for argument in command[1:]:
                if skip_next:
                    skip_next = False
                    continue
                if argument == "-o":
                    skip_next = True
                    continue
                normalized = argument.replace("\\", "/")
                if argument == "-c" or normalized == source:
                    continue
                flags.append(argument)
            return compiler, flags, limitations
        except (KeyError, StopIteration, TypeError, ValueError, json.JSONDecodeError) as exc:
            limitations.append(f"compile_commands.json could not be interpreted: {exc}")

    cache: dict[str, str] = {}
    for line in cache_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line or line.startswith("//") or line.startswith("#") or "=" not in line:
            continue
        key_and_type, value = line.split("=", 1)
        key = key_and_type.split(":", 1)[0]
        cache[key] = value
    compiler = cache.get("CMAKE_CXX_COMPILER", "unknown")
    build_type = cache.get("CMAKE_BUILD_TYPE", "").upper()
    flag_text = " ".join(
        part
        for part in (
            cache.get("CMAKE_CXX_FLAGS", ""),
            cache.get(f"CMAKE_CXX_FLAGS_{build_type}", "") if build_type else "",
        )
        if part
    )
    flags = shlex.split(flag_text, posix=os.name != "nt") if flag_text else []
    if compiler == "unknown":
        limitations.append("CMakeCache.txt did not identify CMAKE_CXX_COMPILER.")
    if not flags:
        limitations.append("CMakeCache.txt reported no explicit C++ compiler flags.")
    return compiler, flags, limitations


def resource_snapshot() -> tuple[float, int | None] | None:
    if resource is None:
        return None
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_seconds = usage.ru_utime + usage.ru_stime
    peak = int(usage.ru_maxrss)
    if sys.platform != "darwin":
        peak *= 1024
    return cpu_seconds, peak


def execute(
    command: list[str], cwd: Path, environment: dict[str, str], timeout_seconds: float
) -> tuple[bytes, bytes, int | None, str, float, float | None, int | None, list[str]]:
    before_resource = resource_snapshot()
    started = time.perf_counter()
    limitations: list[str] = []
    stdout = b""
    stderr = b""
    exit_code: int | None = None
    reason = "spawn-error"
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_code = completed.returncode
        reason = "signal" if completed.returncode < 0 else "exited"
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        reason = "timeout"
    except OSError as exc:
        stderr = str(exc).encode("utf-8", errors="replace")
        reason = "spawn-error"
    wall_seconds = time.perf_counter() - started
    after_resource = resource_snapshot()

    if before_resource is not None and after_resource is not None:
        cpu_seconds = max(0.0, after_resource[0] - before_resource[0])
        peak_memory = after_resource[1]
        if before_resource[1] and after_resource[1] == before_resource[1]:
            limitations.append(
                "Peak memory is the process-wide RUSAGE_CHILDREN maximum and may reflect an earlier child."
            )
    else:
        cpu_seconds = None
        peak_memory = None
        limitations.append("CPU time and peak memory collection are unavailable on this platform.")
    return (
        stdout,
        stderr,
        exit_code,
        reason,
        wall_seconds,
        cpu_seconds,
        peak_memory,
        limitations,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    case_path = args.case if args.case.is_absolute() else REPOSITORY_ROOT / args.case
    output_path = args.output if args.output.is_absolute() else REPOSITORY_ROOT / args.output
    try:
        repository_relative(case_path)
        repository_relative(output_path)
        results_directory = (REPOSITORY_ROOT / "benchmarks" / "results").resolve()
        output_path.resolve().relative_to(results_directory)
        case = load_case(case_path)
        executable = executable_path(case["executable"])
        working_directory = repository_path(case["working_directory"])
        if not working_directory.is_dir():
            raise ValueError("working_directory is not a directory")
        provenance = load_upstream_provenance()
        upstream_commit = provenance["resolved_commit"]
        project_commit, working_tree_status, project_revision = repository_state()
        compiler, compiler_flags, compiler_limitations = cmake_compiler(case)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path = output_path.with_suffix(".stdout.txt")
        stderr_path = output_path.with_suffix(".stderr.txt")
        for generated_path in (output_path, stdout_path, stderr_path):
            if generated_path.exists():
                raise ValueError(
                    f"refusing to overwrite existing benchmark artifact: "
                    f"{repository_relative(generated_path)}"
                )

        relative_executable = repository_relative(executable)
        command_for_record = [relative_executable, *case["arguments"]]
        command_for_process = [str(executable), *case["arguments"]]
        environment = os.environ.copy()
        environment.update(case.get("environment", {}))
        environment["OMP_NUM_THREADS"] = str(case["thread_count"])
        recorded_environment = dict(case.get("environment", {}))
        recorded_environment["OMP_NUM_THREADS"] = str(case["thread_count"])
        compiler_path = Path(compiler)
        if os.name == "nt" and compiler_path.is_file():
            compiler_directory = str(compiler_path.parent)
            environment["PATH"] = os.pathsep.join(
                [compiler_directory, environment.get("PATH", "")]
            )
            recorded_environment["PATH_prepend"] = compiler_path.parent.as_posix()

        started_at = timestamp()
        (
            stdout,
            stderr,
            exit_code,
            termination_reason,
            wall_time_seconds,
            cpu_time_seconds,
            peak_memory_bytes,
            measurement_limitations,
        ) = execute(
            command_for_process,
            working_directory,
            environment,
            float(case["timeout_seconds"]),
        )
        finished_at = timestamp()
        stdout_path.write_bytes(stdout)
        stderr_path.write_bytes(stderr)

        result = {
            "schema_version": "1.0",
            "artifact_kind": "engineering_benchmark",
            "classification": "EMPIRICAL_OBSERVATION",
            "case_id": case["case_id"],
            "project_revision": project_revision,
            "project_commit": project_commit,
            "working_tree_status": working_tree_status,
            "case_definition_sha256": sha256_file(case_path),
            "upstream_commit": upstream_commit,
            "executable_path": relative_executable,
            "executable_sha256": sha256_file(executable),
            "command": command_for_record,
            "k": case["k"],
            "compiler": compiler,
            "compiler_flags": compiler_flags,
            "environment": recorded_environment,
            "operating_system": platform.platform(),
            "architecture": platform.machine() or "unknown",
            "cpu_count": os.cpu_count(),
            "thread_count": case["thread_count"],
            "started_at_utc": started_at,
            "finished_at_utc": finished_at,
            "wall_time_seconds": wall_time_seconds,
            "cpu_time_seconds": cpu_time_seconds,
            "peak_memory_bytes": peak_memory_bytes,
            "exit_code": exit_code,
            "termination_reason": termination_reason,
            "stdout_path": repository_relative(stdout_path),
            "stderr_path": repository_relative(stderr_path),
            "stdout_sha256": sha256_file(stdout_path),
            "stderr_sha256": sha256_file(stderr_path),
            "limitations": [
                *case.get("limitations", []),
                *compiler_limitations,
                *measurement_limitations,
                "This is an engineering benchmark, not evidence of search completeness or a mathematical result.",
            ],
        }

        schema = json.loads(
            (REPOSITORY_ROOT / "schemas" / "benchmark-result.schema.json").read_text(
                encoding="utf-8"
            )
        )
        validator_type = validator_for(schema)
        validator_type.check_schema(schema)
        validator_type(schema, format_checker=FormatChecker()).validate(result)
        write_json(output_path, result)
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        SchemaError,
        ValidationError,
    ) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1

    print(
        json.dumps(
            {
                "case_id": case["case_id"],
                "exit_code": exit_code,
                "ok": True,
                "output": repository_relative(output_path),
                "termination_reason": termination_reason,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
