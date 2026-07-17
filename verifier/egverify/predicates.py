"""Direct graph predicates intended for auditability on small graphs."""

from __future__ import annotations

from collections.abc import Sequence

from .graph import Graph, VertexId, vertex_sort_key


def minimum_degree(graph: Graph) -> int:
    """Return minimum degree, using the documented value 0 for no vertices."""

    return min((graph.degree(vertex) for vertex in graph.vertices), default=0)


def find_induced_path(graph: Graph, k: int) -> tuple[VertexId, ...] | None:
    """Return a deterministic witness for an induced path on ``k`` vertices."""

    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer number of vertices")
    if k > len(graph.vertices):
        return None
    if k == 1:
        return (graph.vertices[0],) if graph.vertices else None

    def extend(path: list[VertexId]) -> tuple[VertexId, ...] | None:
        if len(path) == k:
            return tuple(path)
        last = path[-1]
        for candidate in graph.neighbors(last):
            if candidate in path:
                continue
            # The edge to ``last`` is required. Edges to every earlier path
            # vertex would be a chord and destroy inducedness.
            if any(graph.adjacent(candidate, old) for old in path[:-1]):
                continue
            path.append(candidate)
            witness = extend(path)
            if witness is not None:
                return witness
            path.pop()
        return None

    for start in graph.vertices:
        witness = extend([start])
        if witness is not None:
            return witness
    return None


def has_induced_path(graph: Graph, k: int) -> bool:
    return find_induced_path(graph, k) is not None


def find_exact_cycle(graph: Graph, length: int) -> tuple[VertexId, ...] | None:
    """Return a simple cycle of exact ``length``; chords are permitted."""

    if isinstance(length, bool) or not isinstance(length, int) or length < 3:
        raise ValueError("cycle length must be an integer at least 3")
    if length > len(graph.vertices):
        return None

    def extend(
        start: VertexId, path: list[VertexId]
    ) -> tuple[VertexId, ...] | None:
        if len(path) == length:
            return tuple(path) if graph.adjacent(path[-1], start) else None
        for candidate in graph.neighbors(path[-1]):
            if candidate in path:
                continue
            # Every cycle has a unique least vertex. Starting there avoids
            # redundant starts without excluding any cycle.
            if vertex_sort_key(candidate) < vertex_sort_key(start):
                continue
            path.append(candidate)
            witness = extend(start, path)
            if witness is not None:
                return witness
            path.pop()
        return None

    for start in graph.vertices:
        witness = extend(start, [start])
        if witness is not None:
            return witness
    return None


def has_exact_cycle(graph: Graph, length: int) -> bool:
    return find_exact_cycle(graph, length) is not None


def relevant_power_of_two_lengths(vertex_count: int) -> tuple[int, ...]:
    if isinstance(vertex_count, bool) or not isinstance(vertex_count, int):
        raise ValueError("vertex_count must be a nonnegative integer")
    if vertex_count < 0:
        raise ValueError("vertex_count must be a nonnegative integer")
    lengths: list[int] = []
    length = 4
    while length <= vertex_count:
        lengths.append(length)
        length *= 2
    return tuple(lengths)


def find_power_of_two_cycle(
    graph: Graph,
) -> tuple[int, tuple[VertexId, ...]] | None:
    for length in relevant_power_of_two_lengths(len(graph.vertices)):
        witness = find_exact_cycle(graph, length)
        if witness is not None:
            return (length, witness)
    return None


def has_power_of_two_cycle(graph: Graph) -> bool:
    return find_power_of_two_cycle(graph) is not None


def has_c4_or_c8(graph: Graph) -> bool:
    return has_exact_cycle(graph, 4) or has_exact_cycle(graph, 8)


def is_path_witness(graph: Graph, path: Sequence[VertexId]) -> bool:
    """Check an ordered induced-path witness; useful for report consumers."""

    if len(path) < 1 or len(set(path)) != len(path):
        return False
    if any(vertex not in graph.vertices for vertex in path):
        return False
    for left_index, left in enumerate(path):
        for right_index in range(left_index + 1, len(path)):
            adjacent = graph.adjacent(left, path[right_index])
            if adjacent != (right_index == left_index + 1):
                return False
    return True
