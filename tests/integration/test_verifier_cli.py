from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from egverify import load_graph
from egverify import cli as cli_module


ROOT = Path(__file__).parents[2]
FIXTURES = ROOT / "tests" / "fixtures"


def run_cli(*arguments: object) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    source_path = str(ROOT / "verifier")
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        source_path
        if not existing_pythonpath
        else source_path + os.pathsep + existing_pythonpath
    )
    return subprocess.run(
        [sys.executable, "-m", "egverify", *(str(item) for item in arguments)],
        cwd=ROOT,
        env=environment,
        check=False,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=10,
    )


def output(process: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert process.stderr == ""
    assert process.stdout.count("\n") == 1
    return json.loads(process.stdout)


@pytest.mark.integration
def test_graph_command_emits_machine_readable_summary() -> None:
    process = run_cli("graph", FIXTURES / "complete-k4.json")

    assert process.returncode == 0
    payload = output(process)
    assert payload["ok"] is True
    assert payload["status"] == "valid"
    assert payload["graph"]["vertex_count"] == 4  # type: ignore[index]
    assert payload["graph"]["minimum_degree"] == 3  # type: ignore[index]


@pytest.mark.integration
def test_graph_output_is_byte_deterministic() -> None:
    first = run_cli("graph", FIXTURES / "disconnected.json")
    second = run_cli("graph", FIXTURES / "disconnected.json")

    assert first.returncode == second.returncode == 0
    assert first.stdout.encode("utf-8") == second.stdout.encode("utf-8")


@pytest.mark.integration
def test_structurally_invalid_graph_is_rejected() -> None:
    process = run_cli("graph", FIXTURES / "malformed-loop.json")

    assert process.returncode == 1
    payload = output(process)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "loop"  # type: ignore[index]


@pytest.mark.integration
def test_invalid_json_is_an_input_error() -> None:
    process = run_cli("graph", FIXTURES / "malformed-json.json")

    assert process.returncode == 2
    payload = output(process)
    assert payload["status"] == "input_error"
    assert payload["error"]["type"] == "JSONDecodeError"  # type: ignore[index]


@pytest.mark.integration
def test_counterexample_command_reports_property_failure() -> None:
    process = run_cli(
        "counterexample", "--target", "p14", FIXTURES / "complete-k4.json"
    )

    assert process.returncode == 1
    payload = output(process)
    assert payload["status"] == "rejected"
    report = payload["report"]  # type: ignore[assignment]
    assert report["checks"]["minimum_degree_at_least_3"]["passed"]  # type: ignore[index]
    assert not report["checks"]["no_power_of_two_cycle"]["passed"]  # type: ignore[index]


def counterexample_artifact(tmp_path: Path) -> Path:
    graph = load_graph(FIXTURES / "complete-k4.json")
    data = graph.to_data()
    data.update(
        {
            "graph_id": "cli-artifact-fixture",
            "vertex_count": 4,
            "graph_sha256": graph.canonical_sha256(),
            "source_task": "TASK-20260715__bootstrap_reproducible_baseline",
            "source_project_commit": None,
            "generator_command": ["fixture-only"],
            "generator_environment": {"purpose": "negative CLI test"},
            "target_claim": "EG-P14",
            "k": 14,
            "search_mode": "p14-power2",
            "verification_status": "unverified",
        }
    )
    artifact = tmp_path / "candidate.json"
    artifact.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
    return artifact


@pytest.mark.integration
def test_counterexample_artifact_schema_and_hash_are_checked(tmp_path: Path) -> None:
    artifact = counterexample_artifact(tmp_path)
    process = run_cli("counterexample", "--target", "p14", artifact)

    # Artifact integrity passes, then K4 is rejected by the target predicate.
    assert process.returncode == 1
    payload = output(process)
    assert "errors" not in payload
    assert payload["report"]["accepted"] is False  # type: ignore[index]


@pytest.mark.integration
def test_counterexample_artifact_hash_mismatch_is_rejected(tmp_path: Path) -> None:
    artifact = counterexample_artifact(tmp_path)
    data = json.loads(artifact.read_text("utf-8"))
    data["graph_sha256"] = "0" * 64
    artifact.write_text(json.dumps(data), encoding="utf-8")

    process = run_cli("counterexample", "--target", "p14", artifact)

    assert process.returncode == 1
    payload = output(process)
    assert any(
        error["code"] == "graph_hash_mismatch"  # type: ignore[index]
        for error in payload["errors"]  # type: ignore[union-attr]
    )


@pytest.mark.integration
def test_manifest_command_distinguishes_valid_and_invalid_hashes() -> None:
    valid = run_cli("manifest", FIXTURES / "manifest-valid-hash.json")
    invalid = run_cli("manifest", FIXTURES / "manifest-invalid-hash.json")

    assert valid.returncode == 0
    assert output(valid)["ok"] is True
    assert invalid.returncode == 1
    invalid_payload = output(invalid)
    assert invalid_payload["report"]["schema_valid"] is True  # type: ignore[index]
    assert invalid_payload["report"]["hashes_valid"] is False  # type: ignore[index]


@pytest.mark.integration
def test_usage_error_is_machine_readable() -> None:
    process = run_cli("counterexample", FIXTURES / "empty.json")

    assert process.returncode == 2
    payload = output(process)
    assert payload["command"] == "invocation"
    assert payload["error"]["code"] == "usage"  # type: ignore[index]


def test_unexpected_cli_failure_has_stable_exit_three_and_machine_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail(_path: Path) -> int:
        raise RuntimeError("deliberate test boundary failure")

    monkeypatch.setattr(cli_module, "_run_graph", fail)

    exit_code = cli_module.main(["graph", str(FIXTURES / "empty.json")])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 3
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert payload["status"] == "internal_error"
    assert payload["error"]["code"] == "internal_error"
    assert payload["error"]["type"] == "RuntimeError"
    assert len(payload["error"]["fingerprint"]) == 64
