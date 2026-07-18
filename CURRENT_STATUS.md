# CURRENT_STATUS — erdos-gyarfas-p14

Last updated: 2026-07-18 UTC

## Current state

- Current phase: isolating committed-range whitespace semantics before
  research.
- Active task: `TASK-20260718__isolate_whitespace_git_semantics`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`.
- Task-start HEAD: `ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4`.
- Last reviewed candidate HEAD:
  `ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4`.
- Last review verdict: `REJECT`.
- Accepted task: `TASK-20260717__bind_heavy_workflow_task_identity`.
- Next review: the cumulative range from the accepted baseline through this
  corrective candidate; the candidate SHA is intentionally resolved from Git
  by the reviewer.

The candidate at `ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4` was rejected
because mutable repository, system, global, and process Git configuration and
non-versioned attribute sources could weaken its `git diff --check` verdict.
The accepted baseline therefore remains
`e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`, and the next review remains
cumulative from that commit. The rejected candidate is retained in history;
this task corrects it without reset, revert, or rewrite.

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

## Corrective whitespace candidate and open follow-ups

The corrective candidate preserves the strict review-state, repository-root,
commit-resolution, ancestry, and explicit `<base>..<head>` checks introduced
by the rejected candidate. It defines the intended whitespace policy
explicitly, isolates neutralizable Git configuration and non-versioned
attribute sources, preserves checked-in `.gitattributes`, and fails closed on
a non-versioned repository attribute source that cannot be safely ignored.
The dedicated full-history CI invocation and the separate post-test worktree
checks are unchanged.

The three pending follow-ups remain ordered and `OPEN`:

- `RFU-CI-003`: committed-range whitespace checking, pending review of this
  corrective candidate;
- `RFU-SUPPLY-001`: immutable GitHub Action references;
- `RFU-ENV-001`: complete environment and system-package locking.

No follow-up is closed before review. Hosted GitHub Actions behavior remains
outside local evidence.

Final local verification passes 63 focused whitespace tests, the 222-test
bounded suite, and the 226-test complete suite with no failures, skips, or
xfails. Strict JSON, canonical task resolution, all schemas, the upstream
snapshot, and the real cumulative checker invocation also pass. All
task-created basetemps and synthetic repositories were removed after exact
path checks.

## Current mathematical claim boundary

No P13 or P14 research run has started. This task introduces no mathematical
result and no new theorem, counterexample, exhaustive search,
computer-certified result, reproduced upstream result, certifying pruning
rule, or accepted search certificate. All mathematical target statuses remain
unchanged. The checker and its tests are bounded engineering evidence only.

## Remaining scientific and engineering obligations

- The upstream generation invariant and every pruning proof remain unaudited.
- Search partition coverage, replay, certificate semantics, and independent
  search verification remain provisional or unimplemented.
- The verifier is intentionally exponential and intended for small candidates,
  not search-completeness certification.
- Hosted GitHub Actions execution remains outside local evidence. Action
  immutability and complete environment locking remain open.
- `RS-001` is `NOT STARTED`.
