from __future__ import annotations

from pathlib import Path

import pytest

from egverify import (
    find_exact_cycle,
    find_induced_path,
    find_power_of_two_cycle,
    has_c4_or_c8,
    has_exact_cycle,
    has_induced_path,
    has_power_of_two_cycle,
    load_graph,
    minimum_degree,
)
from egverify.predicates import is_path_witness, relevant_power_of_two_lengths


FIXTURES = Path(__file__).parents[1] / "fixtures"


def fixture(name: str):
    return load_graph(FIXTURES / name)


def test_minimum_degree_below_above_and_empty_convention() -> None:
    assert minimum_degree(fixture("empty.json")) == 0
    assert minimum_degree(fixture("path-p4.json")) == 1
    assert minimum_degree(fixture("complete-k4.json")) == 3
    assert minimum_degree(fixture("complete-k5.json")) == 4
    assert minimum_degree(fixture("disconnected.json")) == 0


def test_induced_path_uses_vertices_not_edge_length() -> None:
    graph = fixture("path-p4.json")

    witness = find_induced_path(graph, 4)
    assert witness == (0, 1, 2, 3)
    assert is_path_witness(graph, witness)
    assert has_induced_path(graph, 3)
    assert not has_induced_path(graph, 5)


def test_chord_destroys_induced_path() -> None:
    assert not has_induced_path(fixture("chorded-p4.json"), 4)
    assert not has_induced_path(fixture("complete-k4.json"), 4)


def test_induced_paths_in_large_and_disconnected_fixtures() -> None:
    assert has_induced_path(fixture("path-p13.json"), 13)
    assert has_induced_path(fixture("path-p14.json"), 14)
    assert has_induced_path(fixture("disconnected.json"), 2)
    assert not has_induced_path(fixture("empty.json"), 1)


@pytest.mark.parametrize("bad_k", [0, -1, True, 1.5])
def test_induced_path_rejects_invalid_k(bad_k: object) -> None:
    with pytest.raises(ValueError):
        has_induced_path(fixture("c3.json"), bad_k)  # type: ignore[arg-type]


def test_exact_cycle_length_and_chords() -> None:
    c5 = fixture("c5.json")
    k4 = fixture("complete-k4.json")

    assert find_exact_cycle(c5, 5) == (0, 1, 2, 3, 4)
    assert not has_exact_cycle(c5, 4)
    assert has_exact_cycle(k4, 3)
    assert has_exact_cycle(k4, 4), "a simple cycle may have graph chords"
    assert not has_exact_cycle(fixture("disconnected.json"), 4)


@pytest.mark.parametrize("bad_length", [0, 2, -4, True, 3.5])
def test_cycle_rejects_invalid_length(bad_length: object) -> None:
    with pytest.raises(ValueError):
        has_exact_cycle(fixture("c4.json"), bad_length)  # type: ignore[arg-type]


def test_relevant_power_of_two_cycle_lengths_start_at_four() -> None:
    assert relevant_power_of_two_lengths(3) == ()
    assert relevant_power_of_two_lengths(4) == (4,)
    assert relevant_power_of_two_lengths(31) == (4, 8, 16)
    assert relevant_power_of_two_lengths(32) == (4, 8, 16, 32)


def test_power_of_two_cycle_predicate() -> None:
    assert not has_power_of_two_cycle(fixture("c3.json"))
    assert find_power_of_two_cycle(fixture("c4.json")) == (4, (0, 1, 2, 3))
    assert find_power_of_two_cycle(fixture("c8.json")) == (
        8,
        (0, 1, 2, 3, 4, 5, 6, 7),
    )
    assert find_power_of_two_cycle(fixture("c16.json")) == (
        16,
        tuple(range(16)),
    )
    assert not has_power_of_two_cycle(fixture("c5.json"))


def test_c4_or_c8_predicate_is_distinct_from_general_power_target() -> None:
    assert has_c4_or_c8(fixture("c4.json"))
    assert has_c4_or_c8(fixture("c8.json"))
    assert not has_c4_or_c8(fixture("c16.json"))
    assert not has_c4_or_c8(fixture("c5.json"))
