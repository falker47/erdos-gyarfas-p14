# TASK-20260717__harden_surprising_outcome_preservation — Status

- Mode: STRICT
- Objective: harden the rejected process-outcome candidate so surprising tiny
  stdout/stderr are frozen before inspection, exit-100 inspection is bounded
  in a separate process, complete CI artifacts survive failure, and the
  original producer failure remains visible.
- Repository: `falker47/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `f8271e74509a017d1631dea72aaa652f44d8c3df`
- Task-start HEAD: `be179265919566b44d40cb1e472cd3db50811502`
- Rejected candidate: `be179265919566b44d40cb1e472cd3db50811502`
- Previous verdict: `REJECT`
- Next review range:
  `f8271e74509a017d1631dea72aaa652f44d8c3df..HEAD`
- Status: `READY_FOR_REVIEW`

## Scope boundary

The task changes only the authorized CI workflow, tiny-integration and
benchmark-preservation code/tests, one new inspector, one new schema,
documentation, current review state, research priority, and this new dossier.
It does not modify the preserved upstream snapshot, graph predicates, claims
registry, pruning registry, heavy workflow, prior dossiers, or mathematical
semantics.

## Implemented correction

- Every nonordinary tiny outcome writes byte-exact stdout and stderr, closes
  both files, hashes the files, and writes a deterministic schema-valid
  `EMPIRICAL_OBSERVATION` outcome record before decoding, graph construction,
  path search, or cycle search.
- Exit `100` launches a direct Python child with binary pipes and an autonomous
  finite timeout. The parent kills, drains, and waits for that child on
  timeout, then writes a separate `completed`, `timeout`, or `error` record.
- The parent pins the outcome-record hash before launch, rechecks the record
  and both raw streams after termination, owns all source-bound envelope
  fields, rejects incomplete/duplicate/non-finite child JSON, and validates the
  final inspection record before its exclusive write.
- Every exit-100 disposition still fails the ordinary integration test. A
  candidate passing every predicate remains only a frozen surprising
  observation for a separate task.
- The benchmark runner freezes stdout/stderr immediately after execution and
  before outcome matching or result construction, without changing its public
  `0/3/1` status contract.
- CI runs result validation, upstream inventory, and hygiene checks after
  producer failure and uploads the complete tiny and benchmark directories
  with compiler/run/attempt-qualified names. No status suppression is used.

## Exact files in the corrective candidate

- `.github/workflows/ci.yml`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `docs/CI.md`
- `research/REPRODUCIBILITY.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `schemas/surprising-process-outcome.schema.json`
- `tests/integration/test_upstream_build.py`
- `tests/unit/test_benchmark_outcomes.py`
- `tests/unit/test_upstream_candidate_inspection.py`
- `tools/run_benchmark.py`
- `tools/inspect_upstream_candidate.py`
- `ops/TASK-20260717__harden_surprising_outcome_preservation/TASK_STATUS.md`
- `ops/TASK-20260717__harden_surprising_outcome_preservation/TASK_LOG.md`
- `ops/TASK-20260717__harden_surprising_outcome_preservation/EVIDENCE.md`

## Claim boundary and limitations

All new records are `EMPIRICAL_OBSERVATION`; no claim is added or upgraded.
`RS-001` remains `NOT STARTED`. No P13/P14 run, upstream reproduction,
counterexample acceptance, proof, exhaustive search, certificate, pruning
change, or new mathematical result is part of this task.

The hosted GitHub Actions job and artifact service were not observed locally.
Job cancellation, runner loss, whole-job timeout, or artifact-service failure
can still prevent upload. The direct-child timeout reaps the inspector process;
it is not a general descendant-process containment mechanism. Action references
remain major-version tags because `RFU-SUPPLY-001` is out of scope and `OPEN`.

## Next atomic task

After cumulative review and acceptance only, address `RFU-WORKFLOW-001` in a
separate task by removing the bootstrap task ID hardcoded in the manual heavy
workflow, without starting research or altering claims. No part of that task
is begun here.
