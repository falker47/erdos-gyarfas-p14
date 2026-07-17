#!/usr/bin/env python3
"""Check project JSON Schemas and optionally validate one JSON instance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from jsonschema.validators import validator_for

from _common import REPOSITORY_ROOT


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def schema_path(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        direct = REPOSITORY_ROOT / candidate
        named = REPOSITORY_ROOT / "schemas" / value
        suffixed = REPOSITORY_ROOT / "schemas" / f"{value}.schema.json"
        candidate = next((path for path in (direct, named, suffixed) if path.is_file()), direct)
    return candidate


def check_schema(path: Path) -> type:
    schema = load_json(path)
    validator = validator_for(schema)
    validator.check_schema(schema)
    return validator


def validate_instance(schema_file: Path, instance_file: Path) -> None:
    schema = load_json(schema_file)
    validator_type = validator_for(schema)
    validator_type.check_schema(schema)
    validator_type(schema, format_checker=FormatChecker()).validate(load_json(instance_file))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema",
        help="schema filename, path, or basename (required with --instance)",
    )
    parser.add_argument("--instance", type=Path, help="JSON instance to validate")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if bool(args.schema) != bool(args.instance):
        raise SystemExit("--schema and --instance must be provided together")

    schema_files = sorted((REPOSITORY_ROOT / "schemas").glob("*.schema.json"))
    if not schema_files:
        raise SystemExit("no schemas/*.schema.json files found")

    try:
        for path in schema_files:
            check_schema(path)
        instance_result: dict[str, str] | None = None
        if args.instance is not None:
            selected_schema = schema_path(args.schema)
            instance_path = args.instance
            if not instance_path.is_absolute():
                instance_path = REPOSITORY_ROOT / instance_path
            validate_instance(selected_schema, instance_path)
            instance_result = {
                "instance": instance_path.relative_to(REPOSITORY_ROOT).as_posix(),
                "schema": selected_schema.relative_to(REPOSITORY_ROOT).as_posix(),
            }
    except (OSError, ValueError, json.JSONDecodeError, SchemaError, ValidationError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1

    result: dict[str, Any] = {
        "ok": True,
        "schemas_checked": [path.relative_to(REPOSITORY_ROOT).as_posix() for path in schema_files],
    }
    if instance_result is not None:
        result["instance_checked"] = instance_result
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
