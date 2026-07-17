"""Bounded differential checks against deliberately simple local oracles.

The exact exhaustive labelled domain is all simple graphs on vertex sets
``{0, ..., n-1}`` for ``0 <= n <= 5``. Counts by n are 1, 1, 2, 8, 64, and
1024, for exactly 1100 graphs. Agreement on this finite domain is classified as
VERIFIED_BOUNDED_COMPUTATION only; it is not a general proof and does not
establish search completeness.
"""

from __future__ import annotations

from itertools import combinations, permutations

from egverify import (
    Graph,
    has_c4_or_c8,
    has_exact_cycle,
    has_induced_path,
    has_power_of_two_cycle,
    minimum_degree,
)


MAX_VERTICES = 5
EXPECTED_COUNTS_BY_ORDER = (1, 1, 2, 8, 64, 1024)
EXPECTED_TOTAL = 1100


def all_labelled_graphs(max_vertices: int):
    for order in range(max_vertices + 1):
        vertices = tuple(range(order))
        possible_edges = tuple(combinations(vertices, 2))
        for edge_mask in range(1 << len(possible_edges)):
            edges = [
                edge
                for index, edge in enumerate(possible_edges)
                if edge_mask & (1 << index)
            ]
            yield Graph(vertices, edges)


def oracle_minimum_degree(graph: Graph) -> int:
    if not graph.vertices:
        return 0
    return min(
        sum(vertex in edge for edge in graph.edges) for vertex in graph.vertices
    )


def oracle_adjacent(graph: Graph, left: int, right: int) -> bool:
    """Scan the edge list directly instead of using production adjacency."""

    return any(
        (edge_left == left and edge_right == right)
        or (edge_left == right and edge_right == left)
        for edge_left, edge_right in graph.edges
    )


def oracle_has_induced_path(graph: Graph, k: int) -> bool:
    if k < 1 or k > len(graph.vertices):
        return False
    for ordered_vertices in permutations(graph.vertices, k):
        correct_adjacencies = True
        for left_index in range(k):
            for right_index in range(left_index + 1, k):
                should_be_edge = right_index == left_index + 1
                if oracle_adjacent(
                    graph,
                    ordered_vertices[left_index], ordered_vertices[right_index]
                ) != should_be_edge:
                    correct_adjacencies = False
                    break
            if not correct_adjacencies:
                break
        if correct_adjacencies:
            return True
    return False


def oracle_has_cycle(graph: Graph, length: int) -> bool:
    if length < 3 or length > len(graph.vertices):
        return False
    for ordered_vertices in permutations(graph.vertices, length):
        if all(
            oracle_adjacent(
                graph,
                ordered_vertices[index], ordered_vertices[(index + 1) % length]
            )
            for index in range(length)
        ):
            return True
    return False


def test_exhaustive_labelled_graph_domain_matches_independent_oracles() -> None:
    counts = [0] * (MAX_VERTICES + 1)
    for graph in all_labelled_graphs(MAX_VERTICES):
        order = len(graph.vertices)
        counts[order] += 1

        assert minimum_degree(graph) == oracle_minimum_degree(graph)
        for k in range(1, order + 2):
            assert has_induced_path(graph, k) == oracle_has_induced_path(graph, k)
        for length in range(3, order + 2):
            assert has_exact_cycle(graph, length) == oracle_has_cycle(graph, length)

        oracle_power2 = any(
            oracle_has_cycle(graph, length)
            for length in (4, 8, 16)
            if length <= order
        )
        assert has_power_of_two_cycle(graph) == oracle_power2
        assert has_c4_or_c8(graph) == (
            oracle_has_cycle(graph, 4) or oracle_has_cycle(graph, 8)
        )

    assert tuple(counts) == EXPECTED_COUNTS_BY_ORDER
    assert sum(counts) == EXPECTED_TOTAL
