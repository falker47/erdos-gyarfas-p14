"""Independent, auditable predicates for small finite simple graphs."""

from .counterexample import CounterexampleReport, validate_counterexample
from .graph import Graph, GraphFormatError, load_graph
from .predicates import (
    find_exact_cycle,
    find_induced_path,
    find_power_of_two_cycle,
    has_c4_or_c8,
    has_exact_cycle,
    has_induced_path,
    has_power_of_two_cycle,
    minimum_degree,
)

__all__ = [
    "CounterexampleReport",
    "Graph",
    "GraphFormatError",
    "find_exact_cycle",
    "find_induced_path",
    "find_power_of_two_cycle",
    "has_c4_or_c8",
    "has_exact_cycle",
    "has_induced_path",
    "has_power_of_two_cycle",
    "load_graph",
    "minimum_degree",
    "validate_counterexample",
]
