# TASK-20260720__bind_stability_evidence_to_exact_worktree - Log

Append-only task chronology. Times are UTC when shown.

## 2026-07-20T07:50:03Z - Startup gate and mandatory inspection

- Plain Git first reported dubious ownership. Successful read-only Git commands
  used only process-local `safe.directory`; no Git configuration changed.
- Resolved the required repository and origin, branch `main`, exact HEAD
  `b1eb792a2a771485f37979cd932303f14ab52f56`, accepted baseline
  `a7066e70b92d80be2d1772127f329c24222c1b41`, successful ancestry, empty
  worktree, and empty index.
- Read every mandatory file in order, both complete earlier dossiers including
  the v1 JSON report, affected workflows and validators, and the cumulative
  baseline-to-HEAD diff and history.
- Recorded the protected inventory and named protected hashes in `EVIDENCE.md`.

## 2026-07-20T07:50:03Z - Rejected-review governance transition

- Kept both accepted-baseline fields and `review_base_commit` fixed at
  `a7066e70b92d80be2d1772127f329c24222c1b41`.
- Recorded last reviewed HEAD
  `b1eb792a2a771485f37979cd932303f14ab52f56`, verdict `REJECT`, and this task
  as active using the actual state-write timestamp.
- Retained `RFU-TEST-001` as `OPEN` and retained the full `RFU-ENV-001` object
  unchanged and `OPEN`.
- Created this dossier at `IN_PROGRESS`. No v2 report or execution result is
  claimed by this initialization.

## 2026-07-20T09:32:09Z - V2 implementation and pre-run verification

- Replaced the v1-oriented runner and verifier behavior with a recursively
  closed v2 evidence contract while leaving the v1 schema and rejected v1
  bundle unchanged.
- Added raw Base64-preserved NUL-delimited Git probes, independently normalized
  worktree records, exact allowlisting and path classification, complete
  execution-input fingerprinting, exact pytest collection identity, guarded
  serial execution, atomic partial reports, and identity-bound cleanup.
- Kept the verifier implementation independent of the runner and added
  same-host Python, Git, source, and native-tool rehashing.
- Added 51 synthetic tests covering every required positive and negative
  family without invoking the real 25-plus-2 plan.
- The focused synthetic suite passed with 51 tests and the complete unit suite
  passed with 335 tests. Schema, task-ID, Action-pin, and upstream-snapshot
  validators passed. A first sandboxed focused-test attempt failed during
  pytest temporary-directory setup; the required exact suite was then run
  outside that filesystem restriction and passed. This was not a v2 runner
  invocation.
- Removed only positively identified task-development basetemps and restored
  the pre-task ignored-path population. The one permitted real v2 runner
  invocation remains unstarted at this point.

## 2026-07-20T09:44:04Z - Independent audit correction and repeated gates

- A read-only independent implementation audit found that the verifier forced
  every valid porcelain-v2 unmerged record to `UU`, while the runner retained
  the actual `DD`, `AU`, `UD`, `UA`, `DU`, `AA`, or `UU` state.
- Corrected the verifier to preserve the raw validated XY state and added one
  synthetic test covering all seven legal unmerged states.
- The first focused attempt after adding that test exposed a test-only helper
  name error: exit `1`, with 51 passes and one failure. Corrected the helper
  call, then reran the exact focused suite successfully: 52 passed in 17.76s.
- Reran the complete unit suite with the required native-tool overrides: 336
  passed in 108.77s. Neither failed nor passing tooling-test run invoked the
  real v2 runner plan.
- The single permitted real runner invocation remained unstarted throughout
  these corrections and checks.

## 2026-07-20T09:46:48Z - Single permitted real runner invocation failed

- Invoked the v2 runner exactly once with the required explicit CMake, C++,
  Ninja, and Make paths. The command exited `1`; it was not and will not be
  retried in this task.
- The runner began at `2026-07-20T09:46:48.207097Z` and finalized its partial
  report at `2026-07-20T09:46:48.414933Z`.
- The first `before:1:collect_focused` worktree snapshot rejected the Git
  ignored-path probe because Git emitted 792 bytes of permission-denied
  warnings for nine pre-existing ignored `build/pytest-*` directories.
- No pytest collection or stability subprocess started. The report records
  zero process records, zero run records, no collection identity, and failure
  detail `Git ignored probe emitted unexpected stderr`.
- Cleanup positively removed the one created `collection-focused` basetemp and
  its owner root. No expected task-owned basetemp, temporary report, or cleanup
  root remains.

## 2026-07-20T09:48:55Z - Partial-report verification and blocked handoff

- The v2 instance validator accepted the canonical partial report.
- The required completed-evidence verifier with same-host rehash exited `1`
  with `report is a valid partial record but not completed evidence`.
- The independent verifier with same-host rehash and `--allow-partial` exited
  `0`, confirming a semantically valid incomplete prefix while returning
  `completed=false` and `evidence_success=false`.
- Set the task to `BLOCKED`. `RFU-TEST-001` and `RFU-ENV-001` remain `OPEN`.
  No completed stability evidence and no mathematical evidence are claimed.

## 2026-07-20T09:53:49Z - Final blocked-state audit

- Revalidated all nine schemas and the v2 partial instance, task-ID/dossier
  resolution, all 11 pinned Action occurrences, the 10-file upstream snapshot,
  and the partial report with independent same-host rehash.
- Reproduced the exact 169-file protected inventory and its initial digest,
  confirmed all named v1 and prior-dossier hashes, and confirmed claims and
  pruning byte identities.
- Confirmed the exact 11-path task allowlist, empty index, unchanged Git config
  and index anchors, absent report temp and basetemp root, UTF-8/LF/trailing
  hygiene, cumulative-baseline diff check, and final `git diff --check`.
- `RFU-ENV-001` remains deep-equal to the task-start object and both follow-ups
  remain `OPEN`. No Git write command was executed.
