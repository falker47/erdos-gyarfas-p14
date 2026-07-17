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

## 2026-07-17 — Bootstrap baseline accepted with follow-up

- The user accepted `TASK-20260715__bootstrap_reproducible_baseline` at commit
  `164d6756fd2f6725f2de0bedbe13f1e8c444ba0c` with verdict
  `ACCEPT WITH FOLLOW-UP`.
- The accepted scope remains an engineering baseline plus the recorded
  `VERIFIED_BOUNDED_COMPUTATION`; no mathematical target advanced.
- Open CI, workflow provenance, action-pinning, and environment-locking items
  remain follow-ups and do not become accepted evidence implicitly.
