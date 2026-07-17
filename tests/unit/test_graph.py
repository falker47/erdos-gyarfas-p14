from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from egverify.graph import Graph, GraphFormatError, load_graph


FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_empty_graph_is_valid_and_canonical() -> None:
    graph = load_graph(FIXTURES / "empty.json")

    assert graph.vertices == ()
    assert graph.edges == ()
    assert graph.canonical_bytes() == (
        b'{"edges":[],"schema_version":"1.0","vertices":[]}\n'
    )


def test_mixed_vertex_types_and_edges_are_sorted_deterministically() -> None:
    graph = Graph(["b", 2, "a", -1], [["b", 2], ["a", -1]])

    assert graph.vertices == (-1, 2, "a", "b")
    assert graph.edges == ((-1, "a"), (2, "b"))
    expected = (
        b'{"edges":[[-1,"a"],[2,"b"]],"schema_version":"1.0",'
        b'"vertices":[-1,2,"a","b"]}\n'
    )
    assert graph.canonical_bytes() == expected
    assert graph.canonical_sha256() == hashlib.sha256(expected).hexdigest()


def test_input_order_and_whitespace_do_not_change_canonical_serialization(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(
        '{ "vertices": [2, 0, 1], "schema_version": "1.0", '
        '"edges": [[2, 1], [1, 0]] }',
        encoding="utf-8",
    )
    second.write_text(
        '{"edges":[[0,1],[1,2]],"schema_version":"1.0",'
        '"vertices":[0,1,2]}\n',
        encoding="utf-8",
    )

    left = load_graph(first)
    right = load_graph(second)
    assert left == right
    assert left.canonical_bytes() == right.canonical_bytes()
    assert left.canonical_sha256() == right.canonical_sha256()


@pytest.mark.parametrize(
    ("fixture", "code"),
    [
        ("malformed-loop.json", "loop"),
        ("malformed-duplicate-edge.json", "duplicate_edge"),
        ("malformed-duplicate-key.json", "duplicate_json_key"),
        ("malformed-endpoint.json", "undeclared_endpoint"),
        ("malformed-nonfinite.json", "nonfinite_json_number"),
    ],
)
def test_malformed_graphs_are_rejected_with_stable_codes(
    fixture: str, code: str
) -> None:
    with pytest.raises(GraphFormatError) as caught:
        load_graph(FIXTURES / fixture)
    assert caught.value.code == code
    assert caught.value.location.startswith("$")


@pytest.mark.parametrize(
    ("data", "code"),
    [
        ({"schema_version": "1.0", "vertices": [True], "edges": []}, "invalid_vertex_id"),
        ({"schema_version": "1.0", "vertices": ["has space"], "edges": []}, "invalid_vertex_id"),
        ({"schema_version": "1.0", "vertices": ["v" * 201], "edges": []}, "invalid_vertex_id"),
        ({"schema_version": "1.0", "vertices": [1, 1], "edges": []}, "duplicate_vertex"),
        ({"schema_version": "2.0", "vertices": [], "edges": []}, "unsupported_schema_version"),
        ({"schema_version": "1.0", "vertices": [], "edges": [], "typo": 1}, "unknown_field"),
        ({"schema_version": "1.0", "vertices": "bad", "edges": []}, "invalid_vertices"),
        ({"schema_version": "1.0", "vertices": [], "edges": {}}, "invalid_edges"),
        ({"schema_version": "1.0", "vertices": []}, "missing_field"),
    ],
)
def test_invalid_documents_are_rejected(data: object, code: str) -> None:
    with pytest.raises(GraphFormatError) as caught:
        Graph.from_data(data)
    assert caught.value.code == code


def test_metadata_is_accepted_only_when_explicitly_enabled() -> None:
    data = {
        "schema_version": "1.0",
        "vertices": [0],
        "edges": [],
        "graph_id": "candidate-1",
    }
    with pytest.raises(GraphFormatError, match="unknown field"):
        Graph.from_data(data)
    assert Graph.from_data(data, allow_metadata=True).vertices == (0,)


def test_neighbor_order_and_degree_are_deterministic() -> None:
    graph = load_graph(FIXTURES / "complete-k4.json")

    assert graph.neighbors(0) == (1, 2, 3)
    assert graph.degree(0) == 3
    assert graph.adjacent(0, 3)
    with pytest.raises(KeyError):
        graph.neighbors(99)


def test_canonical_serialization_round_trips() -> None:
    original = load_graph(FIXTURES / "disconnected.json")
    decoded = json.loads(original.canonical_bytes())

    assert Graph.from_data(decoded) == original
