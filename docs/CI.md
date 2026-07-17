# Continuous integration

## Fast workflow

`.github/workflows/ci.yml` runs for pushes, pull requests, and manual dispatch.
It is intentionally bounded:

- Python 3.11 and 3.12 run the verifier unit and differential suite;
- GCC and Clang configure and build the C++17 wrapper on Ubuntu;
- integration tests build the original Makefile in a temporary copy and run
  only tiny upstream parameters under explicit timeouts, requiring ordinary
  process completion with exit `0` for both `k=3` and `k=4`;
- each compiler job makes one ephemeral `k=3` engineering measurement to test
  the benchmark runner, exact accepted-outcome contract, and result schema; the
  value is not committed or used as mathematical evidence;
- every JSON Schema is checked against Draft 2020-12;
- deterministic graph serialization is covered by the Python tests;
- the per-file upstream inventory is checked before and after tests;
- `git diff --check` and a clean post-test working tree detect accidental
  source modifications.

CI does not run `k=13`, `k=14`, the P13 C4/C8 search, a retained or substantive
performance benchmark, or a certifying search. Passing CI establishes
engineering confidence and bounded test agreement, not a theorem.

## Tiny process-outcome contract

The known tiny cases have one ordinary successful outcome: child-process
`termination_reason: "exited"` paired with `exit_code: 0`. A timeout, spawn
failure, signal, or any other exit code fails and includes the captured streams
in deterministic diagnostics.

Upstream exit `100` is not an alternative smoke-test success. It means that the
upstream process printed a candidate graph and is treated as a surprising path:

- a project-authored interface adapter parses the complete upstream
  adjacency-list output without importing upstream parsing or predicates;
- the adapter rejects malformed syntax, duplicate declarations or neighbors,
  loops, asymmetric adjacency, undeclared endpoints, and noncanonical labels;
- the project-authored `egverify.graph.Graph` and independent verifier
  predicates check simple-graph construction, minimum degree at least 3,
  induced-`P_k` absence, and every relevant power-of-two cycle length;
- successful parsing reports the canonical graph serialization, its SHA-256,
  and every predicate result.

The test still fails in both possible dispositions. A failed predicate is an
upstream correctness failure. If every independent predicate passes, the output
is a surprising mathematical result that requires a separate freeze-and-verify
task. Neither branch is counterexample acceptance or certification.

Each benchmark case declares a required nonempty `accepted_outcomes` array of
exact `(termination_reason, exit_code)` objects. Reasons and codes are not
separate lists, so unintended Cartesian-product pairs cannot pass. The runner
returns `0` only for an exact declared pair. It returns `3` after an attempted
execution whose actual pair is unaccepted, but only after preserving and
schema-validating the result JSON and captured stdout/stderr. Configuration,
schema, or artifact failures return `1`.

CI lets a nonzero runner status fail its step directly. An `always()` step then
schema-validates the generated result, and a failure-only step prints bounded,
JSON-escaped result/stdout/stderr diagnostics with byte counts and SHA-256
hashes. These later steps do not mask the original runner failure. A valid or
invalid exit-100 candidate therefore leaves CI red even though its process
artifacts remain inspectable.

Official actions are major-version pinned (`actions/checkout@v4`,
`actions/setup-python@v5`, and `actions/upload-artifact@v4`). A future release
hardening task may pin immutable action commit SHAs.

## Manual heavy-search scaffold

`.github/workflows/heavy-search.yml` is manual-only. Its accepted mode is
`scaffold-only`; it does not invoke the upstream program or any search. Inputs
record a requested tiny `k`, partition label, time limit, and memory limit so
the interface can be reviewed before execution is enabled.

The workflow rejects P13/P14 and any non-scaffold request, emits a refused or
not-run experiment manifest, validates positive integer resource inputs while
preserving their original strings, and uploads the manifest and log even when
a guard rejects the request. It cannot emit
`COMPUTER_CERTIFIED_RESULT`.

Enabling real work later requires a separate reviewed task covering resource
enforcement, checkpointing, invariant and pruning status, partition coverage,
certificate replay, and failure preservation.
