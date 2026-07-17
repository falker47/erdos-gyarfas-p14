# TASK-20260717__repair_postcommit_review_state — Status

- Mode: STRICT
- Objective: repair the post-commit review-state inconsistency left after the
  cumulative candidate ending at
  `5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf` received verdict `REJECT`, using
  canonical wording that remains true before and after the user's manual
  commit.
- Repository: `falker47/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `164d6756fd2f6725f2de0bedbe13f1e8c444ba0c`
- Task-start HEAD: `5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf`
- Previous reviewed HEAD: `5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf`
- Previous verdict: `REJECT`
- Next review range: cumulative from the unchanged accepted baseline through
  the corrective candidate HEAD resolved by the reviewer from Git.
- Status: `READY_FOR_REVIEW`

## Exact allowed scope

Only these eight paths may change:

- `AGENTS.md`
- `CHATGPT_REVIEW_PROTOCOL.md`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md`
- `ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md`
- `ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md`

No workflow, code, test, schema, Docker, dependency, upstream, benchmark,
experiment, manifest, certificate, search, pruning, mathematical-claim,
claim-registry, prior-dossier, decision-log, or research-log change is
authorized.

## Exact files changed

- `AGENTS.md`
- `CHATGPT_REVIEW_PROTOCOL.md`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md`
- `ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md`
- `ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md`

## Finding and correction

The preceding correction stored “uncommitted correction” in canonical current
state. That description became false when the user created commit
`5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf`. The new policy requires
commit-neutral canonical wording: a corrective candidate remains a candidate
before and after manual commit, and its SHA is intentionally resolved from Git
by the reviewer. Historical dossier chronology may state that a SHA was
unavailable at execution time, but may not present that fact as current
repository state.

## Review state and follow-ups

Both accepted-baseline fields remain
`164d6756fd2f6725f2de0bedbe13f1e8c444ba0c`. The last reviewed candidate is
`5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf`, its verdict is `REJECT`, the
accepted task remains `TASK-20260715__bootstrap_reproducible_baseline`, and
the active task is `TASK-20260717__repair_postcommit_review_state`.

All six prior follow-ups remain unchanged and `OPEN`:

- `RFU-CI-001`
- `RFU-CI-002`
- `RFU-WORKFLOW-001`
- `RFU-CI-003`
- `RFU-SUPPLY-001`
- `RFU-ENV-001`

`RFU-CI-001`, `RFU-CI-002`, and `RS-001` are not started.

## Claim impact and limitations

This correction is a governance `DECISION` only. It produces no mathematical,
CI, benchmark, reproduction, experiment, manifest, certificate, search,
pruning, or bounded graph-predicate evidence. No claim statement, status, or
evidence classification changes, and `research/CLAIMS_REGISTRY.yaml` remains
unchanged.

Required local validators, 59 tests, cumulative Git inspections, preservation
checks, and the exact reproducible ten-assertion audit pass. Hosted GitHub
Actions, Docker, benchmarks, reproductions, searches, pruning analysis,
manifest/certificate execution, and mathematical verification were unavailable
or outside scope and are not represented as evidence.

The first compact audit run reported 9/10 because its reading-order extraction
also counted post-list protocol examples. The failure is preserved in
`EVIDENCE.md`; correcting the non-committed audit boundary produced 10/10
without any repository-content correction. No new engineering risk is known
inside this documentation-only change. The six pre-existing technical
follow-ups remain unresolved.

## Next atomic task

Only after this corrective candidate is accepted, prepare one separate bounded
engineering task for `RFU-CI-001` and `RFU-CI-002`. No part of that task is
started here.
