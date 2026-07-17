"""Single-candidate checks for the two project targets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .graph import Graph
from .predicates import (
    find_exact_cycle,
    find_induced_path,
    find_power_of_two_cycle,
    minimum_degree,
)

Target = Literal["p14", "p13-c4c8"]


@dataclass(frozen=True, slots=True)
class CounterexampleReport:
    target: Target
    accepted: bool
    checks: dict[str, dict[str, Any]]

    def to_data(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "checks": self.checks,
            "target": self.target,
        }


def _json_witness(witness: tuple[object, ...] | None) -> list[object] | None:
    return list(witness) if witness is not None else None


def validate_counterexample(graph: Graph, target: Target) -> CounterexampleReport:
    """Evaluate one graph against a target counterexample predicate.

    Acceptance here is property-level evidence for one input only. It says
    nothing about search generation, completeness, or project acceptance.
    """

    observed_minimum_degree = minimum_degree(graph)
    checks: dict[str, dict[str, Any]] = {
        "minimum_degree_at_least_3": {
            "observed": observed_minimum_degree,
            "passed": observed_minimum_degree >= 3,
        }
    }

    if target == "p14":
        path = find_induced_path(graph, 14)
        power_cycle = find_power_of_two_cycle(graph)
        checks["p14_free"] = {
            "passed": path is None,
            "witness_induced_p14": _json_witness(path),
        }
        checks["no_power_of_two_cycle"] = {
            "passed": power_cycle is None,
            "witness": (
                None
                if power_cycle is None
                else {
                    "length": power_cycle[0],
                    "vertices": list(power_cycle[1]),
                }
            ),
        }
    elif target == "p13-c4c8":
        path = find_induced_path(graph, 13)
        c4 = find_exact_cycle(graph, 4)
        c8 = find_exact_cycle(graph, 8)
        checks["p13_free"] = {
            "passed": path is None,
            "witness_induced_p13": _json_witness(path),
        }
        checks["no_c4"] = {
            "passed": c4 is None,
            "witness_c4": _json_witness(c4),
        }
        checks["no_c8"] = {
            "passed": c8 is None,
            "witness_c8": _json_witness(c8),
        }
    else:
        raise ValueError(f"unsupported target: {target!r}")

    return CounterexampleReport(
        target=target,
        accepted=all(check["passed"] for check in checks.values()),
        checks=checks,
    )
