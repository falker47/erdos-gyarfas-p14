# TASK-20260717__enforce_committed_range_whitespace — Evidence

All evidence in this dossier is bounded engineering and provenance evidence.
It establishes no mathematical result, reproduction, exhaustive coverage,
certificate, counterexample, or proof.

## EV-001 — Startup gate

Successful Git reads used only a process-local `safe.directory` exception
after plain Git reported sandbox ownership mismatch:

```text
git rev-parse --show-toplevel
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14

git branch --show-current
main

git rev-parse HEAD
e33c3bf121d5bb81b4c63adf704ca9b4ecfea970

git status --porcelain=v1 --untracked-files=all
<empty; only unreadable user-global ignore warnings on stderr>

git merge-base --is-ancestor e33c3bf121d5bb81b4c63adf704ca9b4ecfea970 HEAD
<exit 0, no stdout>
```

No repository file, index, ref, object, stash, or Git configuration changed
during the gate.

## EV-002 — Mandatory reads and initial anchors

The canonical startup files were read in required order. The current dossier
was confirmed absent before its authorized creation. The accepted previous
dossier and latest CI-related dossier were read completely, followed by both
workflows, `tools/resolve_review_task_id.py`, `tools/_common.py`,
`pyproject.toml`, every test that directly exercises a workflow, review state,
or a tool under `tools/`, and the two affected documentation files.

Git history placed accepted HEAD at `e33c3bf`; the complete
`e33c3bf..HEAD` stat, name-status, and diff were empty before edits. Artifact
and benchmark-result roots contained only tracked README/`.gitkeep` files.

Protected task-start Git objects:

```text
research/CLAIMS_REGISTRY.yaml                         c770fc2b51c16d575a05fde361403ffbf9c50f22
research/PRUNING_REGISTRY.md                          962075aa9f0c48492162bca322195fed802a1a1f
.github/workflows/heavy-search.yml                    738d0451076fd59f8b9c22d35709f536c1d2ffc2
tools/resolve_review_task_id.py                       1c437bf7fc7e4a07b5b82297c95a501a081d6a78
accepted prior dossier tree                           2aa2235a805dc087ad8af2edc37501fa5da670c1
third_party/erdos-gyarfas tree                        35707222c62e2bc14b90f385f593a66799405eba
```

## EV-003 — Implemented range semantics

The helper accepts only a regular non-symlink in-root UTF-8 state file parsed
as strict JSON with unique keys, finite JSON numbers, top-level object, schema
version `1.0`, and a lowercase full-SHA `review_base_commit`. `ROOT` is
explicitly rejected. Git environment overrides that could redirect repository
discovery are removed in the child environment; the script-derived root must
equal Git's top level. Baseline and `--head` are resolved to full commits and
ancestry is mandatory.

The effective check is:

```text
git -c safe.directory=<root> -c core.quotePath=true --no-pager diff \
  --no-ext-diff --no-color --check <base>..<head> --
```

Arguments are passed as a subprocess vector, not a shell string.
`GIT_OPTIONAL_LOCKS=0` and process-local `safe.directory` avoid Git writes.
Whitespace diagnostics and Git's nonzero result propagate. Success is one
deterministic compact JSON line containing full base, head, and range.

The dedicated `ubuntu-24.04` CI job uses `fetch-depth: 0`, Python 3.11, and
the exact state/head interface. The two endpoint-free matrix checks are named
`Check test-created worktree whitespace` and remain distinct post-test checks.

## EV-004 — Verification before scope block

Passing checks:

```text
python -m pytest -q tests/unit/test_review_range_whitespace.py
36 passed in 13.72s

python -m json.tool REVIEW_STATE.yaml
exit 0

python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD
{"base":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970","head":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970","ok":true,"range":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970..e33c3bf121d5bb81b4c63adf704ca9b4ecfea970"}

python tools/validate_schemas.py
exit 0; six schemas checked

python tools/verify_upstream_snapshot.py
exit 0; 10 expected and observed files, no changes
```

Blocked required check:

```text
python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
193 passed, 1 failed
```

The sole failure is
`tests/unit/test_review_task_id.py::test_current_canonical_state_resolves_exact_active_task`.
The production resolver correctly emits the newly mandated active task, while
that earlier out-of-scope test hardcodes the accepted previous task. Updating
the existing test to derive its canonical expectation from current versioned
state is the minimal durable correction, but it requires explicit addition of
that path to this task's allowlist.

## EV-005 — Recovery-session acquisition anchors

EV-001 through EV-004 above were inherited from the earlier executor session
and were treated as unverified candidate assertions at recovery. The recovery
gate observed at `2026-07-18T06:56:40Z` resolved the exact repository root,
branch `main`, HEAD and baseline
`e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`, successful baseline ancestry,
and exactly the eleven authorized dirty paths. Plain Git first failed with the
expected sandbox ownership diagnostic. The complete gate was then repeated
successfully with only process-local
`-c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`;
no Git configuration or repository state changed.

These byte counts, SHA-256 values, tracked/untracked classifications, and
porcelain states were captured before the recovery session modified any
candidate file:

| Path | Bytes | Initial SHA-256 | Presence | Git state |
| --- | ---: | --- | --- | --- |
| `.github/workflows/ci.yml` | 7300 | `a575a899741cc934a5ada5080f2a817b9b3974116bc7541d288341e6fb2083d4` | tracked | ` M` |
| `CURRENT_STATUS.md` | 4717 | `176a628c0f69857dab96df755166d848bf8153169075fa240460d6089512632d` | tracked | ` M` |
| `REVIEW_STATE.yaml` | 1577 | `ca0988a6a39f73e5e78c0b8074aadeb2907c5f5943ff65ed86083a77c3354839` | tracked | ` M` |
| `docs/CI.md` | 10062 | `d19d4ff8dcd9993c1f80687600aa2ec91209ca83e5fe55b8a1331d5dffbbe3d2` | tracked | ` M` |
| `research/NEXT_RESEARCH_STEPS.md` | 6046 | `4c83b4a36f9ce6d086d01ec57e9ac9fd8353c2b83979a70112269f2bfb4fb249` | tracked | ` M` |
| `research/REPRODUCIBILITY.md` | 12525 | `fb6bf803b19f5d8171d0b7135d170466373aa08fdd4cbf2545f300a31d164cb3` | tracked | ` M` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/EVIDENCE.md` | 4702 | `f1676c33385c1a3b2efe461407f7fca100e62cb0c408a9519c668c9024dc759d` | untracked | `??` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/TASK_LOG.md` | 2415 | `72fb5b78f615b363c96513cd9525c9e43e0c94005e2b8c92a789b0ab50ff84af` | untracked | `??` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/TASK_STATUS.md` | 1687 | `d33163ffa14a452395553b68fabff9806dd614a63c846818f18ab6e8a9324b3a` | untracked | `??` |
| `tests/unit/test_review_range_whitespace.py` | 16041 | `f8ef07e2bcf3f880e7aca89e1f96fc6cd86fd2f85bac993a95b348de8f134eff` | untracked | `??` |
| `tools/check_review_range_whitespace.py` | 9358 | `39a682b7ff9192940ac33498460527ec23dfcfc1efa0dacde8c69a74016de6c7` | untracked | `??` |

The inherited `TASK_LOG.md` prefix was 2,415 bytes and its whole-file SHA-256
was
`72fb5b78f615b363c96513cd9525c9e43e0c94005e2b8c92a789b0ab50ff84af`.
All recovery chronology must be appended after that exact prefix.

## EV-006 — Recovery audit of the inherited candidate

Audit checkpoint: `2026-07-18T07:06:14Z`.

1. Already implemented: the helper derives its root from the checked-in
   script, contains the state path, rejects parent traversal and symlink
   components, requires a regular non-symlink UTF-8 state file, parses strict
   JSON, validates schema `1.0`, rejects `ROOT`, resolves full commit objects,
   proves ancestry, and runs `git diff --check` on the explicit committed
   range without shell interpolation. Git diagnostics and nonzero status are
   propagated. Success is deterministic compact JSON.
2. CI already has one dedicated `ubuntu-24.04` job, full history through
   `fetch-depth: 0`, Python 3.11, and the canonical helper invocation. The two
   endpoint-free checks are separately named post-test worktree checks. No
   error suppression is present.
3. The 36 focused tests cover clean and two invalid committed ranges, dirty
   worktree separation, empty range, ancestry, missing/malformed/non-commit
   endpoints, missing/directory/malformed/duplicate/non-object/wrong-schema/
   non-finite/non-UTF-8 state, traversal/outside/symlink paths, deterministic
   output, read-only behavior, Git-environment redirection, and workflow
   structure.
4. No functional defect was found in the inherited helper or workflow. The
   inherited dossier lacked recovery-session acquisition anchors; EV-005 now
   supplies them.
5. The inherited focused, JSON, range, schema, and snapshot claims are
   reproducible. The default Pytest temporary root is inaccessible to the
   sandbox identity, so successful local test reruns require a dedicated
   workspace basetemp. This changes no tested semantics.
6. The inherited 2,415-byte `TASK_LOG.md` was read and hashed before recovery;
   all recovery chronology is appended after that prefix.
7. `TASK_STATUS.md`, `CURRENT_STATUS.md`, and `REVIEW_STATE.yaml` coherently
   identify the current task and accepted baseline and keep the task
   `BLOCKED`. `RFU-CI-003` remains `OPEN`; it was not closed prematurely.
8. The sole product-level blocker is outside the exclusive allowlist:
   `tests/unit/test_review_task_id.py` hardcodes the previous active task ID
   and its canonical-state subprocess assertion contradicts the mandated
   current `active_task_id`. Changing the state, resolver behavior, test
   selection, or status handling to evade that assertion would violate an
   explicit requirement.
9. Claims, pruning, search semantics, heavy workflow, prior resolver, accepted
   dossier, and upstream snapshot are unchanged. No mathematical or
   certification classification is affected.
10. Test-created basetemps were removed after exact path validation. No
    manifest, benchmark result, search output, certificate, counterexample,
    checkpoint, or other generated artifact influenced the audit result.

## EV-007 — Recovery command results and intermediate failures

Successful governance and focused checks:

```text
python -m json.tool REVIEW_STATE.yaml
exit 0

python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD
{"base":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970","head":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970","ok":true,"range":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970..e33c3bf121d5bb81b4c63adf704ca9b4ecfea970"}

python tools/validate_schemas.py
exit 0; six schemas checked

python tools/verify_upstream_snapshot.py
exit 0; 10 expected and observed files, no additions, changes, or omissions

python -m pytest -q tests/unit/test_review_range_whitespace.py
36 passed in 14.98s
```

The successful focused command used process-local
`PYTEST_ADDOPTS=--basetemp=build/pytest-range-root` because the sandbox cannot
access the user-owned default Pytest temp root. The exact generated path was
resolved, removed, and confirmed absent.

Required suites expose the same single out-of-scope stale assertion:

```text
python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
193 passed, 1 failed in 27.49s

python -m pytest -q --basetemp build/pytest-root
197 passed, 1 failed in 37.97s
```

Both failures are solely
`tests/unit/test_review_task_id.py::test_current_canonical_state_resolves_exact_active_task`:
the resolver emits the required current task while the test expects the
accepted previous task. The full run used explicit MSYS2 `EG_CMAKE`, `EG_CXX`,
`EG_NINJA`, and `EG_MAKE` paths and the matching UCRT64/Unix runtime path; it
had no other failures or skips. Both basetemps were removed and confirmed
absent.

Intermediate non-product failures and dispositions:

- Plain Git initially rejected sandbox ownership; the complete gate was
  repeated with only process-local `safe.directory` and passed.
- Two focused attempts produced 35 setup errors and one pass because the
  default temp root was inaccessible. The attempted dedicated `C:\tmp` path
  was also denied and never created. The workspace-basetemp rerun passed all
  36 tests.
- The first static-check output formatter used invalid PowerShell expression
  syntax. Its output was discarded; the corrected rerun emitted 17 explicit
  `PASS` lines and exited zero.

## EV-008 — Recovery preservation and scope result

Static checks passed for the dedicated job, Ubuntu runner, full-history
checkout, canonical helper invocation, two clearly named post-test worktree
checks, absence of the legacy ambiguous name, absence of `continue-on-error`
and `|| true`, required review-state identities, ordered open follow-ups, and
removal of accepted `RFU-WORKFLOW-001`.

Protected-path diff output is empty. Baseline identities remain:

```text
research/CLAIMS_REGISTRY.yaml                         c770fc2b51c16d575a05fde361403ffbf9c50f22
research/PRUNING_REGISTRY.md                          962075aa9f0c48492162bca322195fed802a1a1f
.github/workflows/heavy-search.yml                    738d0451076fd59f8b9c22d35709f536c1d2ffc2
tools/resolve_review_task_id.py                       1c437bf7fc7e4a07b5b82297c95a501a081d6a78
accepted prior dossier tree                           2aa2235a805dc087ad8af2edc37501fa5da670c1
third_party/erdos-gyarfas tree                        35707222c62e2bc14b90f385f593a66799405eba
```

The dirty-path set remains exactly the eleven-path allowlist, and generated
artifact checks are empty. Because the required bounded and full suites do not
pass and the sole correction path is explicitly excluded, acceptance criteria
12 and 19 cannot both be satisfied within scope. The recovery session
therefore preserves `BLOCKED`; it does not falsely set `READY_FOR_REVIEW`.

## EV-009 — Closing recovery hashes

The SHA-256 of the first 2,415 bytes of the recovery-extended `TASK_LOG.md` is
still
`72fb5b78f615b363c96513cd9525c9e43e0c94005e2b8c92a789b0ab50ff84af`,
exactly the inherited whole-file hash from EV-005. This proves that the
inherited log prefix was not rewritten or truncated.

The following closing byte counts and SHA-256 values were observed after all
substantive implementation, governance, status, and log content reached its
recovery-closing state. For `EVIDENCE.md`, the listed value is the pre-EV-009
anchor: embedding a file's own final digest changes the file, so the exact
post-EV-009 digest is recomputed during the final read-only audit and reported
in the executor handoff.

| Path | Final bytes | Closing SHA-256 |
| --- | ---: | --- |
| `.github/workflows/ci.yml` | 7300 | `a575a899741cc934a5ada5080f2a817b9b3974116bc7541d288341e6fb2083d4` |
| `CURRENT_STATUS.md` | 4909 | `9de58160327998d169e822f7ad97c5ff69c0944717a2fd4bd124d2a88a4dab08` |
| `REVIEW_STATE.yaml` | 1577 | `ca0988a6a39f73e5e78c0b8074aadeb2907c5f5943ff65ed86083a77c3354839` |
| `docs/CI.md` | 10062 | `d19d4ff8dcd9993c1f80687600aa2ec91209ca83e5fe55b8a1331d5dffbbe3d2` |
| `research/NEXT_RESEARCH_STEPS.md` | 6046 | `4c83b4a36f9ce6d086d01ec57e9ac9fd8353c2b83979a70112269f2bfb4fb249` |
| `research/REPRODUCIBILITY.md` | 12525 | `fb6bf803b19f5d8171d0b7135d170466373aa08fdd4cbf2545f300a31d164cb3` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/EVIDENCE.md` | 13990 before EV-009 | `6da44429947855f99f39bc4cb2b957b358bf43e4c03ef6e657cdf7942b8bd080` (pre-EV-009 anchor) |
| `ops/TASK-20260717__enforce_committed_range_whitespace/TASK_LOG.md` | 4544 | `890e00b8ea427265fb45b3958dd816e74487bf7fb10962ee058fbd423f5b175e` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/TASK_STATUS.md` | 2105 | `f64be7d775233f6a0a48792273a1715a95dcfea10bae1efc15c23b90d0ce67c7` |
| `tests/unit/test_review_range_whitespace.py` | 16041 | `f8ef07e2bcf3f880e7aca89e1f96fc6cd86fd2f85bac993a95b348de8f134eff` |
| `tools/check_review_range_whitespace.py` | 9358 | `39a682b7ff9192940ac33498460527ec23dfcfc1efa0dacde8c69a74016de6c7` |

Compared with EV-005, recovery changed only `CURRENT_STATUS.md`, the current
task status/log/evidence, and no implementation, workflow, state, focused
test, CI documentation, reproducibility documentation, or research-priority
semantics. The task remains the same atomic task and remains `BLOCKED` solely
by the unchanged out-of-scope test expectation.

## EV-010 — Corrective recovery gate and initial anchors

The prior EV-001 through EV-009 remain historical evidence of the original
implementation and blocked recovery. This corrective continuation acquired the
same candidate after explicit authorization added
`tests/unit/test_review_task_id.py` as the twelfth allowed path.

Plain Git first reproduced the expected sandbox ownership rejection. Every
successful Git read then used only process-local
`-c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`.
The gate observed:

```text
git rev-parse --show-toplevel
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14

git branch --show-current
main

git rev-parse HEAD
e33c3bf121d5bb81b4c63adf704ca9b4ecfea970

git merge-base --is-ancestor e33c3bf121d5bb81b4c63adf704ca9b4ecfea970 HEAD
exit 0; no stdout

git diff --cached --name-status --
exit 0; no paths
```

The complete porcelain set contained exactly the six inherited modified
tracked paths and five inherited untracked paths below. The newly authorized
test was clean:

| Git state | Paths |
| --- | --- |
| ` M` | `.github/workflows/ci.yml`; `CURRENT_STATUS.md`; `REVIEW_STATE.yaml`; `docs/CI.md`; `research/NEXT_RESEARCH_STEPS.md`; `research/REPRODUCIBILITY.md` |
| `??` | the three current dossier files; `tests/unit/test_review_range_whitespace.py`; `tools/check_review_range_whitespace.py` |
| clean | `tests/unit/test_review_task_id.py` |

The baseline diff stat was six tracked files with 138 insertions and 72
deletions; name-status listed only those same six paths. `git ls-files
--others --exclude-standard` listed only the same five untracked paths.
Baseline ancestry, the twelve-path allowlist, and the empty staged state all
passed.

At `2026-07-18T10:05:22Z`, before any corrective edit, the required byte and
SHA-256 anchors were:

| Path | Bytes | Initial SHA-256 |
| --- | ---: | --- |
| `tests/unit/test_review_task_id.py` | 10923 | `8005e5dbd535e9b96174f01b38bddfcee38c530281f76f073253e4363a3a3495` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/EVIDENCE.md` | 16491 | `584d55612918ac374e8f3b3b32baabaf3ad5f8eb7ee1443ab50f12718ce287cf` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/TASK_LOG.md` | 4544 | `890e00b8ea427265fb45b3958dd816e74487bf7fb10962ee058fbd423f5b175e` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/TASK_STATUS.md` | 2105 | `f64be7d775233f6a0a48792273a1715a95dcfea10bae1efc15c23b90d0ce67c7` |

The inherited log prefix is exactly the initial 4,544-byte whole file. Its
SHA-256 is the value above. Mandatory canonical files, the complete current
dossier, the complete accepted prior status/evidence/log, resolver, both
focused test modules, whitespace helper, CI workflow, affected documentation,
complete tracked diff, all untracked files, recent history, and protected Git
objects were inspected before correction. No distinct blocking defect was
found in production code or workflows.

## EV-011 — Blocker reproduction and cause

Before correction, the exact required command produced one failure:

```text
python -m pytest -q tests/unit/test_review_task_id.py::test_current_canonical_state_resolves_exact_active_task
1 failed in 0.28s
```

The subprocess itself returned exit zero, empty stderr, and stdout
`TASK-20260717__enforce_committed_range_whitespace\n`, exactly matching the
canonical `REVIEW_STATE.yaml:active_task_id`. The test instead expected
`TASK-20260717__bind_heavy_workflow_task_identity\n` from the task-specific
`TASK_ID` synthetic fixture constant. That value is the accepted prior task,
not the active task. The sole observed failure was therefore caused by a stale
test expectation; resolver behavior was correct.

No state rollback, resolver special case, skip, xfail, output normalization,
or workflow/helper change was used. The test path was the only necessary
functional correction.

## EV-012 — Independent canonical expectation and accepted/active regression

The corrected canonical integration test now:

1. reads `REVIEW_STATE.yaml` bytes directly from the repository;
2. decodes them explicitly as UTF-8;
3. calls `json.loads` in the test, without a resolver function;
4. requires a dictionary top level;
5. extracts `active_task_id` and requires a string;
6. independently applies the literal pattern
   `^TASK-[0-9]{8}__[a-z0-9_]+$` without importing the resolver pattern;
7. requires `ops/<active_task_id>/TASK_STATUS.md` to be a file;
8. invokes the production CLI and requires exit zero, exact
   `active_task_id.encode("ascii") + b"\n"`, and empty stderr.

A separate synthetic test writes both
`TASK-20260717__accepted_task` and `TASK-20260718__active_task`, asserts they
differ, creates only
`ops/TASK-20260718__active_task/TASK_STATUS.md`, confirms the accepted dossier
is absent, and requires exact active-only output with empty stderr. It uses
only its temporary repository. The preexisting task-specific constant remains
clearly labeled as a synthetic fixture identity and is not used by the
canonical expectation.

At `2026-07-18T10:13:04Z`, the corrected test file was 12,281 bytes with
SHA-256
`e2fa689f87286eb3b6b75ac8e06154ffc055c1ca399412534e0b44b7f3607de1`.
The production resolver, whitespace helper, both workflows, and review-state
semantics were unchanged by this correction.

## EV-013 — Corrective verification and cleanup

Required governance, focused, bounded, and complete checks passed:

```text
python -m json.tool REVIEW_STATE.yaml
exit 0; schema 1.0, accepted baseline/head e33c3bf..., accepted task
TASK-20260717__bind_heavy_workflow_task_identity, active task
TASK-20260717__enforce_committed_range_whitespace, prior verdict
ACCEPT WITH FOLLOW-UP, and exactly three ordered OPEN follow-ups

python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier
TASK-20260717__enforce_committed_range_whitespace

python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD
{"base":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970","head":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970","ok":true,"range":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970..e33c3bf121d5bb81b4c63adf704ca9b4ecfea970"}

python tools/validate_schemas.py
exit 0; all six schemas checked

python tools/verify_upstream_snapshot.py
exit 0; 10 expected and observed files, no additions, changes, or omissions

python -m pytest -q tests/unit/test_review_task_id.py
35 passed in 0.97s

python -m pytest -q tests/unit/test_review_range_whitespace.py
36 passed in 22.21s

python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
195 passed in 38.06s

python -m pytest -q --basetemp build/pytest-root
199 passed in 37.23s
```

There were no skips, xfails, or unexpected product failures. The focused and
bounded commands used process-local `PYTEST_ADDOPTS` only to select the absent,
workspace-contained basetemps `build/pytest-review-task-id`,
`build/pytest-range-root`, and `build/pytest-bounded-correction`. The complete
command used explicit MSYS2 paths:

```text
EG_CMAKE=C:\msys64\ucrt64\bin\cmake.exe
EG_CXX=C:\msys64\ucrt64\bin\g++.exe
EG_NINJA=C:\msys64\ucrt64\bin\ninja.exe
EG_MAKE=C:\msys64\usr\bin\make.exe
PATH prefix=C:\msys64\ucrt64\bin;C:\msys64\usr\bin
```

The only intermediate command issues were non-product read-only probes: plain
Git's expected ownership rejection, one unsupported `Get-Date -AsUTC` option
in the first hash formatter, and a default-path `Get-Command` probe that could
not find the unexported MSYS2 tools. Corrected read-only probes succeeded; no
repository file or Git state changed.

Before cleanup, all four exact basetemp paths resolved beneath
`C:\Users\Falker\Desktop\Code\circle\erdos-gyarfas-p14\build\`. Only those
session-created directories were recursively removed and all four were
confirmed absent. Preexisting build directories were not removed. No search,
benchmark, manifest, certificate, counterexample, checkpoint, or retained
test artifact was produced.

## EV-014 — Closing preservation, scope, and hashes

The post-suite closing audit returned:

```text
git diff --check e33c3bf121d5bb81b4c63adf704ca9b4ecfea970 --
exit 0; no whitespace diagnostic

git diff --stat e33c3bf121d5bb81b4c63adf704ca9b4ecfea970 --
7 modified tracked files; 180 insertions, 73 deletions

git diff --name-status e33c3bf121d5bb81b4c63adf704ca9b4ecfea970 --
exactly the seven authorized tracked paths

git status --porcelain=v1 --untracked-files=all
exactly seven authorized modified tracked paths and five authorized untracked
paths

git ls-files --others --exclude-standard
exactly the three current dossier files, whitespace test, and whitespace helper

git diff --cached --name-status --
exit 0; no staged paths
```

The only Git diagnostics were the known unreadable user-global ignore warning.
No Git configuration changed. Protected-path diff and porcelain output were
empty. Their accepted-baseline Git object identities remain:

| Protected path | Git object ID |
| --- | --- |
| `research/CLAIMS_REGISTRY.yaml` | `c770fc2b51c16d575a05fde361403ffbf9c50f22` |
| `research/PRUNING_REGISTRY.md` | `962075aa9f0c48492162bca322195fed802a1a1f` |
| `.github/workflows/heavy-search.yml` | `738d0451076fd59f8b9c22d35709f536c1d2ffc2` |
| `tools/resolve_review_task_id.py` | `1c437bf7fc7e4a07b5b82297c95a501a081d6a78` |
| `third_party/erdos-gyarfas` tree | `35707222c62e2bc14b90f385f593a66799405eba` |
| accepted prior dossier tree | `2aa2235a805dc087ad8af2edc37501fa5da670c1` |
| `tools/make_manifest.py` | `f2b9a2c69b8565ad911066963b5d92639ce67ee1` |
| `tools/verify_manifest.py` | `447f1807d54d09c079bb3fe93ecdb9f3544e952f` |
| `tools/validate_schemas.py` | `dbe17dfd0a40cf8b6ef4100729d04eaa2700fccc` |
| `schemas` tree | `8a9ef3e9453ad68d7720f4e5611d1919f4357c4c` |
| `_TEMPLATES` tree | `ed8de6d1af113502be561e4d53ef6cfb60db706f` |

Post-suite upstream verification again reports 10 expected and observed files
with no additions, changes, or omissions. The canonical resolver still emits
the active task after the status transition. The first 4,544 bytes of the
extended task log still hash to
`890e00b8ea427265fb45b3958dd816e74487bf7fb10962ee058fbd423f5b175e`,
exactly the initial whole-log hash from EV-010.

Closing hashes observed at `2026-07-18T10:18:24Z` were:

| Path | Bytes | Closing SHA-256 |
| --- | ---: | --- |
| `.github/workflows/ci.yml` | 7300 | `a575a899741cc934a5ada5080f2a817b9b3974116bc7541d288341e6fb2083d4` |
| `CURRENT_STATUS.md` | 5009 | `95b2cd78b64c1fe0e550e86b09429e4567cd133f84a8fd79fd4363e445618e7a` |
| `REVIEW_STATE.yaml` | 1577 | `ca0988a6a39f73e5e78c0b8074aadeb2907c5f5943ff65ed86083a77c3354839` |
| `docs/CI.md` | 10062 | `d19d4ff8dcd9993c1f80687600aa2ec91209ca83e5fe55b8a1331d5dffbbe3d2` |
| `research/NEXT_RESEARCH_STEPS.md` | 6046 | `4c83b4a36f9ce6d086d01ec57e9ac9fd8353c2b83979a70112269f2bfb4fb249` |
| `research/REPRODUCIBILITY.md` | 12525 | `fb6bf803b19f5d8171d0b7135d170466373aa08fdd4cbf2545f300a31d164cb3` |
| `tests/unit/test_review_task_id.py` | 12281 | `e2fa689f87286eb3b6b75ac8e06154ffc055c1ca399412534e0b44b7f3607de1` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/TASK_LOG.md` | 9533 | `97ff33422d665ea871771453dbb598f97d37f096f45c3c5c707ff3de7e496e4d` |
| `ops/TASK-20260717__enforce_committed_range_whitespace/TASK_STATUS.md` | 2399 | `ec02b65edf01e501469bf5ee49b0e09c7cdd9113db02bb99c2427686daabf0a6` |
| `tests/unit/test_review_range_whitespace.py` | 16041 | `f8ef07e2bcf3f880e7aca89e1f96fc6cd86fd2f85bac993a95b348de8f134eff` |
| `tools/check_review_range_whitespace.py` | 9358 | `39a682b7ff9192940ac33498460527ec23dfcfc1efa0dacde8c69a74016de6c7` |
| `EVIDENCE.md` before EV-014 | 24455 | `ebc1b9fa4b199ba92847b89ec3b6b08c42a22d44fc4ce0863eafb722a1e9f026` |

Embedding the final evidence file's own digest would change that digest. Its
exact post-EV-014 hash is therefore recomputed in the final read-only audit and
reported in the executor handoff. No file is changed after that audit.

Review-state semantics remain exactly as required: accepted baseline/head
`e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`, accepted task
`TASK-20260717__bind_heavy_workflow_task_identity`, active task
`TASK-20260717__enforce_committed_range_whitespace`, and prior verdict
`ACCEPT WITH FOLLOW-UP`. `RFU-CI-003`, `RFU-SUPPLY-001`, and `RFU-ENV-001`
remain ordered and `OPEN`; `RFU-WORKFLOW-001` remains removed; `RS-001`
remains `NOT STARTED`.

Claim impact is none. No claim or pruning record changed, and no search,
reproduction, certificate, counterexample, theorem, or proof is asserted. All
results are bounded engineering and provenance evidence. Hosted GitHub Actions
remains unobserved, and action immutability and complete environment locking
remain open. The current task ends at `READY_FOR_REVIEW`.
