# TASK-20260717__enforce_process_outcome_semantics — Status

- Mode: STRICT
- Objective: enforce exact child-process outcome contracts for the known tiny
  upstream integration cases and the benchmark runner, addressing
  `RFU-CI-001` and `RFU-CI-002` as one bounded engineering change.
- Repository: `falker47/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `f8271e74509a017d1631dea72aaa652f44d8c3df`
- Task-start HEAD: `f8271e74509a017d1631dea72aaa652f44d8c3df`
- Preceding verdict: `ACCEPT WITH FOLLOW-UP`
- Accepted task: `TASK-20260717__repair_postcommit_review_state`
- Status: `READY_FOR_REVIEW`

## Scope boundary

This task changes only the authorized CI, tiny-integration, benchmark-case,
benchmark-runner, benchmark-result-schema, documentation, persistent-state,
and new-dossier paths. It does not modify the upstream snapshot, verifier
implementation, graph predicates, pruning, search semantics, heavy workflow,
claims registry, prior dossiers, or any mathematical claim.

The result classification remains `EMPIRICAL_OBSERVATION`. An exit-100 graph
is a surprising candidate requiring separate freeze-and-verify work; it is
never accepted as ordinary smoke completion or certified by this task.

## Review follow-ups

The candidate addresses `RFU-CI-001` and `RFU-CI-002`, but both follow-ups
remain `OPEN` pending review and acceptance. The four medium follow-ups remain
untouched. `RS-001` remains `NOT STARTED`.

## Exact files changed

- `.github/workflows/ci.yml`
- `tests/integration/test_upstream_build.py`
- `tests/unit/test_benchmark_outcomes.py`
- `tools/run_benchmark.py`
- `benchmarks/cases/upstream-small-k.json`
- `schemas/benchmark-result.schema.json`
- `docs/CI.md`
- `research/REPRODUCIBILITY.md`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260717__enforce_process_outcome_semantics/TASK_STATUS.md`
- `ops/TASK-20260717__enforce_process_outcome_semantics/TASK_LOG.md`
- `ops/TASK-20260717__enforce_process_outcome_semantics/EVIDENCE.md`

No other tracked or untracked path is part of the candidate.

## Implemented outcome contract

- Known tiny `k=3` and `k=4` integration runs require exactly
  `(termination_reason="exited", exit_code=0)`.
- Exit `100` is parsed by a strict project-authored adjacency adapter and
  checked with `egverify.graph.Graph` plus independent verifier predicates.
  Exact captured stream bytes are recoverable from base64 and SHA-256 in the
  failure diagnostic. Parsing failure, predicate failure, and all-predicate
  success each fail ordinary completion.
- Every benchmark case requires a nonempty array of exact accepted outcome
  pairs. Compatibility, unknown fields, duplicate pairs, deterministic order,
  and type-exact matching are enforced without Cartesian-product lists.
- Results record normalized accepted pairs, actual reason/code, and
  `outcome_accepted`, while retaining classification
  `EMPIRICAL_OBSERVATION`.
- Runner status `0` means exact acceptance, status `3` means an attempted but
  unaccepted child outcome with validated artifacts preserved, and status `1`
  means configuration, schema, or artifact failure.
- CI lets the runner fail directly, validates the result under `always()`, and
  emits bounded, hashed stream diagnostics under `failure()` without masking
  the original status.

## Verification summary

- JSON state parsing, all five schemas, and the 10/10 upstream inventory pass.
- Required bounded verifier suite: 94 passed.
- Focused benchmark-outcome suite: 35 passed.
- Upstream build/integration suite with explicit MSYS2 tools: 17 passed.
- Complete suite: 111 passed.
- Release configure/build and the real benchmark case pass.
- Direct real tiny outcomes were `(exited, 0)` for both `k=3` and `k=4`, with
  nonempty stdout and empty stderr; no exit-100 or verifier disagreement
  occurred.
- Final benchmark accepted and actual pairs were both `(exited, 0)` and
  `outcome_accepted` was true. The schema-valid result/stdout/stderr hashes are
  recorded in `EV-006`, and all three generated files were removed afterward.
- Exact allowed scope, cumulative whitespace, untracked UTF-8/newline checks,
  protected Git blobs, raw third-party bytes, and full-diff inspection pass.

## Claim impact, limitations, and risks

No claim is upgraded or added. `research/CLAIMS_REGISTRY.yaml` and
`research/PRUNING_REGISTRY.md` are preserved. These checks are bounded
engineering evidence, not an upstream reproduction, exhaustive search,
certificate, counterexample acceptance, or proof.

The exit-100 predicate path is covered synthetically; no real exit-100 event
occurred. Independent induced-path and cycle checking is deliberately
exponential and intended only for surprising small candidates. JSON Schema
cannot express dynamic membership of the actual pair in `accepted_outcomes`;
the runner and tests enforce that semantic relation. Hosted GitHub Actions and
Docker were unavailable and are not represented as passed. The four medium
follow-ups remain open, including action pinning and environment locking.

## Next atomic task

After this candidate is reviewed and accepted, address only
`RFU-WORKFLOW-001` by removing the bootstrap task ID hardcoded in the manual
heavy-workflow manifest path, with no research run or claim change. No part of
that task is begun here.
