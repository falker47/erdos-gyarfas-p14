# TASK-20260719__stabilize_inspector_timeout_test - Status

- Mode: STRICT
- Objective: make inspector timeout tests deterministic by separating the
  freeze-before-inspection proof from timeout, kill, drain, and reaping
  coverage without changing production behavior.
- Repository: `falker47/erdos-gyarfas-p14`
- Repository root:
  `C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `a7066e70b92d80be2d1772127f329c24222c1b41`
- Task-start HEAD: `a7066e70b92d80be2d1772127f329c24222c1b41`
- Accepted predecessor: `TASK-20260719__define_environment_trust_boundary`
- Previous verdict: `ACCEPT WITH FOLLOW-UP`
- Accepted review occurrence: `2026-07-19T10:24:26Z`
- Addressed follow-up: `RFU-TEST-001` (`OPEN` pending review)
- Preserved follow-up: `RFU-ENV-001` (`OPEN`, unchanged)
- Completion time: `2026-07-19T11:11:50Z`
- Status: `READY_FOR_REVIEW`

## Startup gate

The exact repository root and origin, branch `main`, task-start HEAD, review
base, ancestry, empty worktree, and empty index matched the task
preconditions. Plain Git first rejected the sandbox identity for dubious
ownership. Every successful Git read uses only the permitted process-local
`-c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`
option; no Git configuration changed.

The current dossier was initially absent, as expected. All mandatory files,
the accepted environment-boundary dossier, the earlier process-outcome and
surprising-outcome dossiers, affected code and tests, and relevant Git history
were inspected before modification.

## Authorized scope

Only these seven paths may change:

- `tests/unit/test_upstream_candidate_inspection.py`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260719__stabilize_inspector_timeout_test/TASK_STATUS.md`
- `ops/TASK-20260719__stabilize_inspector_timeout_test/TASK_LOG.md`
- `ops/TASK-20260719__stabilize_inspector_timeout_test/EVIDENCE.md`

Every other path is protected. In particular, the production inspector,
accepted environment-boundary files and dossier, environment inventory and
schema, workflows, build/dependency inputs, verifier, upstream snapshot and
metadata, claims, pruning, manifests, certificates, and benchmarks must remain
byte-identical.

## Exact flake cause

The previous test coupled two independent properties under one 0.75-second
deadline. A fresh Python child had to start, decode the outcome JSON, read both
frozen streams, calculate both SHA-256 hashes, and create a marker before the
same child could be timed out. Under full-suite load the child could be killed
before the marker, so the marker assertion produced a temporal false negative.
This is not evidence of a production inspector defect.

## Correction design

- A real synthetic inspector uses a generous ten-second bound, verifies that
  the outcome and both streams already exist with their recorded sizes and
  SHA-256 hashes, and then terminates in a controlled completed protocol.
- A stateful `Popen` fake deterministically exercises first
  `communicate(timeout=0.75)`, `TimeoutExpired`, `kill`, second
  `communicate()` without a timeout, drained stdout/stderr, return-code
  acquisition, context exit, and wait/reap behavior.
- The deterministic test snapshots the frozen outcome and streams before the
  timeout call, then checks exact bytes and SHA-256 afterward, the timeout
  payload, preserved-source flags, and the non-mathematical classification.
- A real-child smoke test requires no parsing, hashing, heartbeat, or marker
  before its deadline. It checks that state stops changing after return and no
  late marker appears.

No production file is modified.

## Verification state

Two focused development runs pass all 31 tests. All 25 required consecutive
focused runs pass 31 tests each. Two complete suites pass consecutively with
299 tests each and no skip or xfail. Strict JSON, all schemas, Action pins,
upstream inventory, committed-range whitespace, worktree whitespace, exact
allowlist, empty index, follow-up identity, protected inventory, and task
basetemp cleanup pass.

The first strict byte audit found checkout CR bytes in the authorized research
priority file. That file was normalized through `apply_patch`; the repeated
audit passes strict UTF-8, LF-only, final LF, no BOM/NUL, and no trailing
whitespace for all seven authorized paths. Final validators, protected-state
comparison, exact status, cleanup, and complete diff inspection pass.

## Claim boundary and limitations

This task produces bounded V1 engineering-test evidence only. Timeout records
remain `EMPIRICAL_OBSERVATION` diagnostics. The task does not establish an
upstream reproduction, exhaustive search, certificate, theorem, proof,
counterexample, mathematical claim, or pruning rule. `RS-001` remains
`NOT STARTED`; claims and pruning must remain byte-identical.

`RFU-TEST-001` remains `OPEN` until review of the candidate. `RFU-ENV-001`
remains separately `OPEN` and unchanged; no environment attestation begins.

## Risks and unresolved issues

Any required focused or complete-suite failure, any renewed timing failure,
any protected-file change, or any need to modify production code forces the
task to `BLOCKED` without scope expansion. The accepted commit has an
unexpected subject unrelated to the environment-boundary file set; the exact
accepted SHA, task association, and review occurrence remain authoritative.

## Current status

`READY_FOR_REVIEW`
