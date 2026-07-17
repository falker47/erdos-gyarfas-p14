# CURRENT_STATUS — erdos-gyarfas-p14

Last updated: 2026-07-17 UTC

## Current state

- Current phase: accepted bootstrap baseline; review-state synchronization.
- Active task: `TASK-20260717__establish_review_state`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Current HEAD: `164d6756fd2f6725f2de0bedbe13f1e8c444ba0c`.
- Bootstrap review verdict: `ACCEPT WITH FOLLOW-UP`.
- Accepted baseline commit:
  `164d6756fd2f6725f2de0bedbe13f1e8c444ba0c`.
- Review truth: `REVIEW_STATE.yaml` records the machine-readable baseline and
  open follow-ups for the next cumulative review.

The bootstrap task `TASK-20260715__bootstrap_reproducible_baseline` is accepted
at the exact commit above. The earlier dossier correctly records that its
supplied pre-commit directory lacked usable Git metadata; that historical
startup condition no longer describes the current repository.

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

## Open review follow-ups

The following accepted-bootstrap follow-ups remain `OPEN` in
`REVIEW_STATE.yaml` and are not resolved by the current governance task:

- `RFU-CI-001`: distinguish known exit `0` completion from exit `100` candidate
  behavior in tiny CI cases;
- `RFU-CI-002`: validate the benchmark child-process outcome in CI;
- `RFU-WORKFLOW-001`: remove the hardcoded bootstrap task ID from the manual
  heavy-workflow manifest path;
- `RFU-CI-003`: check whitespace over the committed comparison interval;
- `RFU-SUPPLY-001`: pin GitHub Action references immutably;
- `RFU-ENV-001`: complete environment and system-package locking.

The pipeline must not be relied upon as complete evidentiary support until the
applicable CI follow-ups are addressed and reviewed.

## Current mathematical claim boundary

No P13 or P14 research run has started. This task introduces no mathematical
content and no new theorem, counterexample, exhaustive search,
computer-certified result, reproduced upstream result, certifying pruning
rule, or accepted search certificate. All mathematical target statuses remain
unchanged.

## Remaining scientific and engineering obligations

- The upstream generation invariant and every pruning proof remain unaudited.
- Search partition coverage, replay, certificate semantics, and independent
  search verification remain provisional or unimplemented.
- The verifier is intentionally exponential and intended for small candidates,
  not search-completeness certification.
- Docker and hosted GitHub Actions execution remain outside the local bootstrap
  evidence, and environment immutability is incomplete.
- `RS-001` is not started.
