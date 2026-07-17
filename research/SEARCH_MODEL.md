# Search Model

## Status and purpose

This is an initial engineering model of the upstream search. It is not an
accepted invariant proof, completeness proof, partition specification, or
certificate design. Every rule mentioned below remains non-certifying until
its proof obligation is closed under `research/VERIFICATION_PROTOCOL.md`.

## Mathematical modes

The repository keeps two modes distinct:

- `power_of_two`: forbid every simple cycle of length `2^j`, `j >= 2`, not
  exceeding the current graph order; the eventual primary parameter is
  induced `P14`;
- `c4_c8`: forbid simple cycles of length 4 or 8 only; the intermediate target
  uses induced `P13`.

A cycle is simple and need not be induced. By contrast, `P_k` always has
exactly `k` vertices and must occur as an induced subgraph.

## Observed upstream state

Source inspection suggests a state consists of a finite labelled graph, a
target integer `k`, and a construction order implicit in integer labels. The
main program begins with a path and repeatedly chooses a low-degree anchor,
adds a new labelled vertex adjacent to it, and enumerates allowed additional
neighbors of the new vertex.

This description is an `EMPIRICAL_OBSERVATION` about the preserved source. It
does not establish what every reachable state means relative to a hypothetical
minimal counterexample.

## Provisional transition description

For audit purposes only, a transition appears to:

1. identify the highest-labelled vertex of current degree below 3;
2. add one new highest-labelled vertex adjacent to that anchor;
3. classify potential edges from the new vertex as fixed, individually
   forbidden, or undecided;
4. enumerate subsets of undecided incident edges;
5. reject subsets that create a forbidden cycle;
6. recurse if the completed state remains `P_k`-free;
7. restore the prior graph.

The relevant observed rules have stable IDs `PR-UP-001` through `PR-UP-003` in
`research/PRUNING_REGISTRY.md`. They are disabled for certifying use.

## Required invariant proof

Before any exhaustive claim, a reviewed proof must define:

- the meaning of labels and which edges are permanently fixed;
- why the chosen roots cover the intended counterexample domain;
- why every compatible extension occurs in at least one branch;
- why subset enumeration omits no allowed neighbor set;
- why only one low-degree anchor is sufficient;
- why a detected induced path remains a valid terminal witness under the
  construction discipline;
- why forbidden-cycle pruning is monotone for the applicable transition;
- the recursion measure and terminal-state semantics;
- exact correspondence between source return paths and mathematical cases.

Bounded differential tests are evidence about implementations, not substitutes
for any item above.

## Roots and partitions

No certifying root set or partition frontier is accepted at bootstrap. The
schemas under `schemas/` are data-shape scaffolds only. A later atomic task
must define a total, deterministic partition mapping and prove both coverage
and disjointness before a search certificate can have mathematical force.

## Outputs

The unmodified upstream executable emits human-readable output and an elapsed
time. It does not emit a coverage certificate. Project wrappers may capture
bytes and metadata, but wrapping output cannot upgrade it to an exhaustive
result.

## Trust boundary

The generator, independent graph verifier, manifest/hash validation, partition
coverage checker, and certificate replay logic are separate obligations. The
bootstrap Python verifier addresses graph predicates and artifact validation
for small inputs; it does not replay or certify the upstream search tree.
