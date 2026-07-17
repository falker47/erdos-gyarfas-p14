"""JSON Schema and independent artifact-integrity checks for run manifests."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


@dataclass(frozen=True, slots=True)
class ManifestValidationReport:
    accepted: bool
    schema_valid: bool
    hashes_valid: bool
    errors: tuple[dict[str, str], ...]
    schema_path: str

    def to_data(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "errors": list(self.errors),
            "hashes_valid": self.hashes_valid,
            "schema_path": self.schema_path,
            "schema_valid": self.schema_valid,
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_path(parts: list[object]) -> str:
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += f".{part}"
    return result


def _find_repository_root(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "schemas" / "experiment-manifest.schema.json").is_file():
            return candidate
    return None


def resolve_manifest_schema(
    manifest_path: Path, schema_path: str | Path | None
) -> tuple[Path, Path]:
    if schema_path is not None:
        resolved_schema = Path(schema_path).resolve()
        repository_root = (
            resolved_schema.parent.parent
            if resolved_schema.parent.name == "schemas"
            else (_find_repository_root(resolved_schema) or Path.cwd().resolve())
        )
        return resolved_schema, repository_root
    repository_root = _find_repository_root(manifest_path)
    if repository_root is None:
        repository_root = _find_repository_root(Path.cwd())
    if repository_root is None:
        raise FileNotFoundError(
            "could not locate schemas/experiment-manifest.schema.json"
        )
    return (
        repository_root / "schemas" / "experiment-manifest.schema.json",
        repository_root,
    )


def _schema_errors(instance: Any, schema: Any) -> list[dict[str, str]]:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures = sorted(
        validator.iter_errors(instance),
        key=lambda error: (_json_path(list(error.absolute_path)), error.message),
    )
    return [
        {
            "code": "schema_validation",
            "location": _json_path(list(error.absolute_path)),
            "message": error.message,
        }
        for error in failures
    ]


def _artifact_hash_errors(
    manifest: Any, repository_root: Path
) -> list[dict[str, str]]:
    # Structural shape is the schema's responsibility. Bail out quietly when
    # those fields do not have the required types so errors do not cascade.
    if not isinstance(manifest, dict):
        return []
    artifacts = manifest.get("artifacts")
    declared_hashes = manifest.get("artifact_sha256")
    if not isinstance(artifacts, list) or not all(
        isinstance(item, str) for item in artifacts
    ):
        return []
    if not isinstance(declared_hashes, dict):
        return []

    errors: list[dict[str, str]] = []
    artifact_set = set(artifacts)
    hash_key_set = set(declared_hashes)
    for missing in sorted(artifact_set - hash_key_set):
        errors.append(
            {
                "code": "missing_artifact_hash",
                "location": "$.artifact_sha256",
                "message": f"no SHA-256 declared for artifact {missing!r}",
            }
        )
    for extra in sorted(hash_key_set - artifact_set):
        errors.append(
            {
                "code": "unlisted_artifact_hash",
                "location": f"$.artifact_sha256.{extra}",
                "message": f"hash key {extra!r} is not listed in artifacts",
            }
        )

    root = repository_root.resolve()
    for artifact in artifacts:
        expected = declared_hashes.get(artifact)
        if not isinstance(expected, str):
            continue
        pure_path = PurePosixPath(artifact)
        if pure_path.is_absolute() or ".." in pure_path.parts or "\\" in artifact:
            errors.append(
                {
                    "code": "unsafe_artifact_path",
                    "location": "$.artifacts",
                    "message": (
                        "artifact path is not a safe repository-relative "
                        f"POSIX path: {artifact!r}"
                    ),
                }
            )
            continue
        candidate = (root / Path(*pure_path.parts)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(
                {
                    "code": "unsafe_artifact_path",
                    "location": "$.artifacts",
                    "message": f"artifact resolves outside repository root: {artifact!r}",
                }
            )
            continue
        if not candidate.is_file():
            errors.append(
                {
                    "code": "missing_artifact",
                    "location": "$.artifacts",
                    "message": f"declared artifact does not exist as a file: {artifact!r}",
                }
            )
            continue
        actual = sha256_file(candidate)
        if actual != expected:
            errors.append(
                {
                    "code": "artifact_hash_mismatch",
                    "location": f"$.artifact_sha256.{artifact}",
                    "message": (
                        f"artifact {artifact!r} SHA-256 is {actual}, expected {expected}"
                    ),
                }
            )
    return errors


def validate_manifest(
    manifest_path: str | Path, schema_path: str | Path | None = None
) -> ManifestValidationReport:
    source = Path(manifest_path)
    resolved_schema, repository_root = resolve_manifest_schema(source, schema_path)
    with source.open("r", encoding="utf-8", newline="") as handle:
        manifest = json.load(handle)
    with resolved_schema.open("r", encoding="utf-8", newline="") as handle:
        schema = json.load(handle)

    schema_errors = _schema_errors(manifest, schema)
    hash_errors = _artifact_hash_errors(manifest, repository_root)
    errors = tuple(schema_errors + hash_errors)
    schema_valid = not schema_errors
    hashes_valid = not hash_errors
    try:
        displayed_schema = resolved_schema.relative_to(repository_root).as_posix()
    except ValueError:
        displayed_schema = str(resolved_schema)
    return ManifestValidationReport(
        accepted=schema_valid and hashes_valid,
        schema_valid=schema_valid,
        hashes_valid=hashes_valid,
        errors=errors,
        schema_path=displayed_schema,
    )


__all__ = [
    "ManifestValidationReport",
    "SchemaError",
    "resolve_manifest_schema",
    "sha256_file",
    "validate_manifest",
]
