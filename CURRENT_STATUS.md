# CURRENT_STATUS — erdos-gyarfas-p14

Last updated: 2026-07-17 UTC

## Current state

- Current phase: bounded process-outcome contract enforcement before research.
- Active task: `TASK-20260717__enforce_process_outcome_semantics`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `f8271e74509a017d1631dea72aaa652f44d8c3df`.
- Task-start HEAD: `f8271e74509a017d1631dea72aaa652f44d8c3df`.
- Last reviewed candidate HEAD:
  `f8271e74509a017d1631dea72aaa652f44d8c3df`.
- Last review verdict: `ACCEPT WITH FOLLOW-UP`.
- Accepted task: `TASK-20260717__repair_postcommit_review_state`.
- Next review: cumulative from the accepted review baseline through this
  process-outcome candidate; the candidate SHA is intentionally resolved from
  Git by the reviewer.

The preceding governance task was accepted at
`f8271e74509a017d1631dea72aaa652f44d8c3df` with verdict
`ACCEPT WITH FOLLOW-UP`, advancing both accepted-baseline fields to that
commit. This candidate enforces the missing process-outcome contract for the
two high-severity CI follow-ups. Its current-state wording remains valid before
and after the user's manual commit because the reviewer resolves the candidate
SHA from Git.
`REVIEW_STATE.yaml` is the machine-readable review truth.

## Accepted bootstrap scope

- All six requested upstream refs resolved; none is absent or unresolved.
- The ten-file raw `main` snapshot and upstream MIT license are preserved and
  match the selected Git tree and recorded SHA-256 inventory.
- Original Make and project CMake Debug/Release builds completed in the tested
  MSYS2 environment without changing the snapshot.
- Tiny upstream `k=3` and `k=4` processes terminated within ten-second test
  timeouts.
- The independent Python graph verifier, machine-JSON CLI, fixtures, unit
  tests, bounded differential oracles, and CLI integration tests are present.
- The accepted local bootstrap suite passed 63 tests, including the exact
  1,100-graph bounded differential domain on orders zero through five.
- Five JSON Schemas, manifest/hash validation, a benchmark harness, fast CI,
  and a manual non-certifying heavy-workflow scaffold are present.

These are bounded engineering and predicate checks only. The accepted verdict
does not convert them into an upstream reproduction, exhaustive computation,
certificate, or mathematical proof.

## Process-outcome candidate and open follow-ups

This candidate addresses `RFU-CI-001` and `RFU-CI-002`; both remain `OPEN`
pending review and acceptance:

- known `k=3` and `k=4` cases require `(exited, 0)` as the only ordinary
  successful outcome;
- exit `100` is independently parsed and checked by project-authored verifier
  code, reported canonically, and always fails the ordinary integration test;
- benchmark cases declare exact accepted outcome pairs, and the runner returns
  success only for an exact match after preserving validated artifacts;
- CI retains the runner failure while always validating the result and
  surfacing bounded failure diagnostics.

The four medium follow-ups remain untouched and `OPEN`:

- `RFU-WORKFLOW-001`: remove the hardcoded bootstrap task ID from the manual
  heavy-workflow manifest path;
- `RFU-CI-003`: check whitespace over the committed comparison interval;
- `RFU-SUPPLY-001`: pin GitHub Action references immutably;
- `RFU-ENV-001`: complete environment and system-package locking.

No follow-up is removed or closed by an unreviewed candidate.

## Current mathematical claim boundary

No P13 or P14 research run has started. This task introduces no mathematical
result and no new theorem, counterexample, exhaustive search,
computer-certified result, reproduced upstream result, certifying pruning
rule, or accepted search certificate. All mathematical target statuses remain
unchanged. Benchmark results remain `EMPIRICAL_OBSERVATION`, and the new checks
are bounded engineering evidence only.

## Remaining scientific and engineering obligations

- The upstream generation invariant and every pruning proof remain unaudited.
- Search partition coverage, replay, certificate semantics, and independent
  search verification remain provisional or unimplemented.
- The verifier is intentionally exponential and intended for small candidates,
  not search-completeness certification.
- Docker and hosted GitHub Actions execution remain outside the local bootstrap
  evidence, and environment immutability is incomplete.
- `RS-001` is `NOT STARTED`.
