# TASK-20260718__isolate_whitespace_git_semantics — Log

Append-only task chronology. Times are UTC when shown.

## 2026-07-18T15:33:21Z — Startup gate, cumulative audit, and state transition

- Every successful repository Git read used only process-local
  `-c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`;
  no Git configuration was changed.
- The required gate resolved the exact repository root, branch `main`, task
  start HEAD `ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4`, empty worktree and index,
  and successful ancestry from accepted baseline
  `e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`. Installed Git is
  `2.45.1.windows.1`.
- The complete cumulative accepted-base-to-HEAD diff was read before edits.
  It contains the rejected candidate's twelve paths; `.github/workflows/ci.yml`
  and `tests/unit/test_review_task_id.py` are retained prior-candidate content
  and are outside this corrective task's change scope.
- Read all mandatory governance, research, prior-dossier, tool, test, workflow,
  attribute, CI, and reproducibility files in the required order. Read the
  relevant installed Git documentation for whitespace configuration,
  configuration-source precedence, attribute precedence, and `diff --check`.
- Persistent state now records the rejected HEAD/verdict, keeps the accepted
  baseline and accepted task unchanged, identifies this corrective active
  task, and retains the three ordered `OPEN` follow-ups without content
  changes.
- A first read-only cumulative-diff command that attempted a process-level
  `GIT_CONFIG_COUNT` safe-directory override failed repository discovery. The
  corrected `git -c safe.directory=...` read succeeded; no file or Git state
  changed.
- One evidence hash formatter used an unavailable PowerShell
  `[SHA256]::HashData` method after reading the file. The corrected
  `Get-FileHash` command succeeded; no repository file changed.

## 2026-07-18T15:33:21Z — Trust-boundary decision

- Git documents that `diff --check` is controlled by `core.whitespace`; the
  explicit policy is `blank-at-eol,space-before-tab,blank-at-eof`.
- System/global/process configuration and global/system attributes can be
  neutralized in the child environment and command-line configuration.
  Repository-local `core.whitespace` is overridden explicitly.
- Checked-in `.gitattributes` remains part of the verdict. In particular, the
  versioned `third_party/erdos-gyarfas/** -diff` rule remains untouched.
- `$GIT_DIR/info/attributes` has highest attribute precedence and is not
  versioned. A nonempty or nonregular source there is therefore rejected
  fail-closed with a deterministic diagnostic instead of being trusted.

## 2026-07-18T15:53:46Z — Implementation and adversarial verification

- The checker now supplies the explicit whitespace policy and null global
  attributes through command-line Git configuration, removes repository
  redirects and all system/global/process configuration injection from its
  child environment, disables system attributes, and fixes locale and optional
  locks without mutating the parent environment.
- The diff receives `--attr-source=<resolved-head>` and `--no-textconv`; this
  retains checked-in head-tree attributes while excluding dirty worktree
  attributes and external diff/text-conversion helpers.
- The actual Git-resolved `info/attributes` path is checked before and after
  the diff. Absence and a zero-byte regular file pass. A nonempty, unreadable,
  nonregular, or symlink entry produces one path-independent fail-closed error
  line and prevents a successful verdict.
- Added blank-at-EOF coverage and real temporary-repository cases for hostile
  local/global/system/process configuration, `core.attributesFile`,
  `info/attributes`, dirty worktree attributes, and checked-in attributes.
  Each neutralizable bad control first proved that an unisolated Git command
  returned zero; the production checker then detected the committed error.
  Clean twins, deterministic repetition, parent-environment equality, and
  repository byte/status/ref/object equality are asserted.
- The required focused command passed twice after implementation: 54 tests in
  30.47 seconds and 54 tests in 28.68 seconds. Collection listed exactly 54
  tests and no skip marker was produced.
- Final-state preliminary governance checks passed: strict JSON parsing,
  canonical active-task resolution, six-schema validation, upstream inventory,
  and the real cumulative checker invocation.
- The bounded suite passed 213 tests in 40.34 seconds. The complete suite used
  the documented MSYS2 tools and required `build/pytest-root`, passing 217
  tests in 54.73 seconds. Neither run reported a failure, skip, or xfail.
- The exact resolved complete-suite basetemp was verified equal to the intended
  workspace path, removed recursively with native PowerShell, and confirmed
  absent. The independent Git-semantics probe used only a synthetic directory
  below `C:\tmp`; it too was removed and confirmed absent.

## 2026-07-18T16:01:36Z — Independent-review bypass and correction

- A read-only independent review found and reproduced a blocking static-config
  bypass: checked-in `diff=hostile` combined with local
  `diff.hostile.binary=true` made Git treat a text file as binary despite
  `--no-ext-diff` and `--no-textconv`, hiding committed trailing whitespace.
- Git cannot skip only repository-local config. The checker now queries the
  effective local config with local includes before and after the diff and
  fails closed on any `diff.*` key. Existing safely neutralized local
  `core.whitespace` and `core.attributesFile` cases continue to run.
- Added real bad and clean diff-driver cases. Their isolated-but-unguarded raw
  controls return zero; the production checker now returns the same byte-exact
  fail-closed diagnostic twice without changing repository or environment.
- One exploratory test hypothesized that `core.bigFileThreshold=1` would hide
  the one-line trailing-space fixture. The raw control instead returned two
  and reported the error, so the test failed once (57 passed, 1 failed). The
  unsupported hypothesis and unnecessary production pin were removed rather
  than weakening the assertion. The corrected focused suite passed 56 tests
  in 32.76 seconds.

## 2026-07-18T16:13:31Z — Worktree scope, symlink correction, and final suites

- Independent re-review reproduced the same diff-driver bypass in the separate
  per-worktree config scope enabled by `extensions.worktreeConfig`. Validation
  now covers both `--local` and `--worktree`, with includes, before and after
  the diff. Direct and included bad/clean regressions cover all four forms.
- A new real symlink regression initially failed because
  `rev-parse --path-format=absolute` canonicalized the final path component,
  causing `lstat` to observe the empty target. The checker now uses
  non-canonicalizing `rev-parse --git-path info/attributes`, anchors relative
  output to the validated root, and rejects the link itself. That failed run
  reported 62 passed and one failed assertion; the corrected focused run
  passed 63 tests in 40.42 seconds with no skip.
- Final independent static-semantics and path reviews report no blocker after
  the local/worktree/include and symlink corrections. The documented
  concurrent-replacement limitation remains separate from static invocation
  semantics.
- Final bounded verification used workspace basetemp
  `build/pytest-bounded-final` and passed 222 tests in 62.51 seconds. Final
  complete verification used the required `build/pytest-root`, documented
  MSYS2 tool variables/runtime path, and passed 226 tests in 65.16 seconds.
  Neither suite reported a failure, skip, or xfail.
- Both final workspace basetemps were verified by exact resolved path, removed,
  and confirmed absent. Three retained default-Pytest roots from intermediate
  runs (`pytest-59`, `pytest-60`, `pytest-61`) and their `pytest-current` link
  could not be listed by the ordinary sandbox identity. An approved read then
  identified them by path/timestamp; they were removed with explicit approval
  and confirmed absent. No unrelated temporary directory was removed.
- Final strict JSON, active-task resolver, six-schema validator, upstream
  inventory, and real cumulative committed-range checker commands all exited
  zero on the final implementation and governance state.

## 2026-07-18T16:13:31Z — Closing scope and preservation audit

- The required cumulative `git diff --check` exited zero. Cumulative stat from
  the unchanged accepted baseline reports 12 tracked paths, 2,418 insertions,
  and 86 deletions before addition of this task's three untracked dossier
  files. Its name-status set is exactly the rejected candidate's tracked scope
  with the seven authorized corrective tracked paths updated.
- Task-local comparison against start HEAD contains exactly seven modified
  tracked allowlist paths. Porcelain adds exactly the three new allowed dossier
  files; the ten-path allowlist comparison passes and the index is empty.
- Task-start diff checks pass for `.gitattributes`, both workflows, the task-ID
  resolver/test, claims, pruning, both earlier dossiers, upstream snapshot and
  metadata, schemas, and templates. Their SHA-256/blob/tree identities match
  the recorded anchors.
- All three new dossier files have a final LF and no trailing-whitespace line.
  Workspace basetemps, the supporting `C:\tmp` synthetic repository, and
  workflow-log output are absent. The only remaining untracked files are the
  three authorized current-dossier files.
- Git emitted only the known warning that the sandbox identity cannot read the
  user-global ignore file. No Git configuration was modified. Full final diff
  and untracked-file reads plus closing hashes follow in `EVIDENCE.md`; the
  task remains `READY_FOR_REVIEW` and no next task is started.
