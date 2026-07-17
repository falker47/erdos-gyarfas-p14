# CURRENT_STATUS — erdos-gyarfas-p14

Last updated: 2026-07-17 UTC

## Current state

- Current phase: bootstrap baseline prepared; scientific work has not begun.
- Active task: `TASK-20260715__bootstrap_reproducible_baseline`.
- Task status: `READY_FOR_REVIEW`.
- Awaiting user review: yes.
- Initial and current HEAD: `NO_GIT_REPOSITORY`.
- Working branch: none.
- Accepted baseline commit: none; the user has not yet reviewed or committed
  this baseline.
- Exact next action: the user reviews the complete file set, initializes or
  restores Git metadata, runs the documented checks plus normal Git diff
  checks, and manually creates the accepted bootstrap commit if satisfied.

The supplied directory had no Git repository at startup. At handoff an empty
directory named `.git` is present, but it contains no metadata and every normal
Git query still reports “not a git repository.” No task agent reports creating
it, and its filesystem origin is unresolved. Because Git writes are prohibited,
Codex did not initialize, populate, or remove it.

## Completed bootstrap scope

- All six requested upstream refs resolved; none is absent or unresolved.
- The ten-file raw `main` snapshot and upstream MIT license are preserved and
  match the selected Git tree and recorded SHA-256 inventory.
- Original Make and project CMake Debug/Release builds completed in the tested
  MSYS2 environment without changing the snapshot.
- Tiny upstream `k=3` and `k=4` processes terminated within ten-second test
  timeouts with ordinary upstream exit `0`.
- The independent Python graph verifier, machine-JSON CLI, fixtures, unit
  tests, bounded differential oracles, and CLI integration tests are present.
- The full accepted local suite passed 63 tests: 48 unit, one differential,
  ten verifier-CLI integration, and four upstream-build integration tests.
- Five JSON Schemas, manifest/hash validation, a benchmark harness, fast CI,
  and a manual non-certifying heavy-workflow scaffold are present.
- Repeated verifier serialization was byte-identical. A real ephemeral `k=3`
  benchmark result validated against its schema and was then removed.
- Final snapshot, schema, required-structure, claim-language, absolute-path,
  generated-product, and project-file whitespace audits passed. The vendored
  snapshot retains upstream whitespace and is marked `-diff`; its exact bytes
  are enforced independently by the inventory verifier.

## Checks not executed in their target environments

- Docker image build: not run because Docker is unavailable locally.
- GitHub Actions: not run; both workflows received local syntax and guard
  review, but `actionlint` was unavailable.
- Normal `git status`, `git diff`, and `git diff --check`: unavailable because
  there is no valid Git repository. A no-index project-file whitespace audit
  was used as the bootstrap equivalent.

## Current mathematical claim boundary

There is no new theorem, counterexample, exhaustive search, computer-certified
result, accepted search certificate, or certifying pruning rule. Published P13
and P12 results remain external and have not been independently reproduced.
The 1,100-graph predicate comparison is `VERIFIED_BOUNDED_COMPUTATION` only on
labelled simple graphs of orders zero through five. Tiny upstream invocations
and the ephemeral benchmark are engineering smoke evidence only.

## Unresolved scientific and engineering obligations

- The upstream generation invariant and every pruning proof remain unaudited.
- Search partition coverage, replay, certificate semantics, and independent
  search verification remain provisional or unimplemented.
- The verifier is intentionally exponential and intended for small candidates,
  not search-completeness certification.
- CI portability across its configured GCC/Clang and Python matrix awaits the
  first GitHub Actions run; the Docker interface also awaits an actual build.
- Transitive Python dependencies and Ubuntu archive package versions are not
  immutably locked by this bootstrap.

No P13 or P14 search may begin as part of this task.
