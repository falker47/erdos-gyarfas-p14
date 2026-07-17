# TASK-20260717__bind_heavy_workflow_task_identity — Log

Append-only task chronology. Times are UTC when shown.

## 2026-07-17T15:35:09Z — Startup and initial state

- Plain Git first reported dubious ownership. No Git configuration was
  changed. The gate was repeated with process-local
  `-c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`.
- The gate resolved the correct root, branch `main`, exact HEAD
  `0d08a58d87e7aaa5749ed2d3428cc0906a6bade6`, an empty porcelain worktree,
  and successful baseline ancestry.
- All mandatory files were read in canonical order. The current dossier did
  not yet exist, as expected, and was created only after the gate and reads.
- Relevant manifest/review/workflow tests and fixtures, Git history, the
  complete empty baseline diff, and all requested reference classes were
  inspected.
- Persistent review state was advanced to the already accepted baseline.
  `RFU-CI-001` and `RFU-CI-002` were removed; the other four follow-ups remain
  `OPEN` in unchanged relative order and content.

## 2026-07-17 — Implementation

- Added `tools/resolve_review_task_id.py` with strict JSON parsing, duplicate
  key and non-finite constant rejection, top-level/schema/task-ID checks,
  repository-root containment, and required regular non-symlink dossier
  status validation.
- Bound `.github/workflows/heavy-search.yml` to the resolved value through
  `RESOLVED_TASK_ID`, added the canonical source/path and two observed SHA-256
  parameters, and retained all scaffold/refusal/validation/upload boundaries.
- Added 32 focused tests using only temporary synthetic fixture directories,
  plus current-state and workflow-static assertions.
- Updated CI/reproducibility documentation and commit-neutral current state.

## 2026-07-17 — Intermediate failures and dispositions

- The first focused run reported 29 passed and one failure because Python
  `print()` translated LF to CRLF on Windows. The resolver now writes explicit
  UTF-8 bytes with one LF; focused reruns passed first 30/30 and finally 32/32.
- The first full-suite attempt encountered a stale/inaccessible
  `build/pytest-root`: 99 passed, 3 skipped, and 56 setup errors, all rooted in
  `PermissionError: [WinError 5]` while Pytest removed the basetemp. After
  verified workspace-contained cleanup, the exact command passed with 154
  passed and four expected toolchain skips.
- A rerun with MSYS2 overrides was mistakenly attempted without first cleaning
  that same basetemp and reproduced setup-only access errors (99 passed, 59
  errors). The generated directory was removed after containment checks.
- Windows-localized `takeown /D Y` rejected the English response token, and a
  later ownership attempt was denied. Neither command changed repository
  sources. The ordinary sandbox identity that owned the generated directory
  then removed it successfully.
- The final complete run used the documented MSYS2 tools and runtime path,
  passed 160 tests with no skips, and its basetemp was removed immediately.

## 2026-07-17T15:49:24Z — Verification and handoff

- Strict review-state resolution, schema validation, upstream inventory,
  focused tests, bounded tests, and the complete suite passed.
- Static checks proved the obsolete literal and all hardcoded production
  `--task-id TASK-...` forms absent, and showed the resolver before the
  manifest producer with `RESOLVED_TASK_ID` and all four provenance fields.
- Claims, pruning, fast CI, manifest tooling/schema/template, upstream
  snapshot, and all earlier dossiers remain unchanged from task-start HEAD.
- Generated Pytest basetemp content was removed. Final allowlist, whitespace,
  status, full diff, and complete untracked-file inspection all passed.
- Work stops at `READY_FOR_REVIEW`; no next task is started.

## Exact material command ledger

Git reads used the process-local prefix:

```text
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
```

Material commands included:

```text
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --porcelain=v1 --untracked-files=all
git merge-base --is-ancestor 0d08a58d87e7aaa5749ed2d3428cc0906a6bade6 HEAD
python -m json.tool REVIEW_STATE.yaml
python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier
python tools/validate_schemas.py
python tools/verify_upstream_snapshot.py
python -m pytest -q tests/unit/test_review_task_id.py
python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
python -m pytest -q --basetemp build/pytest-root
git diff --check 0d08a58d87e7aaa5749ed2d3428cc0906a6bade6 --
git diff --stat 0d08a58d87e7aaa5749ed2d3428cc0906a6bade6 --
git diff --name-status 0d08a58d87e7aaa5749ed2d3428cc0906a6bade6 --
git status --porcelain=v1 --untracked-files=all
```

The final complete pytest run set `EG_CMAKE`, `EG_CXX`, `EG_NINJA`, and
`EG_MAKE` to their documented MSYS2 executables and prepended the MSYS2 UCRT64
and Unix runtime directories to `PATH`.

## 2026-07-17T16:57:59Z — Recovery acquisition

- A new executor session acquired the existing eleven-path dirty candidate as
  explicitly authorized; no new task or dossier was created.
- Plain Git again failed with dubious ownership. The full recovery gate was
  repeated successfully using only process-local `safe.directory`: root,
  branch, exact HEAD/baseline, ancestry, and the dirty-path allowlist all
  matched the prompt.
- The complete tracked diff and all three inherited dossier files were read.
  The initial byte count, SHA-256, and porcelain state of every allowed path
  were recorded in `EVIDENCE.md` before this append.
- One read-only hash-collection attempt failed before execution because of
  orchestrator quoting; the corrected command succeeded. No repository or Git
  configuration change resulted.
- All earlier log entries remain byte-for-byte in place above this recovery
  append. They describe the prior executor session and are not treated as
  evidence that the recovery session itself began from a clean worktree.

## 2026-07-17T17:02:23Z — Inherited-candidate audit

- Read the current and baseline forms of every modified tracked file, every
  inherited untracked file, both workflows, manifest producer/verifiers,
  shared tooling, schema/template, related tests/fixtures, affected verifier
  code, requested reference map, and Git history.
- Confirmed the inherited resolver and workflow satisfy the functional scope;
  no production-code defect was found.
- Confirmed the inherited dossier commands are reproducible and its current
  state/follow-up/claim boundaries are coherent. The recovery append preserves
  the complete inherited log prefix.
- Required recovery reruns passed: JSON/resolver/schema/snapshot checks, 32
  focused tests, 156 bounded tests, and 160 complete tests. The exact generated
  `build/pytest-root` was path-checked, removed, and confirmed absent.
- Identified two test-only robustness gaps: exercise all three Python JSON
  non-finite constants and reject optionally quoted hardcoded task IDs. These
  are corrected next within the existing authorized test file.

## 2026-07-17T17:07:35Z — Recovery correction and closing verification

- Parameterized the non-finite JSON regression over `NaN`, `Infinity`, and
  `-Infinity`, and strengthened the workflow assertion to detect an optionally
  quoted hardcoded task ID. No production resolver/workflow code changed.
- Updated the canonical review-state timestamp to the actually observed
  `2026-07-17T17:04:29Z`; no baseline, verdict, task, or follow-up semantics
  changed.
- Post-correction focused, bounded, and complete suites passed 34, 158, and 162
  tests respectively, with no skips. JSON, resolver, schema, and upstream
  snapshot checks also passed on the final governance state.
- Each complete-suite basetemp was verified as the exact intended
  workspace-contained `build/pytest-root`, removed, and confirmed absent.
- The first workflow-static output formatter used invalid PowerShell syntax
  and emitted non-terminating formatting errors. Its results were discarded;
  a corrected script returned 16 explicit `PASS` lines and exit zero.
- Protected paths, prior dossier, claims, pruning, upstream tree, artifact
  roots, and the exact eleven-path allowlist passed preservation checks. The
  inherited 5,036-byte log prefix still hashes to its initial SHA-256.
- Final diff hygiene, hashes, porcelain/allowlist, complete diff, and complete
  untracked-file rereads are performed after this append. The task remains the
  same atomic task and ends at `READY_FOR_REVIEW`; no next task is started.
