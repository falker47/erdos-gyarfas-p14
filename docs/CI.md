# Continuous integration

## Fast workflow

`.github/workflows/ci.yml` runs for pushes, pull requests, and manual dispatch.
It is intentionally bounded:

- Python 3.11 and 3.12 run the verifier unit and differential suite;
- GCC and Clang configure and build the C++17 wrapper on Ubuntu;
- integration tests build the original Makefile in a temporary copy and run
  only tiny upstream parameters under explicit timeouts;
- each compiler job makes one ephemeral `k=3` engineering measurement to test
  the benchmark runner and result schema; the value is not committed or used
  as mathematical evidence;
- every JSON Schema is checked against Draft 2020-12;
- deterministic graph serialization is covered by the Python tests;
- the per-file upstream inventory is checked before and after tests;
- `git diff --check` and a clean post-test working tree detect accidental
  source modifications.

CI does not run `k=13`, `k=14`, the P13 C4/C8 search, a retained or substantive
performance benchmark, or a certifying search. Passing CI establishes
engineering confidence and bounded test agreement, not a theorem.

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
