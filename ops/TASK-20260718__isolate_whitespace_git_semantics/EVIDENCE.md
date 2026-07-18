# TASK-20260718__isolate_whitespace_git_semantics — Evidence

All evidence in this dossier is bounded CI/governance engineering evidence.
It establishes no mathematical result, reproduction, exhaustive coverage,
certificate, counterexample, theorem, or proof.

## EV-001 — Startup gate

Successful Git reads used only process-local `safe.directory` and produced:

```text
git rev-parse --show-toplevel
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14

git branch --show-current
main

git rev-parse HEAD
ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4

git status --porcelain=v1 --untracked-files=all
<empty; only the known unreadable user-global ignore warning on stderr>

git diff --cached --name-status --
<empty>

git merge-base --is-ancestor \
  e33c3bf121d5bb81b4c63adf704ca9b4ecfea970 HEAD
<exit 0, no stdout>

git --version
git version 2.45.1.windows.1
```

No worktree file, index entry, ref, object, stash, or Git configuration changed
during the gate.

## EV-002 — Cumulative range and mandatory reads

The complete cumulative diff
`e33c3bf121d5bb81b4c63adf704ca9b4ecfea970..ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4`
was read before edits. It contains 12 paths with 1,782 insertions and 73
deletions. The rejected candidate remains intact; this correction does not
reset, revert, or rewrite it.

All 24 required read groups were read in order, including the complete
rejected dossier, complete accepted workflow-identity dossier, current checker
and tests, both relevant workflow/test files, checked-in `.gitattributes`, and
the installed Git HTML documentation under
`C:/Program Files/Git/mingw64/share/doc/git-doc/`.

Installed documentation establishes:

- `git diff --check` takes its error policy from `core.whitespace`;
- the intended defaults are `blank-at-eol`, `space-before-tab`, and
  `blank-at-eof`;
- process `GIT_CONFIG_COUNT` pairs override files but explicit `git -c`
  options override those pairs;
- system/global config can be bypassed through documented environment inputs;
- `$GIT_DIR/info/attributes` has highest precedence, checked-in
  `.gitattributes` follows it, and global/system attributes have lower
  precedence;
- an unset per-path `whitespace` attribute disables notices entirely.

## EV-003 — Task-start preservation anchors

| Protected item | Task-start identity |
| --- | --- |
| `.gitattributes` | SHA-256 `3d4fcd555869954eab9bbe5147d04514f8525dc500e8aa301bc20740a104f040`; blob `00f2ed1b` |
| `.github/workflows/ci.yml` | SHA-256 `a575a899741cc934a5ada5080f2a817b9b3974116bc7541d288341e6fb2083d4`; blob `8321a284` |
| `.github/workflows/heavy-search.yml` | SHA-256 `5cbab2f2b55437becc7ca2ac580a9e84f377cad57d0d91d7e7edaf0e8d47e140`; blob `738d0451` |
| `tools/resolve_review_task_id.py` | SHA-256 `affab6ed5d49ccf1ecfa38ee550fe6e23b8d354914190fce4f8e58ae66a4e584`; blob `1c437bf7` |
| `tests/unit/test_review_task_id.py` | SHA-256 `e2fa689f87286eb3b6b75ac8e06154ffc055c1ca399412534e0b44b7f3607de1`; blob `98071ed9` |
| `research/CLAIMS_REGISTRY.yaml` | SHA-256 `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c`; blob `c770fc2b` |
| `research/PRUNING_REGISTRY.md` | SHA-256 `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a`; blob `962075aa` |
| rejected predecessor dossier | tree `5f92917ee99cc57023e4b290b977c327dfbdc499` |
| accepted workflow-identity dossier | tree `2aa2235a805dc087ad8af2edc37501fa5da670c1` |
| vendored upstream snapshot | tree `35707222c62e2bc14b90f385f593a66799405eba` |

## EV-004 — Trust boundary

The checker will preserve all state/path/revision/ancestry validation and its
explicit `<base>..<head>` range. Its child Git policy is:

```text
core.whitespace=blank-at-eol,space-before-tab,blank-at-eof
core.attributesFile=<platform null device>
```

System/global/process configuration inputs and system/global attribute inputs
are neutralized only in the child environment. The parent environment is not
modified. Checked-in `.gitattributes` remains active. A nonempty or nonregular
`$GIT_DIR/info/attributes` is rejected before the range diff with empty stdout,
nonzero exit, and one byte-deterministic error line.

Implementation, adversarial matrix, exact command output, final preservation,
and limitations are recorded in later sections after verification.

## EV-005 — Implemented child Git semantics

Every child Git command receives a copied environment. Matching is
case-insensitive when removing repository redirects, system/global/process
configuration variables, all `GIT_CONFIG_KEY_*` and `GIT_CONFIG_VALUE_*`
members, `GIT_CONFIG_PARAMETERS`, and inherited attribute-source variables.
The child then receives:

```text
GIT_CONFIG_COUNT=0
GIT_CONFIG_GLOBAL=<platform-null-device>
GIT_CONFIG_SYSTEM=<platform-null-device>
GIT_CONFIG_NOSYSTEM=1
GIT_ATTR_NOSYSTEM=1
GIT_NO_REPLACE_OBJECTS=1
GIT_OPTIONAL_LOCKS=0
LANG=C
LC_ALL=C
```

Command-line configuration, which Git documents as higher precedence than
process injection, supplies `safe.directory`, deterministic path quoting, the
fixed whitespace policy, and a null global attributes file. The committed diff
uses `--attr-source=<resolved-head>` so only checked-in head-tree
`.gitattributes` is the reviewable per-path source below
`$GIT_DIR/info/attributes`. External diff and text conversion are disabled.

Git cannot disable only its repository-local configuration source. The checker
therefore queries effective local keys with includes enabled before and after
the diff. Any `diff.*` key yields exactly:

```text
check_review_range_whitespace: error: repository-local diff configuration is not permitted
```

This closes a reproduced bypass in which checked-in `diff=hostile` and local
`diff.hostile.binary=true` made a text blob binary and suppressed its
whitespace diagnostic. Local `core.whitespace` and `core.attributesFile`
remain safely neutralized rather than rejected.

The actual non-canonicalized Git path returned by
`git rev-parse --git-path info/attributes` is inspected before and after the
diff without modification. A nonempty, unreadable,
nonregular, or symlink entry yields exactly:

```text
check_review_range_whitespace: error: non-versioned Git attributes are not permitted: $GIT_DIR/info/attributes
```

Stdout is empty and exit is one. The diagnostic contains no host-dependent
absolute path. Existing successful compact JSON and state/path/revision/
ancestry error behavior are unchanged.

## EV-006 — Real-Git adversarial matrix

All cases use production `checker.main()` and real temporary Git repositories
with actual commits. They do not mock subprocesses or inspect only source text.

| Source | Hostile setting | Unisolated bad control | Production bad range | Production clean twin |
| --- | --- | ---: | --- | --- |
| local config | `core.whitespace=-trailing-space,-space-before-tab` | exit 0 | nonzero; trailing whitespace reported | exact success JSON |
| supplied global config | same policy in `GIT_CONFIG_GLOBAL` file | exit 0 | nonzero; trailing whitespace reported | exact success JSON |
| supplied system config | same policy in `GIT_CONFIG_SYSTEM` with `NOSYSTEM=0` | exit 0 | nonzero; trailing whitespace reported | exact success JSON |
| process config | `GIT_CONFIG_COUNT=1` plus key/value pair | exit 0 | nonzero; trailing whitespace reported | exact success JSON |
| global attributes | local `core.attributesFile` points to `* -whitespace` | exit 0 | nonzero; trailing whitespace reported | exact success JSON |
| repository info attributes | `.git/info/attributes` contains `* -whitespace` | exit 0 | exact fail-closed diagnostic | exact fail-closed diagnostic |
| local diff driver | checked-in `diff=hostile` plus local `diff.hostile.binary=true` | exit 0 | exact local-config fail-closed diagnostic | exact local-config fail-closed diagnostic |

The clean `info/attributes` twin intentionally fails closed: Git cannot ignore
that highest-precedence unversioned source without also changing metadata or
discarding checked-in attributes, so the range is not evaluated. This is the
explicit exception to clean hostile-source success authorized by the task's
fail-closed requirement.

Additional behavioral cases establish:

- committed blank-at-EOL, space-before-tab, and blank-at-EOF errors fail;
- malformed process config injection is removed rather than causing Git's own
  configuration parser to fail;
- a dirty worktree `.gitattributes` containing `* -whitespace` hides the raw
  control but cannot hide the production committed error;
- a checked-in `tracked.txt -whitespace` remains effective even when the parent
  requests a different `GIT_ATTR_SOURCE`;
- the repository's exact checked-in `.gitattributes` bytes, including
  `third_party/erdos-gyarfas/** -diff`, are asserted;
- a zero-byte regular `info/attributes` is harmless and a directory fails
  closed;
- each hostile case invokes the checker twice and obtains identical bytes;
- observations before and after include the entire synthetic temporary tree,
  explicit object inventory, porcelain status, refs, and parent environment.

An intermediate proposed `core.bigFileThreshold=1` adversary did not hide the
fixture: its raw Git control correctly returned nonzero. That single focused
run reported 57 passed and one failed assertion. The invalid adversary and its
unnecessary production pin were removed; no acceptance claim relies on it.

## EV-007 — Required verification results

```text
python -m json.tool REVIEW_STATE.yaml
exit 0; parsed schema 1.0, accepted baseline e33c3bf..., rejected head
ac9c4c4..., verdict REJECT, accepted bind task, active isolate task, and exactly
three ordered OPEN follow-ups

python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier
TASK-20260718__isolate_whitespace_git_semantics

python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD
{"base":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970","head":"ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4","ok":true,"range":"e33c3bf121d5bb81b4c63adf704ca9b4ecfea970..ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4"}

python tools/validate_schemas.py
{"ok": true, "schemas_checked": ["schemas/benchmark-result.schema.json", "schemas/counterexample.schema.json", "schemas/experiment-manifest.schema.json", "schemas/search-certificate.schema.json", "schemas/search-partition.schema.json", "schemas/surprising-process-outcome.schema.json"]}

python tools/verify_upstream_snapshot.py
{"added": [], "changed": [], "expected_file_count": 10, "missing": [], "observed_file_count": 10, "ok": true, "snapshot_path": "third_party/erdos-gyarfas"}

python -m pytest -q tests/unit/test_review_range_whitespace.py
63 passed in 40.42s

python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
222 passed in 62.51s

python -m pytest -q --basetemp build/pytest-root
226 passed in 65.16s
```

The complete command set `EG_CMAKE`, `EG_CXX`, `EG_NINJA`, and `EG_MAKE` to
the recorded MSYS2 executables and prepended the matching UCRT64 and Unix
runtime directories. No suite reported failures, skips, or xfails.

## EV-008 — Temporary-resource disposition

The complete suite created only its requested workspace basetemp. Before
removal both the resolved and expected paths were exactly:

```text
C:\Users\Falker\Desktop\Code\circle\erdos-gyarfas-p14\build\pytest-root
```

Only that verified path was removed; `EXISTS_AFTER=False`. The supporting
Git-semantics experiment's synthetic
`C:\tmp\egp14_git_semantics_20260718_a` directory was separately removed and
confirmed absent. Focused adversarial repositories were owned and cleaned by
Pytest outside the project tree. No search, benchmark, manifest, certificate,
counterexample, checkpoint, or retained test artifact was produced.

The final bounded basetemp
`C:\Users\Falker\Desktop\Code\circle\erdos-gyarfas-p14\build\pytest-bounded-final`
was likewise resolved exactly, removed, and confirmed absent. Pytest retained
three default temporary roots from the intermediate focused runs. An escalated
read identified only `pytest-59`, `pytest-60`, `pytest-61`, and their
`pytest-current` link with task-time creation timestamps. Exact contained
paths were removed with explicit approval and all four now report `False`.

## EV-009 — Closing scope and preservation

Required closing commands produced:

```text
git diff --check e33c3bf121d5bb81b4c63adf704ca9b4ecfea970 --
exit 0; no whitespace diagnostic

git diff --stat e33c3bf121d5bb81b4c63adf704ca9b4ecfea970 --
12 tracked paths; 2,418 insertions; 86 deletions

git diff --name-status e33c3bf121d5bb81b4c63adf704ca9b4ecfea970 --
exactly the 12 cumulative tracked paths from the accepted baseline

git status --porcelain=v1 --untracked-files=all
seven modified tracked corrective paths and three untracked current-dossier
paths, all authorized

git diff --cached --name-status --
exit 0; no staged paths
```

Task-local comparison against
`ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4` contains exactly seven modified
tracked allowlist paths. Combining those with the three untracked dossier paths
matches the ten-path allowlist exactly. The cumulative 12-path output includes
the rejected candidate, as required; this task neither removes nor rewrites
it.

Protected task-start checks are empty and retain these exact identities:

| Protected path | SHA-256 / Git object |
| --- | --- |
| `.gitattributes` | `3d4fcd555869954eab9bbe5147d04514f8525dc500e8aa301bc20740a104f040` / `00f2ed1bc58cbab1d95b2f9b80ff3bf9e3f07200` |
| `.github/workflows/ci.yml` | `a575a899741cc934a5ada5080f2a817b9b3974116bc7541d288341e6fb2083d4` / `8321a28409b7d81f4b6a83ae17d0e0857072a9f3` |
| `.github/workflows/heavy-search.yml` | `5cbab2f2b55437becc7ca2ac580a9e84f377cad57d0d91d7e7edaf0e8d47e140` / `738d0451076fd59f8b9c22d35709f536c1d2ffc2` |
| `tools/resolve_review_task_id.py` | `affab6ed5d49ccf1ecfa38ee550fe6e23b8d354914190fce4f8e58ae66a4e584` / `1c437bf7fc7e4a07b5b82297c95a501a081d6a78` |
| `tests/unit/test_review_task_id.py` | `e2fa689f87286eb3b6b75ac8e06154ffc055c1ca399412534e0b44b7f3607de1` / `98071ed9f653ac03cc45c4313a1e5a4bbfa85fb1` |
| `research/CLAIMS_REGISTRY.yaml` | `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` / `c770fc2b51c16d575a05fde361403ffbf9c50f22` |
| `research/PRUNING_REGISTRY.md` | `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` / `962075aa9f0c48492162bca322195fed802a1a1f` |
| rejected predecessor dossier | tree `5f92917ee99cc57023e4b290b977c327dfbdc499` |
| accepted workflow-identity dossier | tree `2aa2235a805dc087ad8af2edc37501fa5da670c1` |
| vendored upstream | tree `35707222c62e2bc14b90f385f593a66799405eba` |
| upstream metadata | tree `33a3742d92278b2e29c49f36b7aea17a99632470` |
| schemas | tree `8a9ef3e9453ad68d7720f4e5611d1919f4357c4c` |
| templates | tree `ed8de6d1af113502be561e4d53ef6cfb60db706f` |

The three new dossier files each have final LF and zero trailing-whitespace
lines. Session basetemps, the supporting `C:\tmp` repository, and workflow-log
output are absent. The only untracked paths are the three authorized dossier
files.

## EV-010 — Closing hashes, follow-ups, claims, and limitations

Closing hashes after every non-evidence file reached final content:

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/check_review_range_whitespace.py` | 12,999 | `dd25a91c452dd0c02ba89e614a78e23d651acfa9f06c47970d684768f94bf08d` |
| `tests/unit/test_review_range_whitespace.py` | 29,343 | `3a966fde7241bf2ae828528f5ea34e809e1b88ccdcfd9564a2fe10125f4e33fc` |
| `docs/CI.md` | 12,468 | `73b0e3a55c19d7174dc1ea5e89b63b381a8c1c799a27ec9201e3073b607e63f2` |
| `research/REPRODUCIBILITY.md` | 14,052 | `9fbfd63b033e68ad06de7c8ac9470226d6c281f1d5b006f8023fac2573715199` |
| `REVIEW_STATE.yaml` | 1,560 | `c0b556942f66f76abaa05ec14a0205b472b98c9b5d750f1f378c53514e84b9a1` |
| `CURRENT_STATUS.md` | 4,740 | `cf5d25be88e724fff73592d9b0aafa667e97183cb27d3a7db5b77dfda133660d` |
| `research/NEXT_RESEARCH_STEPS.md` | 6,383 | `bc8ae809dbe92da0b1b2df9e7fb42b08c8e3bbe8c7751d27322693156ff569c1` |
| `TASK_STATUS.md` | 3,172 | `d67492fc5b8f7fc61cb14253eb8190ee46dd7bea473d16e9cf304b561db54adf` |
| `TASK_LOG.md` | 9,916 | `ad6be3c5faf3e9af7316f4efdac0de935ff86d04c29cc8bbca0a84cb7d8a4350` |
| `EVIDENCE.md` before EV-009/EV-010 | 12,218 | `aa5c8a1bd7c19100348ea10f8432cfaf625e7bbb5c0b79eaee4badd02e941e9c` |

Embedding the evidence file's own final digest would change it. Its final
SHA-256 is therefore recomputed in the read-only handoff audit and reported to
the user without another file edit.

`RFU-CI-003`, `RFU-SUPPLY-001`, and `RFU-ENV-001` remain in that order and
`OPEN`. `RFU-CI-003` is not closed before review. `RS-001` remains
`NOT STARTED`.

Claim and pruning impact is none. Both registries are byte/Git-object
identical to task-start HEAD. No search, reproduction, benchmark,
counterexample, certificate, exhaustive result, pruning rule, theorem, or
proof was created or changed.

Limitations:

- hosted GitHub Actions execution and its installed Git version were not
  observed; local behavior is verified with Git `2.45.1.windows.1`;
- the synthetic suite cannot redirect Git's compiled system-attributes path
  without modifying an installation, so system attributes are disabled using
  the installed Git binary's supported `GIT_ATTR_NOSYSTEM` input and the other
  required sources receive direct adversarial execution;
- the before/after guards catch static and persistent local-config or
  `info/attributes` changes, but an actively coordinated transient filesystem
  replacement entirely within the child-process window cannot be excluded
  atomically without modifying or mirroring Git metadata; such concurrent
  mutation is outside this read-only invocation boundary;
- checked-in `.gitattributes` can intentionally alter per-path whitespace or
  binary policy. That is preserved versioned policy, not a non-versioned
  bypass, and remains visible in the cumulative review.

All accepted evidence is bounded engineering evidence. Final task status is
`READY_FOR_REVIEW`.
