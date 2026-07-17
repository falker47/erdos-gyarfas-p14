# Reproducibility Contract

## Bootstrap status

The bootstrap establishes reproducible engineering interfaces and bounded
checks. It does not reproduce a published P13/P12 result and does not certify
the upstream algorithm. Exact run details and failures are in
`ops/TASK-20260715__bootstrap_reproducible_baseline/`.

## Preserved upstream

The immutable snapshot is identified by:

- repository/ref/commit and Git tree SHA;
- sorted path-plus-raw-file-SHA inventory digest;
- raw SHA-256 for every file and the upstream MIT license;
- acquisition timestamp and commands;
- all requested branch ref outcomes.

Canonical values are machine-readable in
`upstream/UPSTREAM_PROVENANCE.json` and `upstream/UPSTREAM_REFS.json`. Run:

```text
python tools/verify_upstream_snapshot.py
```

before and after builds or tests. The original Makefile is never built in
place: it writes `out/`, so integration tests copy the exact snapshot to a
temporary directory.

## Build layers

### Original Make interface

The byte-preserved Makefile uses `g++`, C++17, `-Wall -Wextra -O3`, Unix
`mkdir`/`rm`, and emits `out/a.out` inside its working copy. The exercised
project command is:

```text
python -m pytest -q tests/integration/test_upstream_build.py
```

That test performs a clean original Make build in a temporary copy, performs a
separate out-of-source CMake build, and runs only `k=3` and `k=4` under a
ten-second subprocess timeout. Exit `0` is the only ordinary successful
outcome for both known tiny cases. Timeout, spawn failure, signal, exit `100`,
or any other exit code fails with captured diagnostics.

Exit `100` means that the upstream source printed a candidate, so the test
takes a surprising diagnostic path rather than accepting smoke completion. A
project-authored interface adapter parses the complete adjacency-list output
and rejects malformed syntax, duplicate declarations or neighbors, loops,
asymmetry, undeclared endpoints, and noncanonical labels. It constructs the
project-authored `egverify.graph.Graph` and uses independent verifier
predicates—not upstream parsing or predicate code—to check simplicity, minimum
degree at least 3, induced-`P_k` absence, and absence of every relevant
power-of-two cycle. Successful parsing reports canonical graph bytes and their
SHA-256 together with every predicate result. An invalid candidate is an
upstream correctness failure; a candidate passing all independent predicates
is a surprising mathematical result requiring a separate freeze-and-verify
task. Both dispositions fail, and neither is acceptance or certification.

### Project CMake interface

The wrapper names the same three upstream translation units explicitly,
requires C++17, and keeps all generated files under `build/`:

```text
cmake --preset debug
cmake --build --preset debug
cmake --preset release
cmake --build --preset release
```

Both presets were configured and built during bootstrap. Release is the route
for engineering benchmarks; Debug is for diagnostics. CMake changes build
orchestration only and adds no algorithm patch.

### Container interface

`Dockerfile` pins the Ubuntu 24.04 multi-platform image index by digest,
installs build/Python tools, builds as an unprivileged user, and defaults to
the bounded test suite. `.dockerignore` excludes local state.

The image was not built locally because Docker is unavailable. Ubuntu archive
package versions are resolved at image-build time and must be captured from
the build log; the public archive does not preserve every superseded version.

## Python interface

Python 3.11 or newer is supported. Direct build/runtime/test dependencies are
exactly pinned in `pyproject.toml`. The bootstrap local suite used Python
3.14.3; CI is configured for Python 3.11 and 3.12. Transitive Python packages,
the interpreter distribution, and installer artifacts are not hash-locked in
this baseline, so package metadata alone is not a complete immutable
environment.

Install in an isolated environment:

```text
python -m venv .venv
python -m pip install -e ".[test]"
```

The dependency/metadata route was checked without modifying the environment:

```text
python -m pip install --dry-run --no-build-isolation -e ".[test]"
```

## Exercised fast verification

These repository-relative commands completed successfully during bootstrap:

```text
python -m pytest -q --basetemp build/pytest-root
python tools/validate_schemas.py
python tools/validate_schemas.py --schema experiment-manifest --instance _TEMPLATES/EXPERIMENT_MANIFEST_TEMPLATE.json
python tools/verify_upstream_snapshot.py
python tools/verify_manifest.py tests/fixtures/manifest-valid-hash.json
```

The complete local test suite passed 63 tests. The differential test enumerates
exactly 1,100 labelled simple graphs of orders 0 through 5. This is
`VERIFIED_BOUNDED_COMPUTATION`, not a proof outside that domain. The deliberately
invalid manifest-hash fixture is also required to fail verification.

With `verifier/` on `PYTHONPATH`, the exercised CLI forms are:

```text
python -m egverify graph tests/fixtures/disconnected.json
python -m egverify counterexample --target p14 tests/fixtures/complete-k4.json
python -m egverify counterexample --target p13-c4c8 tests/fixtures/c8.json
python -m egverify manifest tests/fixtures/manifest-valid-hash.json
```

Repeated graph CLI serialization was byte-identical. Both counterexample
fixtures were rejected as expected; no accepted counterexample fixture exists.

## Benchmark discipline

The tiny case definition can exercise the machine-readable runner after a
Release build:

```text
python tools/run_benchmark.py benchmarks/cases/upstream-small-k.json --output benchmarks/results/bootstrap-harness-check.json
python tools/validate_schemas.py --schema benchmark-result --instance benchmarks/results/bootstrap-harness-check.json
```

The bootstrap harness execution terminated with upstream exit `0` and its
result validated. Its generated JSON/stdout/stderr were then removed; no
benchmark measurement is committed. A benchmark remains performance/process
evidence only and never proves search correctness or completeness.

The case now declares one exact accepted process outcome:
`termination_reason: "exited"` paired with `exit_code: 0`. Every case requires
a nonempty array of exact pairs; accepted reasons and codes are not independent
lists and cannot admit Cartesian-product combinations. The runner normalizes
and records those pairs, the actual reason and code, and
`outcome_accepted`. It returns `0` only for an exact match, returns `3` for an
attempted child outcome that is not accepted, and returns `1` for
configuration, schema, or artifact failures.

After execution is attempted, an unaccepted exit, timeout, signal, or spawn
error still produces captured stdout/stderr and a schema-validated result JSON
before the runner returns `3`. Its machine-readable diagnostic includes the
case ID, accepted and actual pairs, paths, and SHA-256 hashes, with `ok: false`.
CI independently validates that result even after the runner step fails and
surfaces bounded stream diagnostics without masking the failure. These remain
`EMPIRICAL_OBSERVATION` engineering artifacts and do not establish search
coverage, reproduction, a certificate, or a mathematical result.

## Search-run discipline

A future material search must content-address its executable and inputs,
serialize configuration and pruning IDs, identify a deterministic partition,
record environment/resources/failures, hash every artifact, and undergo
independent certificate verification. The current search-partition and
certificate schemas are provisional and cannot support a certifying claim.

## Tested local toolchain and residual portability

The native Windows checks used GCC 13.1.0, CMake 3.26.4, Ninja 1.11.1, and GNU
Make 4.4.1 from MSYS2. The original Make route depends on Unix utilities.
MinGW-built executables require the matching runtime DLL directory on the
child process path; the benchmark runner records and supplies that directory
from CMake metadata on Windows.

An initial Windows Git archive inherited `core.autocrlf=true` and was rejected.
The accepted snapshot was reacquired with conversion disabled and checked
against all raw Git blobs. This failure and the rejected archive hash remain in
provenance so the correction is independently visible.
