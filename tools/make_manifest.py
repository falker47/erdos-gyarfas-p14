#!/usr/bin/env python3
"""Create a schema-valid experiment manifest from observed run metadata.

This command does not execute a search and never upgrades a mathematical
claim. It records caller-supplied outcomes and hashes files that actually
exist. Non-run/refused scaffold records may omit executable and stream hashes.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
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
    utc_now,
    write_json,
)


def json_array(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"invalid JSON: {exc}") from exc
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise argparse.ArgumentTypeError("expected a JSON array of strings")
    return parsed


def key_value(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected KEY=VALUE")
    key, raw = value.split("=", 1)
    if not key:
        raise argparse.ArgumentTypeError("KEY must not be empty")
    return key, raw


def json_key_value(value: str) -> tuple[str, Any]:
    key, raw = key_value(value)
    try:
        return key, json.loads(raw)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"invalid JSON value for {key}: {exc}") from exc


def nonnegative_int_key_value(value: str) -> tuple[str, int]:
    key, raw = key_value(value)
    try:
        number = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"counter {key} is not an integer") from exc
    if number < 0:
        raise argparse.ArgumentTypeError(f"counter {key} must be nonnegative")
    return key, number


def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def optional_path(value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else REPOSITORY_ROOT / path


def seed_value(value: str | None) -> str | int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--claim-id", action="append", default=[])
    parser.add_argument(
        "--classification",
        choices=[
            "COMPUTER_CERTIFIED_RESULT",
            "VERIFIED_BOUNDED_COMPUTATION",
            "REPRODUCED_UPSTREAM_RESULT",
            "EMPIRICAL_OBSERVATION",
            "ENGINEERING_ASSUMPTION",
            "HEURISTIC",
            "NEGATIVE_RESULT",
        ],
        required=True,
    )
    parser.add_argument("--target-statement", required=True)
    parser.add_argument("--project-commit")
    parser.add_argument(
        "--working-tree-status",
        choices=["clean", "dirty", "unborn", "not-a-git-repository", "unknown"],
    )
    parser.add_argument(
        "--upstream-provenance",
        type=Path,
        default=Path("upstream/UPSTREAM_PROVENANCE.json"),
    )
    parser.add_argument("--upstream-repository")
    parser.add_argument("--upstream-commit")
    parser.add_argument("--executable")
    parser.add_argument("--command-json", type=json_array, required=True)
    parser.add_argument("--parameter", type=json_key_value, action="append", default=[])
    parser.add_argument("--parameter-string", type=key_value, action="append", default=[])
    parser.add_argument(
        "--search-mode",
        choices=["upstream-power2", "p14-power2", "p13-c4c8", "heuristic", "scaffold-only"],
        required=True,
    )
    parser.add_argument("--k", type=int)
    parser.add_argument("--forbidden-cycle-length", type=int, action="append", default=[])
    parser.add_argument("--pruning-rule-id", action="append", default=[])
    parser.add_argument("--partition-id")
    parser.add_argument("--seed")
    parser.add_argument("--started-at-utc")
    parser.add_argument("--finished-at-utc")
    parser.add_argument("--exit-code", type=int)
    parser.add_argument(
        "--termination-reason",
        choices=[
            "completed",
            "failed",
            "timeout",
            "cancelled",
            "interrupted",
            "out-of-memory",
            "refused",
            "not-run",
            "error",
        ],
        required=True,
    )
    parser.add_argument("--completed", action="store_true")
    parser.add_argument("--compiler")
    parser.add_argument("--compiler-flag", action="append", default=[])
    parser.add_argument("--runtime-dependency", type=key_value, action="append", default=[])
    parser.add_argument("--environment", type=json_key_value, action="append", default=[])
    parser.add_argument("--memory-limit-bytes", type=int)
    parser.add_argument("--peak-memory-bytes", type=int)
    parser.add_argument("--wall-time-seconds", type=float)
    parser.add_argument("--cpu-time-seconds", type=float)
    parser.add_argument("--counter", type=nonnegative_int_key_value, action="append", default=[])
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--stdout")
    parser.add_argument("--stderr")
    parser.add_argument("--verifier-name")
    parser.add_argument("--verifier-version")
    parser.add_argument("--verifier-command-json", type=json_array)
    parser.add_argument("--verifier-executable")
    parser.add_argument(
        "--verifier-result",
        choices=["not-run", "passed", "failed", "error"],
        default="not-run",
    )
    parser.add_argument("--limitation", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.classification == "COMPUTER_CERTIFIED_RESULT":
        raise SystemExit(
            "COMPUTER_CERTIFIED_RESULT emission is disabled while the certificate design is provisional"
        )
    if args.search_mode == "scaffold-only" and (
        args.completed or args.termination_reason not in {"refused", "not-run"}
    ):
        raise SystemExit("scaffold-only manifests must be incomplete and refused/not-run")
    if args.completed and (args.termination_reason != "completed" or args.exit_code is None):
        raise SystemExit("--completed requires termination reason completed and an exit code")
    if args.wall_time_seconds is None and args.termination_reason not in {"refused", "not-run"}:
        raise SystemExit("a measured --wall-time-seconds is required for an executed run")

    try:
        auto_commit, auto_status, _ = repository_state()
        provenance_path = args.upstream_provenance
        if not provenance_path.is_absolute():
            provenance_path = REPOSITORY_ROOT / provenance_path
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        upstream_repository = args.upstream_repository or provenance["repository"]
        upstream_commit = args.upstream_commit or provenance.get("resolved_commit")

        executable = optional_path(args.executable)
        executable_sha256 = sha256_file(executable) if executable is not None else None

        artifact_paths = [optional_path(value) for value in args.artifact]
        artifact_paths = [path for path in artifact_paths if path is not None]
        for stream_path in (optional_path(args.stdout), optional_path(args.stderr)):
            if stream_path is not None and stream_path not in artifact_paths:
                artifact_paths.append(stream_path)
        artifact_by_name = {repository_relative(path): path for path in artifact_paths}
        if len(artifact_by_name) != len(artifact_paths):
            raise ValueError("duplicate artifact path after canonicalization")
        artifact_names = sorted(artifact_by_name)
        artifact_hashes = {
            name: sha256_file(artifact_by_name[name]) for name in artifact_names
        }

        verifier: dict[str, Any] | None = None
        if args.verifier_name is not None:
            if args.verifier_version is None or args.verifier_command_json is None:
                raise ValueError("verifier name requires version and command")
            verifier_executable = optional_path(args.verifier_executable)
            verifier = {
                "name": args.verifier_name,
                "version": args.verifier_version,
                "command": args.verifier_command_json,
                "executable_sha256": (
                    sha256_file(verifier_executable) if verifier_executable is not None else None
                ),
            }

        runtime_dependencies = pairs(args.runtime_dependency)
        runtime_dependencies.setdefault("python", platform.python_version())
        environment = pairs(args.environment)
        for name in ("GITHUB_ACTIONS", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT"):
            if name in os.environ:
                environment.setdefault(name, os.environ[name])

        now = utc_now()
        manifest = {
            "schema_version": "1.0",
            "run_id": args.run_id,
            "task_id": args.task_id,
            "claim_ids": sorted(set(args.claim_id)),
            "classification": args.classification,
            "target_statement": args.target_statement,
            "project_commit": args.project_commit or auto_commit,
            "working_tree_status": args.working_tree_status or auto_status,
            "upstream_repository": upstream_repository,
            "upstream_commit": upstream_commit,
            "executable_sha256": executable_sha256,
            "command": args.command_json,
            "parameters": pairs([*args.parameter, *args.parameter_string]),
            "search_mode": args.search_mode,
            "k": args.k,
            "forbidden_cycle_lengths": sorted(set(args.forbidden_cycle_length)),
            "pruning_rule_ids": sorted(set(args.pruning_rule_id)),
            "partition_id": args.partition_id,
            "seed": seed_value(args.seed),
            "started_at_utc": args.started_at_utc or now,
            "finished_at_utc": args.finished_at_utc or now,
            "exit_code": args.exit_code,
            "termination_reason": args.termination_reason,
            "completed": args.completed,
            "host": platform.node() or None,
            "operating_system": platform.platform(),
            "architecture": platform.machine() or "unknown",
            "compiler": args.compiler,
            "compiler_flags": args.compiler_flag,
            "runtime_dependencies": runtime_dependencies,
            "environment": environment,
            "cpu_count": os.cpu_count(),
            "memory_limit_bytes": args.memory_limit_bytes,
            "peak_memory_bytes": args.peak_memory_bytes,
            "wall_time_seconds": args.wall_time_seconds,
            "cpu_time_seconds": args.cpu_time_seconds,
            "counters": pairs(args.counter),
            "artifacts": artifact_names,
            "artifact_sha256": artifact_hashes,
            "stdout_sha256": sha256_file(optional_path(args.stdout)) if args.stdout else None,
            "stderr_sha256": sha256_file(optional_path(args.stderr)) if args.stderr else None,
            "verifier": verifier,
            "verifier_result": args.verifier_result,
            "limitations": args.limitation,
        }

        schema_path = REPOSITORY_ROOT / "schemas" / "experiment-manifest.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator_type = validator_for(schema)
        validator_type.check_schema(schema)
        validator_type(schema, format_checker=FormatChecker()).validate(manifest)

        output = args.output if args.output.is_absolute() else REPOSITORY_ROOT / args.output
        output_name = repository_relative(output)
        if not output_name.startswith("artifacts/manifests/"):
            raise ValueError("manifest output must be below artifacts/manifests/")
        if output.exists():
            raise ValueError(f"refusing to overwrite existing manifest: {output_name}")
        write_json(output, manifest)
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
            {"ok": True, "output": repository_relative(output), "run_id": args.run_id},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
