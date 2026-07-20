# CURRENT_STATUS - erdos-gyarfas-p14

Last updated: 2026-07-19 UTC

## Current state

- Current phase: make the inspector timeout-test stability evidence auditable
  before any environment attestation or upstream research execution.
- Active task:
  `TASK-20260719__make_inspector_stability_evidence_auditable`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `a7066e70b92d80be2d1772127f329c24222c1b41`.
- Task-start HEAD:
  `c71d66995ae6a36620a2aa8f938faf6d84fe1af7`.
- Last reviewed candidate HEAD:
  `c71d66995ae6a36620a2aa8f938faf6d84fe1af7`.
- Last review verdict: `REJECT`.
- Accepted task: `TASK-20260719__define_environment_trust_boundary`.
- Accepted review occurrence: `2026-07-19T10:24:26Z`.
- Rejected review occurrence: `2026-07-19T11:58:09Z`.
- Next review: the cumulative range from the unchanged accepted baseline
  through this evidence-audit correction; the candidate SHA is intentionally
  resolved from Git by the reviewer.

The environment trust-boundary task remains accepted at exact commit
`a7066e70b92d80be2d1772127f329c24222c1b41`. Both accepted-baseline fields
remain fixed there. The later timeout-test stabilization candidate at
`c71d66995ae6a36620a2aa8f938faf6d84fe1af7` was rejected solely because its
central repeated-stability evidence was available only as Markdown
transcription. The test redesign was statically sound, but the repository did
not contain raw output, JUnit results, a machine-readable run bundle, a CI
artifact, or another independently checkable execution record for the claimed
25 focused runs and two complete suites.

The rejected dossier under
`ops/TASK-20260719__stabilize_inspector_timeout_test/` is immutable historical
evidence and is not reused or edited by this correction.

## Active evidence-audit correction

The current task has created a strict, closed-world JSON evidence format, a
serial standard-library runner, an independent verifier, focused unit tests,
and one completed report at
`ops/TASK-20260719__make_inspector_stability_evidence_auditable/STABILITY_EVIDENCE.json`.
That JSON report, not a Markdown table, will be the canonical record of exactly
25 focused inspector-test executions followed immediately by two complete
pytest-suite executions.

The one and only actual runner invocation completed from
`2026-07-19T13:31:35.919158Z` through `2026-07-19T13:37:40.838505Z` with exit
zero. All 27 required serial attempts passed without retry: each of the 25
focused attempts reported 31 passes, and both complete suites reported 333
passes. Every recorded non-passing outcome count is zero. Cleanup removed all
27 task basetemps, left none, and removed the task-owned root.

The canonical report is 93,644 bytes with SHA-256
`b370e24312b69423c757a69368860f0316added6f86af4c9c7fe7fddc9c484f1`.
Its 170-file execution scope has fingerprint
`415ef1d6ab427a28f5c437371364f181fc3a489f228b2b87cbba80887400f26a`.
The independent verifier, including opt-in same-host source and tool
rehashing, exited zero and recomputed the report hashes and counts. Schema,
focused tooling, all-unit, Action-pin, upstream-snapshot, strict-state, and
protected-inventory checks also pass.

This bounded result is not accepted review state. Final complete-diff,
exact-allowlist, protected-inventory, and `git diff --check` inspections pass,
so the task is `READY_FOR_REVIEW`. `RFU-TEST-001` remains `OPEN` until the
machine-readable report and cumulative candidate receive independent review.

## Accepted environment boundary

`research/ENVIRONMENT_LOCK_INVENTORY.json` remains the canonical
machine-readable inventory tied to the accepted environment-boundary task. Its
58 stable IDs distinguish locked, captured, mutable-resolution, and external
service dependencies across hosted runners, Actions, Python, container/APT,
native tools, local MSYS2, platform resources, and execution-affecting
environment state.

`research/ENVIRONMENT_TRUST_BOUNDARY.md` continues to define the distinct V1,
V3, V4, and exploratory-observation boundaries. Inventorying an environment
gap does not resolve it. No implementation-level environment lock or
attestation is accepted, and this correction does not begin that work.

## Accepted engineering baseline

- The exact upstream `main` snapshot and license remain byte-preserved under
  recorded commit, tree, and SHA-256 provenance.
- The independent Python verifier, strict schemas, bounded fixtures, unit and
  differential tests, native build wrappers, fast CI, and non-executing heavy
  scaffold remain the accepted bootstrap engineering interface.
- All eleven external Action occurrences remain pinned to the accepted
  checkout `v4.3.1`, setup-python `v5.6.0`, and upload-artifact `v4.6.2`
  commits.

These are bounded engineering facts only. They do not establish an upstream
reproduction, exhaustive computation, certificate, theorem, or proof.

## Follow-up state

- `RFU-DOC-001`: resolved by accepted commit
  `41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d` and no longer pending.
- `RFU-TEST-001`: `OPEN`; the correction must produce independently auditable
  repeated-stability evidence, and the follow-up cannot close before review.
- `RFU-ENV-001`: `OPEN` and unchanged; its canonical scope remains the
  unresolved locking, capture, and external-service trust obligations in
  `research/ENVIRONMENT_LOCK_INVENTORY.json` and
  `research/ENVIRONMENT_TRUST_BOUNDARY.md`.

## Current mathematical claim boundary

No P13 or P14 research run has started. This task can produce only bounded V1
engineering-test evidence classified as `EMPIRICAL_OBSERVATION`. It creates no
mathematical result, theorem, counterexample, exhaustive search,
computer-certified result, reproduced upstream result, certifying pruning
rule, or accepted search certificate. `research/CLAIMS_REGISTRY.yaml` and
`research/PRUNING_REGISTRY.md` remain protected and byte-identical. All
mathematical target statuses remain unchanged.

## Remaining scientific and engineering obligations

- Review the cumulative candidate from the unchanged accepted baseline.
- Keep `RFU-TEST-001` open until that review accepts the evidence.
- Resolve or explicitly accept every relevant environment lock, capture, and
  external-service dependency under later `RFU-ENV-001` work before using that
  interface for V3 or V4 evidence.
- Audit the upstream generation invariant and every pruning proof separately.
- Define and prove search partition coverage, certificate semantics, replay,
  and verifier independence before any certifying execution.
- `RS-001` remains `NOT STARTED`.
