"""Canonical graph parsing and serialization.

This module intentionally has no dependency on the upstream generator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, TypeAlias

VertexId: TypeAlias = int | str

_STRING_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]*\Z")
_CORE_FIELDS = frozenset({"schema_version", "vertices", "edges"})


class GraphFormatError(ValueError):
    """A deterministic validation error for a graph document."""

    def __init__(self, code: str, location: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.location = location
        self.message = message

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "location": self.location,
            "message": self.message,
        }


def vertex_sort_key(vertex: VertexId) -> tuple[int, int | str]:
    """Return the documented total-order key for a vertex identifier."""

    if isinstance(vertex, bool) or not isinstance(vertex, (int, str)):
        raise TypeError("vertex identifier must be an integer or string")
    if isinstance(vertex, int):
        return (0, vertex)
    return (1, vertex)


def _validate_vertex(vertex: Any, location: str) -> VertexId:
    if isinstance(vertex, bool) or not isinstance(vertex, (int, str)):
        raise GraphFormatError(
            "invalid_vertex_id",
            location,
            "vertex identifiers must be JSON integers or canonical strings",
        )
    if isinstance(vertex, str) and _STRING_ID.fullmatch(vertex) is None:
        raise GraphFormatError(
            "invalid_vertex_id",
            location,
            "string vertex identifiers must match [A-Za-z0-9][A-Za-z0-9_.:-]*",
        )
    if isinstance(vertex, str) and len(vertex) > 200:
        raise GraphFormatError(
            "invalid_vertex_id",
            location,
            "string vertex identifiers must contain at most 200 characters",
        )
    return vertex


@dataclass(frozen=True, slots=True, init=False)
class Graph:
    """An immutable finite simple undirected graph in canonical order."""

    vertices: tuple[VertexId, ...]
    edges: tuple[tuple[VertexId, VertexId], ...]
    _adjacency: Mapping[VertexId, frozenset[VertexId]] = field(
        repr=False, compare=False
    )

    def __init__(
        self,
        vertices: Iterable[VertexId],
        edges: Iterable[tuple[VertexId, VertexId] | list[VertexId]],
    ) -> None:
        raw_vertices = list(vertices)
        seen_vertices: set[VertexId] = set()
        normalized_vertices: list[VertexId] = []
        for index, raw_vertex in enumerate(raw_vertices):
            vertex = _validate_vertex(raw_vertex, f"$.vertices[{index}]")
            if vertex in seen_vertices:
                raise GraphFormatError(
                    "duplicate_vertex",
                    f"$.vertices[{index}]",
                    f"duplicate vertex identifier {vertex!r}",
                )
            seen_vertices.add(vertex)
            normalized_vertices.append(vertex)
        normalized_vertices.sort(key=vertex_sort_key)

        seen_edges: set[tuple[VertexId, VertexId]] = set()
        normalized_edges: list[tuple[VertexId, VertexId]] = []
        for index, raw_edge in enumerate(edges):
            if not isinstance(raw_edge, (list, tuple)) or len(raw_edge) != 2:
                raise GraphFormatError(
                    "invalid_edge",
                    f"$.edges[{index}]",
                    "each edge must be a two-element JSON array",
                )
            left = _validate_vertex(raw_edge[0], f"$.edges[{index}][0]")
            right = _validate_vertex(raw_edge[1], f"$.edges[{index}][1]")
            if left not in seen_vertices:
                raise GraphFormatError(
                    "undeclared_endpoint",
                    f"$.edges[{index}][0]",
                    f"edge endpoint {left!r} is not declared in vertices",
                )
            if right not in seen_vertices:
                raise GraphFormatError(
                    "undeclared_endpoint",
                    f"$.edges[{index}][1]",
                    f"edge endpoint {right!r} is not declared in vertices",
                )
            if left == right:
                raise GraphFormatError(
                    "loop",
                    f"$.edges[{index}]",
                    f"loop at vertex {left!r} is not allowed",
                )
            edge = (
                (left, right)
                if vertex_sort_key(left) < vertex_sort_key(right)
                else (right, left)
            )
            if edge in seen_edges:
                raise GraphFormatError(
                    "duplicate_edge",
                    f"$.edges[{index}]",
                    f"duplicate undirected edge {edge!r}",
                )
            seen_edges.add(edge)
            normalized_edges.append(edge)

        normalized_edges.sort(
            key=lambda edge: (vertex_sort_key(edge[0]), vertex_sort_key(edge[1]))
        )
        adjacency: dict[VertexId, set[VertexId]] = {
            vertex: set() for vertex in normalized_vertices
        }
        for left, right in normalized_edges:
            adjacency[left].add(right)
            adjacency[right].add(left)

        object.__setattr__(self, "vertices", tuple(normalized_vertices))
        object.__setattr__(self, "edges", tuple(normalized_edges))
        object.__setattr__(
            self,
            "_adjacency",
            {vertex: frozenset(neighbors) for vertex, neighbors in adjacency.items()},
        )

    @classmethod
    def from_data(
        cls, data: Any, *, allow_metadata: bool = False
    ) -> "Graph":
        if not isinstance(data, dict):
            raise GraphFormatError(
                "invalid_document", "$", "graph document must be a JSON object"
            )
        missing = sorted(_CORE_FIELDS - data.keys())
        if missing:
            raise GraphFormatError(
                "missing_field",
                "$",
                "missing required field(s): " + ", ".join(missing),
            )
        extra = sorted(set(data) - _CORE_FIELDS)
        if extra and not allow_metadata:
            raise GraphFormatError(
                "unknown_field",
                "$",
                "unknown field(s) in canonical graph document: " + ", ".join(extra),
            )
        if data["schema_version"] != "1.0":
            raise GraphFormatError(
                "unsupported_schema_version",
                "$.schema_version",
                "supported graph schema_version is exactly '1.0'",
            )
        if not isinstance(data["vertices"], list):
            raise GraphFormatError(
                "invalid_vertices", "$.vertices", "vertices must be a JSON array"
            )
        if not isinstance(data["edges"], list):
            raise GraphFormatError(
                "invalid_edges", "$.edges", "edges must be a JSON array"
            )
        return cls(data["vertices"], data["edges"])

    def neighbors(self, vertex: VertexId) -> tuple[VertexId, ...]:
        if vertex not in self._adjacency:
            raise KeyError(vertex)
        return tuple(sorted(self._adjacency[vertex], key=vertex_sort_key))

    def adjacent(self, left: VertexId, right: VertexId) -> bool:
        return right in self._adjacency[left]

    def degree(self, vertex: VertexId) -> int:
        return len(self._adjacency[vertex])

    def to_data(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "vertices": list(self.vertices),
            "edges": [list(edge) for edge in self.edges],
        }

    def canonical_bytes(self) -> bytes:
        text = json.dumps(
            self.to_data(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return (text + "\n").encode("utf-8")

    def canonical_sha256(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def decode_graph_document(path: str | Path) -> dict[str, Any]:
    """Decode a graph JSON file without performing graph validation."""

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise GraphFormatError(
                    "duplicate_json_key",
                    "$",
                    f"duplicate JSON object key {key!r}",
                )
            result[key] = value
        return result

    def reject_nonfinite_number(token: str) -> None:
        raise GraphFormatError(
            "nonfinite_json_number",
            "$",
            f"non-finite JSON number {token!r} is not permitted",
        )

    source = Path(path)
    with source.open("r", encoding="utf-8", newline="") as handle:
        data = json.load(
            handle,
            object_pairs_hook=unique_object,
            parse_constant=reject_nonfinite_number,
        )
    if not isinstance(data, dict):
        raise GraphFormatError(
            "invalid_document", "$", "graph document must be a JSON object"
        )
    return data


def load_graph(path: str | Path, *, allow_metadata: bool = False) -> Graph:
    return Graph.from_data(
        decode_graph_document(path), allow_metadata=allow_metadata
    )
