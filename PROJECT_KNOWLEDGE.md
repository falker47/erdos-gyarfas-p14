# Project Knowledge

Last reviewed: 2026-07-17

This file holds stable reusable project facts. Definitions are canonical in
`research/PROBLEM_STATEMENT.md`; external results in
`research/KNOWN_RESULTS.md`; current state in `CURRENT_STATUS.md`; chronology
in `RESEARCH_LOG.md`; and run truth in machine-readable manifests.

## Identity and definitions

- `DEFINITION`: the repository name is `erdos-gyarfas-p14` and its primary
  target is claim `EG-P14`.
- `DEFINITION`: graphs are finite, simple, and undirected; `P_t` denotes a path
  on `t` vertices and `P_t`-free means no induced copy of that path.
- `DEFINITION`: a cycle is simple and need not be induced. Relevant
  power-of-two lengths are `2^j` for `j >= 2`, beginning 4, 8, 16, ….
- `DEFINITION`: `EG-P13-C4C8` is a distinct target asking only for C4 or C8.

The exact wording and counterexample predicates are in
`research/PROBLEM_STATEMENT.md` and are not duplicated here.

## External-result boundary

- `EXTERNAL_COMPUTATIONAL_RESULT`: Hegde, Sandeep, and Shashank report the
  P13-free power-of-two-cycle result and the P12-free C4/C8 result in
  arXiv:2410.22842v2.
- `EXTERNAL_THEOREM`: Hu and Shen report the P10-free C4/C8 theorem; Gao and
  Shan report the P8-free C4/C8 theorem.

These literature statements have not been independently reproduced or
certified by this project. Their canonical records and citations are in
`research/KNOWN_RESULTS.md` and `research/BIBLIOGRAPHY.md`.

## Upstream observations

- `EMPIRICAL_OBSERVATION`: the required read-only ref resolution on 2026-07-17
  resolved upstream `main` to
  `27d9cb22705905fac32314c5e95addf6e11ce283`, matching the design-time
  observation.
- `EMPIRICAL_OBSERVATION`: all five additional requested refs (`cilk`, `tests`,
  `logs`, `special-graphs`, and `4-8-cycles`) resolved; exact SHAs are canonical
  in `upstream/UPSTREAM_REFS.json`.
- `EMPIRICAL_OBSERVATION`: source inspection identifies a C++17 recursive
  labelled-graph implementation with independent recursive checks for simple
  forbidden cycles and induced paths.
- `EMPIRICAL_OBSERVATION`: upstream is distributed under the MIT License.
- `EMPIRICAL_OBSERVATION`: all ten preserved `main` files match their raw Git
  blobs at the recorded tree; the canonical inventory digest is maintained in
  `upstream/UPSTREAM_PROVENANCE.json`.
- `EMPIRICAL_OBSERVATION`: the preserved original Make route and the CMake
  Debug/Release wrapper built under the bootstrap MSYS2 toolchain, and tiny
  `k=3`/`k=4` processes terminated. This is not an upstream-result
  reproduction.

Exact snapshot identity, tree/file hashes, acquisition time, and license hash
belong only in `upstream/UPSTREAM_PROVENANCE.json`.

## Trust boundaries

- `ENGINEERING_ASSUMPTION`: upstream source is treated as untrusted until its
  invariant and implementation receive separate review.
- `DECISION`: compilation, unit tests, bounded agreement, and reproduced output
  cannot by themselves establish search completeness or a theorem.
- `DECISION`: generator and independent verifier do not share critical graph
  predicate implementations unless that dependency is explicitly admitted to
  the trust base.
- `DECISION`: a pruning rule is disabled for certifying use until its
  correctness proof is accepted and recorded under a stable ID.
- `DECISION`: schemas constrain data shape; semantic validation and mathematical
  proof remain separate obligations.

## Stable architecture

- `DECISION`: preserve one exact, unmodified upstream `main` snapshot under
  `third_party/erdos-gyarfas/`, with other branch identities recorded but not
  merged.
- `DECISION`: preserve the original GNU Make build and expose the same serial
  sources through an out-of-source CMake C++17 wrapper.
- `DECISION`: implement the bootstrap independent verifier in Python for small
  graphs and candidate validation, without using upstream predicate code.
- `DECISION`: use deterministic JSON, SHA-256, JSON Schema plus semantic checks,
  and machine-readable manifests.
- `DECISION`: keep fast bounded CI separate from manually dispatched heavy
  workflows.
- `DECISION`: one atomic task has one immutable dossier; the user performs all
  Git commits.

Rationale and decision history are canonical in `DECISION_LOG.md`.

## Current internal results

There is no project-internal mathematical result. There is no project theorem,
counterexample, computer-certified result,
accepted exhaustive-search result, certifying pruning rule, or accepted search
certificate. The independent verifier agreed with deliberately simple
test-local oracles on exactly 1,100 labelled graphs of orders 0 through 5;
this is `VERIFIED_BOUNDED_COMPUTATION` for that domain only. Bootstrap builds,
smoke executions, and ephemeral engineering benchmarks remain engineering
evidence and do not establish a theorem.
