# DECISION_LOG

Append-only decision register.

A decision may be `PROPOSED`, `ACCEPTED`, `SUPERSEDED`, or `REJECTED`.
A superseding decision must identify the earlier decision explicitly.

## D-001 — Repository as durable memory

- Date: 2026-07-15
- Status: ACCEPTED
- Decision:
  repository files, manifests, and task dossiers are authoritative; chat
  history is not.
- Rationale:
  the workflow must survive new chats, context truncation, and model changes.
- Consequence:
  every material result and decision must be promoted to a canonical file.

## D-002 — One task and one dossier per atomic commit

- Date: 2026-07-15
- Status: ACCEPTED
- Decision:
  each Codex task prepares one coherent commit and receives a distinct dossier.
- Rationale:
  this preserves reviewability and prevents a dossier from changing purpose.
- Consequence:
  corrections and errata use new task IDs.

## D-003 — Preserve an exact upstream snapshot

- Date: 2026-07-15
- Status: ACCEPTED
- Decision:
  copy or vendor one exact upstream main commit under `third_party/` and record
  its provenance and hashes.
- Rationale:
  a moving remote branch is not a reproducible dependency.
- Consequence:
  the snapshot is read-only; local changes are separate patches or new code.

## D-004 — Separate generator and verifier

- Date: 2026-07-15
- Status: ACCEPTED
- Decision:
  search generation and independent verification use separate implementations
  for critical graph predicates and certificate checking.
- Rationale:
  shared bugs must not automatically validate their own outputs.
- Consequence:
  test-only brute-force reference implementations are intentionally simple.

## D-005 — No unproved certifying pruning

- Date: 2026-07-15
- Status: ACCEPTED
- Decision:
  a pruning rule enters a certifying run only after a correctness proof is
  recorded and reviewed.
- Rationale:
  an unsound pruning rule invalidates exhaustive-search conclusions.
- Consequence:
  experimental pruning runs are labeled heuristic and cannot support a proof.

## D-006 — Machine-readable run truth

- Date: 2026-07-15
- Status: ACCEPTED
- Decision:
  every material run emits a schema-validated manifest and hashes its outputs.
- Rationale:
  prose logs are insufficient for partition coverage and independent replay.
- Consequence:
  benchmark, search, interruption, and failure states are all serialized.

## D-007 — Fast CI and separate heavy execution

- Date: 2026-07-15
- Status: ACCEPTED
- Decision:
  ordinary CI covers builds, small tests, differential checks, schema checks,
  and tiny upstream cases; heavy searches require manual dispatch.
- Rationale:
  pull-request CI must remain reliable and bounded.
- Consequence:
  heavy workflows upload manifests and partial artifacts even when interrupted.

## D-008 — Initial implementation languages

- Date: 2026-07-15
- Status: ACCEPTED
- Decision:
  preserve C++17 for the upstream baseline and use Python 3.11 or newer for the
  first independent verifier and orchestration.
- Rationale:
  this minimizes semantic changes to upstream while favoring clarity in the
  independent checker.
- Consequence:
  later performance rewrites require differential equivalence evidence.