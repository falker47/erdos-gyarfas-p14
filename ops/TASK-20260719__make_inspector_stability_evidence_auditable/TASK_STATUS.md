# TASK-20260719__make_inspector_stability_evidence_auditable - Status

- Mode: STRICT
- Objective: replace Markdown-only stability claims with an independently
  inspectable, machine-readable evidence bundle for the inspector timeout-test
  stabilization.
- Repository: `falker47/erdos-gyarfas-p14`
- Repository root:
  `C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `a7066e70b92d80be2d1772127f329c24222c1b41`
- Task-start HEAD: `c71d66995ae6a36620a2aa8f938faf6d84fe1af7`
- Rejected candidate: `c71d66995ae6a36620a2aa8f938faf6d84fe1af7`
- Previous verdict: `REJECT`
- Rejected review occurrence: `2026-07-19T11:58:09Z`
- Accepted predecessor: `TASK-20260719__define_environment_trust_boundary`
- Targeted follow-up: `RFU-TEST-001` (`MEDIUM`, `OPEN`)
- Preserved follow-up: `RFU-ENV-001` (`MEDIUM`, `OPEN`, unchanged)
- Governance state-write time: `2026-07-19T12:22:54Z`
- Status: `READY_FOR_REVIEW`

## Startup gate

Before modification, read-only Git inspection resolved the intended repository
root and origin, branch `main`, exact task-start HEAD, and accepted baseline.
The baseline resolves to a commit and is an ancestor of task-start HEAD. The
worktree and index were empty.

Plain Git first rejected the sandbox identity for dubious ownership. Every
successful Git read uses only the process-local option:

```text
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
```

No global or repository Git configuration was changed. The inaccessible
owner-global ignore file emitted warnings but produced no status entry.

The mandatory governance and research state, rejected dossier, affected
timeout test, production inspector, schema-validation interface, relevant
schema/test patterns, and cumulative Git history were inspected. This new
dossier was absent, as expected.

## Review correction

The rejected candidate's test redesign is statically sound. Its blocking
defect is evidentiary: the claimed 25 consecutive focused runs and two
consecutive complete suites exist only as Markdown transcription. No raw
output, JUnit result, machine-readable run bundle, CI artifact, or equivalent
independently checkable record was committed.

The accepted baseline therefore remains
`a7066e70b92d80be2d1772127f329c24222c1b41`. The next review is cumulative
from that baseline through this correction; the candidate SHA is intentionally
resolved from Git by the reviewer. The rejected dossier is immutable
historical evidence and is not edited or reused.

## Authorized scope

Only these paths may change:

- `schemas/inspector-timeout-stability-evidence.schema.json`
- `tools/run_inspector_timeout_stability.py`
- `tools/verify_inspector_timeout_stability.py`
- `tools/validate_schemas.py`
- `tests/unit/test_inspector_timeout_stability_evidence.py`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260719__make_inspector_stability_evidence_auditable/TASK_STATUS.md`
- `ops/TASK-20260719__make_inspector_stability_evidence_auditable/TASK_LOG.md`
- `ops/TASK-20260719__make_inspector_stability_evidence_auditable/EVIDENCE.md`
- `ops/TASK-20260719__make_inspector_stability_evidence_auditable/STABILITY_EVIDENCE.json`

Every other path is protected. In particular, the rejected dossier, production
inspector, stabilized timeout-test file, workflows, environment-boundary
artifacts, build/dependency inputs, verifier, upstream snapshot, claims,
pruning, manifests, certificates, and benchmarks must remain byte-identical.

## Implemented evidence design

- A strict recursively closed-world JSON Schema constrains the report.
- The standard-library runner implements exactly 25 focused runs followed
  immediately by two complete suites, with distinct task-owned basetemps,
  serial execution, no retry, and stop-on-first-failure behavior.
- The runner preserves a partial canonical report after each completed attempt
  and retains complete stdout and stderr bytes with Base64, sizes, and SHA-256.
- The independent verifier does not import the runner. It recomputes schema,
  canonical serialization, source and stream hashes, ordering, counts,
  completion, cleanup, and limitation requirements. Core verification is
  portable; opt-in `--rehash-environment` also binds the report to the local
  Python and four recorded tool files.
- Focused unit tests use fake subprocesses and temporary fixtures; they do not
  perform the 27 real pytest subprocesses.
- `STABILITY_EVIDENCE.json`, not a Markdown table, is the canonical execution
  record. Markdown summarizes rather than duplicates its 27 run records.

## Verification state

The one and only actual runner invocation exited zero. It began at
`2026-07-19T13:31:35.919158Z` and finished at
`2026-07-19T13:37:40.838505Z`. All 27 required attempts passed in order: the 25
focused attempts each reported 31 passes, and the two complete suites each
reported 333 passes. Failed, error, skipped, xfailed, and xpassed counts are
all zero; the runner made zero retries. Cleanup removed 27 basetemps, reported
zero remaining paths, and left no task-owned basetemp root.

The canonical 93,644-byte report has SHA-256
`b370e24312b69423c757a69368860f0316added6f86af4c9c7fe7fddc9c484f1`.
Its 170-file execution-source fingerprint is
`415ef1d6ab427a28f5c437371364f181fc3a489f228b2b87cbba80887400f26a`.
The independent verifier with `--rehash-environment` exited zero and returned
the same report hash, source fingerprint, and run counts.

Strict report-instance and all-schema validation pass. The final focused
tooling command passes 34 tests, and the final all-unit command passes 318.
Action-pin validation reports 11 immutable references in two workflows;
upstream-snapshot verification reports 10 of 10 files. Strict review-state
parsing, empty-index inspection, protected-file equality, source/tool
rehashing, cleanup inspection, and `git diff --check` also pass. The actual 11
changed paths are all authorized. The 164-file protected inventory exactly
matches its startup 17,827-byte serialization and SHA-256
`7ac977493f2f6058e8fd190a36b84ce707ea398ec8787fc815fbab469c7af1ce`.

Development-only harness checks before the actual execution encountered a
60-second shell timeout/OSError, an invalid inherited Windows stdin handle,
and sandbox denial of pytest's default user temporary directory. `DEVNULL`
made subprocess stdin explicit, and the required exact pytest gates ran
outside the sandbox. These were not evidence attempts. The actual report has
no failure, interruption, partial-failure record, or retry.

Final post-edit complete-diff, exact-allowlist, protected-inventory, text
hygiene, and `git diff --check` inspections pass. The task is
`READY_FOR_REVIEW`.

## Claim boundary and limitations

This task can produce only bounded V1 engineering-test evidence classified as
`EMPIRICAL_OBSERVATION`. It cannot establish an upstream reproduction,
exhaustive search, certificate, theorem, proof, counterexample, mathematical
claim, or pruning result.

`RFU-TEST-001` remains `OPEN` until independent cumulative review.
`RFU-ENV-001` remains separately `OPEN` and unchanged. No environment
attestation begins, `RS-001` remains `NOT STARTED`, and claims and pruning
remain protected.

## Current status

`READY_FOR_REVIEW`
