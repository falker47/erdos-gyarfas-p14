# Certified Erdős–Gyárfás P14 Research

Repository: `erdos-gyarfas-p14`

This project develops a reproducible, independently reviewable computational
study of the Erdős–Gyárfás conjecture for graphs without long induced paths.
Repository files—not chat history—are durable project memory.

## Targets

- Primary open target `EG-P14`: every finite simple P14-free graph of minimum
  degree at least 3 contains a simple cycle whose length is a power of 2.
- Alternative target `CE-P14`: produce and independently verify a
  counterexample.
- Intermediate open target `EG-P13-C4C8`: every finite simple P13-free graph of
  minimum degree at least 3 contains C4 or C8.

`P_t` has `t` vertices and must occur as an induced path. Cycles are simple but
need not be induced. The general target forbids lengths 4, 8, 16, …; the
intermediate target asks only for C4 or C8.

## Current claim boundary

The repository currently makes no new theorem claim. The published P13-free
power-of-two result and P12-free C4/C8 result are external computational
results. Local bootstrap builds, smoke executions, fixtures, and bounded
differential tests do not prove search completeness. No pruning rule and no
search-certificate design is certifying at bootstrap.

## Workflow

ChatGPT acts as scientific reviewer/orchestrator, Codex executes one atomic
repository task, and the user reviews and commits manually. Each task has one
dossier. Heavy searches are separate from ordinary CI and require exact
machine-readable manifests.

## Canonical reading order

1. `AGENTS.md`
2. `start.md`
3. `CHATGPT_REVIEW_PROTOCOL.md`
4. `REVIEW_STATE.yaml`
5. `CURRENT_STATUS.md`
6. `PROJECT_KNOWLEDGE.md`
7. `research/PROBLEM_STATEMENT.md`
8. `research/KNOWN_RESULTS.md`
9. `research/VERIFICATION_PROTOCOL.md`
10. `research/CLAIMS_REGISTRY.yaml`
11. `research/PRUNING_REGISTRY.md`
12. `research/NEXT_RESEARCH_STEPS.md`
13. the current task dossier under `ops/`
14. the latest relevant earlier dossiers
15. affected workflows, tests, manifests, certificates, benchmarks, artifacts,
    implementation files, and Git history

## Initial phases

1. Bootstrap provenance, builds, verifier, schemas, tests, and CI.
2. Reproduce bounded upstream cases under recorded conditions.
3. Audit the mathematical invariant, implementation, and pruning rules.
4. Design and prove deterministic partition/certificate semantics.
5. Engineer and rehearse a certifying search without semantic drift.
6. Execute, preserve, and independently verify all required work.

## External references

- Hegde, Sandeep, Shashank, arXiv:2410.22842v2.
- Hu and Shen, *Discrete Mathematics* 347(12), 114175, 2024;
  arXiv:2308.05675.
- Gao and Shan, *Graphs and Combinatorics* 38, 168, 2022;
  arXiv:2109.01277.
- Erdős, *Discrete Mathematics* 165–166, 227–231, 1997.
- Upstream source: `https://github.com/rbsandeep/Erdos-Gyarfas`.
- Operational reference only: `https://github.com/falker47/ringmin-squared`.

Full bibliographic records and verification boundaries are in
`research/BIBLIOGRAPHY.md` and `research/KNOWN_RESULTS.md`.
