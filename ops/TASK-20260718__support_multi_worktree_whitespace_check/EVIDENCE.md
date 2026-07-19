# TASK-20260718__support_multi_worktree_whitespace_check — Evidence

All evidence in this dossier is bounded CI/governance engineering evidence.
It establishes no mathematical result, reproduction, exhaustive coverage,
certificate, counterexample, theorem, proof, or pruning rule.

## EV-001 — Startup gate

Successful project Git reads used only process-local `safe.directory` and
established:

```text
repository root
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14

origin
https://github.com/falker47/erdos-gyarfas-p14.git

branch
main

HEAD and review base
0dd6e5dc1362e866dd806e205750d82695d3c555

git status --porcelain=v1 --untracked-files=all
<empty; only the unreadable user-global ignore warning on stderr>

git diff --cached --name-status --
<empty>

git merge-base --is-ancestor 0dd6e5dc1362e866dd806e205750d82695d3c555 HEAD
exit 0; no stdout

git --version
git version 2.45.1.windows.1
```

No project file, index entry, ref, object, worktree, attribute source, or Git
configuration changed during the gate.

## EV-002 — Installed Git semantics

The installed documentation records system, global, local, worktree, and
command scopes; default multi-source reads; `--show-scope`; and explicit
`--includes`. It says `include.path` inserts included content at the directive,
with relative paths resolved from the including config file. It also says
`config.worktree` is loaded after common local config when
`extensions.worktreeConfig` is enabled, and a linked worktree has a private
Git directory below the common directory.

The `git-config` option text describes `--worktree` as the same as `--local`
when the extension is disabled. The installed Git 2.45.1 binary has a stricter
multi-worktree behavior: the reproduction below returns 128. The chosen
solution therefore reads the effective stack once rather than assuming that a
separate disabled worktree-scope query returns no values.

## EV-003 — Pre-fix reproduction

The controlled repository had exactly two worktrees and a clean nonempty
range:

```text
git worktree list --porcelain
worktree .../build/task-multi-worktree-repro/main
HEAD 9c7f465e2442638e3fd034c5fa18095a22cdb858
branch refs/heads/main

worktree .../build/task-multi-worktree-repro/linked
HEAD 9c7f465e2442638e3fd034c5fa18095a22cdb858
branch refs/heads/linked-check

git config --local --get extensions.worktreeConfig
exit 1; stdout empty; stderr empty

git diff --no-ext-diff --no-textconv --no-color --check \
  aea983f3aa174f02ec82f4472c0eee1a6ad67112..\
  9c7f465e2442638e3fd034c5fa18095a22cdb858 --
exit 0; stdout empty; stderr empty

git config --worktree --includes --name-only --get-regexp \
  '^[dD][iI][fF][fF]\.'
exit 128
stdout: <empty>
stderr:
fatal: --worktree cannot be used with multiple working trees unless the config
extension worktreeConfig is enabled. Please read "CONFIGURATION FILE"
section in "git help worktree" for details

python -c "... checker.main(..., repository_root=<synthetic-main>)"
exit 1
stdout: <empty>
stderr:
check_review_range_whitespace: error: Git failed while validating repository-local diff configuration
```

The checker module was the version at task-start HEAD
`0dd6e5dc1362e866dd806e205750d82695d3c555`. The exact resolved synthetic
root
`C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14/build/task-multi-worktree-repro`
was verified, removed, and reported `exists_after: false`.

## EV-004 — Task-start preservation anchors

| Protected item | Task-start identity |
| --- | --- |
| `.git/config` | 308 bytes; SHA-256 `212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10` |
| `.git/config.worktree` | absent |
| `.git/index` | 16,497 bytes; SHA-256 `723614675939a3df68b27c023867d4952fa3fba4a473b0a87c4784448d9cd61a` |
| `.git/info/attributes` | absent |
| `.gitattributes` | SHA-256 `3d4fcd555869954eab9bbe5147d04514f8525dc500e8aa301bc20740a104f040` |
| `.github/workflows/ci.yml` | SHA-256 `a575a899741cc934a5ada5080f2a817b9b3974116bc7541d288341e6fb2083d4` |
| `.github/workflows/heavy-search.yml` | SHA-256 `5cbab2f2b55437becc7ca2ac580a9e84f377cad57d0d91d7e7edaf0e8d47e140` |
| `research/CLAIMS_REGISTRY.yaml` | SHA-256 `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` |
| `research/PRUNING_REGISTRY.md` | SHA-256 `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` |
| loose-object inventory | 328 files; SHA-256 `94a8c30a50ee6fd0636620462781b16eebd900fd60367426cc966ad75c1abc92` |
| parent environment | 64 variables; SHA-256 `d0e3aeb47be7868ec2dbc4c8d43134aab13feb024b84df2544ce61f74f45713d` |

Task-start refs were the Codex turn-diff base
`cf1b0debe9323e4c2e6b9707f9e8076142cc0090`, local `main` at task-start
HEAD, and `origin/main` at the same HEAD. The project had exactly one worktree.

## EV-005 — Implemented config semantics and trust boundary

The checker now performs exactly one config query before and after the range
diff:

```text
git config --includes --name-only --get-regexp '^[dD][iI][fF][fF]\.'
```

The query runs only through the existing `_run_git` boundary. That boundary
removes inherited repository redirects and system/global/process config
injection, sets `GIT_CONFIG_COUNT=0`, selects null global/system config files,
disables system config, and supplies only authorized command-scope settings.
It therefore sees shared local config plus the current worktree config exactly
when Git activates that source. `include.path` and further effective includes
remain visible. The implementation does not need to parse hostile names or
origins: any output is forbidden.

Accepted query outcomes are deliberately narrow:

- exit one with empty stdout and stderr: no effective `diff.*` key;
- exit zero with any match: existing local-diff fail-closed diagnostic;
- every other result, including parsing/include/query errors: existing generic
  config-validation diagnostic.

The committed diff still uses the fixed whitespace policy,
`--attr-source=<head>`, `--no-ext-diff`, and `--no-textconv`. Checked-in
attributes remain effective. The pre/post `$GIT_DIR/info/attributes` guards
and all state/path/root/revision/ancestry checks are unchanged. No checker
operation writes Git or filesystem state.

## EV-006 — Real-Git test matrix

| Requirement | Real temporary-repository coverage |
| --- | --- |
| Single worktree, disabled, clean | Existing clean-range test now proves `extensions.worktreeConfig` is absent before success. |
| Multiple worktrees, disabled, clean | Extension absent and explicit false, invoked independently from main and linked worktrees. |
| Multiple worktrees, disabled, bad | The same four layouts report committed trailing whitespace. |
| Local `diff.*` direct | Two-worktree, explicit disabled extension, invoked from main and linked. |
| Local `diff.*` through include | Two-worktree included config, invoked from main and linked. |
| Enabled worktree config, no `diff.*` | Clean range invoked from main and linked. |
| Per-worktree `diff.*` direct | Enabled config set in the exact main or linked worktree later checked. |
| Per-worktree `diff.*` through include | Enabled config include set in the exact main or linked worktree later checked. |
| Main worktree execution | Covered across disabled, enabled, local, and per-worktree cases. |
| Linked worktree execution | Covered across disabled, enabled, local, and per-worktree cases. |
| Byte-identical repetition | Every new multi-worktree and external-scope case calls the checker twice and compares the full result tuple. |
| Read-only preservation | Whole temporary tree bytes plus both statuses, all refs, common objects, worktree list, config/attributes/index bytes, and parent environment are equal before and after. |
| Neutralized external scopes | Injected global, system, and process `diff.hostile.binary` is visible to an unisolated control query but not read by the checker. |

The new cases do not mock `subprocess`, and none has a skip or xfail path.
The existing hostile configuration, attributes, path, state, revision,
ancestry, workflow, and determinism cases remain collected.

## EV-007 — Focused verification

```text
python -m pytest -q tests/unit/test_review_range_whitespace.py
........................................................................ [ 85%]
............                                                             [100%]
84 passed in 68.06s (0:01:08)
exit 0
```

This was the final repetition after the result-classification refinement. No
failure, skip, or xfail was reported. This is bounded engineering evidence for
the exact tested layouts only.

## EV-008 — Required governance and broad verification

```text
python -m json.tool REVIEW_STATE.yaml
exit 0; strict JSON contains schema 1.0, accepted baseline/head 0dd6e5d...,
ACCEPT WITH FOLLOW-UP, accepted isolate task, active support task, and ordered
OPEN follow-ups RFU-CI-004, RFU-SUPPLY-001, RFU-ENV-001

python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier
TASK-20260718__support_multi_worktree_whitespace_check
exit 0

python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD
{"base":"0dd6e5dc1362e866dd806e205750d82695d3c555","head":"0dd6e5dc1362e866dd806e205750d82695d3c555","ok":true,"range":"0dd6e5dc1362e866dd806e205750d82695d3c555..0dd6e5dc1362e866dd806e205750d82695d3c555"}
exit 0

python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
243 passed in 79.95s (0:01:19)
exit 0

python -m pytest -q --basetemp build/pytest-root
247 passed in 94.84s (0:01:34)
exit 0

python tools/validate_schemas.py
{"ok": true, "schemas_checked": ["schemas/benchmark-result.schema.json", "schemas/counterexample.schema.json", "schemas/experiment-manifest.schema.json", "schemas/search-certificate.schema.json", "schemas/search-partition.schema.json", "schemas/surprising-process-outcome.schema.json"]}
exit 0

python tools/verify_upstream_snapshot.py
{"added": [], "changed": [], "expected_file_count": 10, "missing": [], "observed_file_count": 10, "ok": true, "snapshot_path": "third_party/erdos-gyarfas"}
exit 0
```

The complete suite set `EG_CMAKE`, `EG_CXX`, `EG_NINJA`, and `EG_MAKE` to
the documented MSYS2 executables and prepended the UCRT64 and Unix runtime
directories. No required test run reported a failure, skip, or xfail.

## EV-009 — Project preservation and cleanup

Task-start and closing observations are identical for:

- `.git/config`: 308 bytes, SHA-256
  `212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10`;
- `.git/config.worktree`: absent;
- `.git/index`: 16,497 bytes, SHA-256
  `723614675939a3df68b27c023867d4952fa3fba4a473b0a87c4784448d9cd61a`;
- `$GIT_DIR/info/attributes`: absent;
- `.gitattributes`, both workflows, claims, and pruning: the EV-004 hashes;
- refs: the same Codex capture base, local main, and origin/main object IDs;
- objects: 328 loose files with canonical inventory SHA-256
  `94a8c30a50ee6fd0636620462781b16eebd900fd60367426cc966ad75c1abc92`;
- parent environment: 64 variables with canonical SHA-256
  `d0e3aeb47be7868ec2dbc4c8d43134aab13feb024b84df2544ce61f74f45713d`;
- project worktrees: exactly the original main worktree at task-start HEAD.

The test observation helper separately proves byte identity for each synthetic
repository's full temporary tree, both worktree statuses, both indexes,
common objects, refs, config, attributes, worktree list, and parent
environment across two checker invocations.

Cleanup performed only after absolute-path validation:

- workspace reproduction:
  `C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14/build/task-multi-worktree-repro`;
- complete-suite basetemp, after each run:
  `C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14/build/pytest-root`;
- each task-time pair `pytest-0`, `pytest-1`, and `pytest-current` below
  `C:/Users/Falker/AppData/Local/Temp/pytest-of-Falker`, after approved reads;
- both abandoned inline-harness directory prefixes below `C:/tmp`.

Final checks report the two workspace paths absent and zero
`egp14_prefx_multi_worktree_*` entries below `C:/tmp`. Current Codex app
background Git processes were identified by command line and left untouched;
they are not test artifacts.

## EV-010 — Claim boundary, follow-ups, and limitations

`RFU-CI-004`, `RFU-SUPPLY-001`, and `RFU-ENV-001` remain in that order and
`OPEN`. `RFU-CI-003` is absent. Direct JSON-object comparison with task-start
state confirms `RFU-SUPPLY-001` and `RFU-ENV-001` are unchanged. `RS-001`
remains `NOT STARTED`.

Claims and pruning are unchanged by both SHA-256 and Git object identity. No
search, reproduction, benchmark, counterexample, certificate, exhaustive
result, pruning rule, theorem, or proof was created or changed.

Residual limitations:

- hosted GitHub Actions and its installed Git were not executed; local
  multi-worktree evidence uses Git `2.45.1.windows.1`;
- the pre/post guards detect static and persistent config/attribute changes,
  but do not make a concurrently coordinated transient filesystem replacement
  atomic; this existing read-only trust-boundary limit is unchanged;
- checked-in `.gitattributes` remains intentional reviewable per-path policy;
- a physically present but inactive `config.worktree` is not read when the
  extension is false, matching Git's effective config semantics;
- the two initial inline pipeline timeouts are a harness/tooling anomaly and
  are not product evidence; the direct reproduction and all acceptance tests
  completed normally.

All accepted evidence is bounded CI/governance engineering evidence only.

## EV-011 — Closing scope, whitespace, and static audit

```text
git diff --check 0dd6e5dc1362e866dd806e205750d82695d3c555 --
exit 0; no whitespace diagnostic

git diff --stat 0dd6e5dc1362e866dd806e205750d82695d3c555 --
7 tracked paths; 437 insertions; 114 deletions

git diff --name-status 0dd6e5dc1362e866dd806e205750d82695d3c555 --
M CURRENT_STATUS.md
M REVIEW_STATE.yaml
M docs/CI.md
M research/NEXT_RESEARCH_STEPS.md
M research/REPRODUCIBILITY.md
M tests/unit/test_review_range_whitespace.py
M tools/check_review_range_whitespace.py

git status --porcelain=v1 --untracked-files=all
the same seven modified tracked paths plus exactly the three current-dossier
paths, all authorized

git diff --cached --name-status --
exit 0; no staged paths
```

Git also emitted only the known warning that the sandbox identity cannot read
the user's global ignore file. It did not change Git configuration. Because
`git diff --check` does not inspect untracked dossiers, a separate UTF-8 byte
audit checked all ten files: every file has final LF and zero lines ending in
space or tab.

Static final-source results:

```text
production "--worktree" option count: 0
pre/post effective diff-config guard calls: 2
pre/post info/attributes guard calls: 2
--attr-source=<head>: present
--no-ext-diff: present
--no-textconv: present
new skip/xfail additions: 0
```

Combining the seven tracked paths with the three untracked dossier paths equals
the ten-path allowlist exactly. No workflow, upstream, resolver, claim,
pruning, manifest, schema, certificate, benchmark, graph verifier, or search
path changed.

## EV-012 — Closing file hashes

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/check_review_range_whitespace.py` | 12,886 | `858662bd40a3ddd8ff3c89a3819bada8c053be64a95cf9585e92d569dfd90c09` |
| `tests/unit/test_review_range_whitespace.py` | 37,513 | `0d2c33fbeeb215452fbedf91ff263766f7a5bcf4af86f119660f829dbee3e80e` |
| `docs/CI.md` | 14,147 | `1d13e5272ca5c153b0bd6d8529ca7a6f7cb5abdf6b47e521d8accd713ac2ca09` |
| `research/REPRODUCIBILITY.md` | 15,178 | `8ce2ef95fce99ebf5e7b2566ad1ee6e1087fafde8492ddef0e08c14bec9294bf` |
| `REVIEW_STATE.yaml` | 1,781 | `d752ea78d880a16b6a6d3cf2ddd267692beaba44bab5a4ba380593a0b9557401` |
| `CURRENT_STATUS.md` | 4,946 | `1e761f0290157afd9d80f704ed04ddcb0f6a7ee643593701c0f107014981913d` |
| `research/NEXT_RESEARCH_STEPS.md` | 6,269 | `0dd964a428032d97aff4a0ee1de32b4b66d866fec5393134f899bd9b9470541e` |
| `TASK_STATUS.md` | 2,377 | `3288cbed5b841d3a22b1e8e00ea5e1c479906ea3aec67588256ab43366ce0458` |
| `TASK_LOG.md` | 8,472 | `1a445b1031232209fda8708563734fc74100ec0ae63e53c5c81e1879b4ecf040` |
| `EVIDENCE.md` before EV-012 | 15,149 | `a538ae846b8b9d0f6fd379d00572da577a6387c6fea6a7b0b85a4eced535ff01` |

Embedding this file's own final digest would change it. Its final SHA-256 is
therefore computed in the closing read-only audit and reported at handoff
without another file edit.
