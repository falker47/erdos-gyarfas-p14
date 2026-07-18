# CURRENT_STATUS — erdos-gyarfas-p14

Last updated: 2026-07-18 UTC

## Current state

- Current phase: enforcing committed-range whitespace validation before
  research.
- Active task: `TASK-20260717__enforce_committed_range_whitespace`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`.
- Task-start HEAD: `e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`.
- Last reviewed candidate HEAD:
  `e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`.
- Last review verdict: `ACCEPT WITH FOLLOW-UP`.
- Accepted task: `TASK-20260717__bind_heavy_workflow_task_identity`.
- Next review: this committed-range-whitespace candidate from the accepted
  review baseline; the candidate SHA is intentionally resolved from Git by
  the reviewer.

The workflow-provenance task
`TASK-20260717__bind_heavy_workflow_task_identity` was accepted at
`e33c3bf121d5bb81b4c63adf704ca9b4ecfea970` with verdict
`ACCEPT WITH FOLLOW-UP`. That acceptance resolved `RFU-WORKFLOW-001`. This
candidate addresses only `RFU-CI-003` by separating a canonical committed
range check from post-test worktree checks. Its SHA is intentionally resolved
from Git by the reviewer, so this wording remains true before and after the
user's manual commit. `REVIEW_STATE.yaml` is the machine-readable review truth.

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

## Committed-range-whitespace candidate and open follow-ups

`RFU-WORKFLOW-001` was removed after acceptance of the workflow-provenance
task. The three remaining follow-ups are `OPEN`:

- `RFU-CI-003`: check whitespace over the committed comparison interval; it
  remains open pending review of this candidate;
- `RFU-SUPPLY-001`: pin GitHub Action references immutably;
- `RFU-ENV-001`: complete environment and system-package locking.

No remaining follow-up is closed by this candidate before review. The
candidate adds a read-only strict-JSON helper for
`REVIEW_STATE.yaml:review_base_commit..HEAD`, gives that helper one dedicated
full-history CI job, and retains the matrix-local `git diff --check` steps only
for changes created in the worktree by tests.

The authorized corrective continuation reproduced the sole stale-test
failure, then made the canonical resolver test derive its expectation
independently from `REVIEW_STATE.yaml:active_task_id`. A synthetic regression
also proves that distinct accepted and active task IDs resolve only the active
ID when only its dossier exists. The production resolver, whitespace helper,
and workflows are unchanged by the correction.

Final local verification passes 35 resolver tests, 36 committed-range
whitespace tests, the 195-test bounded suite, and the 199-test complete suite
with no failures or skips. JSON, canonical resolver/range commands, all
schemas, and the upstream snapshot also pass. Session-created basetemps were
removed after containment checks.

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
- Hosted GitHub Actions execution remains outside local evidence. Action
  immutability and complete environment locking remain open.
- `RS-001` is `NOT STARTED`.
