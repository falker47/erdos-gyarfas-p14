from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import pytest

from tools import resolve_review_task_id as resolver


ROOT = Path(__file__).parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "heavy-search.yml"
# Synthetic fixture identity only; canonical repository expectations come from state.
TASK_ID = "TASK-20260717__bind_heavy_workflow_task_identity"
OBSOLETE_TASK_ID = "TASK-20260715__bootstrap_reproducible_baseline"


def write_state(root: Path, value: Any) -> Path:
    state = root / "REVIEW_STATE.yaml"
    state.write_bytes(
        (json.dumps(value, ensure_ascii=True, sort_keys=True) + "\n").encode("utf-8")
    )
    return state


def make_valid_root(tmp_path: Path, task_id: str = TASK_ID) -> tuple[Path, Path]:
    root = tmp_path / "repository"
    root.mkdir()
    state = write_state(
        root,
        {
            "active_task_id": task_id,
            "schema_version": "1.0",
        },
    )
    status = root / "ops" / task_id / "TASK_STATUS.md"
    status.parent.mkdir(parents=True)
    status.write_bytes(b"# Synthetic task status\n")
    return root, state


def invoke(
    root: Path,
    state: str | Path = "REVIEW_STATE.yaml",
    *,
    require_dossier: bool = True,
) -> tuple[int, bytes, bytes]:
    arguments = ["--state", os.fspath(state)]
    if require_dossier:
        arguments.append("--require-dossier")
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = resolver.main(arguments, repository_root=root)
    return code, stdout.getvalue().encode("utf-8"), stderr.getvalue().encode("utf-8")


def test_valid_state_and_existing_dossier_resolves(tmp_path: Path) -> None:
    root, _ = make_valid_root(tmp_path)

    code, stdout, stderr = invoke(root)

    assert code == 0
    assert stdout == f"{TASK_ID}\n".encode("ascii")
    assert stderr == b""


def test_output_is_byte_deterministic(tmp_path: Path) -> None:
    root, _ = make_valid_root(tmp_path)

    first = invoke(root)
    second = invoke(root)

    assert first == second == (0, f"{TASK_ID}\n".encode("ascii"), b"")


def test_active_task_id_wins_when_accepted_task_id_differs(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    accepted_task_id = "TASK-20260717__accepted_task"
    active_task_id = "TASK-20260718__active_task"
    assert accepted_task_id != active_task_id
    write_state(
        root,
        {
            "schema_version": "1.0",
            "accepted_task_id": accepted_task_id,
            "active_task_id": active_task_id,
        },
    )
    active_status = root / "ops" / active_task_id / "TASK_STATUS.md"
    active_status.parent.mkdir(parents=True)
    active_status.write_bytes(b"# Synthetic active task status\n")

    assert not (root / "ops" / accepted_task_id).exists()

    code, stdout, stderr = invoke(root)

    assert code == 0
    assert stdout == active_task_id.encode("ascii") + b"\n"
    assert stderr == b""


def test_malformed_json_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    (root / "REVIEW_STATE.yaml").write_bytes(b'{"schema_version": "1.0",')

    code, stdout, stderr = invoke(root, require_dossier=False)

    assert code == 1
    assert stdout == b""
    assert stderr.startswith(b"resolve_review_task_id: error: state is not valid strict JSON:")


def test_missing_state_file_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()

    code, stdout, stderr = invoke(root, require_dossier=False)

    assert code == 1
    assert stdout == b""
    assert b"state file is missing or not a regular file: REVIEW_STATE.yaml" in stderr


def test_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    (root / "REVIEW_STATE.yaml").write_bytes(
        b'{"schema_version":"1.0","active_task_id":"TASK-20260717__one",'
        b'"active_task_id":"TASK-20260717__two"}\n'
    )

    code, stdout, stderr = invoke(root, require_dossier=False)

    assert code == 1
    assert stdout == b""
    assert b'duplicate JSON key: "active_task_id"' in stderr


@pytest.mark.parametrize("constant", [b"NaN", b"Infinity", b"-Infinity"])
def test_nonfinite_numeric_constant_is_rejected(
    tmp_path: Path, constant: bytes
) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    (root / "REVIEW_STATE.yaml").write_bytes(
        b'{"schema_version":"1.0","active_task_id":"TASK-20260717__valid",'
        b'"unexpected":' + constant + b"}\n"
    )

    code, stdout, stderr = invoke(root, require_dossier=False)

    assert code == 1
    assert stdout == b""
    assert b"non-finite numeric constant: " + constant in stderr


@pytest.mark.parametrize("value", [[], "state", None, 17])
def test_top_level_non_object_is_rejected(tmp_path: Path, value: Any) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    write_state(root, value)

    code, _, stderr = invoke(root, require_dossier=False)

    assert code == 1
    assert b"state top-level value must be an object" in stderr


def test_wrong_schema_version_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    write_state(root, {"schema_version": "2.0", "active_task_id": TASK_ID})

    code, _, stderr = invoke(root, require_dossier=False)

    assert code == 1
    assert b'schema_version must equal "1.0"' in stderr


def test_missing_active_task_id_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    write_state(root, {"schema_version": "1.0"})

    code, _, stderr = invoke(root, require_dossier=False)

    assert code == 1
    assert b"active_task_id is missing" in stderr


@pytest.mark.parametrize("value", [None, 17, [], {}])
def test_non_string_active_task_id_is_rejected(tmp_path: Path, value: Any) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    write_state(root, {"schema_version": "1.0", "active_task_id": value})

    code, _, stderr = invoke(root, require_dossier=False)

    assert code == 1
    assert b"active_task_id must be a string" in stderr


@pytest.mark.parametrize(
    "task_id",
    [
        "TASK-20260717__Uppercase",
        "TASK-20260717__with/slash",
        "TASK-20260717__with space",
        "TASK-20260717__../escape",
        "TASK-2026071__short_date",
        "TASK-20260717__hyphenated-name",
        "TASK-20260717__",
    ],
)
def test_noncanonical_task_ids_are_rejected(tmp_path: Path, task_id: str) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    write_state(root, {"schema_version": "1.0", "active_task_id": task_id})

    code, _, stderr = invoke(root, require_dossier=False)

    assert code == 1
    assert b"active_task_id is not canonical" in stderr


def test_state_parent_traversal_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    write_state(tmp_path, {"schema_version": "1.0", "active_task_id": TASK_ID})

    code, stdout, stderr = invoke(root, "../REVIEW_STATE.yaml", require_dossier=False)

    assert code == 1
    assert stdout == b""
    assert b"state path is not canonical: parent traversal" in stderr


def test_absolute_state_path_outside_root_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    outside = write_state(
        tmp_path,
        {"schema_version": "1.0", "active_task_id": TASK_ID},
    )

    code, stdout, stderr = invoke(root, outside, require_dossier=False)

    assert code == 1
    assert stdout == b""
    assert b"state path resolves outside repository root" in stderr


def test_missing_dossier_is_rejected(tmp_path: Path) -> None:
    root, _ = make_valid_root(tmp_path)
    (root / "ops" / TASK_ID / "TASK_STATUS.md").unlink()

    code, _, stderr = invoke(root)

    assert code == 1
    assert b"dossier status is missing or not a regular file" in stderr


def test_dossier_directory_instead_of_file_is_rejected(tmp_path: Path) -> None:
    root, _ = make_valid_root(tmp_path)
    status = root / "ops" / TASK_ID / "TASK_STATUS.md"
    status.unlink()
    status.mkdir()

    code, _, stderr = invoke(root)

    assert code == 1
    assert b"dossier status is missing or not a regular file" in stderr


def test_dossier_symlink_is_rejected_where_supported(tmp_path: Path) -> None:
    root, _ = make_valid_root(tmp_path)
    status = root / "ops" / TASK_ID / "TASK_STATUS.md"
    target = root / "actual-status.md"
    target.write_bytes(b"# Actual status\n")
    status.unlink()
    try:
        status.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"file symlinks are unavailable: {exc}")

    code, _, stderr = invoke(root)

    assert code == 1
    assert b"dossier status path must not contain a symbolic link" in stderr


def inventory(root: Path) -> dict[str, tuple[str, bytes | None, int]]:
    result: dict[str, tuple[str, bytes | None, int]] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        stat = path.lstat()
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path).encode(), stat.st_mtime_ns)
        elif path.is_file():
            result[relative] = ("file", path.read_bytes(), stat.st_mtime_ns)
        else:
            result[relative] = ("directory", None, stat.st_mtime_ns)
    return result


def test_resolver_does_not_write_files_or_environment(tmp_path: Path) -> None:
    root, _ = make_valid_root(tmp_path)
    before_files = inventory(root)
    before_environment = os.environ.copy()

    code, _, _ = invoke(root)

    assert code == 0
    assert inventory(root) == before_files
    assert os.environ == before_environment


def test_current_canonical_state_resolves_exact_active_task() -> None:
    state_text = (ROOT / "REVIEW_STATE.yaml").read_bytes().decode("utf-8")
    state = json.loads(state_text)
    assert isinstance(state, dict)
    active_task_id = state["active_task_id"]
    assert isinstance(active_task_id, str)
    assert re.fullmatch(r"^TASK-[0-9]{8}__[a-z0-9_]+$", active_task_id) is not None
    assert (ROOT / "ops" / active_task_id / "TASK_STATUS.md").is_file()

    process = subprocess.run(
        [
            sys.executable,
            "tools/resolve_review_task_id.py",
            "--state",
            "REVIEW_STATE.yaml",
            "--require-dossier",
        ],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=10,
    )

    assert process.returncode == 0
    assert process.stdout == active_task_id.encode("ascii") + b"\n"
    assert process.stderr == b""


def test_workflow_binds_manifest_to_canonical_resolver_output() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    resolver_index = workflow.index("python tools/resolve_review_task_id.py")
    manifest_index = workflow.index("python tools/make_manifest.py")

    assert OBSOLETE_TASK_ID not in workflow
    assert resolver_index < manifest_index
    assert '--state REVIEW_STATE.yaml' in workflow
    assert '--require-dossier' in workflow
    assert '--task-id "$RESOLVED_TASK_ID"' in workflow
    assert re.search(r'''--task-id\s+["']?TASK-''', workflow) is None
    assert "task_id_source=REVIEW_STATE.yaml:active_task_id" in workflow
    assert "task_dossier_status_path=$task_status_path" in workflow
    assert "review_state_sha256=$review_state_sha256" in workflow
    assert "task_status_sha256=$task_status_sha256" in workflow


def test_workflow_has_no_manual_task_identity_input() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    inputs = workflow.split("    inputs:\n", 1)[1].split("\npermissions:", 1)[0]

    assert "task_id:" not in inputs
    assert "task-id:" not in inputs
    assert "active_task_id:" not in inputs
    assert "inputs.task_id" not in workflow
    assert "inputs.active_task_id" not in workflow
    assert "RESOLVED_TASK_ID: ${{ inputs." not in workflow
