from __future__ import annotations

import json
from pathlib import Path

from egverify.manifest import sha256_file, validate_manifest


ROOT = Path(__file__).parents[2]
FIXTURES = ROOT / "tests" / "fixtures"


def test_known_fixture_digest_is_stable() -> None:
    assert sha256_file(FIXTURES / "manifest-hash-target.txt") == (
        "fe444d0d8bbde9d2b3b7828bf7ec74aaafd9039a991ff3055d743a26f8e9800b"
    )


def test_manifest_schema_and_artifact_hash_pass() -> None:
    report = validate_manifest(FIXTURES / "manifest-valid-hash.json")

    assert report.accepted
    assert report.schema_valid
    assert report.hashes_valid
    assert report.errors == ()
    assert report.schema_path == "schemas/experiment-manifest.schema.json"


def test_valid_schema_with_wrong_artifact_hash_is_rejected() -> None:
    report = validate_manifest(FIXTURES / "manifest-invalid-hash.json")

    assert not report.accepted
    assert report.schema_valid
    assert not report.hashes_valid
    assert [error["code"] for error in report.errors] == [
        "artifact_hash_mismatch"
    ]


def test_schema_failure_is_distinct_from_hash_failure(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "artifacts": [],
                "artifact_sha256": {},
            }
        ),
        encoding="utf-8",
    )

    report = validate_manifest(invalid)

    assert not report.accepted
    assert not report.schema_valid
    assert report.hashes_valid
    assert all(error["code"] == "schema_validation" for error in report.errors)


def test_artifact_list_and_hash_keys_must_match_semantically(tmp_path: Path) -> None:
    data = json.loads((FIXTURES / "manifest-valid-hash.json").read_text("utf-8"))
    data["artifact_sha256"] = {}
    manifest = tmp_path / "missing-hash.json"
    manifest.write_text(json.dumps(data), encoding="utf-8")

    report = validate_manifest(manifest)

    assert report.schema_valid
    assert not report.hashes_valid
    assert any(error["code"] == "missing_artifact_hash" for error in report.errors)


def test_unsafe_or_missing_artifact_path_is_rejected(tmp_path: Path) -> None:
    data = json.loads((FIXTURES / "manifest-valid-hash.json").read_text("utf-8"))
    data["artifacts"] = ["../outside.txt"]
    data["artifact_sha256"] = {"../outside.txt": "0" * 64}
    manifest = tmp_path / "unsafe.json"
    manifest.write_text(json.dumps(data), encoding="utf-8")

    report = validate_manifest(manifest)

    assert not report.accepted
    assert not report.schema_valid
    assert not report.hashes_valid
    assert any(error["code"] == "unsafe_artifact_path" for error in report.errors)
