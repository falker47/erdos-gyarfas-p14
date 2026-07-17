#!/usr/bin/env python3
"""Resolve the canonical active task ID from versioned review state."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TASK_ID_PATTERN = re.compile(r"^TASK-[0-9]{8}__[a-z0-9_]+$")


class ResolutionError(ValueError):
    """A deterministic review-state or path validation failure."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            rendered = json.dumps(key, ensure_ascii=True)
            raise ResolutionError(f"state contains duplicate JSON key: {rendered}")
        result[key] = value
    return result


def _reject_nonfinite(constant: str) -> None:
    raise ResolutionError(
        f"state contains non-finite numeric constant: {constant}"
    )


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _inside_root(argument: Path, root: Path, label: str) -> Path:
    if ".." in argument.parts:
        raise ResolutionError(f"{label} path is not canonical: parent traversal")
    candidate = argument if argument.is_absolute() else root / argument
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ResolutionError(f"{label} path resolves outside repository root") from exc
    return candidate


def _reject_symlink_components(path: Path, root: Path, label: str) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ResolutionError(f"{label} path resolves outside repository root") from exc
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ResolutionError(
                f"{label} path must not contain a symbolic link: "
                f"{_display_path(current, root)}"
            )


def _load_state(state_path: Path, root: Path) -> dict[str, Any]:
    display = _display_path(state_path, root)
    _reject_symlink_components(state_path, root, "state")
    if not state_path.is_file():
        raise ResolutionError(
            f"state file is missing or not a regular file: {display}"
        )
    try:
        text = state_path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ResolutionError("state is not valid UTF-8") from exc
    except OSError as exc:
        raise ResolutionError(f"state file cannot be read: {display}") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_nonfinite,
        )
    except ResolutionError:
        raise
    except json.JSONDecodeError as exc:
        raise ResolutionError(
            f"state is not valid strict JSON: line {exc.lineno} column {exc.colno}"
        ) from exc
    if not isinstance(value, dict):
        raise ResolutionError("state top-level value must be an object")
    return value


def resolve_task_id(
    state_argument: Path,
    *,
    require_dossier: bool,
    repository_root: Path = REPOSITORY_ROOT,
) -> str:
    """Return a validated active task ID without changing repository state."""

    try:
        root = repository_root.resolve(strict=True)
    except OSError as exc:
        raise ResolutionError("repository root is missing or inaccessible") from exc
    if not root.is_dir():
        raise ResolutionError("repository root is not a directory")

    state_path = _inside_root(state_argument, root, "state")
    state = _load_state(state_path, root)

    if state.get("schema_version") != "1.0":
        raise ResolutionError('state schema_version must equal "1.0"')
    if "active_task_id" not in state:
        raise ResolutionError("state active_task_id is missing")
    task_id = state["active_task_id"]
    if not isinstance(task_id, str):
        raise ResolutionError("state active_task_id must be a string")
    if TASK_ID_PATTERN.fullmatch(task_id) is None:
        raise ResolutionError("state active_task_id is not canonical")

    if require_dossier:
        dossier_status = _inside_root(
            Path("ops") / task_id / "TASK_STATUS.md",
            root,
            "dossier status",
        )
        _reject_symlink_components(dossier_status, root, "dossier status")
        if not dossier_status.is_file():
            raise ResolutionError(
                "dossier status is missing or not a regular file: "
                f"{_display_path(dossier_status, root)}"
            )

    return task_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--require-dossier", action="store_true")
    return parser


def _write_utf8_line(stream: Any, value: str) -> None:
    payload = value.encode("utf-8") + b"\n"
    binary_stream = getattr(stream, "buffer", None)
    if binary_stream is not None:
        binary_stream.write(payload)
        binary_stream.flush()
    else:
        stream.write(payload.decode("utf-8"))
        stream.flush()


def main(
    argv: Sequence[str] | None = None,
    *,
    repository_root: Path = REPOSITORY_ROOT,
) -> int:
    args = build_parser().parse_args(argv)
    try:
        task_id = resolve_task_id(
            args.state,
            require_dossier=args.require_dossier,
            repository_root=repository_root,
        )
    except ResolutionError as exc:
        _write_utf8_line(sys.stderr, f"resolve_review_task_id: error: {exc}")
        return 1
    _write_utf8_line(sys.stdout, task_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
