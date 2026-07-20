# Next Research Steps

This file contains open work and priority only.

It must not duplicate known results or task histories.

## Current priority

### RS-000 — Bootstrap reproducible baseline

Status: COMPLETED and accepted with `ACCEPT WITH FOLLOW-UP` at commit
`164d6756fd2f6725f2de0bedbe13f1e8c444ba0c`.

Objectives:

- initialize repository structure;
- preserve exact upstream main snapshot;
- resolve and record upstream refs;
- retain upstream license;
- add reproducible C++ build;
- add independent Python graph verifier;
- add unit, differential, and integration tests;
- add machine-readable schemas;
- add benchmark runner without invented results;
- add fast CI and manual heavy workflow;
- create the first task dossier;
- state all unverified claims explicitly.

Completion does not imply mathematical reproduction.

### RFU-TEST-001 - Make inspector stability evidence auditable

Status: `OPEN`; the corrective task is `READY_FOR_REVIEW`.

`TASK-20260719__define_environment_trust_boundary` remains accepted with
`ACCEPT WITH FOLLOW-UP` at exact commit
`a7066e70b92d80be2d1772127f329c24222c1b41`. The timeout-test stabilization
candidate at `c71d66995ae6a36620a2aa8f938faf6d84fe1af7` received `REJECT` at
`2026-07-19T11:58:09Z`, so the accepted baseline remains unchanged.

The rejected implementation separated controlled freeze-order verification
from deterministic timeout/kill/drain/reap coverage. Its central repeated-run
claim, however, was recorded only as Markdown transcription: the repository
contained no raw output, JUnit result, machine-readable run bundle, CI
artifact, or equivalent independently checkable record for the stated 25
focused runs and two complete suites. The rejected dossier is immutable
historical evidence.

`TASK-20260719__make_inspector_stability_evidence_auditable` is the active
correction. It has created a strict evidence schema, a serial no-retry runner,
an independent verifier, focused tooling tests, and one canonical JSON report
containing exactly 25 focused executions followed by two complete-suite
executions. The single actual invocation completed all 27 attempts: every
focused attempt reported 31 passes and both complete suites reported 333
passes, with no failed attempt, non-passing outcome, or retry. The independent
verifier passed with same-host source and tool rehashing. Markdown summarizes
the report but does not duplicate its 27 run records. Final post-edit
complete-diff, allowlist, protected-inventory, and whitespace inspections pass,
so the corrective task is `READY_FOR_REVIEW`. The next review remains
cumulative from `a7066e70b92d80be2d1772127f329c24222c1b41`; the candidate
SHA is intentionally resolved from Git by the reviewer.

`RFU-TEST-001` remains `OPEN` until the cumulative candidate and its
machine-readable evidence receive independent review. This work changes no
production inspector behavior and has no mathematical implication.

### Subsequent RFU-ENV-001 work

`RFU-ENV-001` remains `OPEN` and unchanged. A later atomic task may implement
or attest the locking, capture, and external-service controls catalogued in
`research/ENVIRONMENT_LOCK_INVENTORY.json` and interpreted by
`research/ENVIRONMENT_TRUST_BOUNDARY.md`. The current evidence-audit correction
does not begin that work.

`RS-001` remains `NOT STARTED`. Neither this evidence-audit correction nor
environment specification starts an upstream reproduction or mathematical
research task, and neither has a mathematical implication.

## Planned sequence

### RS-001 — Reproduce tiny upstream cases

Status: NOT STARTED. Do not execute as part of the current inspector
stability-evidence correction; starting `RS-001` requires a separate reviewed
task after its environment prerequisites are explicitly addressed.

Run the preserved baseline for small `k`, beginning with values that complete
quickly.

Record:

- command;
- environment;
- output;
- exit status;
- wall and CPU time;
- peak memory where available;
- output hashes;
- manifest;
- comparison with upstream expectations.

Do not optimize.

### RS-002 — Audit independent graph predicates

Differentially compare:

- minimum degree;
- induced `P_k` detection;
- simple cycle detection;
- power-of-two-cycle detection;
- C4/C8 detection;

against deliberately simple brute-force implementations on all feasible small
labelled graphs and curated fixtures.

### RS-003 — Formalize the upstream search invariant

Write a self-contained proof of:

- why starting from `P_k` is sufficient;
- what a recursive state represents;
- why selecting the largest low-degree anchor preserves completeness;
- why every minimal counterexample follows at least one branch;
- why the safe-neighbor enumeration covers every compatible extension;
- why cycle-based edge pruning is monotone.

The proof must refer to the implemented state transitions exactly.

### RS-004 — Instrument without semantic change

Add deterministic counters and event records for:

- recursive states;
- candidate neighbor subsets;
- induced-path rejections;
- forbidden-cycle rejections;
- low-degree expansions;
- completed leaves;
- maximum vertex count;
- maximum recursion depth;
- memory statistics.

Compare instrumented and uninstrumented output on small cases.

### RS-005 — Define search partitioning

Choose deterministic partition boundaries.

Prove:

- partition disjointness;
- partition coverage;
- stable serialization;
- restart and checkpoint semantics.

Produce testable partition manifests.

### RS-006 — Define the certification format

Select a certificate model capable of supporting a negative result.

Candidate models include:

- complete replay traces;
- recursive subtree summaries with verifiable local witnesses;
- deterministic partition replay;
- Merkleized search trees;
- independently regenerable frontier plus leaf/pruning records.

The selected model must be accepted before a P14 certifying run.

### RS-007 — Reproduce published boundary cases

Attempt controlled reproduction of:

- the general search through `k = 13`;
- the C4/C8 variant through `k = 12`.

A reproduction report must separate:

- matching mathematical output;
- runtime agreement;
- implementation agreement;
- independent verification status.

### RS-008 — Profile and optimize

Only after the reference implementation and verifier are stable:

- profile runtime and memory;
- identify bottlenecks;
- propose one optimization per task;
- prove semantic preservation;
- compare against the reference on bounded cases;
- benchmark before and after;
- reject changes that alter explored-state digests unexpectedly.

### RS-009 — Execute the P14 search

Prerequisites:

- accepted invariant proof;
- accepted pruning registry;
- accepted partitioning;
- accepted certificate format;
- deterministic reference;
- independent verifier;
- successful smaller-case rehearsal;
- resource and checkpoint plan.

No P14 execution is certifying before these prerequisites.

### RS-010 — Study P13 C4/C8

After recovering or reconstructing the upstream C4/C8 mode:

- reproduce P12;
- certify the modified forbidden-cycle semantics;
- profile `k = 13`;
- execute only after the same certificate prerequisites.

## Explicitly deferred

- unrestricted Erdős–Gyárfás conjecture;
- non-path forbidden induced subgraphs;
- unverified GPU or distributed rewrites;
- heuristic pruning in certifying mode;
- publication claims;
- large runs without checkpoint and manifest support.
