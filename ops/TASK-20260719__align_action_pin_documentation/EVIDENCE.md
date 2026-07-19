# TASK-20260719__align_action_pin_documentation - Evidence

All evidence in this dossier is documentation, review-governance, and bounded
engineering evidence. It establishes no mathematical result, reproduction,
exhaustive coverage, certificate, counterexample, theorem, proof, or pruning
rule.

## EV-001 - Startup gate

An initial sandboxed read-only Git batch exited `1` on Git's
dubious-ownership check. No `safe.directory` entry or other configuration was
added. Successful read-only gate commands ran through the repository owner's
execution boundary and produced:

```text
git rev-parse --show-toplevel
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
exit 0

git branch --show-current
main
exit 0

git rev-parse HEAD
265c1474da9e2b91b6779281289eb23129edac33
exit 0

git status --short
<no entries>
exit 0

git merge-base --is-ancestor \
  265c1474da9e2b91b6779281289eb23129edac33 HEAD
<no stdout>
exit 0
```

Thus branch, task-start HEAD, declared review baseline, ancestry, worktree, and
index satisfied the mandatory gate. `Test-Path` confirmed that the current
task dossier and both task-specific pytest basetemp directories were absent.

## EV-002 - Mandatory inputs and accepted implementation

The following files were read in the required order before modification:

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
13. `ops/TASK-20260719__pin_github_actions_immutable_shas/TASK_STATUS.md`
14. `ops/TASK-20260719__pin_github_actions_immutable_shas/TASK_LOG.md`
15. `ops/TASK-20260719__pin_github_actions_immutable_shas/EVIDENCE.md`
16. `.github/workflows/ci.yml`
17. `.github/workflows/heavy-search.yml`
18. `tools/check_github_action_pins.py`
19. `tests/unit/test_github_action_pins.py`
20. `docs/CI.md`
21. `research/REPRODUCIBILITY.md`

Relevant Git history was then inspected with `git log`, `git show --stat`, and
the prior accepted range's changed-file list. Commit
`265c1474da9e2b91b6779281289eb23129edac33` exists on `main`, has subject
`ci: pin GitHub Actions to immutable SHAs`, and contains the twelve paths in
the accepted task dossier. The task prompt records its verdict as
`ACCEPT WITH FOLLOW-UP`.

Direct workflow inspection, rather than the stale description, established
that the two workflow files contain eleven external Action references. Each of
the three `actions/upload-artifact` occurrences uses commit
`ea165f8d65b6e75b540449e92b4886f43607fa02` and explanatory release comment
`# v4.6.2`.

## EV-003 - Exact correction and authorized scope

Historical documentation wording, quoted only to identify the defect and not
as active configuration, began:

```text
The last two job steps use `actions/upload-artifact@v4` ...
```

The corrected wording states:

```text
The last two compiler-job steps use the official `actions/upload-artifact`
release `v4.6.2`, pinned to commit
`ea165f8d65b6e75b540449e92b4886f43607fa02`, ...
The adjacent `# v4.6.2` release comment is explanatory and non-operative;
GitHub selects the Action from the repository and commit before that comment.
```

This identifies the repository, exact release, immutable commit, and comment
semantics while leaving the existing detailed pin table as the canonical
identity summary. No unrelated `docs/CI.md` description changed.

The exact authorized change set is:

- `docs/CI.md`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260719__align_action_pin_documentation/TASK_STATUS.md`
- `ops/TASK-20260719__align_action_pin_documentation/TASK_LOG.md`
- `ops/TASK-20260719__align_action_pin_documentation/EVIDENCE.md`

## EV-004 - Task-start hashes

The four existing files authorized for modification had these task-start
bytes and SHA-256 hashes. The three new dossier files were absent.

| Modified path | Initial bytes | Initial SHA-256 |
| --- | ---: | --- |
| `docs/CI.md` | 16,864 | `0ca2957ba48cc1f1737dd9022fe4b6a612234819c881c30be75c49c9a0505742` |
| `REVIEW_STATE.yaml` | 1,291 | `69619d27039ee841ba96a8bf42ba5287de0bfb07b2898877cd5d65e72c3985b4` |
| `CURRENT_STATUS.md` | 5,476 | `40fa2b3a8b53ad7e2c2990dc55e699293e1081c78f9f3bf53aae047fde5da081` |
| `research/NEXT_RESEARCH_STEPS.md` | 6,198 | `5e03e175176aa3772d7fcef2d7fb8b777ce609321c457d3e1472881648310db4` |
| `ops/TASK-20260719__align_action_pin_documentation/TASK_STATUS.md` | absent | absent |
| `ops/TASK-20260719__align_action_pin_documentation/TASK_LOG.md` | absent | absent |
| `ops/TASK-20260719__align_action_pin_documentation/EVIDENCE.md` | absent | absent |

Protected task-start anchors were:

| Protected path | Initial bytes | Initial SHA-256 |
| --- | ---: | --- |
| `.git/config` | 308 | `212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10` |
| `.git/index` | 17,650 | `7adf17f5bc45a1e061e1c675b0a5ee1144d950053b626a9672dea00e5f643662` |
| `.github/workflows/ci.yml` | 7,780 | `7bfef1f1d09a46bf7b0c1bd85eb19c44cec75071d943ce74dddaa88c17eaf809` |
| `.github/workflows/heavy-search.yml` | 8,572 | `3af7eb1ddf7c12940f2251ac38a30115e29530b75e304e981b254149921cc803` |
| `tools/check_github_action_pins.py` | 15,603 | `34cdb531193f0e46d85c736d12a5d0a67ff47336b8040d2cca369683439f0d77` |
| `tests/unit/test_github_action_pins.py` | 15,149 | `4474418c44cc3d6310a362f753a77bcbf76b3bc8b63f87d2658c270e42536822` |
| `research/REPRODUCIBILITY.md` | 17,670 | `dba71c9cd31d92ce012371d8b0c02a84eac0d82e2968dde43a2861a9b2d08b18` |
| `PROJECT_KNOWLEDGE.md` | 4,836 | `ca4a8764e8a4f50cb92a6412b190147d4568c70c525aefebcdb3c9d58ebde09c` |
| `research/CLAIMS_REGISTRY.yaml` | 5,495 | `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` |
| `research/PRUNING_REGISTRY.md` | 3,160 | `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` |
| accepted `TASK_STATUS.md` | 2,707 | `ba4bb26966226b457da6be4360f68d15430707366b2d5dfd2ff35d0ca7d0a9f6` |
| accepted `TASK_LOG.md` | 7,207 | `d624fadc1f2f67d71ae0fe86a08cadfaaa052d4ab82ce1dab02fade20699aa0b` |
| accepted `EVIDENCE.md` | 16,344 | `5d2cfb17500eaa8e290aeb580fd746592f29d7791885d6f5777a06e09de3a060` |
| `upstream/README.md` | 5,188 | `29daba524345584e837b8b4d396358f0243956e4c7f31b885a874e5003532e0c` |
| `upstream/UPSTREAM_PROVENANCE.json` | 4,468 | `0fbad279d79b61fbdd29a0b9f3fabbdfd09d41a3aaf546a11434ec52413439b5` |
| `upstream/UPSTREAM_REFS.json` | 1,528 | `562a5c8b9faad3fe2f7c80f97e262f14a51332eacc4da1ddc9b0ed0fff619130` |

The accepted-dossier labels above resolve under
`ops/TASK-20260719__pin_github_actions_immutable_shas/`.

## EV-005 - State, pin, and test verification

State and documentation commands produced:

```text
python -m json.tool REVIEW_STATE.yaml
exit 0; strict JSON contains baseline/head/accepted baseline 265c1474...,
accepted pin task, active documentation task, RFU-DOC-001 OPEN, and
RFU-ENV-001 OPEN

python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier
TASK-20260719__align_action_pin_documentation
exit 0

python -c "from pathlib import Path; text=Path('docs/CI.md').read_text(encoding='utf-8'); assert 'actions/upload-artifact@v4' not in text; assert 'ea165f8d65b6e75b540449e92b4886f43607fa02' in text"
<no stdout>
exit 0
```

The real pin validator produced:

```text
python tools/check_github_action_pins.py
ok=true; workflow_count=2; external_reference_count=11
three actions/upload-artifact records use
ea165f8d65b6e75b540449e92b4886f43607fa02
exit 0
```

Focused verification was:

```text
python -m pytest -q tests/unit/test_github_action_pins.py \
  --basetemp build/pytest-root-pins
44 passed in 0.62s
exit 0; no failure, skip, or xfail
```

The first complete run used the exact requested Python command without native
tool overrides:

```text
python -m pytest -q --basetemp build/pytest-root
287 passed, 4 skipped in 83.90s
exit 0; no failure or xfail
```

A focused diagnostic explained every skip:

```text
python -m pytest -q tests/integration/test_upstream_build.py -rs \
  --basetemp build/pytest-root
4 skipped in 1.45s
exit 0
```

One skip required `make` on `PATH`; three required `cmake`. Inspection of the
test module confirmed the supported explicit overrides, and `Test-Path`
returned `True` for the documented MSYS2 CMake, GCC, Ninja, and Make
executables.

The first toolchain-enabled full rerun exited `1` because pytest could not
remove its task-created basetemp and reported repeated `PermissionError:
[WinError 5]` fixture-setup errors. No code assertion failure was identified,
the output was truncated, and that run is not counted as a successful suite.
The exact absolute basetemp was resolved beneath repository `build/`.
Sandboxed removal exited `1` with access denied; removal through the approved
repository-owner boundary exited `0`, and absence was confirmed.

The terminal complete-suite result used these exact process-local overrides:

```text
$env:EG_CMAKE='C:\msys64\ucrt64\bin\cmake.exe'
$env:EG_CXX='C:\msys64\ucrt64\bin\g++.exe'
$env:EG_NINJA='C:\msys64\ucrt64\bin\ninja.exe'
$env:EG_MAKE='C:\msys64\usr\bin\make.exe'
python -m pytest -q --basetemp build/pytest-root
291 passed in 88.08s
exit 0; no failure, skip, or xfail
```

The initial four skips are therefore explained local tool-discovery outcomes,
and the terminal run exercised the entire collected suite with the same
documented toolchain used by the accepted pin task.

## EV-006 - Canonical checks and current scope

```text
python tools/validate_schemas.py
ok=true; 6 schemas checked
exit 0

python tools/verify_upstream_snapshot.py
ok=true; expected_file_count=10; observed_file_count=10;
added=[]; changed=[]; missing=[]
exit 0

python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD
ok=true; base=head=265c1474da9e2b91b6779281289eb23129edac33
range=265c1474da9e2b91b6779281289eb23129edac33..265c1474da9e2b91b6779281289eb23129edac33
exit 0

git diff --check
<no stdout>
exit 0
```

The range-whitespace result checks a committed empty range because the new
accepted baseline equals task-start HEAD. It validates state resolution and
that exact committed range, not the worktree candidate. `git diff --check`
checks the four tracked worktree modifications, while the three untracked
dossier files require the separate closing byte audit.

Current scope inspection before dossier closure reports:

```text
git status --short --untracked-files=all
 M CURRENT_STATUS.md
 M REVIEW_STATE.yaml
 M docs/CI.md
 M research/NEXT_RESEARCH_STEPS.md
?? ops/TASK-20260719__align_action_pin_documentation/EVIDENCE.md
?? ops/TASK-20260719__align_action_pin_documentation/TASK_LOG.md
?? ops/TASK-20260719__align_action_pin_documentation/TASK_STATUS.md

git diff --name-only
CURRENT_STATUS.md
REVIEW_STATE.yaml
docs/CI.md
research/NEXT_RESEARCH_STEPS.md

git diff --cached --name-only
<no entries>
```

This is exactly the seven-path allowlist when untracked files are expanded.
The terminal repeat produced the same path sets and empty staged output.
Automated set comparison reported `expected_count=7`, `actual_count=7`, and
`ok=true`. Root, branch, HEAD, ancestry, and `git diff --check` were also
repeated successfully after status became `READY_FOR_REVIEW`.

A terminal strict-byte audit covered all seven authorized paths. Every file is
valid UTF-8 without BOM or NUL, ends with LF, contains no bare CR, and has zero
trailing-whitespace lines. The three new dossier files and the other three
modified tracked files are LF-only. The checked-out
`research/NEXT_RESEARCH_STEPS.md` retains valid mixed LF/CRLF bytes; no line
contains a bare CR, and Git normalization plus `git diff --check` accept the
file. Earlier audit-script variants that failed or emitted PowerShell overload
diagnostics were discarded and are recorded in `TASK_LOG.md`; the terminal
audit used terminating errors and exited `0`.

Both task-created pytest directories were absent initially, were resolved
inside repository `build/` before removal, and are absent after cleanup:

```text
Test-Path build/pytest-root-pins
False

Test-Path build/pytest-root
False
```

## EV-007 - Protected state, limitations, and classification

Every protected anchor has the same task-start and terminal bytes and SHA-256:

| Protected path | Bytes | Initial and final SHA-256 |
| --- | ---: | --- |
| `.git/config` | 308 | `212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10` |
| `.git/index` | 17,650 | `7adf17f5bc45a1e061e1c675b0a5ee1144d950053b626a9672dea00e5f643662` |
| `.github/workflows/ci.yml` | 7,780 | `7bfef1f1d09a46bf7b0c1bd85eb19c44cec75071d943ce74dddaa88c17eaf809` |
| `.github/workflows/heavy-search.yml` | 8,572 | `3af7eb1ddf7c12940f2251ac38a30115e29530b75e304e981b254149921cc803` |
| `tools/check_github_action_pins.py` | 15,603 | `34cdb531193f0e46d85c736d12a5d0a67ff47336b8040d2cca369683439f0d77` |
| `tests/unit/test_github_action_pins.py` | 15,149 | `4474418c44cc3d6310a362f753a77bcbf76b3bc8b63f87d2658c270e42536822` |
| `research/REPRODUCIBILITY.md` | 17,670 | `dba71c9cd31d92ce012371d8b0c02a84eac0d82e2968dde43a2861a9b2d08b18` |
| `PROJECT_KNOWLEDGE.md` | 4,836 | `ca4a8764e8a4f50cb92a6412b190147d4568c70c525aefebcdb3c9d58ebde09c` |
| `research/CLAIMS_REGISTRY.yaml` | 5,495 | `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` |
| `research/PRUNING_REGISTRY.md` | 3,160 | `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` |
| accepted `TASK_STATUS.md` | 2,707 | `ba4bb26966226b457da6be4360f68d15430707366b2d5dfd2ff35d0ca7d0a9f6` |
| accepted `TASK_LOG.md` | 7,207 | `d624fadc1f2f67d71ae0fe86a08cadfaaa052d4ab82ce1dab02fade20699aa0b` |
| accepted `EVIDENCE.md` | 16,344 | `5d2cfb17500eaa8e290aeb580fd746592f29d7791885d6f5777a06e09de3a060` |
| `upstream/README.md` | 5,188 | `29daba524345584e837b8b4d396358f0243956e4c7f31b885a874e5003532e0c` |
| `upstream/UPSTREAM_PROVENANCE.json` | 4,468 | `0fbad279d79b61fbdd29a0b9f3fabbdfd09d41a3aaf546a11434ec52413439b5` |
| `upstream/UPSTREAM_REFS.json` | 1,528 | `562a5c8b9faad3fe2f7c80f97e262f14a51332eacc4da1ddc9b0ed0fff619130` |

The accepted-dossier labels resolve below
`ops/TASK-20260719__pin_github_actions_immutable_shas/`. In addition to the
hash comparison, `git diff --quiet HEAD --` over every protected tracked path,
`upstream`, and `third_party` exited `0`; the independent upstream verifier
confirmed the full ten-file snapshot. Direct JSON-object comparison against
`HEAD:REVIEW_STATE.yaml` confirmed that `RFU-ENV-001` is identical,
`RFU-SUPPLY-001` is absent from pending follow-ups, and `RFU-DOC-001` remains
`LOW` and `OPEN`.

Limitations and residual boundaries are:

- committed-range whitespace verification covers the empty accepted range,
  not current worktree bytes; tracked `git diff --check` and the separate
  untracked dossier audit cover that candidate boundary;
- hosted GitHub Actions execution was not observed locally;
- `RFU-DOC-001` stays `OPEN` until review of this candidate;
- `RFU-ENV-001` stays separately `OPEN`; no environment lock was attempted;
- the explained four-skip run and the basetemp permission failure are retained
  as environment observations and are not substituted for the terminal
  291-test success;
- no P13/P14 run, upstream reproduction, exhaustive computation, certificate,
  counterexample, theorem, proof, claim upgrade, or pruning change occurred.

Observed commands, outputs, file identities, and hashes are bounded
documentation/governance engineering evidence and `EMPIRICAL_OBSERVATION`.
They have no mathematical implication. Final task status is
`READY_FOR_REVIEW`; no next task was started.

## EV-008 - Closing modified-file hashes

The task-start values for the same paths are in EV-004. These are the terminal
bytes and SHA-256 hashes for every modified file except the unavoidable
self-reference qualification on the final row:

| Modified path | Final bytes | Final SHA-256 |
| --- | ---: | --- |
| `docs/CI.md` | 17,114 | `30c909b0ae861aed9d03ebed31b1edf7a1b5d24b4618edff5276965d5ecb169d` |
| `REVIEW_STATE.yaml` | 1,249 | `c04e7becbd5f984f8becf809027adc3131d644ccf19a299e02c23b2bf75164fb` |
| `CURRENT_STATUS.md` | 5,929 | `862bf3296550bfdb6ddf56cab20e6a7d71db2a136c23ab4c4a5ec1fa5eb4890d` |
| `research/NEXT_RESEARCH_STEPS.md` | 5,831 | `dec299c222e5a001505761bad8327c4759d1efc80a3b279313efb7c9aafe3152` |
| `ops/TASK-20260719__align_action_pin_documentation/TASK_STATUS.md` | 4,025 | `f1c321916f252cb0c5dc53d94a2d8159b3de94cee4e8c8b40111b9662f1ef7ab` |
| `ops/TASK-20260719__align_action_pin_documentation/TASK_LOG.md` | 8,494 | `bc5aaad24b63276f0ef7d87d5f30654d6445d674476a03bcaedd3b21ac030e1e` |
| `EVIDENCE.md` immediately before EV-008 | 15,734 | `d54d150a2fbbad13a395ad8034a99547692da84cc2b228ebe1fa63517ec16a68` |

`EVIDENCE.md` cannot contain its own post-edit digest without changing that
digest. Its actual final bytes and SHA-256 are therefore computed after this
last edit and reported in the Codex handoff; no placeholder or invented hash
is used.
