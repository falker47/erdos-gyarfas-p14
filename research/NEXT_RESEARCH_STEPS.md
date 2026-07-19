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

### Current immutable Action pinning candidate

`TASK-20260719__pin_github_actions_immutable_shas` is the active supply-chain
candidate. `TASK-20260718__support_multi_worktree_whitespace_check` is
accepted, and `dde4e6cbd06be8ebc8192097930f40b06cf2f9f6` is the accepted
review baseline. The next review is cumulative from that baseline through the
current candidate, whose SHA is intentionally resolved from Git by the
reviewer.

`RFU-CI-004` is resolved. This candidate addresses `RFU-SUPPLY-001` by pinning
the already-used checkout v4, setup-python v5, and upload-artifact v4 releases
to verified full commit SHAs without a major upgrade. A deterministic
repository-local validator scans every workflow and rejects mutable, dynamic,
short, uppercase, Docker-tagged, or ambiguous external `uses:` forms. The
control does not freeze hosted runner images or package installations and does
not enable a search or change mathematical semantics.

The two remaining follow-ups are `OPEN`:

- `RFU-SUPPLY-001`: immutable action references, pending review of this
  candidate;
- `RFU-ENV-001`: complete environment and system-package locking.

`RS-001` remains `NOT STARTED`; no upstream reproduction or mathematical
research result is part of this supply-chain correction.

## Planned sequence

### RS-001 — Reproduce tiny upstream cases

Status: NOT STARTED. Do not execute before the current supply-chain candidate
is reviewed and accepted and applicable follow-ups are explicitly accounted
for.

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
