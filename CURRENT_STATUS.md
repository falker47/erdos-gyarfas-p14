# CURRENT_STATUS — erdos-gyarfas-p14

Last updated: 2026-07-17 UTC

## Current state

- Current phase: hardening surprising process-outcome preservation before
  research.
- Active task: `TASK-20260717__harden_surprising_outcome_preservation`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `f8271e74509a017d1631dea72aaa652f44d8c3df`.
- Task-start HEAD: `be179265919566b44d40cb1e472cd3db50811502`.
- Last reviewed candidate HEAD:
  `be179265919566b44d40cb1e472cd3db50811502`.
- Last review verdict: `REJECT`.
- Accepted task: `TASK-20260717__repair_postcommit_review_state`.
- Next review: cumulative from the accepted review baseline through this
  corrective preservation candidate; the candidate SHA is intentionally
  resolved from Git by the reviewer.

The governance task `TASK-20260717__repair_postcommit_review_state` was
accepted at `f8271e74509a017d1631dea72aaa652f44d8c3df`; both accepted-baseline
fields remain fixed there. The subsequent process-outcome candidate at
`be179265919566b44d40cb1e472cd3db50811502` was rejected because surprising
streams were not durably uploaded and exit-100 inspection could block before a
durable freeze. This corrective candidate hardens those paths without changing
mathematical semantics. Its SHA is intentionally resolved from Git by the
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

## Corrective outcome-preservation candidate and open follow-ups

The rejected candidate attempted to address `RFU-CI-001` and `RFU-CI-002`;
both remain `OPEN`. This corrective candidate preserves the exact outcome
contract while repairing the review blockers:

- known `k=3` and `k=4` cases require `(exited, 0)` as the only ordinary
  successful outcome;
- every nonordinary tiny outcome writes byte-exact stdout/stderr, file hashes,
  and a deterministic `EMPIRICAL_OBSERVATION` record before inspection;
- exit `100` is independently inspected in a direct child with a separate
  cross-platform timeout, and `completed`, `timeout`, and `error` are recorded
  without accepting any mathematical claim;
- benchmark cases declare exact accepted outcome pairs, and the runner returns
  success only for an exact match after immediately preserving stdout/stderr;
- CI retains producer failures, still runs result/inventory/hygiene checks, and
  uploads complete tiny and benchmark artifact directories on failure.

The four medium follow-ups remain untouched and `OPEN`:

- `RFU-WORKFLOW-001`: remove the hardcoded bootstrap task ID from the manual
  heavy-workflow manifest path;
- `RFU-CI-003`: check whitespace over the committed comparison interval;
- `RFU-SUPPLY-001`: pin GitHub Action references immutably;
- `RFU-ENV-001`: complete environment and system-package locking.

No follow-up is removed or closed by this unreviewed corrective candidate.

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
