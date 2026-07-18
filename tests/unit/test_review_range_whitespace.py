from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Sequence

import pytest

from tools import check_review_range_whitespace as checker


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def run_git(
    root: Path,
    arguments: Sequence[str],
    *,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    environment["LANG"] = "C"
    environment["LC_ALL"] = "C"
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-c",
            "commit.gpgSign=false",
            *arguments,
        ],
        cwd=root,
        check=False,
        stdin=None if input_bytes is not None else subprocess.DEVNULL,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )
    assert result.returncode == 0, (
        f"git {' '.join(arguments)} failed with {result.returncode}\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    return result


def commit_file(root: Path, content: bytes, message: str) -> str:
    (root / "tracked.txt").write_bytes(content)
    run_git(root, ["add", "--", "tracked.txt"])
    run_git(root, ["commit", "--quiet", "--no-gpg-sign", "-m", message])
    return run_git(root, ["rev-parse", "HEAD"]).stdout.decode("ascii").strip()


def make_repository(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repository"
    root.mkdir()
    run_git(root, ["init", "--quiet", "--initial-branch=main"])
    run_git(root, ["config", "--local", "user.name", "Synthetic Reviewer"])
    run_git(
        root,
        ["config", "--local", "user.email", "reviewer@example.invalid"],
    )
    run_git(root, ["config", "--local", "core.autocrlf", "false"])
    base = commit_file(root, b"base\n", "base")
    write_state(root, base)
    return root, base


def write_state(root: Path, base: str, **extra: Any) -> Path:
    value = {
        "review_base_commit": base,
        "schema_version": "1.0",
        **extra,
    }
    path = root / "REVIEW_STATE.yaml"
    path.write_bytes(
        (json.dumps(value, ensure_ascii=True, sort_keys=True) + "\n").encode(
            "utf-8"
        )
    )
    return path


def invoke(
    root: Path,
    *,
    state: str | Path = "REVIEW_STATE.yaml",
    head: str = "HEAD",
) -> tuple[int, bytes, bytes]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = checker.main(
            ["--state", os.fspath(state), "--head", head],
            repository_root=root,
        )
    return (
        code,
        stdout.getvalue().encode("utf-8"),
        stderr.getvalue().encode("utf-8"),
    )


def success_record(base: str, head: str) -> bytes:
    return (
        json.dumps(
            {
                "base": base,
                "head": head,
                "ok": True,
                "range": f"{base}..{head}",
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("ascii")


def test_clean_committed_range_succeeds(tmp_path: Path) -> None:
    root, base = make_repository(tmp_path)
    head = commit_file(root, b"clean content\n", "clean range")

    code, stdout, stderr = invoke(root)

    assert (code, stdout, stderr) == (0, success_record(base, head), b"")


def test_committed_trailing_whitespace_fails(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    commit_file(root, b"bad trailing spaces  \n", "trailing whitespace")

    code, stdout, stderr = invoke(root)

    assert code != 0
    assert b"trailing whitespace" in stdout
    assert stderr == b""


def test_committed_space_before_tab_fails(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    commit_file(root, b" \tbad indentation\n", "space before tab")

    code, stdout, stderr = invoke(root)

    assert code != 0
    assert b"space before tab in indent" in stdout
    assert stderr == b""


def test_dirty_worktree_does_not_replace_committed_range(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    commit_file(root, b"committed clean\n", "clean commit")
    (root / "tracked.txt").write_bytes(b"dirty trailing spaces  \n")

    clean_code, _, clean_stderr = invoke(root)

    assert clean_code == 0
    assert clean_stderr == b""

    commit_file(root, b"committed trailing spaces  \n", "bad commit")
    (root / "tracked.txt").write_bytes(b"dirty worktree fixes the line\n")

    bad_code, bad_stdout, bad_stderr = invoke(root)

    assert bad_code != 0
    assert b"trailing whitespace" in bad_stdout
    assert bad_stderr == b""


def test_baseline_equal_to_head_succeeds_for_empty_range(tmp_path: Path) -> None:
    root, base = make_repository(tmp_path)

    code, stdout, stderr = invoke(root)

    assert (code, stdout, stderr) == (0, success_record(base, base), b"")


def test_nonancestor_baseline_is_rejected(tmp_path: Path) -> None:
    root, original = make_repository(tmp_path)
    baseline = commit_file(root, b"baseline branch\n", "baseline child")
    tree = run_git(root, ["rev-parse", f"{baseline}^{{tree}}"]).stdout.strip()
    sibling = run_git(
        root,
        ["commit-tree", tree.decode("ascii"), "-p", original],
        input_bytes=b"sibling child\n",
    ).stdout.decode("ascii").strip()
    write_state(root, baseline)

    code, stdout, stderr = invoke(root, head=sibling)

    assert code == 1
    assert stdout == b""
    assert b"review baseline is not an ancestor of head" in stderr
    assert f"{baseline}..{sibling}".encode("ascii") in stderr


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        ("0" * 40, b"does not resolve to an existing commit"),
        ("abc123", b"must be a lowercase 40-character Git SHA"),
        ("A" * 40, b"must be a lowercase 40-character Git SHA"),
        ("ROOT", b"ROOT is not supported"),
    ],
)
def test_missing_or_malformed_baseline_is_rejected(
    tmp_path: Path, base: str, expected: bytes
) -> None:
    root, _ = make_repository(tmp_path)
    write_state(root, base)

    code, stdout, stderr = invoke(root)

    assert code == 1
    assert stdout == b""
    assert expected in stderr


def test_noncommit_baseline_object_is_rejected(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    tree = run_git(root, ["rev-parse", "HEAD^{tree}"]).stdout.decode(
        "ascii"
    ).strip()
    write_state(root, tree)

    code, stdout, stderr = invoke(root)

    assert code == 1
    assert stdout == b""
    assert b"does not resolve to an existing commit" in stderr


@pytest.mark.parametrize("head_kind", ["missing", "tree"])
def test_missing_or_noncommit_head_is_rejected(
    tmp_path: Path, head_kind: str
) -> None:
    root, _ = make_repository(tmp_path)
    head = "refs/heads/does-not-exist"
    if head_kind == "tree":
        head = run_git(root, ["rev-parse", "HEAD^{tree}"]).stdout.decode(
            "ascii"
        ).strip()

    code, stdout, stderr = invoke(root, head=head)

    assert code == 1
    assert stdout == b""
    assert b"head does not resolve to an existing commit" in stderr


def test_missing_state_is_rejected(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    (root / "REVIEW_STATE.yaml").unlink()

    code, stdout, stderr = invoke(root)

    assert code == 1
    assert stdout == b""
    assert b"state file is missing or not a regular file" in stderr


def test_state_directory_is_rejected(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    state = root / "REVIEW_STATE.yaml"
    state.unlink()
    state.mkdir()

    code, stdout, stderr = invoke(root)

    assert code == 1
    assert stdout == b""
    assert b"state file is missing or not a regular file" in stderr


def test_malformed_state_is_rejected(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    (root / "REVIEW_STATE.yaml").write_bytes(b'{"schema_version":"1.0",')

    code, stdout, stderr = invoke(root)

    assert code == 1
    assert stdout == b""
    assert b"state is not valid strict JSON" in stderr


def test_duplicate_state_key_is_rejected(tmp_path: Path) -> None:
    root, base = make_repository(tmp_path)
    (root / "REVIEW_STATE.yaml").write_bytes(
        (
            '{"schema_version":"1.0","review_base_commit":"'
            + base
            + '","review_base_commit":"'
            + base
            + '"}\n'
        ).encode("ascii")
    )

    code, stdout, stderr = invoke(root)

    assert code == 1
    assert stdout == b""
    assert b'duplicate JSON key: "review_base_commit"' in stderr


@pytest.mark.parametrize("value", [[], "state", None, 17])
def test_nonobject_state_is_rejected(tmp_path: Path, value: Any) -> None:
    root, _ = make_repository(tmp_path)
    (root / "REVIEW_STATE.yaml").write_text(
        json.dumps(value) + "\n", encoding="utf-8", newline="\n"
    )

    code, _, stderr = invoke(root)

    assert code == 1
    assert b"state top-level value must be an object" in stderr


def test_wrong_state_schema_is_rejected(tmp_path: Path) -> None:
    root, base = make_repository(tmp_path)
    write_state(root, base, schema_version="2.0")

    code, _, stderr = invoke(root)

    assert code == 1
    assert b'schema_version must equal "1.0"' in stderr


def test_missing_state_baseline_is_rejected(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    (root / "REVIEW_STATE.yaml").write_text(
        '{"schema_version":"1.0"}\n', encoding="utf-8", newline="\n"
    )

    code, _, stderr = invoke(root)

    assert code == 1
    assert b"state review_base_commit is missing" in stderr


@pytest.mark.parametrize("value", [None, 17, [], {}])
def test_nonstring_state_baseline_is_rejected(
    tmp_path: Path, value: Any
) -> None:
    root, _ = make_repository(tmp_path)
    (root / "REVIEW_STATE.yaml").write_text(
        json.dumps(
            {"review_base_commit": value, "schema_version": "1.0"},
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    code, _, stderr = invoke(root)

    assert code == 1
    assert b"state review_base_commit must be a string" in stderr


@pytest.mark.parametrize("constant", [b"NaN", b"Infinity", b"-Infinity"])
def test_nonfinite_state_number_is_rejected(
    tmp_path: Path, constant: bytes
) -> None:
    root, base = make_repository(tmp_path)
    (root / "REVIEW_STATE.yaml").write_bytes(
        b'{"schema_version":"1.0","review_base_commit":"'
        + base.encode("ascii")
        + b'","unexpected":'
        + constant
        + b"}\n"
    )

    code, _, stderr = invoke(root)

    assert code == 1
    assert b"non-finite numeric constant: " + constant in stderr


def test_non_utf8_state_is_rejected(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    (root / "REVIEW_STATE.yaml").write_bytes(b"\xff")

    code, _, stderr = invoke(root)

    assert code == 1
    assert b"state is not valid UTF-8" in stderr


def test_state_parent_traversal_and_outside_path_are_rejected(
    tmp_path: Path,
) -> None:
    root, base = make_repository(tmp_path)
    outside = write_state(tmp_path, base)

    traversal = invoke(root, state="../REVIEW_STATE.yaml")
    absolute = invoke(root, state=outside)

    assert traversal[0] == 1
    assert b"state path is not canonical: parent traversal" in traversal[2]
    assert absolute[0] == 1
    assert b"state path resolves outside repository root" in absolute[2]


def test_state_symlink_is_rejected_where_supported(tmp_path: Path) -> None:
    root, _ = make_repository(tmp_path)
    link = root / "linked-state.json"
    try:
        link.symlink_to(root / "REVIEW_STATE.yaml")
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"file symlinks are unavailable: {exc}")

    code, stdout, stderr = invoke(root, state=link)

    assert code == 1
    assert stdout == b""
    assert b"state path must not contain a symbolic link" in stderr


def byte_inventory(root: Path) -> dict[str, tuple[str, bytes]]:
    result: dict[str, tuple[str, bytes]] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("symlink", os.fsencode(os.readlink(path)))
        elif path.is_file():
            result[relative] = ("file", path.read_bytes())
    return result


def test_output_is_deterministic_and_helper_is_read_only(tmp_path: Path) -> None:
    root, base = make_repository(tmp_path)
    head = commit_file(root, b"second clean commit\n", "second")
    (root / "tracked.txt").write_bytes(b"dirty but ignored  \n")
    before_status = run_git(
        root, ["status", "--porcelain=v1", "--untracked-files=all"]
    ).stdout
    before_refs = run_git(
        root, ["for-each-ref", "--format=%(refname) %(objectname)"]
    ).stdout
    before_files = byte_inventory(root)
    before_environment = os.environ.copy()

    first = invoke(root)
    second = invoke(root)

    assert first == second == (0, success_record(base, head), b"")
    assert byte_inventory(root) == before_files
    assert (
        run_git(root, ["status", "--porcelain=v1", "--untracked-files=all"]).stdout
        == before_status
    )
    assert (
        run_git(root, ["for-each-ref", "--format=%(refname) %(objectname)"]).stdout
        == before_refs
    )
    assert os.environ == before_environment


def test_git_environment_cannot_redirect_script_derived_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    intended_parent = tmp_path / "intended"
    other_parent = tmp_path / "other"
    intended_parent.mkdir()
    other_parent.mkdir()
    root, base = make_repository(intended_parent)
    head = commit_file(root, b"intended clean range\n", "intended")
    other, _ = make_repository(other_parent)
    monkeypatch.setenv("GIT_DIR", os.fspath(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", os.fspath(other))

    code, stdout, stderr = invoke(root)

    assert (code, stdout, stderr) == (0, success_record(base, head), b"")


def workflow_job(workflow: str, job_id: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(job_id)}:\n(.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)",
        workflow,
    )
    assert match is not None
    return match.group(0)


def test_workflow_separates_committed_range_from_worktree_checks() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    committed_job = workflow_job(workflow, "committed-range-whitespace")
    python_job = workflow_job(workflow, "python-verifier")
    cpp_job = workflow_job(workflow, "cpp-upstream")

    assert "runs-on: ubuntu-24.04" in committed_job
    assert "fetch-depth: 0" in committed_job
    assert 'python-version: "3.11"' in committed_job
    assert re.search(
        r"python tools/check_review_range_whitespace\.py\s+"
        r"--state REVIEW_STATE\.yaml\s+--head HEAD",
        committed_job,
    )
    assert committed_job.count("tools/check_review_range_whitespace.py") == 1
    assert "git diff --check" not in committed_job

    assert workflow.count("- name: Check test-created worktree whitespace") == 2
    assert workflow.count("run: git diff --check") == 2
    assert "- name: Check diff whitespace" not in workflow
    assert python_job.index("python -m pytest") < python_job.index(
        "Check test-created worktree whitespace"
    )
    assert cpp_job.index("test_upstream_build.py") < cpp_job.index(
        "Check test-created worktree whitespace"
    )
    assert "continue-on-error" not in workflow
    assert "|| true" not in workflow
