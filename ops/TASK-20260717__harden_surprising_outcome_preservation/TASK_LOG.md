# TASK-20260717__harden_surprising_outcome_preservation — Log

Append-only task chronology. Times are UTC when shown.

## 2026-07-17 — Startup and gate

- Plain Git initially reported dubious ownership. No Git configuration was
  changed. Every subsequent Git read used process-local
  `-c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`.
- Gate commands resolved the repository root, branch `main`, exact HEAD
  `be179265919566b44d40cb1e472cd3db50811502`, a clean worktree, and ancestry
  from `f8271e74509a017d1631dea72aaa652f44d8c3df`.
- The complete cumulative diff
  `f8271e74509a017d1631dea72aaa652f44d8c3df..HEAD` was read before edits.
- All mandatory files were read in canonical order, including every file in
  both earlier dossiers, relevant verifier tests, callers/consumers, and Git
  history. The new dossier did not yet exist, as expected.

## 2026-07-17 — Implementation

- Added freeze-first raw outcome records and an out-of-process bounded
  inspector, then moved the strict upstream adapter from the pytest process
  into that inspector boundary.
- Added the surprising-outcome JSON Schema and deterministic behavioral tests
  for ordinary completion, parse failure, predicate failure, synthetic
  all-pass, timeout/reap, inspector error, non-UTF-8 bytes, ordering, survival,
  collisions, deterministic serialization, and exact outcome matching.
- Moved benchmark raw stream writes immediately after child completion.
- Updated CI failure uploads and `always()` post-producer checks.
- Updated CI/reproducibility documentation and rejected-review state.

## 2026-07-17 — Intermediate failures and corrections

- The first new inspector-unit run had one fixture failure because a Python
  `-c` source string contained a literal non-UTF-8 byte. Replaced it with
  `bytes([255])`; the rerun passed.
- Read-only adversarial review found that the parent trusted child envelope
  fields, did not pin the outcome-record hash, accepted non-finite timeouts,
  resolved the artifact directory after upstream completion, and could let a
  secondary formatting error mask the first failure line. All were corrected,
  with new regression tests for incomplete protocol and record mutation.
- The timeout unit used `0.15` seconds and could race cold Python startup.
  Raised it to `0.75` seconds while retaining an under-two-second bound and
  post-kill heartbeat stability check.
- A direct tiny run without MSYS2 runtime directories in `PATH` returned
  Windows status `3221225781` and empty streams for both `k=3` and `k=4`.
  This was an environment-launch failure, not an upstream result. Repeating
  with the documented MSYS2 runtime produced `(exited, 0)` for both cases.
- A parallel required-test batch failed at setup because sandbox permissions
  denied pytest's global `%TEMP%/pytest-of-Falker`. Reruns used distinct
  repository-local `PYTEST_ADDOPTS=--basetemp build/...` directories and all
  passed.
- `Get-Date -AsUTC` was unsupported by the installed PowerShell. The portable
  `(Get-Date).ToUniversalTime().ToString(...)` form supplied the timestamp.

## 2026-07-17T14:55:25Z — Verification state

- Schema validation, 10/10 upstream inventory, release configure/build,
  corrected real tiny runs, focused suites, bounded suite, and complete suite
  passed.
- The complete suite reported 128 passed and no skips.
- A deliberately red synthetic exit-100/timeout proof preserved all four
  records, printed their hashes, confirmed pre-inspection freeze, returned
  status 1, and removed its temporary directory.
- Final protected-blob, allowlist, diff-hygiene, artifact-cleanup, and full-diff
  inspection remained to be recorded before changing status to
  `READY_FOR_REVIEW`.

## 2026-07-17 — Final audit and handoff

- A final read-only adversarial audit found no P0/P1 blocker. It prompted one
  additional hardening: benchmark stream hashes are now computed immediately
  after the closed raw files and before outcome matching. The regression test
  observes both hash calls before deliberately raising in the matcher.
- Focused benchmark tests reran at 36 passed; the complete suite reran at 128
  passed with no skips.
- Claims, pruning, heavy workflow, and upstream snapshot matched their
  task-start blobs/bytes. The current-task path set matched the 15-path
  allowlist exactly. Only `.gitkeep` remained in the two persistent artifact
  roots.
- Cumulative whitespace, status, stat, name-status, porcelain, exact full diff,
  and complete task-local tracked/untracked content were inspected. No
  out-of-scope task-local change or unintended artifact remained.
- Persistent state and this dossier were set to `READY_FOR_REVIEW`. Work stops
  here; no next task was started.

## Exact material command ledger

Startup Git reads used this prefix throughout:

```text
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
```

The gate and cumulative inspection commands were:

```text
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --porcelain=v1 --untracked-files=all
git merge-base --is-ancestor f8271e74509a017d1631dea72aaa652f44d8c3df HEAD
git diff --no-ext-diff --no-color f8271e74509a017d1631dea72aaa652f44d8c3df..HEAD --
git log --oneline --decorate -8
```

Canonical reads used PowerShell `Get-Content -LiteralPath` on every path in the
prompt, every file under the two named earlier dossiers, and the relevant
verifier tests returned by `rg --files tests verifier`; caller/consumer
inspection used `rg -n` over `tests`, `tools`, `schemas`, `.github`, `docs`, and
`research`.

The exact required verification commands are recorded with final results in
`EVIDENCE.md`:

```text
python -m json.tool REVIEW_STATE.yaml
python tools/validate_schemas.py
python tools/verify_upstream_snapshot.py
python -m pytest -q tests/unit/test_benchmark_outcomes.py
python -m pytest -q tests/unit/test_upstream_candidate_inspection.py
python -m pytest -q tests/integration/test_upstream_build.py
python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
python -m pytest -q --basetemp build/pytest-root
cmake -S . -B build/release -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build/release --target eg-upstream-serial
```

The integration commands set `EG_CMAKE=C:\msys64\ucrt64\bin\cmake.exe`,
`EG_CXX=C:\msys64\ucrt64\bin\g++.exe`,
`EG_NINJA=C:\msys64\ucrt64\bin\ninja.exe`, and
`EG_MAKE=C:\msys64\usr\bin\make.exe`. Where pytest's global temporary root
was inaccessible, `PYTEST_ADDOPTS` supplied the exact repository-local
`--basetemp` paths recorded in `EVIDENCE.md`.
