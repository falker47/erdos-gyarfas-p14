from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import pytest

from tools import check_github_action_pins as checker


ROOT = Path(__file__).resolve().parents[2]
FULL_SHA = "0123456789abcdef0123456789abcdef01234567"
OTHER_SHA = "89abcdef0123456789abcdef0123456789abcdef"
DOCKER_DIGEST = "a" * 64
EXPECTED_OFFICIAL_ACTIONS = {
    "actions/checkout": (
        "34e114876b0b11c390a56381ad16ebd13914f8d5",
        "v4.3.1",
    ),
    "actions/setup-python": (
        "a26af69be951a213d495a4c3e4e4022e16d87065",
        "v5.6.0",
    ),
    "actions/upload-artifact": (
        "ea165f8d65b6e75b540449e92b4886f43607fa02",
        "v4.6.2",
    ),
}


def write_workflow(
    root: Path,
    relative: str,
    content: str | bytes,
) -> Path:
    path = root / ".github" / "workflows" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8", newline="\n")
    return path


def invoke(root: Path) -> tuple[int, bytes, bytes]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = checker.main([], repository_root=root)
    return (
        code,
        stdout.getvalue().encode("utf-8"),
        stderr.getvalue().encode("utf-8"),
    )


def success_payload(result: tuple[int, bytes, bytes]) -> dict[str, Any]:
    code, stdout, stderr = result
    assert code == 0
    assert stderr == b""
    assert stdout.endswith(b"\n")
    assert stdout.count(b"\n") == 1
    value = json.loads(stdout)
    assert isinstance(value, dict)
    return value


def test_full_external_commit_sha_is_accepted(tmp_path: Path) -> None:
    write_workflow(
        tmp_path,
        "ci.yml",
        f"name: synthetic\njobs:\n  reusable:\n    uses: owner/action@{FULL_SHA}\n",
    )

    payload = success_payload(invoke(tmp_path))

    assert payload == {
        "external_reference_count": 1,
        "external_references": [
            {
                "commit": FULL_SHA,
                "kind": "github",
                "line": 4,
                "reference": f"owner/action@{FULL_SHA}",
                "repository": "owner/action",
                "workflow": ".github/workflows/ci.yml",
            }
        ],
        "ok": True,
        "workflow_count": 1,
        "workflows": [".github/workflows/ci.yml"],
    }


def test_same_action_in_multiple_workflows_is_sorted_by_path(
    tmp_path: Path,
) -> None:
    write_workflow(
        tmp_path,
        "z-last.yaml",
        f"jobs:\n  z:\n    uses: owner/action@{FULL_SHA}\n",
    )
    write_workflow(
        tmp_path,
        "nested/a-first.yml",
        f"jobs:\n  a:\n    uses: owner/action@{FULL_SHA}\n",
    )

    payload = success_payload(invoke(tmp_path))

    assert payload["workflows"] == [
        ".github/workflows/nested/a-first.yml",
        ".github/workflows/z-last.yaml",
    ]
    assert payload["external_reference_count"] == 2
    assert [
        record["workflow"] for record in payload["external_references"]
    ] == payload["workflows"]


def test_external_action_subpath_is_accepted(tmp_path: Path) -> None:
    write_workflow(
        tmp_path,
        "subpath.yml",
        f"jobs:\n  job:\n    uses: owner/repository/path/to/action@{FULL_SHA}\n",
    )

    payload = success_payload(invoke(tmp_path))

    record = payload["external_references"][0]
    assert record["repository"] == "owner/repository"
    assert record["reference"] == (
        f"owner/repository/path/to/action@{FULL_SHA}"
    )


def test_local_action_is_accepted_and_not_counted_as_external(
    tmp_path: Path,
) -> None:
    write_workflow(
        tmp_path,
        "local.yml",
        "jobs:\n  job:\n    steps:\n      - uses: ./.github/actions/local\n",
    )

    payload = success_payload(invoke(tmp_path))

    assert payload["external_reference_count"] == 0
    assert payload["external_references"] == []


def test_content_addressed_docker_action_is_accepted(tmp_path: Path) -> None:
    reference = f"docker://ghcr.io/example/action@sha256:{DOCKER_DIGEST}"
    write_workflow(
        tmp_path,
        "docker.yml",
        f"jobs:\n  job:\n    steps:\n      - uses: {reference}\n",
    )

    payload = success_payload(invoke(tmp_path))

    assert payload["external_reference_count"] == 1
    assert payload["external_references"] == [
        {
            "kind": "docker",
            "line": 4,
            "reference": reference,
            "workflow": ".github/workflows/docker.yml",
        }
    ]


@pytest.mark.parametrize(
    "reference",
    [
        "actions/checkout@v4",
        "actions/checkout@v4.3.1",
        "actions/checkout@main",
        "actions/checkout@0123456789ab",
        "actions/checkout@0123456789ABCDEF0123456789ABCDEF01234567",
    ],
    ids=["major_tag", "release_tag", "branch", "short_sha", "uppercase_sha"],
)
def test_mutable_or_noncanonical_github_ref_is_rejected(
    tmp_path: Path,
    reference: str,
) -> None:
    write_workflow(
        tmp_path,
        "invalid.yml",
        f"jobs:\n  job:\n    uses: {reference}\n",
    )

    code, stdout, stderr = invoke(tmp_path)

    assert code != 0
    assert stdout == b""
    assert b"lowercase 40-character commit SHA" in stderr


@pytest.mark.parametrize(
    "reference",
    [
        "actions/checkout",
        f"actions@{FULL_SHA}",
        f"actions/checkout@@{FULL_SHA}",
        f"actions//checkout@{FULL_SHA}",
    ],
    ids=["missing_at", "missing_repository", "multiple_at", "empty_segment"],
)
def test_malformed_external_reference_is_rejected(
    tmp_path: Path,
    reference: str,
) -> None:
    write_workflow(
        tmp_path,
        "malformed.yml",
        f"jobs:\n  job:\n    uses: {reference}\n",
    )

    code, stdout, stderr = invoke(tmp_path)

    assert code != 0
    assert stdout == b""
    assert b"owner/repository[/subpath]@ref" in stderr


def test_dynamic_expression_is_rejected(tmp_path: Path) -> None:
    write_workflow(
        tmp_path,
        "dynamic.yml",
        "jobs:\n  job:\n    uses: ${{inputs.action}}\n",
    )

    code, stdout, stderr = invoke(tmp_path)

    assert code != 0
    assert stdout == b""
    assert b"dynamic expressions are not permitted" in stderr


@pytest.mark.parametrize(
    "reference",
    [
        "docker://alpine:3.20",
        "docker://alpine@sha256:abc123",
        f"docker://alpine@sha256:{'A' * 64}",
        f"docker://alpine:3.20@sha256:{DOCKER_DIGEST}",
    ],
    ids=["tag", "short_digest", "uppercase_digest", "tag_and_digest"],
)
def test_mutable_or_noncanonical_docker_action_is_rejected(
    tmp_path: Path,
    reference: str,
) -> None:
    write_workflow(
        tmp_path,
        "docker-invalid.yml",
        f"jobs:\n  job:\n    steps:\n      - uses: {reference}\n",
    )

    code, stdout, stderr = invoke(tmp_path)

    assert code != 0
    assert stdout == b""
    assert b"Docker Action" in stderr or b"mutable tag" in stderr


@pytest.mark.parametrize(
    "content",
    [
        f"jobs:\n  job:\n    uses:\n      owner/action@{FULL_SHA}\n",
        f"jobs:\n  job:\n    uses: >-\n      owner/action@{FULL_SHA}\n",
        f"jobs:\n  job:\n    uses : owner/action@{FULL_SHA}\n",
        f"jobs:\n  job:\n    \"uses\": owner/action@{FULL_SHA}\n",
        f"jobs:\n  job:\n    value: {{uses: owner/action@{FULL_SHA}}}\n",
        f"jobs:\n  job:\n    ? uses\n    : owner/action@{FULL_SHA}\n",
    ],
    ids=[
        "empty_multiline",
        "folded_multiline",
        "space_before_colon",
        "quoted_key",
        "flow_mapping",
        "explicit_key",
    ],
)
def test_multiline_or_ambiguous_uses_key_is_rejected(
    tmp_path: Path,
    content: str,
) -> None:
    write_workflow(tmp_path, "ambiguous.yml", content)

    code, stdout, stderr = invoke(tmp_path)

    assert code != 0
    assert stdout == b""
    assert b"uses" in stderr


def test_comments_and_run_block_scalars_do_not_create_uses_keys(
    tmp_path: Path,
) -> None:
    write_workflow(
        tmp_path,
        "scripts.yml",
        "jobs:\n"
        "  job:\n"
        "    steps:\n"
        "      # uses: actions/checkout@v4\n"
        "      - run: |\n"
        "          echo \"uses: actions/checkout@v4\"\n"
        "      - run: >-\n"
        "          printf '%s\\n' 'uses: docker://alpine:latest'\n"
        "      - uses: ./.github/actions/local # local action\n",
    )

    payload = success_payload(invoke(tmp_path))

    assert payload["external_reference_count"] == 0


@pytest.mark.parametrize(
    ("indicator", "content_indent"),
    [
        ("|", 10),
        ("|2", 10),
        ("|4", 12),
        (">2-", 10),
        (">4-", 12),
    ],
    ids=["implicit", "literal_2", "literal_4", "folded_2", "folded_4"],
)
def test_block_scalar_does_not_hide_sibling_uses_key(
    tmp_path: Path,
    indicator: str,
    content_indent: int,
) -> None:
    content = (
        "jobs:\n"
        "  job:\n"
        "    steps:\n"
        f"      - name: {indicator}\n"
        f"{' ' * content_indent}Mutable action\n"
        "        uses: actions/checkout@v4\n"
    )
    write_workflow(tmp_path, "block-sibling.yml", content)

    code, stdout, stderr = invoke(tmp_path)

    assert code != 0
    assert stdout == b""
    assert b"lowercase 40-character commit SHA" in stderr


def test_non_utf8_workflow_is_rejected(tmp_path: Path) -> None:
    write_workflow(tmp_path, "invalid.yml", b"name: invalid\n\xff\n")

    code, stdout, stderr = invoke(tmp_path)

    assert code != 0
    assert stdout == b""
    assert stderr == (
        b"check_github_action_pins: error: workflow is not valid UTF-8: "
        b".github/workflows/invalid.yml\n"
    )


def test_utf8_bom_cannot_hide_first_line_uses_key(tmp_path: Path) -> None:
    write_workflow(
        tmp_path,
        "bom.yml",
        b"\xef\xbb\xbfuses: actions/checkout@v4\n",
    )

    code, stdout, stderr = invoke(tmp_path)

    assert code != 0
    assert stdout == b""
    assert stderr == (
        b"check_github_action_pins: error: workflow contains a UTF-8 BOM: "
        b".github/workflows/bom.yml\n"
    )


def test_first_failure_is_selected_in_sorted_path_order(tmp_path: Path) -> None:
    write_workflow(tmp_path, "z-invalid.yml", b"\xff")
    write_workflow(tmp_path, "a-invalid.yaml", b"\xff")

    first = invoke(tmp_path)
    second = invoke(tmp_path)

    assert first == second
    assert first == (
        1,
        b"",
        b"check_github_action_pins: error: workflow is not valid UTF-8: "
        b".github/workflows/a-invalid.yaml\n",
    )


def test_success_and_failure_outputs_are_byte_deterministic(
    tmp_path: Path,
) -> None:
    valid = tmp_path / "valid"
    invalid = tmp_path / "invalid"
    write_workflow(
        valid,
        "valid.yml",
        f"jobs:\n  job:\n    uses: owner/action@{FULL_SHA} # v1.2.3\n",
    )
    write_workflow(
        invalid,
        "invalid.yml",
        "jobs:\n  job:\n    uses: owner/action@main\n",
    )

    assert invoke(valid) == invoke(valid)
    first_failure = invoke(invalid)
    assert first_failure == invoke(invalid)
    assert first_failure[0] != 0
    assert first_failure[1] == b""


@pytest.mark.parametrize(
    "content",
    [
        f"jobs:\n  job:\n    *action_key: owner/action@{FULL_SHA}\n",
        "jobs:\n  job:\n    \"u\\u0073es\": actions/checkout@v4\n",
        "jobs:\n  job:\n    !!str uses: actions/checkout@v4\n",
        "jobs:\n  job:\n    ? >-\n      uses\n    : actions/checkout@v4\n",
        "jobs:\n  job: {? uses\n    : actions/checkout@v4}\n",
    ],
    ids=[
        "alias_key",
        "escaped_quoted_key",
        "tagged_key",
        "folded_explicit_key",
        "flow_explicit_key",
    ],
)
def test_noncanonical_mapping_key_is_rejected_fail_closed(
    tmp_path: Path,
    content: str,
) -> None:
    write_workflow(
        tmp_path,
        "alias.yml",
        content,
    )

    code, stdout, stderr = invoke(tmp_path)

    assert code != 0
    assert stdout == b""
    assert b"noncanonical YAML mapping-key syntax is not supported" in stderr


def test_real_repository_workflows_pass_cli_scan() -> None:
    process = subprocess.run(
        [sys.executable, "tools/check_github_action_pins.py"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=10,
    )

    assert process.returncode == 0
    assert process.stderr == b""
    payload = json.loads(process.stdout)
    assert payload["ok"] is True
    assert payload["workflow_count"] == 2
    assert payload["external_reference_count"] == 11
    assert payload["workflows"] == [
        ".github/workflows/ci.yml",
        ".github/workflows/heavy-search.yml",
    ]


def test_real_official_action_occurrences_use_one_sha_per_repository() -> None:
    payload = checker.scan_workflows(ROOT)
    observed: dict[str, set[str]] = {}
    counts: dict[str, int] = {}
    for record in payload["external_references"]:
        assert record["kind"] == "github"
        repository = record["repository"]
        observed.setdefault(repository, set()).add(record["commit"])
        counts[repository] = counts.get(repository, 0) + 1

    assert observed == {
        repository: {identity[0]}
        for repository, identity in EXPECTED_OFFICIAL_ACTIONS.items()
    }
    assert counts == {
        "actions/checkout": 4,
        "actions/setup-python": 4,
        "actions/upload-artifact": 3,
    }


def test_real_workflow_pin_comments_name_exact_verified_releases() -> None:
    payload = checker.scan_workflows(ROOT)
    line_pattern = re.compile(
        r"^\s*(?:-\s+)?uses:\s+(?P<reference>\S+)\s+"
        r"#\s+(?P<release>v[0-9]+\.[0-9]+\.[0-9]+)\s*$"
    )
    for record in payload["external_references"]:
        path = ROOT / record["workflow"]
        line = path.read_text(encoding="utf-8").splitlines()[
            record["line"] - 1
        ]
        match = line_pattern.fullmatch(line)
        assert match is not None
        expected_sha, expected_release = EXPECTED_OFFICIAL_ACTIONS[
            record["repository"]
        ]
        assert match.group("reference") == (
            f"{record['repository']}@{expected_sha}"
        )
        assert match.group("release") == expected_release


def test_fast_ci_runs_repository_local_pin_validator_once() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert workflow.count("- name: Check immutable GitHub Action pins") == 1
    assert workflow.count("run: python tools/check_github_action_pins.py") == 1
    assert workflow.index("Check out full review history") < workflow.index(
        "Check immutable GitHub Action pins"
    )
    assert workflow.index("Set up Python") < workflow.index(
        "Check immutable GitHub Action pins"
    )
    assert "continue-on-error" not in workflow
