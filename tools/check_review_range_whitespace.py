#!/usr/bin/env python3
"""Check whitespace in the canonical committed Git review range."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class CheckError(ValueError):
    """A deterministic state, path, revision, or ancestry failure."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            rendered = json.dumps(key, ensure_ascii=True)
            raise CheckError(f"state contains duplicate JSON key: {rendered}")
        result[key] = value
    return result


def _reject_nonfinite(constant: str) -> None:
    raise CheckError(f"state contains non-finite numeric constant: {constant}")


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _inside_root(argument: Path, root: Path, label: str) -> Path:
    if ".." in argument.parts:
        raise CheckError(f"{label} path is not canonical: parent traversal")
    candidate = argument if argument.is_absolute() else root / argument
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise CheckError(f"{label} path resolves outside repository root") from exc
    return candidate


def _reject_symlink_components(path: Path, root: Path, label: str) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise CheckError(f"{label} path resolves outside repository root") from exc
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise CheckError(
                f"{label} path must not contain a symbolic link: "
                f"{_display_path(current, root)}"
            )


def _load_state(state_path: Path, root: Path) -> dict[str, Any]:
    display = _display_path(state_path, root)
    _reject_symlink_components(state_path, root, "state")
    if not state_path.is_file():
        raise CheckError(f"state file is missing or not a regular file: {display}")
    try:
        text = state_path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CheckError("state is not valid UTF-8") from exc
    except OSError as exc:
        raise CheckError(f"state file cannot be read: {display}") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_nonfinite,
        )
    except CheckError:
        raise
    except json.JSONDecodeError as exc:
        raise CheckError(
            f"state is not valid strict JSON: line {exc.lineno} column {exc.colno}"
        ) from exc
    if not isinstance(value, dict):
        raise CheckError("state top-level value must be an object")
    if value.get("schema_version") != "1.0":
        raise CheckError('state schema_version must equal "1.0"')
    return value


def _git_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in (
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CEILING_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_DIR",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_REPLACE_REF_BASE",
        "GIT_WORK_TREE",
    ):
        environment.pop(name, None)
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    environment["LANG"] = "C"
    environment["LC_ALL"] = "C"
    return environment


def _run_git(root: Path, arguments: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-c",
            "core.quotePath=true",
            *arguments,
        ],
        cwd=root,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_git_environment(),
    )


def _validate_git_root(root: Path) -> None:
    result = _run_git(root, ["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        raise CheckError("repository root is not a readable Git worktree")
    try:
        observed = Path(result.stdout.decode("utf-8").strip()).resolve(strict=True)
    except (OSError, UnicodeDecodeError) as exc:
        raise CheckError("Git returned an invalid repository root") from exc
    if observed != root:
        raise CheckError("script-derived root is not the Git worktree root")


def _resolve_commit(root: Path, revision: str, label: str) -> str:
    result = _run_git(
        root,
        ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"],
    )
    if result.returncode != 0:
        rendered = json.dumps(revision, ensure_ascii=True)
        raise CheckError(f"{label} does not resolve to an existing commit: {rendered}")
    try:
        resolved = result.stdout.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise CheckError(f"Git returned a non-ASCII {label}") from exc
    if FULL_SHA_PATTERN.fullmatch(resolved) is None:
        raise CheckError(f"Git returned a noncanonical full SHA for {label}")
    return resolved


def _review_base(state: dict[str, Any], root: Path) -> str:
    if "review_base_commit" not in state:
        raise CheckError("state review_base_commit is missing")
    value = state["review_base_commit"]
    if not isinstance(value, str):
        raise CheckError("state review_base_commit must be a string")
    if value == "ROOT":
        raise CheckError("state review_base_commit ROOT is not supported")
    if FULL_SHA_PATTERN.fullmatch(value) is None:
        raise CheckError(
            "state review_base_commit must be a lowercase 40-character Git SHA"
        )
    return _resolve_commit(root, value, "state review_base_commit")


def _validate_ancestry(root: Path, base: str, head: str) -> None:
    result = _run_git(root, ["merge-base", "--is-ancestor", base, head])
    if result.returncode == 1:
        raise CheckError(
            f"review baseline is not an ancestor of head: {base}..{head}"
        )
    if result.returncode != 0:
        raise CheckError("Git failed while validating review-range ancestry")


def _write_bytes(stream: Any, payload: bytes) -> None:
    binary_stream = getattr(stream, "buffer", None)
    if binary_stream is not None:
        binary_stream.write(payload)
        binary_stream.flush()
    else:
        stream.write(payload.decode("utf-8", errors="replace"))
        stream.flush()


def _write_json_line(stream: Any, value: dict[str, Any]) -> None:
    payload = (
        json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")
    _write_bytes(stream, payload)


def check_review_range(
    state_argument: Path,
    head_argument: str,
    *,
    repository_root: Path = REPOSITORY_ROOT,
) -> tuple[subprocess.CompletedProcess[bytes], str, str]:
    """Validate the range and run Git's committed-object whitespace check."""

    try:
        root = repository_root.resolve(strict=True)
    except OSError as exc:
        raise CheckError("repository root is missing or inaccessible") from exc
    if not root.is_dir():
        raise CheckError("repository root is not a directory")
    _validate_git_root(root)

    state_path = _inside_root(state_argument, root, "state")
    state = _load_state(state_path, root)
    base = _review_base(state, root)
    head = _resolve_commit(root, head_argument, "head")
    _validate_ancestry(root, base, head)

    result = _run_git(
        root,
        [
            "--no-pager",
            "diff",
            "--no-ext-diff",
            "--no-color",
            "--check",
            f"{base}..{head}",
            "--",
        ],
    )
    return result, base, head


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--head", required=True)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    repository_root: Path = REPOSITORY_ROOT,
) -> int:
    args = build_parser().parse_args(argv)
    try:
        result, base, head = check_review_range(
            args.state,
            args.head,
            repository_root=repository_root,
        )
    except CheckError as exc:
        _write_bytes(
            sys.stderr,
            f"check_review_range_whitespace: error: {exc}\n".encode("utf-8"),
        )
        return 1

    if result.returncode != 0:
        _write_bytes(sys.stdout, result.stdout)
        _write_bytes(sys.stderr, result.stderr)
        return result.returncode if result.returncode > 0 else 1

    _write_json_line(
        sys.stdout,
        {
            "base": base,
            "head": head,
            "ok": True,
            "range": f"{base}..{head}",
        },
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
