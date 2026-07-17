"""Small, dependency-free helpers shared by repository tooling.

This module is tooling infrastructure, not part of the independent graph
verifier's mathematical trust base.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    """Return a second-resolution RFC 3339 UTC timestamp."""

    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_relative(path: Path, root: Path = REPOSITORY_ROOT) -> str:
    """Return a normalized repository-relative path or raise ValueError."""

    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"path is outside repository: {path}") from exc
    return relative.as_posix()


def write_json(path: Path, value: Any) -> None:
    """Write stable UTF-8 JSON, creating parent directories as needed."""

    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(serialized, encoding="utf-8", newline="\n")


def file_hash_inventory(directory: Path) -> dict[str, str]:
    """Hash all ordinary files below *directory* in POSIX-path order.

    Symbolic links are rejected because following a link outside an imported
    snapshot would make the integrity check depend on external state.
    """

    root = directory.resolve()
    if not root.is_dir():
        raise ValueError(f"not a directory: {directory}")
    inventory: dict[str, str] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_symlink():
            raise ValueError(f"symbolic link is not supported: {path.relative_to(root)}")
        if path.is_file():
            inventory[path.relative_to(root).as_posix()] = sha256_file(path)
    return inventory


def inventory_digest(inventory: dict[str, str]) -> str:
    """Hash a file inventory using an unambiguous documented byte stream."""

    digest = hashlib.sha256()
    for relative_path in sorted(inventory):
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(inventory[relative_path].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _run_git(root: Path, arguments: Iterable[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _dirty_digest(root: Path, head: str | None) -> str:
    digest = hashlib.sha256()
    if head is not None:
        diff = _run_git(root, ["diff", "--binary", "HEAD", "--"])
        if diff.returncode == 0:
            digest.update(diff.stdout)
    else:
        cached = _run_git(root, ["diff", "--binary", "--cached", "--"])
        if cached.returncode == 0:
            digest.update(cached.stdout)

    untracked = _run_git(root, ["ls-files", "--others", "--exclude-standard", "-z"])
    if untracked.returncode == 0:
        for raw_name in sorted(name for name in untracked.stdout.split(b"\0") if name):
            relative_name = os.fsdecode(raw_name)
            path = root / relative_name
            if path.is_file() and not path.is_symlink():
                digest.update(raw_name)
                digest.update(b"\0")
                digest.update(sha256_file(path).encode("ascii"))
                digest.update(b"\n")
    return digest.hexdigest()


def repository_state(root: Path = REPOSITORY_ROOT) -> tuple[str | None, str, str]:
    """Return ``(commit, status, reproducible revision description)``."""

    inside = _run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != b"true":
        inventory: dict[str, str] = {}
        excluded = {".git", ".agents", ".codex", "build", ".pytest_cache", "__pycache__"}
        for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
            relative = path.relative_to(root)
            if any(part in excluded for part in relative.parts):
                continue
            if (
                len(relative.parts) >= 2
                and relative.parts[0] == "benchmarks"
                and relative.parts[1] == "results"
                and path.name != ".gitkeep"
            ):
                continue
            if (
                len(relative.parts) >= 2
                and relative.parts[0] == "artifacts"
                and relative.parts[1]
                in {"manifests", "certificates", "counterexamples", "checkpoints", "workflow-logs"}
                and path.name != ".gitkeep"
            ):
                continue
            if path.is_file() and not path.is_symlink():
                inventory[relative.as_posix()] = sha256_file(path)
        digest = inventory_digest(inventory)
        return None, "not-a-git-repository", f"not-a-git-repository:sha256:{digest}"

    head_result = _run_git(root, ["rev-parse", "--verify", "HEAD"])
    head = head_result.stdout.decode("ascii").strip() if head_result.returncode == 0 else None
    status_result = _run_git(root, ["status", "--porcelain=v1", "--untracked-files=all"])
    if status_result.returncode != 0:
        revision = head or "unborn"
        return head, "unknown", f"unknown:{revision}"
    if not status_result.stdout:
        if head is None:
            return None, "unborn", "unborn:clean-index"
        return head, "clean", head

    digest = _dirty_digest(root, head)
    prefix = head or "unborn"
    return head, "dirty" if head else "unborn", f"dirty:{prefix}:sha256:{digest}"


def load_upstream_provenance(root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    path = root / "upstream" / "UPSTREAM_PROVENANCE.json"
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value
