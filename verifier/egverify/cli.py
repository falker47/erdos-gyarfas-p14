"""Machine-readable command-line interface."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, NoReturn, Sequence

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .counterexample import validate_counterexample
from .graph import Graph, GraphFormatError, decode_graph_document
from .manifest import validate_manifest
from .predicates import minimum_degree

EXIT_ACCEPTED = 0
EXIT_REJECTED = 1
EXIT_INPUT_ERROR = 2
EXIT_INTERNAL_ERROR = 3


def _emit(payload: dict[str, Any]) -> None:
    print(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        flush=True,
    )


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        _emit(
            {
                "command": "invocation",
                "error": {"code": "usage", "message": message},
                "ok": False,
                "status": "input_error",
            }
        )
        raise SystemExit(EXIT_INPUT_ERROR)


def _parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(prog="egverify", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    graph_parser = subparsers.add_parser(
        "graph", help="validate and canonically summarize a graph"
    )
    graph_parser.add_argument("file", type=Path)

    counterexample_parser = subparsers.add_parser(
        "counterexample", help="check one graph against a target predicate"
    )
    counterexample_parser.add_argument(
        "--target", choices=("p14", "p13-c4c8"), required=True
    )
    counterexample_parser.add_argument("file", type=Path)

    manifest_parser = subparsers.add_parser(
        "manifest", help="validate manifest structure and declared artifact hashes"
    )
    manifest_parser.add_argument("file", type=Path)
    manifest_parser.add_argument("--schema", type=Path)
    return parser


def _graph_summary(graph: Graph) -> dict[str, Any]:
    return {
        "canonical_graph": graph.to_data(),
        "canonical_sha256": graph.canonical_sha256(),
        "edge_count": len(graph.edges),
        "minimum_degree": minimum_degree(graph),
        "vertex_count": len(graph.vertices),
    }


def _json_path(parts: list[object]) -> str:
    result = "$"
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else f".{part}"
    return result


def _find_repository_schema(source: Path, filename: str) -> Path:
    starts = (source.resolve().parent, Path.cwd().resolve())
    visited: set[Path] = set()
    for start in starts:
        for candidate in (start, *start.parents):
            if candidate in visited:
                continue
            visited.add(candidate)
            schema = candidate / "schemas" / filename
            if schema.is_file():
                return schema
    raise FileNotFoundError(f"could not locate schemas/{filename}")


def _counterexample_schema_errors(
    document: dict[str, Any], source: Path
) -> list[dict[str, str]]:
    schema_path = _find_repository_schema(source, "counterexample.schema.json")
    with schema_path.open("r", encoding="utf-8", newline="") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    failures = sorted(
        validator.iter_errors(document),
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


def _counterexample_semantic_errors(
    document: dict[str, Any], graph: Graph, target: str
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    canonical = graph.to_data()
    if document["vertices"] != canonical["vertices"]:
        errors.append(
            {
                "code": "noncanonical_vertices",
                "location": "$.vertices",
                "message": "vertices are not in canonical order",
            }
        )
    if document["edges"] != canonical["edges"]:
        errors.append(
            {
                "code": "noncanonical_edges",
                "location": "$.edges",
                "message": "edges are not canonically oriented and sorted",
            }
        )
    if "vertex_count" in document and document["vertex_count"] != len(graph.vertices):
        errors.append(
            {
                "code": "vertex_count_mismatch",
                "location": "$.vertex_count",
                "message": "vertex_count does not match the vertices array",
            }
        )
    expected_claim = "EG-P14" if target == "p14" else "EG-P13-C4C8"
    if "target_claim" in document and document["target_claim"] != expected_claim:
        errors.append(
            {
                "code": "target_mismatch",
                "location": "$.target_claim",
                "message": f"artifact target_claim does not match CLI target {target!r}",
            }
        )
    declared_hash = document.get("graph_sha256")
    if declared_hash is not None and declared_hash != graph.canonical_sha256():
        errors.append(
            {
                "code": "graph_hash_mismatch",
                "location": "$.graph_sha256",
                "message": "graph_sha256 does not match the canonical graph payload",
            }
        )
    return errors


def _run_graph(path: Path) -> int:
    document = decode_graph_document(path)
    graph = Graph.from_data(document)
    _emit(
        {
            "command": "graph",
            "graph": _graph_summary(graph),
            "ok": True,
            "status": "valid",
        }
    )
    return EXIT_ACCEPTED


def _run_counterexample(path: Path, target: str) -> int:
    document = decode_graph_document(path)
    graph = Graph.from_data(document, allow_metadata=True)
    metadata_fields = set(document) - {"schema_version", "vertices", "edges"}
    schema_errors = (
        _counterexample_schema_errors(document, path) if metadata_fields else []
    )
    semantic_errors = _counterexample_semantic_errors(document, graph, target)
    artifact_errors = schema_errors + semantic_errors
    if artifact_errors:
        _emit(
            {
                "command": "counterexample",
                "errors": artifact_errors,
                "graph": _graph_summary(graph),
                "ok": False,
                "status": "rejected",
                "target": target,
            }
        )
        return EXIT_REJECTED
    report = validate_counterexample(graph, target)  # type: ignore[arg-type]
    _emit(
        {
            "command": "counterexample",
            "graph": _graph_summary(graph),
            "ok": report.accepted,
            "report": report.to_data(),
            "status": "accepted" if report.accepted else "rejected",
            "target": target,
        }
    )
    return EXIT_ACCEPTED if report.accepted else EXIT_REJECTED


def _run_manifest(path: Path, schema: Path | None) -> int:
    report = validate_manifest(path, schema)
    _emit(
        {
            "command": "manifest",
            "ok": report.accepted,
            "report": report.to_data(),
            "status": "valid" if report.accepted else "rejected",
        }
    )
    return EXIT_ACCEPTED if report.accepted else EXIT_REJECTED


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "graph":
            return _run_graph(args.file)
        if args.command == "counterexample":
            return _run_counterexample(args.file, args.target)
        if args.command == "manifest":
            return _run_manifest(args.file, args.schema)
        raise AssertionError(f"unhandled command {args.command!r}")
    except GraphFormatError as error:
        _emit(
            {
                "command": args.command,
                "error": error.as_dict(),
                "ok": False,
                "status": "rejected",
            }
        )
        return EXIT_REJECTED
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        _emit(
            {
                "command": args.command,
                "error": {
                    "code": "input_error",
                    "message": str(error),
                    "type": type(error).__name__,
                },
                "ok": False,
                "status": "input_error",
            }
        )
        return EXIT_INPUT_ERROR
    except SchemaError as error:
        _emit(
            {
                "command": args.command,
                "error": {
                    "code": "invalid_schema",
                    "message": error.message,
                },
                "ok": False,
                "status": "input_error",
            }
        )
        return EXIT_INPUT_ERROR
    except Exception as error:  # defensive CLI boundary
        _emit(
            {
                "command": args.command,
                "error": {
                    "code": "internal_error",
                    "fingerprint": hashlib.sha256(
                        f"{type(error).__name__}:{error}".encode("utf-8")
                    ).hexdigest(),
                    "message": "unexpected verifier failure",
                    "type": type(error).__name__,
                },
                "ok": False,
                "status": "internal_error",
            }
        )
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
