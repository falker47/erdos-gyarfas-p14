# TASK-20260717__bind_heavy_workflow_task_identity — Status

- Mode: STRICT
- Objective: bind the manual heavy-workflow scaffold manifest task identity to
  `REVIEW_STATE.yaml:active_task_id`, require the matching dossier, and record
  checkout-derived provenance without enabling any search.
- Repository: `falker47/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `0d08a58d87e7aaa5749ed2d3428cc0906a6bade6`
- Task-start HEAD: `0d08a58d87e7aaa5749ed2d3428cc0906a6bade6`
- Previous verdict: `ACCEPT WITH FOLLOW-UP`
- Previous accepted task:
  `TASK-20260717__harden_surprising_outcome_preservation`
- Follow-up addressed: `RFU-WORKFLOW-001` (`OPEN` pending review)
- Status: `READY_FOR_REVIEW`

## Scope and claim boundary

Only the prompt allowlist may change. The manual workflow remains
`scaffold-only`, non-certifying, and incapable of invoking a P13/P14 search.
No mathematical claim, pruning rule, upstream source, schema, template, fast
CI behavior, or earlier dossier changes in this task.

## Implemented result

- Added a deterministic read-only strict-JSON resolver for
  `REVIEW_STATE.yaml:active_task_id` with duplicate-key, non-finite-number,
  schema, canonical-ID, root-containment, and dossier-file checks.
- The manual workflow exports only the resolver output as
  `RESOLVED_TASK_ID`, passes it to `--task-id`, and records the canonical
  source/path plus checkout-computed SHA-256 hashes of review state and task
  status.
- Resolver failure is fatal before manifest creation; there is no fallback or
  manual task-identity input.
- The workflow remains manual, `scaffold-only`, `ENGINEERING_ASSUMPTION`, and
  refuses P13/P14 or certifying requests. It invokes no search executable.

## Exact changed-file allowlist

- `.github/workflows/heavy-search.yml`
- `tools/resolve_review_task_id.py`
- `tests/unit/test_review_task_id.py`
- `docs/CI.md`
- `research/REPRODUCIBILITY.md`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260717__bind_heavy_workflow_task_identity/TASK_STATUS.md`
- `ops/TASK-20260717__bind_heavy_workflow_task_identity/TASK_LOG.md`
- `ops/TASK-20260717__bind_heavy_workflow_task_identity/EVIDENCE.md`

## Verification and limitations

All required validators and focused/bounded/full tests pass; the recovery-final
full suite reports 162 passed with no skips. Static checks establish workflow text
and ordering, not hosted GitHub Actions behavior. GitHub runner execution,
artifact upload, action immutability, and complete environment locking remain
unobserved or open. Schema/hash checks do not prove run semantics.

`RFU-WORKFLOW-001` remains `OPEN` pending review. `RFU-CI-003`,
`RFU-SUPPLY-001`, and `RFU-ENV-001` remain unchanged and `OPEN`.
`RFU-CI-001` and `RFU-CI-002` were removed only because the prior accepted
task resolved them.

No claim is added, upgraded, downgraded, or used as support. `RS-001` remains
`NOT STARTED`; there is no search, reproduction, counterexample, certificate,
pruning change, or mathematical result.

The candidate SHA is intentionally resolved from Git by the reviewer.

## Final status

`READY_FOR_REVIEW`
