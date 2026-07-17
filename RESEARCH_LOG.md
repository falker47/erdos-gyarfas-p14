# RESEARCH_LOG

Append-only global research chronology.

This file records only high-level milestones. Detailed commands, intermediate
reasoning, and evidence belong in task dossiers and machine-readable manifests.

## 2026-07-15 — Project design established

- Defined the primary target `EG-P14`.
- Defined the alternative counterexample target.
- Defined the intermediate target `EG-P13-C4C8`.
- Chose `ringmin-squared` as an operational reference only.
- Inspected the upstream Hegde–Sandeep–Shashank implementation and associated
  paper.
- Identified the initial sequence:
  bootstrap, upstream reproduction, correctness audit, certificate design,
  semantics-preserving optimization, P14 execution, independent verification.
- No repository implementation, benchmark, search, certificate, or new
  mathematical result was produced.
- Next milestone:
  complete `TASK-20260715__bootstrap_reproducible_baseline`.

## 2026-07-17 — Reproducible bootstrap baseline prepared

- Preserved and content-addressed the exact resolved upstream `main` snapshot.
- Established original Make and project CMake build checks, an independent
  small-graph verifier, bounded differential tests, schemas, benchmark
  infrastructure, fast CI, and a manual non-certifying workflow scaffold.
- Local verification passed 63 tests; the exact differential domain is 1,100
  labelled graphs of orders 0 through 5.
- Classification: engineering bootstrap plus `VERIFIED_BOUNDED_COMPUTATION`
  only; no theorem, counterexample, exhaustive search, reproduced published
  result, certifying pruning rule, or certificate was produced.
- Status: awaiting user review and manual commit.
