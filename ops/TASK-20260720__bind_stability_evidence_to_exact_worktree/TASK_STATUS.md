# TASK-20260720__bind_stability_evidence_to_exact_worktree - Status

- Mode: STRICT
- Objective: bind inspector timeout-test stability evidence to every tracked
  and untracked worktree input capable of affecting pytest, and to the exact
  observed test collection.
- Repository: `falker47/erdos-gyarfas-p14`
- Repository root:
  `C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `a7066e70b92d80be2d1772127f329c24222c1b41`
- Task-start HEAD: `b1eb792a2a771485f37979cd932303f14ab52f56`
- Previous verdict: `REJECT`
- Active follow-up: `RFU-TEST-001` (`MEDIUM`, `OPEN`)
- Preserved follow-up: `RFU-ENV-001` (`MEDIUM`, `OPEN`, unchanged)
- Governance state-write time: `2026-07-20T07:50:03Z`
- Status: `BLOCKED`

## Startup gate

The exact root and origin, branch `main`, task-start HEAD, accepted baseline,
ancestry, empty worktree, and empty index matched the mandatory gate before
modification. Plain Git first rejected sandbox ownership; all successful Git
reads use only process-local `-c safe.directory=...`. No Git configuration was
changed.

All required governance, research, schema, runner, verifier, test, workflow,
validator, earlier-dossier, report, cumulative-diff, and Git-history inputs
were inspected before modification. This dossier was initially absent.

## Authorized scope

Only the paths named in the task prompt may change. The v1 schema, both earlier
dossiers and report, production inspector and timeout test, workflows,
environment-boundary files, claims, pruning, upstream snapshot, mathematical
tools, manifests, certificates, and benchmarks are protected.

## Execution rule

The task permits one real v2 runner invocation only after implementation,
synthetic tests, schema validation, finalized governance, finalized allowlist,
and absence of unexpected files. A failed or interrupted real invocation makes
the task `BLOCKED` and cannot be retried.

## Claim boundary

The strongest possible result is bounded V1 engineering-test evidence
classified as `EMPIRICAL_OBSERVATION`. No mathematical implication, upstream
reproduction, exhaustive search, certificate, theorem, proof, counterexample,
or pruning result can follow.

## Current status

`BLOCKED`

Implementation and synthetic verification are complete, but the single
permitted real runner invocation failed before the first collection subprocess.
The fail-closed Git ignored-path probe exited `0` but emitted 792 bytes of
permission-denied warnings for nine pre-existing ignored `build/pytest-*`
directories. The runner rejected that stderr, recorded zero subprocesses and
zero stability runs, atomically preserved a canonical partial report, and
completed its task-owned cleanup.

The report is schema-valid and the independent verifier accepts it only with
`--allow-partial --rehash-environment`, returning `completed=false` and
`evidence_success=false`. The normal completed-evidence verification correctly
fails. The task rule forbids a second runner invocation, so this task cannot
reach `READY_FOR_REVIEW` or produce the requested 25-plus-2 evidence.

No source, worktree, or collection digest and no focused or full-suite count
were established by the partial execution. `RFU-TEST-001` remains `OPEN`;
`RFU-ENV-001` remains unchanged and `OPEN`. No mathematical claim follows.
