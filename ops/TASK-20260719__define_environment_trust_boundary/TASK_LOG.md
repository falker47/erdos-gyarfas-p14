# TASK-20260719__define_environment_trust_boundary - Log

Append-only task chronology. Times are UTC when shown.

## 2026-07-19T09:15:11Z - Startup gate and mandatory inspection

- Plain read-only Git first exited `1` on Git's dubious-ownership check for the
  sandbox identity. No Git configuration changed. All successful repository
  Git reads used the process-local `-c safe.directory=...` option permitted by
  the task.
- The gate resolved the required root and origin, branch `main`, exact HEAD and
  task-supplied review base
  `41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d`, successful ancestry, an empty
  worktree, and an empty index. Sandboxed status also warned that the owner's
  global ignore file was unreadable; empty status and index output remained
  unambiguous.
- Read every mandatory governance, research, accepted-dossier,
  reproducibility, workflow, Docker, Python, CMake, schema, test, native-build,
  and relevant Git-history input in the required order before modification.
  The new task dossier and all seven task-created files were initially absent.
- Inspected actual selector expressions rather than deriving the inventory
  from prose. Official `action.yml` bytes at each accepted Action commit were
  read from the exact official raw commit URLs; all three declare `node20`.
  This external metadata observation is separated from the GitHub-supplied
  runtime executable boundary.

## 2026-07-19T09:15:11Z - Initial preservation audit and accepted transition

- Recorded bytes and SHA-256 for every existing authorized file and every
  specifically required protected workflow, Docker, dependency, build,
  project-knowledge, claim, pruning, upstream, accepted-dossier, Git config,
  and index anchor.
- A first read-only recursive-digest helper used unavailable older-runtime APIs
  `Path.GetRelativePath` and `Convert.ToHexString`; it emitted method errors and
  null digests and is discarded. The portable retry used substring path
  normalization and `SHA256.Create().ComputeHash`, exited `0`, and produced
  valid group digests. A separate one-line PowerShell pipeline attempt had a
  parse error before execution; its corrected read-only form recorded the
  remaining hashes. No file changed in either diagnostic.
- Independently recorded a canonical protected tracked inventory excluding the
  four authorized existing modifications: 154 files, 904,336 raw bytes,
  16,553 serialized inventory bytes, SHA-256
  `9502eeec910a0b34040d2857cf5716a911a791a67e986b1cb63ca376d6ce0eca`.
- Persisted the already completed review transition before representing this
  task as active. The observed state-write time is
  `2026-07-19T09:15:11Z`; the accepted review occurrence remains the historical
  `2026-07-19T08:52:08Z`. Removed resolved `RFU-DOC-001`, kept and refined
  `RFU-ENV-001` as `OPEN`, and validated strict state JSON.

## 2026-07-19T09:27:06Z - Inventory, schema, test, and interpretation

- Created the strict JSON Schema and deterministic 58-entry inventory. Stable
  entries separate Action source commits from the Node runtime, base-image
  index from platform/APT resolution, version pins from artifact hashes, and
  repository-pinnable values from capture-only and externally trusted inputs.
- Represented all four `runs-on` occurrences, all eleven Action occurrences,
  both setup-python version families, interpreter acquisition, hosted native
  tools, direct/transitive Python state, Docker platform/context/APT and all
  eight unversioned packages, container toolchain/Python/environment, local
  Python/Git/platform state, and four accepted MSYS2 paths plus runtime/PATH
  provenance gaps.
- Created a simple regression test that strict-loads and schema-validates JSON,
  enforces deterministic order/bytes and normalized source paths, invokes the
  existing Action validator through a subprocess, parses only the repository's
  current simple workflow/Docker/TOML forms, compares Markdown metadata, and
  checks the exact inspected commit rather than future HEAD.
- Created the trust-boundary interpretation and made both artifacts canonical
  in `research/REPRODUCIBILITY.md`. Updated current status and research
  priority without accepting an implementation-level lock or starting
  `RS-001`.

## 2026-07-19T09:44:17Z - Focused verification and corrections

- Strict inventory JSON and explicit schema-instance validation exited `0`.
- The first focused pytest run collected six tests and exited `1` with three
  bounded test failures: one `concurrency` source range started one line late;
  the local Python/pytest capture environment produced `WinError 6` for the
  test's `capture_output=True` subprocess handles; and a Markdown ID regex also
  matched the suffix `ENV-001` inside `RFU-ENV-001`.
- Corrected the source range, adopted the repository's existing explicit
  `stdin=DEVNULL` and binary `stdout/stderr=PIPE` subprocess pattern, and made
  the reference regex reject an identifier prefix. The second focused run
  exposed one additional source-expression mismatch in a broad accepted
  dossier range; replacing it with the exact in-range phrase preserved the
  selector semantics.
- The terminal focused run then passed all six tests in 0.20 seconds with no
  failure, skip, or xfail. All failed attempts and their dispositions remain
  part of task evidence rather than being replaced by the terminal success.

## 2026-07-19T10:01:13Z - Complete-suite evidence and bounded corrections

- The first complete-suite run passed 296 tests and failed the new inventory
  contract because one reproducibility source range still pointed to its old
  location. A first narrowly written edit accidentally changed another equal
  numeric range; a read-only all-entry audit then identified every stale
  locator. Exact source inspection corrected all affected ranges, the audit
  reported zero mismatches, and the focused contract passed 6 tests in 0.27
  seconds.
- The second complete-suite run passed 296 tests and failed one protected,
  pre-existing Windows timing test because its child did not create the
  verified-before-sleep marker within the 0.75-second timeout. No protected
  test or implementation changed. The exact failing test passed in isolation
  in 1.16 seconds, and the terminal complete-suite retry passed all 297 tests
  in 99.16 seconds with no failure, skip, or xfail.
- Final focused verification passed 6 tests in 0.22 seconds. Strict state and
  inventory JSON parsing, all-schema validation, explicit inventory-instance
  validation, Action-pin validation, upstream preservation, and the
  review-range whitespace checker all exited `0`.

## 2026-07-19T10:01:13Z - Scope, preservation, cleanup, and handoff

- `git diff --check` passed. Final scope before dossier closure contained
  exactly four authorized tracked modifications and seven authorized new
  paths; the index remained empty. HEAD and branch remained the exact
  task-start SHA and `main`.
- Every specifically protected file retained its initial byte count and
  SHA-256. The canonical protected tracked inventory remained 154 files,
  904,336 bytes, and SHA-256 `9502eeec910a0b34040d2857cf5716a911a791a67e986b1cb63ca376d6ce0eca`.
  All seven protected directory digests also matched their task-start values.
- A first closing group-comparison wrapper captured both a display label and
  its digest as the function return, so it exited `1` with seven false
  mismatches. The corrected read-only wrapper returned only the digest scalar
  and proved all seven exact matches. Neither helper changed repository state.
- The authorized-file byte audit found strict UTF-8, no BOM, no NUL, a final
  LF, no trailing whitespace, and no bare CR in every path. The deterministic
  inventory serialization check passed.
- The task-created `build/pytest-root` directory was removed. The focused
  basetemp was already absent. Removal of the verified task-created
  `build/pytest-root-timeout-retry` directory was denied by the sandbox; the
  same exact bounded path was removed with approval. Pre-existing build output
  was not touched.
- The task status and canonical current status advanced to
  `READY_FOR_REVIEW`. No subsequent task was started.
