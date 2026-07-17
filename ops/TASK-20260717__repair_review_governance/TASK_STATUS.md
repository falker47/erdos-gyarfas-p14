# TASK-20260717__repair_review_governance — Status

- Mode: STRICT
- Objective: repair the rejected cumulative-review governance implementation
  without beginning mathematical, CI, workflow, benchmark, environment, or
  claim work.
- Repository: `falker47/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `164d6756fd2f6725f2de0bedbe13f1e8c444ba0c`
- Task-start HEAD: `d7b28390482ca026aa6180728992fa2c0c816a60`
- Last reviewed candidate HEAD:
  `d7b28390482ca026aa6180728992fa2c0c816a60`
- Last verdict: `REJECT`
- Next review range: cumulative from the accepted review baseline through the
  candidate HEAD resolved by the reviewer from Git.
- Status: `READY_FOR_REVIEW`

## Scope

This task is a documentation-only governance `DECISION`. It corrects canonical
reading order, mandatory review output, revision terminology, persistent review
state, current research priority, and task-local evidence. The future
corrective commit SHA is not stored because it does not yet exist.

No mathematical claim, claim classification, pruning status, code, workflow,
test, schema, Docker definition, upstream snapshot, benchmark, manifest,
certificate, environment, reproduction, or search is changed or started.

## Blocking findings addressed

- `RGV-001`: all three canonical lists now contain the same twelve files in the
  required order, followed by current and earlier dossier inspection and the
  complete affected-material inspection tail.
- `RGV-002`: `CHATGPT_REVIEW_PROTOCOL.md` now requires exactly ten mandatory
  output categories in the contract order while retaining the existing stricter
  provenance, manifest, hash, pruning, independence, surprise, claim-boundary,
  and baseline-transition rules.
- `RGV-003`: persistent state now distinguishes the accepted review baseline,
  task-start HEAD, last reviewed rejected candidate, and future candidate HEAD
  resolved by the reviewer from Git.
- `RGV-004`: the rejected dossier remains immutable historical evidence. This
  new dossier records that its passing reading-order audit tested an incomplete
  checklist and supplies the corrected reproducible audit.

## Exact files changed

- `AGENTS.md`
- `start.md`
- `CHATGPT_REVIEW_PROTOCOL.md`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260717__repair_review_governance/TASK_STATUS.md`
- `ops/TASK-20260717__repair_review_governance/TASK_LOG.md`
- `ops/TASK-20260717__repair_review_governance/EVIDENCE.md`

## Review state and follow-ups

Both accepted-baseline fields remain
`164d6756fd2f6725f2de0bedbe13f1e8c444ba0c`. The last reviewed candidate is
`d7b28390482ca026aa6180728992fa2c0c816a60`, the verdict is `REJECT`, the
accepted task remains `TASK-20260715__bootstrap_reproducible_baseline`, and the
active task is `TASK-20260717__repair_review_governance`.

All six prior follow-ups remain open and unchanged:

- `RFU-CI-001`
- `RFU-CI-002`
- `RFU-WORKFLOW-001`
- `RFU-CI-003`
- `RFU-SUPPLY-001`
- `RFU-ENV-001`

## Claim impact

The correction is classified as a governance `DECISION`. No entry, status,
evidence classification, or mathematical statement in
`research/CLAIMS_REGISTRY.yaml` changes. Passing documentation and engineering
checks will not constitute mathematical verification.

## Verification and limitations

Required local verification completed successfully:

- the reproducible governance/state/scope audit passed all assertions after one
  detected and corrected line-wrap issue;
- `REVIEW_STATE.yaml` parsed as JSON;
- all five JSON Schemas validated;
- the preserved upstream inventory remained 10/10 with no changes;
- the required test suite passed 59 tests;
- cumulative whitespace, status, stat, task-local changed paths, raw rejected-
  dossier blobs, unchanged claim registry, and exact nine-path scope passed.

Hosted GitHub Actions, Docker, benchmarks, reproductions, searches, pruning
analysis, manifest or certificate execution, and mathematical verification
were unavailable or deliberately not run because they are outside this task.
No engineering risk is known within the documentation-only correction; the six
pre-existing technical follow-ups remain unresolved and outside its scope.

## Next atomic task

Only after this correction is accepted, prepare one separate bounded
engineering task for the high-severity outcome follow-ups `RFU-CI-001` and
`RFU-CI-002`. Do not begin it in this dossier.
