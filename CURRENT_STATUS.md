# CURRENT_STATUS - erdos-gyarfas-p14

Last updated: 2026-07-20 UTC

## Current state

- Current phase: bind inspector timeout-test stability evidence to the exact
  execution-affecting worktree before any environment attestation or upstream
  research execution.
- Active task:
  `TASK-20260720__bind_stability_evidence_to_exact_worktree`.
- Task status: `BLOCKED`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `a7066e70b92d80be2d1772127f329c24222c1b41`.
- Task-start HEAD:
  `b1eb792a2a771485f37979cd932303f14ab52f56`.
- Last reviewed candidate HEAD:
  `b1eb792a2a771485f37979cd932303f14ab52f56`.
- Last review verdict: `REJECT`.
- Accepted task: `TASK-20260719__define_environment_trust_boundary`.
- Accepted review occurrence: `2026-07-19T10:24:26Z`.
- Governance update occurrence: `2026-07-20T07:50:03Z`.
- No candidate is ready for review from this task. A later atomic correction
  must begin from the unchanged accepted baseline; its candidate SHA will be
  intentionally resolved from Git by the reviewer.

The environment trust-boundary task remains accepted at exact commit
`a7066e70b92d80be2d1772127f329c24222c1b41`. Both accepted-baseline fields
remain fixed there. The cumulative candidate through
`b1eb792a2a771485f37979cd932303f14ab52f56` received `REJECT`. Its v1 report
contains raw streams for 25 focused runs and two full suites, but its execution
identity is not fail-closed over every untracked input that can alter pytest
collection or behavior. It also accepts full-suite counts through an arbitrary
minimum threshold instead of binding every run to one recorded collection.

Both earlier dossiers under
`ops/TASK-20260719__stabilize_inspector_timeout_test/` and
`ops/TASK-20260719__make_inspector_stability_evidence_auditable/` are immutable
historical evidence and are not reused or edited by this correction.

## Blocked exact-worktree correction

The strict v2 schema, runner, independent verifier, and 52-case synthetic test
suite are implemented. The tooling gate passed with 52 focused synthetic tests
and 336 total unit tests. The final preflight accepted the exact task allowlist
with zero staged or unexpected paths and 195 execution inputs.

The single permitted real runner invocation then failed before its first
collection subprocess. Git's ignored-path probe exited `0` but emitted 792
bytes of permission-denied warnings while attempting to open nine pre-existing
ignored `build/pytest-*` directories. The runner correctly failed closed,
recorded zero subprocesses and zero stability attempts, preserved a canonical
partial report, and removed its one created basetemp and task-owned root. The
task rule prohibits retry, so this task is `BLOCKED`.

The partial report is schema-valid. The independent same-host verifier accepts
it only with `--allow-partial`, returning `completed=false` and
`evidence_success=false`; normal completed-evidence verification correctly
fails. No source, normalized worktree, or collection digest and no focused or
full-suite count were established. `RFU-TEST-001` remains `OPEN`.

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
- `RFU-TEST-001`: `OPEN`; this correction is blocked without completed
  stability evidence. A later atomic task must address the unreadable ignored
  paths before producing a new independently reviewable execution.
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

- Resolve the ignored-path readability/authority mismatch in a separate atomic
  task and produce a fresh exact-worktree correction from the unchanged
  accepted baseline.
- Keep `RFU-TEST-001` open until that review accepts the evidence.
- Resolve or explicitly accept every relevant environment lock, capture, and
  external-service dependency under later `RFU-ENV-001` work before using that
  interface for V3 or V4 evidence.
- Audit the upstream generation invariant and every pruning proof separately.
- Define and prove search partition coverage, certificate semantics, replay,
  and verifier independence before any certifying execution.
- `RS-001` remains `NOT STARTED`.
