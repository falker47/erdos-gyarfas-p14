# TASK-20260717__bind_heavy_workflow_task_identity — Evidence

All evidence in this dossier is bounded engineering and provenance evidence.
It establishes no mathematical result, reproduction, exhaustive coverage,
certificate, or proof.

## EV-001 — Startup gate

Commands used process-local `safe.directory` after the initial ownership
warning:

```text
git rev-parse --show-toplevel
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14

git branch --show-current
main

git rev-parse HEAD
0d08a58d87e7aaa5749ed2d3428cc0906a6bade6

git status --porcelain=v1 --untracked-files=all
<empty; only an unreadable user-global ignore warning on stderr>

git merge-base --is-ancestor 0d08a58d87e7aaa5749ed2d3428cc0906a6bade6 HEAD
<exit 0, no stdout>
```

No file or Git configuration changed during the gate.

## EV-002 — Trust boundary design

`REVIEW_STATE.yaml` is decoded as strict JSON from the checkout. The resolver
accepts only schema version `1.0`, a canonical lowercase task ID, and,
when requested, a regular non-symlink status file at the exact repository path
`ops/<active_task_id>/TASK_STATUS.md`. It provides no operator task-ID
input, fallback, or replacement identity. Resolver failure is
fatal before manifest creation.

`active_task_id` is used because it is the canonical versioned identity of the
task whose candidate files and dossier are present in the same checkout;
`accepted_task_id` identifies the prior accepted work and would misattribute
the new scaffold record.

## EV-003 — Initial preservation anchors

Task-start Git object IDs:

```text
research/CLAIMS_REGISTRY.yaml  c770fc2b51c16d575a05fde361403ffbf9c50f22
research/PRUNING_REGISTRY.md    962075aa9f0c48492162bca322195fed802a1a1f
third_party/erdos-gyarfas      35707222c62e2bc14b90f385f593a66799405eba
previous accepted dossier      d4d939f79e049749a203e3e67583c4175fbb9191
```

Final preservation and verification results are in EV-010 and EV-011.

## EV-004 — Mandatory reads and reference map

The following were read in full and in the required order before
implementation: `AGENTS.md`, `start.md`, `CHATGPT_REVIEW_PROTOCOL.md`,
`REVIEW_STATE.yaml`, `CURRENT_STATUS.md`, `PROJECT_KNOWLEDGE.md`, the six
required research governance files, all three files in the accepted prior
dossier, both workflows, all three manifest helpers, the experiment-manifest
schema/template, `docs/CI.md`, and `research/REPRODUCIBILITY.md`.

Relevant tests and fixtures read in full were
`tests/unit/test_manifest.py`, `tests/integration/test_verifier_cli.py`, both
manifest JSON fixtures, their hash payload, and `tests/fixtures/README.md`.
The current dossier was confirmed absent before its authorized creation. Git
history and the empty baseline-to-HEAD diff were also inspected.

An `rg` map covered every requested reference. The obsolete task ID occurred
in the baseline workflow production argument and in historical logs, claims,
fixtures, reproducibility text, and earlier dossiers. Only the production
workflow occurrence was in scope for removal. `--task-id` was consumed only by
the workflow and `tools/make_manifest.py`; `active_task_id` and
`RFU-WORKFLOW-001` were concentrated in review state/governance history; and
`heavy-search-scaffold` named only the manual workflow artifacts and logs.

## EV-005 — Resolver semantics and failure boundary

Success requires all of the following:

1. `--state` resolves inside the script-derived repository root without any
   parent traversal or symlink component;
2. the state is a readable regular file and strict UTF-8 JSON;
3. no JSON object contains duplicate keys and no numeric constant is
   `NaN`, `Infinity`, or `-Infinity`;
4. the top level is an object with `schema_version == "1.0"`;
5. `active_task_id` is a string matching exactly
   `^TASK-[0-9]{8}__[a-z0-9_]+$`;
6. with `--require-dossier`, the exact in-root
   `ops/<active_task_id>/TASK_STATUS.md` is a regular non-symlink file.

On success stdout is exactly the ASCII/UTF-8 task ID plus one LF and exit is
zero. On failure stdout is empty, exit is one, and stderr is one deterministic
`resolve_review_task_id: error: ...` line. There is no task-ID argument,
fallback, environment mutation, or file write. Internal root injection exists
only as a Python function parameter for temporary-directory unit tests; the
CLI root is fixed from the checked-in tool path.

`active_task_id` is the correct field because it identifies the candidate task
and dossier in the same checkout. `accepted_task_id` intentionally identifies
the previous accepted work and would misattribute a candidate scaffold.

## EV-006 — Workflow binding

The workflow runs the resolver before any guard output or manifest creation,
exports its sole stdout value via `GITHUB_ENV`, and later uses:

```text
--task-id "$RESOLVED_TASK_ID"
```

The manifest parameters add exactly these provenance semantics:

```text
task_id_source=REVIEW_STATE.yaml:active_task_id
task_dossier_status_path=ops/${RESOLVED_TASK_ID}/TASK_STATUS.md
review_state_sha256=<SHA-256 read from checkout REVIEW_STATE.yaml>
task_status_sha256=<SHA-256 read from the resolved checkout TASK_STATUS.md>
```

Hash commands fail under `set -euo pipefail` if their real files are absent.
Resolver failure is not suppressed and occurs before manifest creation. The
workflow still uses `project_commit="$GITHUB_SHA"`, classification
`ENGINEERING_ASSUMPTION`, `search_mode=scaffold-only`, explicit P13/P14 and
certifying refusals, `tools/verify_manifest.py`, and `if: always()` for the
manifest/log upload. No upstream or search executable is named or launched.

## EV-007 — Required command results

```text
python -m json.tool REVIEW_STATE.yaml
exit 0; strict resolver subsequently confirmed the same file, with accepted
baseline/head 0d08a58d87e7aaa5749ed2d3428cc0906a6bade6, accepted task
TASK-20260717__harden_surprising_outcome_preservation, active task
TASK-20260717__bind_heavy_workflow_task_identity, verdict
ACCEPT WITH FOLLOW-UP, and four ordered OPEN follow-ups.

python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier
TASK-20260717__bind_heavy_workflow_task_identity

python tools/validate_schemas.py
{"ok": true, "schemas_checked": ["schemas/benchmark-result.schema.json", "schemas/counterexample.schema.json", "schemas/experiment-manifest.schema.json", "schemas/search-certificate.schema.json", "schemas/search-partition.schema.json", "schemas/surprising-process-outcome.schema.json"]}

python tools/verify_upstream_snapshot.py
{"added": [], "changed": [], "expected_file_count": 10, "missing": [], "observed_file_count": 10, "ok": true, "snapshot_path": "third_party/erdos-gyarfas"}

python -m pytest -q tests/unit/test_review_task_id.py
................................                                         [100%]
32 passed in 0.31s

python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
........................................................................ [ 46%]
........................................................................ [ 92%]
............                                                             [100%]
156 passed in 8.80s

python -m pytest -q --basetemp build/pytest-root
........................................................................ [ 45%]
........................................................................ [ 90%]
................                                                         [100%]
160 passed in 16.52s
```

The final full run used the documented explicit MSYS2 tool variables and
runtime path. There were no skips, xfails, searches, or retained test
artifacts.

## EV-008 — Static checks

Observed static results:

```text
PASS: obsolete bootstrap task literal absent from heavy workflow
PASS: no hardcoded --task-id TASK-... in heavy workflow
PASS: heavy workflow contains no upstream/search executable path

resolver invocation: workflow line 77
RESOLVED_TASK_ID export: workflow line 81
manifest producer: workflow line 158
resolved --task-id: workflow line 161
four provenance parameters: workflow lines 174-177
manifest verifier: workflow line 191
always upload: workflow line 194
```

The focused static test also rejects any workflow-dispatch input or input
expression capable of replacing the task identity.

## EV-009 — Claim, follow-up, and verification limits

- Claim effect: none. `research/CLAIMS_REGISTRY.yaml` is byte/Git-blob
  unchanged; no result classification changes.
- Pruning effect: none. `research/PRUNING_REGISTRY.md` is byte/Git-blob
  unchanged and no pruning rule is enabled.
- `RS-001`: `NOT STARTED`.
- `RFU-CI-001`, `RFU-CI-002`: removed after acceptance of the prior task.
- `RFU-WORKFLOW-001`: `OPEN` pending review of this candidate.
- `RFU-CI-003`, `RFU-SUPPLY-001`, `RFU-ENV-001`: unchanged and `OPEN`.
- Hosted GitHub Actions and artifact upload were not executed locally. Static
  workflow checks do not establish hosted behavior, run semantics, search
  completeness, or a mathematical conclusion.

## EV-010 — Final provenance hashes

SHA-256 values observed from the final files:

```text
REVIEW_STATE.yaml
e36b2b6f8fb8abb12844b9a414a43a9e49071ad41f88ab754d6903426e8b4d20

ops/TASK-20260717__bind_heavy_workflow_task_identity/TASK_STATUS.md
aeb3d6604f1159630a417e9479fa5a5f49b6bd21c020fa9dc8529a47f336b6be

.github/workflows/heavy-search.yml
5cbab2f2b55437becc7ca2ac580a9e84f377cad57d0d91d7e7edaf0e8d47e140

tools/resolve_review_task_id.py
affab6ed5d49ccf1ecfa38ee550fe6e23b8d354914190fce4f8e58ae66a4e584

tests/unit/test_review_task_id.py
4ebc27097d8a67c7d12f227a7785ce611a5d7b4bcb461d5e2719e8b236b6e4a4

research/CLAIMS_REGISTRY.yaml
0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c

research/PRUNING_REGISTRY.md
34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a
```

The final claims/pruning Git blob IDs remain respectively
`c770fc2b51c16d575a05fde361403ffbf9c50f22` and
`962075aa9f0c48492162bca322195fed802a1a1f`, exactly matching task-start HEAD.
The upstream tree remains `35707222c62e2bc14b90f385f593a66799405eba`
and the accepted prior dossier tree remains
`d4d939f79e049749a203e3e67583c4175fbb9191`.

## EV-011 — Closing preservation and diff audit

Protected-path `git diff --quiet` checks returned exit zero for claims,
pruning, the upstream snapshot, fast CI, manifest tooling, schemas/templates,
and the entire tracked `ops/` tree. The new dossier is untracked by policy
until the user reviews and commits; porcelain accounts for it explicitly.

The exact task allowlist check passed with six modified tracked paths and five
new paths, totaling the eleven paths listed in `TASK_STATUS.md`. Every new file
has a final LF and no trailing whitespace. `build/pytest-root` was absent after
cleanup.

```text
git diff --check 0d08a58d87e7aaa5749ed2d3428cc0906a6bade6 --
exit 0; no diff-hygiene output

git diff --stat 0d08a58d87e7aaa5749ed2d3428cc0906a6bade6 --
 .github/workflows/heavy-search.yml | 22 +++++++++++--
 CURRENT_STATUS.md                  | 66 +++++++++++++++++---------------------
 REVIEW_STATE.yaml                  | 34 ++++----------------
 docs/CI.md                         | 15 +++++++++
 research/NEXT_RESEARCH_STEPS.md    | 36 ++++++++++-----------
 research/REPRODUCIBILITY.md        | 11 +++++++
 6 files changed, 99 insertions(+), 85 deletions(-)

git diff --name-status 0d08a58d87e7aaa5749ed2d3428cc0906a6bade6 --
M .github/workflows/heavy-search.yml
M CURRENT_STATUS.md
M REVIEW_STATE.yaml
M docs/CI.md
M research/NEXT_RESEARCH_STEPS.md
M research/REPRODUCIBILITY.md

git status --porcelain=v1 --untracked-files=all
 M .github/workflows/heavy-search.yml
 M CURRENT_STATUS.md
 M REVIEW_STATE.yaml
 M docs/CI.md
 M research/NEXT_RESEARCH_STEPS.md
 M research/REPRODUCIBILITY.md
?? ops/TASK-20260717__bind_heavy_workflow_task_identity/EVIDENCE.md
?? ops/TASK-20260717__bind_heavy_workflow_task_identity/TASK_LOG.md
?? ops/TASK-20260717__bind_heavy_workflow_task_identity/TASK_STATUS.md
?? tests/unit/test_review_task_id.py
?? tools/resolve_review_task_id.py
```

The Git warnings concerned only the unreadable user-global ignore file. No Git
configuration was changed; all Git reads used process-local `safe.directory`.

## EV-012 — Recovery-session inherited candidate anchors

The preceding EV-001 through EV-011 were inherited from the earlier executor
session and were treated as unverified candidate assertions at recovery. The
recovery gate at `2026-07-17T16:57:59Z` observed the exact expected root,
branch `main`, HEAD and baseline
`0d08a58d87e7aaa5749ed2d3428cc0906a6bade6`, successful baseline ancestry,
and exactly the eleven allowed dirty paths. Plain Git first failed with the
expected dubious-ownership diagnostic; all successful Git reads used the
process-local `-c safe.directory=...` exception and made no configuration
change. A first hash-collection orchestration command did not start because of
JavaScript quoting; the corrected read-only command produced the anchors
below.

These byte counts, SHA-256 values, and porcelain states were recorded before
the recovery session modified any candidate file:

| Path | Bytes | Initial SHA-256 | Initial Git state |
| --- | ---: | --- | --- |
| `.github/workflows/heavy-search.yml` | 8431 | `5cbab2f2b55437becc7ca2ac580a9e84f377cad57d0d91d7e7edaf0e8d47e140` | ` M` |
| `CURRENT_STATUS.md` | 4522 | `3ca4ebe439d116b1017a6269ec957e417bf60cd2d50393317944829c45598f98` | ` M` |
| `REVIEW_STATE.yaml` | 1882 | `e36b2b6f8fb8abb12844b9a414a43a9e49071ad41f88ab754d6903426e8b4d20` | ` M` |
| `docs/CI.md` | 8409 | `9748cce2e2f467508b2aceea8c3c9b33f8a10c7a81392e60e5b2f760ab7eb959` | ` M` |
| `research/NEXT_RESEARCH_STEPS.md` | 6172 | `630df7c379033401bbf027d43b16661dfb0ba9d4d4ce84435f09c1af1d9ed653` | ` M` |
| `research/REPRODUCIBILITY.md` | 11651 | `0bd4d01aaad1d9a2ba8abc617f031570f5661b3b40e88da1ca5c768f8a7398f6` | ` M` |
| `ops/TASK-20260717__bind_heavy_workflow_task_identity/EVIDENCE.md` | 12206 | `993b0b3306aec7bc64649d1d2ee6b8a89523584f8ab903f163ab13c3fe6b469e` | `??` |
| `ops/TASK-20260717__bind_heavy_workflow_task_identity/TASK_LOG.md` | 5036 | `3697bde73b82e033b4f26b0dba9d6f6950a404c9222a1a1ba3702882ade363a4` | `??` |
| `ops/TASK-20260717__bind_heavy_workflow_task_identity/TASK_STATUS.md` | 3153 | `aeb3d6604f1159630a417e9479fa5a5f49b6bd21c020fa9dc8529a47f336b6be` | `??` |
| `tests/unit/test_review_task_id.py` | 10769 | `4ebc27097d8a67c7d12f227a7785ce611a5d7b4bcb461d5e2719e8b236b6e4a4` | `??` |
| `tools/resolve_review_task_id.py` | 5939 | `affab6ed5d49ccf1ecfa38ee550fe6e23b8d354914190fce4f8e58ae66a4e584` | `??` |

The recovery session next audits the inherited implementation, tests,
documentation, and dossier claims against repository evidence before deciding
whether any correction beyond recovery evidence is necessary.

## EV-013 — Recovery audit of the inherited candidate

Audit checkpoint: `2026-07-17T17:02:23Z`.

1. Already implemented: the resolver is read-only, emits one LF-terminated
   task ID, performs strict JSON duplicate-key and non-finite-constant checks,
   validates the top-level object/schema/canonical ID, contains the state path,
   and requires a regular non-symlink dossier status. The workflow resolves
   before the guard/producer, exports `RESOLVED_TASK_ID`, passes only that value
   to `--task-id`, records the required source/path/two file hashes, retains
   `GITHUB_SHA`, `ENGINEERING_ASSUMPTION`, `scaffold-only`, all P13/P14 and
   certifying refusals, manifest validation, and `if: always()` upload.
2. Incomplete recovery evidence: the inherited dossier had selected final
   hashes but no byte/SHA-256/Git-state anchors for all eleven acquired files.
   EV-012 supplies those anchors and explicitly distinguishes the inherited
   EV-001 through EV-011 from this recovery session.
3. Functional errors found: none in the resolver or workflow. Two test
   robustness gaps remain before correction: the non-finite test exercises
   only `NaN`, not `Infinity` and `-Infinity`; the hardcoded-task assertion
   catches only the exact unquoted `--task-id TASK-` spelling rather than an
   optionally quoted hardcoded task ID.
4. Existing tests: 32 focused tests cover the required valid state,
   deterministic bytes, malformed/duplicate/top-level/schema/missing/type/ID
   cases, traversal, dossier absence/directory/symlink, no writes, canonical
   checkout resolution, resolver ordering/value use, and manual-input absence.
5. Reproducibility: the inherited command ledger names every required command;
   the full-suite tool overrides and runtime paths are recorded explicitly.
   Recovery reruns passed JSON parsing, canonical resolution, all schema and
   snapshot checks, 32 focused tests, 156 bounded tests, and 160 complete tests
   with the recorded MSYS2 environment.
6. Append-only log: the inherited 5,036-byte `TASK_LOG.md` was read and hashed
   before recovery; all recovery chronology is appended after that prefix.
7. State coherence: `TASK_STATUS.md`, `CURRENT_STATUS.md`, and
   `REVIEW_STATE.yaml` agree on task, baseline, prior verdict/accepted task,
   `READY_FOR_REVIEW`, and the four ordered `OPEN` follow-ups. The final status
   will be reasserted only after recovery corrections and closing verification.
8. Premature closure/claim audit: `RFU-WORKFLOW-001` remains `OPEN` pending
   review; the other three follow-ups remain `OPEN`; `RS-001` remains
   `NOT STARTED`; claims, pruning, prior dossiers, protected tooling/workflows,
   and upstream content remain unchanged from task-start HEAD.

The two focused-test gaps are corrected next without changing resolver or
workflow semantics.

## EV-014 — Recovery corrections and final verification

Recovery correction was limited to authorized files:

- `tests/unit/test_review_task_id.py` now parameterizes strict-JSON extension
  rejection over `NaN`, `Infinity`, and `-Infinity` and uses a whitespace- and
  optional-quote-aware regular expression for hardcoded `--task-id TASK-...`
  detection;
- `REVIEW_STATE.yaml:updated_at_utc` is the actually observed
  `2026-07-17T17:04:29Z`; all required baseline, verdict, accepted/active task,
  and ordered follow-up fields are unchanged from the acquired candidate;
- `TASK_STATUS.md` reports the recovery-final 162-test result;
- EV-012 through this section and the corresponding append-only log entries
  distinguish recovery evidence from the inherited dossier.

No production resolver or workflow correction was necessary. Final required
commands after the test and governance edits produced:

```text
python -m json.tool REVIEW_STATE.yaml
exit 0; parsed schema 1.0, all three required baseline/head fields at
0d08a58d87e7aaa5749ed2d3428cc0906a6bade6, prior verdict/task, active task,
observed timestamp, and exactly four ordered OPEN follow-ups

python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier
TASK-20260717__bind_heavy_workflow_task_identity

python tools/validate_schemas.py
{"ok": true, "schemas_checked": ["schemas/benchmark-result.schema.json", "schemas/counterexample.schema.json", "schemas/experiment-manifest.schema.json", "schemas/search-certificate.schema.json", "schemas/search-partition.schema.json", "schemas/surprising-process-outcome.schema.json"]}

python tools/verify_upstream_snapshot.py
{"added": [], "changed": [], "expected_file_count": 10, "missing": [], "observed_file_count": 10, "ok": true, "snapshot_path": "third_party/erdos-gyarfas"}

python -m pytest -q tests/unit/test_review_task_id.py
..................................                                       [100%]
34 passed in 0.43s

python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
........................................................................ [ 45%]
........................................................................ [ 91%]
..............                                                           [100%]
158 passed in 9.24s

python -m pytest -q --basetemp build/pytest-root
........................................................................ [ 44%]
........................................................................ [ 88%]
..................                                                       [100%]
162 passed in 17.48s
```

The complete run used the recorded `EG_CMAKE`, `EG_CXX`, `EG_NINJA`, and
`EG_MAKE` MSYS2 paths and prepended the UCRT64/Unix runtime directories. The
exact resolved `build/pytest-root` path was checked against the intended
workspace path, removed recursively, and confirmed absent.

The corrected static audit returned 16 `PASS` results: obsolete/hardcoded task
IDs absent; resolver ordered before producer; resolved ID exported and used;
manual task-ID input absent; four provenance values present; `GITHUB_SHA`,
`ENGINEERING_ASSUMPTION`, `scaffold-only`, manifest verification, `always()`
upload, and the no-search-executable boundary preserved. The resolver and
producer string offsets were respectively 2,215 and 5,959. The first static
script's check computations ran, but its output formatter used invalid
PowerShell conditional-expression syntax and emitted non-terminating errors;
that run was discarded and the corrected all-pass run is the evidence.

## EV-015 — Recovery preservation, append-only, and claim audit

- Protected diff and porcelain checks were empty for fast CI, manifest
  producer/verifiers/common tooling, experiment schema/template, claims,
  pruning, the accepted prior dossier, and the upstream snapshot.
- Baseline object identities remain: claims blob
  `c770fc2b51c16d575a05fde361403ffbf9c50f22`, pruning blob
  `962075aa9f0c48492162bca322195fed802a1a1f`, accepted-prior-dossier tree
  `d4d939f79e049749a203e3e67583c4175fbb9191`, and upstream tree
  `35707222c62e2bc14b90f385f593a66799405eba`.
- SHA-256 of the first 5,036 bytes of the recovery-extended `TASK_LOG.md` is
  still `3697bde73b82e033b4f26b0dba9d6f6950a404c9222a1a1ba3702882ade363a4`,
  exactly the inherited whole-file hash, proving the inherited log prefix was
  not rewritten or truncated.
- `build/pytest-root` is absent. Artifact roots contain only their tracked
  `.gitkeep` files; `artifacts/workflow-logs` is absent. No search, benchmark,
  manifest, certificate, counterexample, checkpoint, or retained test output
  was produced.
- `RFU-WORKFLOW-001` remains `OPEN` pending review. `RFU-CI-003`,
  `RFU-SUPPLY-001`, and `RFU-ENV-001` remain unchanged and `OPEN`.
  `RFU-CI-001` and `RFU-CI-002` remain removed only by the accepted prior
  task. `RS-001` remains `NOT STARTED`.
- Claim impact is none: no claim or pruning registry edit, new claim,
  classification change, search result, reproduction, certificate,
  counterexample, proof, or theorem. All evidence remains bounded engineering
  and provenance evidence.

Hosted GitHub Actions, its artifact service, immutable action pinning, and
complete environment locking remain unverified/open limitations. Static
workflow inspection and passing local tests do not establish hosted behavior,
search semantics, exhaustive coverage, or a mathematical result.

## EV-016 — Closing file hashes

The following byte counts and SHA-256 values were observed after all substantive
code, governance, status, log, and evidence text above had reached its closing
state. They are the exact handoff hashes for ten paths. For `EVIDENCE.md`, the
listed value is the closing pre-EV-016 anchor: embedding a file's own final
SHA-256 changes that file and makes a literal self-hash impossible. The exact
post-EV-016 `EVIDENCE.md` hash is therefore recomputed by the final read-only
audit and reported out of band in the executor handoff; no file is changed
after that audit.

| Path | Final bytes | Closing SHA-256 |
| --- | ---: | --- |
| `.github/workflows/heavy-search.yml` | 8431 | `5cbab2f2b55437becc7ca2ac580a9e84f377cad57d0d91d7e7edaf0e8d47e140` |
| `CURRENT_STATUS.md` | 4522 | `3ca4ebe439d116b1017a6269ec957e417bf60cd2d50393317944829c45598f98` |
| `REVIEW_STATE.yaml` | 1882 | `8f325cf1c08a6edba1de0f5444cdaf5e8870a2ae6f50d85c846d4dcbccf2f3fd` |
| `docs/CI.md` | 8409 | `9748cce2e2f467508b2aceea8c3c9b33f8a10c7a81392e60e5b2f760ab7eb959` |
| `research/NEXT_RESEARCH_STEPS.md` | 6172 | `630df7c379033401bbf027d43b16661dfb0ba9d4d4ce84435f09c1af1d9ed653` |
| `research/REPRODUCIBILITY.md` | 11651 | `0bd4d01aaad1d9a2ba8abc617f031570f5661b3b40e88da1ca5c768f8a7398f6` |
| `ops/TASK-20260717__bind_heavy_workflow_task_identity/EVIDENCE.md` | 23074 before EV-016 | `428ca751473176842c5d85bf649dde0ee7f6933cd69b2b0237f9e2bb02edcc5b` (pre-EV-016 anchor) |
| `ops/TASK-20260717__bind_heavy_workflow_task_identity/TASK_LOG.md` | 8669 | `b3370536fbaf8b773b9729a21cc3a70aa676d59b6cd431aeff55ffa0e0c5e94f` |
| `ops/TASK-20260717__bind_heavy_workflow_task_identity/TASK_STATUS.md` | 3162 | `6f8daf910747c19b42e75f5ae50b26615e388dc2b555b40c7c9ba4fbc1a8fe6c` |
| `tests/unit/test_review_task_id.py` | 10923 | `8005e5dbd535e9b96174f01b38bddfcee38c530281f76f073253e4363a3a3495` |
| `tools/resolve_review_task_id.py` | 5939 | `affab6ed5d49ccf1ecfa38ee550fe6e23b8d354914190fce4f8e58ae66a4e584` |

Compared with EV-012, the workflow, current-status prose, CI/reproducibility
documentation, research-priority prose, and production resolver are byte
unchanged from the acquired candidate. Recovery changed only the observed
review-state timestamp, strengthened the authorized test, corrected the
current test count, and appended recovery evidence/log chronology.
