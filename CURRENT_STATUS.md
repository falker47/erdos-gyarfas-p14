# CURRENT_STATUS — erdos-gyarfas-p14

Last updated: 2026-07-18 UTC

## Current state

- Current phase: supporting multi-worktree committed-range whitespace
  validation before research.
- Active task: `TASK-20260718__support_multi_worktree_whitespace_check`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `0dd6e5dc1362e866dd806e205750d82695d3c555`.
- Task-start HEAD: `0dd6e5dc1362e866dd806e205750d82695d3c555`.
- Last reviewed candidate HEAD:
  `0dd6e5dc1362e866dd806e205750d82695d3c555`.
- Last review verdict: `ACCEPT WITH FOLLOW-UP`.
- Accepted task: `TASK-20260718__isolate_whitespace_git_semantics`.
- Next review: the cumulative range from the accepted baseline through the
  current multi-worktree corrective candidate; the candidate SHA is
  intentionally resolved from Git by the reviewer.

The cumulative range from
`e33c3bf121d5bb81b4c63adf704ca9b4ecfea970` through the current accepted
baseline was accepted with follow-up. `RFU-CI-003` is resolved. The accepted
checker isolates mutable Git configuration and non-versioned attributes, but
its unconditional per-worktree scope query fails on a legitimate repository
with multiple worktrees when `extensions.worktreeConfig` is absent or false.
That fail-closed portability defect is tracked as `RFU-CI-004` and is the sole
scope of this task.

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

## Multi-worktree whitespace candidate and open follow-ups

The candidate replaces separate local and unconditional `--worktree` config
queries with one read of Git's effective configuration stack after system,
global, and inherited process sources have been neutralized. Local config and
its includes remain visible. Git automatically adds the current worktree's
config only when `extensions.worktreeConfig` is enabled. Any effective
`diff.*` still fails closed before and after the committed range check.

All other state, revision, ancestry, whitespace-policy, checked-in attribute,
non-versioned attribute, external-diff, text-conversion, and read-only checks
remain in place. The workflow is unchanged.

The three pending follow-ups remain ordered and `OPEN`:

- `RFU-CI-004`: multi-worktree whitespace config validation, pending review of
  this candidate;
- `RFU-SUPPLY-001`: immutable GitHub Action references;
- `RFU-ENV-001`: complete environment and system-package locking.

No follow-up is closed before review. Hosted GitHub Actions behavior remains
outside local evidence. Local verification passes 84 focused tests, the
243-test bounded suite, and the 247-test complete suite with no failure, skip,
or xfail. Strict JSON, canonical task resolution, schemas, the upstream
snapshot, and the real checker invocation also pass. Final scope,
whitespace, Git-state preservation, registry preservation, and cleanup audits
pass; the candidate stops at `READY_FOR_REVIEW`.

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
