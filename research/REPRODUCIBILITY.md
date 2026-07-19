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
or any other exit code fails. Before each child starts, the integration path
collects the command, executable path/hash, project revision/commit, and
upstream commit. An ordinary exit `0` produces no surprising-outcome artifact.

For every nonordinary outcome, stdout and stderr are first written as complete
raw `.bin` files in a configured directory below
`artifacts/counterexamples/`. Their sizes and SHA-256 hashes are recomputed from
the closed files. Only then is a deterministic immutable outcome JSON written,
with classification `EMPIRICAL_OBSERVATION`, the upstream timeout, the original
outcome, artifact-relative stream paths, and initial inspection state. No graph
parsing or recursive predicate runs before these three files exist. Existing
evidence is not overwritten. `launcher_error` records a spawn failure
separately because no child stderr exists in that disposition.

Exit `100` means that the upstream source printed a candidate, so the test
takes a surprising diagnostic path rather than accepting smoke completion. A
separate Python inspector process reads the already-frozen raw files and
verifies their sizes and hashes before decoding. A project-authored interface
adapter rejects malformed syntax, duplicate declarations or neighbors, loops,
asymmetry, undeclared endpoints, and noncanonical labels. It constructs the
project-authored `egverify.graph.Graph` and uses independent verifier
predicates—not upstream parsing or predicate code—to check simplicity, minimum
degree at least 3, induced-`P_k` absence, and absence of every relevant
power-of-two cycle. Successful parsing reports canonical graph bytes and their
SHA-256 together with every predicate result.

The inspector has an autonomous default five-second timeout, distinct from the
upstream ten-second limit. The parent uses a direct binary-pipe subprocess and,
on Windows or POSIX timeout, kills, drains, and waits for that child. It owns a
separate inspection JSON whose status is `completed`, `timeout`, or `error`.
Parsing and predicate failures are completed inspections; inspector timeout,
spawn failure, nonzero exit, or invalid/incomplete JSON protocol are explicit
non-completions. The parent pins the outcome-record hash before launch, rebuilds
the source-bound inspection envelope itself, schema-validates it, and rechecks
the record and both raw streams after the child terminates. All dispositions
leave the integration test failed. A candidate passing all predicates is
described only as a surprising result frozen for a separate task. It is not
accepted as a counterexample, reproduction, certificate, or mathematical
result.

The CI integration step sets repository-relative
`EG_SURPRISING_OUTCOME_DIR` and an explicit
`EG_CANDIDATE_INSPECTION_TIMEOUT_SECONDS`. Local integration tests use a pytest
temporary directory when the artifact variable is absent; unit tests likewise
use temporary directories and synthetic direct inspector children to verify
timeout/error preservation without retaining measurement artifacts.

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

Fast CI additionally separates committed-range whitespace from post-test
worktree hygiene. The canonical committed check is:

```text
python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD
```

It requires complete history containing the strict-JSON
`review_base_commit`, resolves both endpoints to commits, proves ancestry, and
executes `git diff --check` on the explicit `<base>..<head>` object range under
the fixed policy
`blank-at-eol,space-before-tab,blank-at-eof,tabwidth=8`. Command-line Git
configuration overrides repository-local whitespace policy, while the child
environment neutralizes system/global configuration, process configuration
injection, global attributes, and system attributes. The resolved head commit
is the explicit attribute source, so checked-in `.gitattributes` remains
effective and an uncommitted worktree copy cannot change the verdict.

Repository-local `core.whitespace` and `core.attributesFile` are explicitly
overridden. The checker then runs one unscoped
`git config --includes --name-only --get-regexp` query for `diff.*` over the
effective configuration stack. System, global, and inherited process sources
have already been neutralized. Git therefore reads the shared local config and
loads the current worktree's `config.worktree` automatically only when
`extensions.worktreeConfig` is enabled; `include.path` remains effective.
Only a no-match exit with empty stdout and stderr is accepted. Any matched
`diff.*` or config parsing/query failure is fatal before and after the diff,
because a diff-driver `binary` setting can otherwise suppress whitespace
diagnostics. Both bad and clean ranges are rejected under such unreviewed
effective diff configuration.

The checker does not probe `--worktree` as a separate scope. Although the
installed Git 2.45.1 `git-config` documentation describes that option as
equivalent to `--local` when the extension is disabled, the installed binary
returns exit `128` in a real multi-worktree repository when the extension is
absent or false. The unscoped effective-stack query accepts that legitimate
layout and still includes per-worktree config whenever Git activates it.

Git exposes no supported read-only switch that ignores only its highest
precedence non-versioned source, `$GIT_DIR/info/attributes`, while retaining
checked-in attributes. The checker therefore permits only absence or a
zero-byte regular file and otherwise fails closed before the diff; it repeats
the check after the diff. This deliberate failure also applies to a clean
range. Concurrent hostile replacement during the subprocess window cannot be
made atomic without modifying or mirroring Git metadata, so it remains outside
the read-only trust boundary; the before/after checks catch persistent changes.

Success records both full SHAs and the range deterministically. The later
endpoint-free `git diff --check` steps are intentionally narrower: they check
only changes created in each test worktree. Neither form changes Git state.
Temporary real Git repositories in the focused unit suite provide substantive
single- and multi-worktree clean/failing cases, main- and linked-worktree
invocations, direct and included local/per-worktree hostile configuration,
neutralized system/global/process configuration, hostile attributes,
deterministic repetition, and read-only preservation checks. They do not
invoke a search or retain research artifacts.

The focused whitespace suite passed 84 tests, and the complete local suite
passed 247 tests. Neither reported a failure, skip, or xfail. The differential
test enumerates exactly 1,100 labelled simple graphs of orders 0 through 5.
This is `VERIFIED_BOUNDED_COMPUTATION`, not a proof outside that domain. The
deliberately invalid manifest-hash fixture is also required to fail
verification.

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
The runner writes and hashes both streams immediately after `execute()`
returns, before outcome matching, timestamps, result construction, or schema
work. Thus even a post-execution matching/configuration error cannot discard
the child streams.

If the producer ran, CI checks that the result JSON exists and independently
schema-validates it even after runner failure. Bounded stream diagnostics do
not replace the full files. On any compiler-job failure, the complete
`benchmarks/results/` directory and the complete tiny-surprise directory are
uploaded under names containing compiler, run ID, and run attempt. The
post-test upstream inventory and final hygiene checks also run through
`always()`. No later validation or upload masks the original nonzero step.
These remain `EMPIRICAL_OBSERVATION` engineering artifacts and do not establish
search coverage, reproduction, a certificate, or a mathematical result.

## Search-run discipline

A future material search must content-address its executable and inputs,
serialize configuration and pruning IDs, identify a deterministic partition,
record environment/resources/failures, hash every artifact, and undergo
independent certificate verification. The current search-partition and
certificate schemas are provisional and cannot support a certifying claim.

The current manual heavy workflow is only a non-executing scaffold. Its
manifest task ID is resolved from strict JSON
`REVIEW_STATE.yaml:active_task_id` in the checked-out commit, with the matching
regular non-symlink dossier status file required under `ops/`. The manifest
records the source field, canonical dossier-status path, and observed SHA-256
of both governance files. A missing, malformed, duplicate-key, non-finite,
noncanonical, escaping, or dossier-incomplete state fails before manifest
creation; there is no operator-supplied task identity or fallback. This
provenance binding does not run a search and does not make schema validation a
semantic or mathematical verification.

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
