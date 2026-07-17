# CURRENT_STATUS — erdos-gyarfas-p14

Last updated: 2026-07-17 UTC

## Current state

- Current phase: binding manual heavy-workflow manifest provenance to canonical
  repository task identity before research.
- Active task: `TASK-20260717__bind_heavy_workflow_task_identity`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `0d08a58d87e7aaa5749ed2d3428cc0906a6bade6`.
- Task-start HEAD: `0d08a58d87e7aaa5749ed2d3428cc0906a6bade6`.
- Last reviewed candidate HEAD:
  `0d08a58d87e7aaa5749ed2d3428cc0906a6bade6`.
- Last review verdict: `ACCEPT WITH FOLLOW-UP`.
- Accepted task: `TASK-20260717__harden_surprising_outcome_preservation`.
- Next review: this workflow-provenance candidate from the accepted review
  baseline; the candidate SHA is intentionally
  resolved from Git by the reviewer.

The process-outcome hardening task
`TASK-20260717__harden_surprising_outcome_preservation` was accepted at
`0d08a58d87e7aaa5749ed2d3428cc0906a6bade6` with verdict
`ACCEPT WITH FOLLOW-UP`. This candidate addresses only `RFU-WORKFLOW-001` by
binding the manual scaffold manifest task identity to the versioned review
state and its dossier. Its SHA is intentionally resolved from Git by the
reviewer, so this wording remains true before and after the user's manual
commit.
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

## Workflow-provenance candidate and open follow-ups

`RFU-CI-001` and `RFU-CI-002` were removed from pending follow-ups after
acceptance of the process-outcome hardening task. The four remaining follow-ups
are `OPEN`:

- `RFU-WORKFLOW-001`: remove the hardcoded bootstrap task ID from the manual
  heavy-workflow manifest path; it remains open pending review of this
  candidate;
- `RFU-CI-003`: check whitespace over the committed comparison interval;
- `RFU-SUPPLY-001`: pin GitHub Action references immutably;
- `RFU-ENV-001`: complete environment and system-package locking.

No remaining follow-up is closed by this candidate before review.

The candidate adds a read-only strict-JSON resolver, requires the canonical
task dossier, and records the review-state source, dossier path, and both file
hashes in scaffold parameters. Resolution failure stops the job before
manifest creation. The workflow still validates any emitted manifest and
uploads the manifest and log with `if: always()`.

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
