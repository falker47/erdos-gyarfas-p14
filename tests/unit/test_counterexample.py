from __future__ import annotations

from pathlib import Path

import pytest

from egverify import load_graph, validate_counterexample


FIXTURES = Path(__file__).parents[1] / "fixtures"


def report(fixture: str, target: str):
    graph = load_graph(FIXTURES / fixture)
    return validate_counterexample(graph, target)  # type: ignore[arg-type]


def test_empty_graph_is_not_a_counterexample() -> None:
    result = report("empty.json", "p14")

    assert not result.accepted
    assert result.checks["minimum_degree_at_least_3"] == {
        "observed": 0,
        "passed": False,
    }
    assert result.checks["p14_free"]["passed"]
    assert result.checks["no_power_of_two_cycle"]["passed"]


def test_p14_report_exposes_induced_path_witness() -> None:
    result = report("path-p14.json", "p14")

    assert not result.accepted
    assert not result.checks["p14_free"]["passed"]
    assert result.checks["p14_free"]["witness_induced_p14"] == list(range(14))


def test_p14_report_exposes_forbidden_cycle_witness() -> None:
    result = report("complete-k4.json", "p14")

    assert not result.accepted
    assert result.checks["minimum_degree_at_least_3"]["passed"]
    assert result.checks["p14_free"]["passed"]
    assert not result.checks["no_power_of_two_cycle"]["passed"]
    assert result.checks["no_power_of_two_cycle"]["witness"]["length"] == 4


def test_p13_c4c8_report_checks_path_and_both_cycle_lengths() -> None:
    path_result = report("path-p13.json", "p13-c4c8")
    c4_result = report("complete-k4.json", "p13-c4c8")
    c8_result = report("c8.json", "p13-c4c8")

    assert not path_result.checks["p13_free"]["passed"]
    assert not c4_result.checks["no_c4"]["passed"]
    assert c4_result.checks["no_c8"]["passed"]
    assert c8_result.checks["no_c4"]["passed"]
    assert not c8_result.checks["no_c8"]["passed"]
    assert not path_result.accepted
    assert not c4_result.accepted
    assert not c8_result.accepted


def test_unknown_target_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported target"):
        report("empty.json", "not-a-target")
