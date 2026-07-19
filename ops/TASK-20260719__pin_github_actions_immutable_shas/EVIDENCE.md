# TASK-20260719__pin_github_actions_immutable_shas - Evidence

All evidence in this dossier is bounded supply-chain, CI, and reproducibility
engineering evidence. It establishes no mathematical result, reproduction,
exhaustive coverage, certificate, counterexample, theorem, proof, or pruning
rule.

## EV-001 - Startup gate and task-start preservation

Plain Git first reported dubious ownership. No Git configuration changed.
Every successful project Git read used only the process-local option
`-c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`.
The mandatory gate established:

```text
git rev-parse --show-toplevel
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14

git remote get-url origin
https://github.com/falker47/erdos-gyarfas-p14.git

git branch --show-current
main

git rev-parse HEAD
dde4e6cbd06be8ebc8192097930f40b06cf2f9f6

git status --short
<no entries; only the sandbox warning about the unreadable user-global ignore>

git diff --cached --name-status --
<no entries>

git merge-base --is-ancestor \
  dde4e6cbd06be8ebc8192097930f40b06cf2f9f6 HEAD
exit 0; stdout empty
```

The root, origin, `main` branch, task-start HEAD, required baseline, ancestry,
empty worktree, and empty index therefore matched the task preconditions. The
current dossier did not exist before the gate. Exactly two workflow YAML files
existed and contained eleven active external references: checkout four times,
setup-python four times, and upload-artifact three times.

Task-start Git-state anchors were:

| Protected item | Bytes | SHA-256 |
| --- | ---: | --- |
| `.git/config` | 308 | `212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10` |
| `.git/index` | 16,985 | `242c346f8d2438ce4f109c0c5b321d55315600f25e4fa97264a07194a39806b3` |
| `.gitattributes` | 193 | `3d4fcd555869954eab9bbe5147d04514f8525dc500e8aa301bc20740a104f040` |
| `.github/workflows/ci.yml` | 7,300 | `a575a899741cc934a5ada5080f2a817b9b3974116bc7541d288341e6fb2083d4` |
| `.github/workflows/heavy-search.yml` | 8,431 | `5cbab2f2b55437becc7ca2ac580a9e84f377cad57d0d91d7e7edaf0e8d47e140` |
| `research/CLAIMS_REGISTRY.yaml` | 5,495 | `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` |
| `research/PRUNING_REGISTRY.md` | 3,160 | `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` |
| `PROJECT_KNOWLEDGE.md` | 4,836 | `ca4a8764e8a4f50cb92a6412b190147d4568c70c525aefebcdb3c9d58ebde09c` |
| `upstream/UPSTREAM_PROVENANCE.json` | 4,468 | `0fbad279d79b61fbdd29a0b9f3fabbdfd09d41a3aaf546a11434ec52413439b5` |

## EV-002 - Official release and commit resolution

The resolution window was 2026-07-19T01:18:16.853Z through
2026-07-19T01:20:55Z UTC. Only the official Git remotes, GitHub release pages,
and GitHub REST objects below supplied identities. No blog, third-party
workflow, or copied snippet supplied a SHA.

Exact ref queries were:

```text
git ls-remote https://github.com/actions/checkout.git \
  refs/tags/v4 refs/tags/v4.3.1 'refs/tags/v4.3.1^{}'
git ls-remote https://github.com/actions/setup-python.git \
  refs/tags/v5 refs/tags/v5.6.0 'refs/tags/v5.6.0^{}'
git ls-remote https://github.com/actions/upload-artifact.git \
  refs/tags/v4 refs/tags/v4.6.2 'refs/tags/v4.6.2^{}'
```

The exact outputs were:

```text
34e114876b0b11c390a56381ad16ebd13914f8d5  refs/tags/v4
34e114876b0b11c390a56381ad16ebd13914f8d5  refs/tags/v4.3.1
a26af69be951a213d495a4c3e4e4022e16d87065  refs/tags/v5
a26af69be951a213d495a4c3e4e4022e16d87065  refs/tags/v5.6.0
ea165f8d65b6e75b540449e92b4886f43607fa02  refs/tags/v4
ea165f8d65b6e75b540449e92b4886f43607fa02  refs/tags/v4.6.2
```

No `^{}` row was returned for any exact tag. Official GitHub ref objects also
reported `object.type=commit`, so each exact tag is lightweight and its peel
identity is the displayed commit. In every case the floating major tag matched
the exact release at observation time.

Read-only GitHub API requests used `Accept: application/vnd.github+json`, API
version `2022-11-28`, and a read-only User-Agent. For each `<repository>`,
`<tag>`, `<major>`, and `<sha>`, the checked official endpoints were:

```text
GET https://api.github.com/repos/actions/<repository>
GET https://api.github.com/repos/actions/<repository>/releases?per_page=100
GET https://api.github.com/repos/actions/<repository>/releases/tags/<tag>
GET https://api.github.com/repos/actions/<repository>/git/ref/tags/<major>
GET https://api.github.com/repos/actions/<repository>/git/ref/tags/<tag>
GET https://api.github.com/repos/actions/<repository>/git/commits/<sha>
GET https://api.github.com/repos/actions/<repository>/contents/action.yml?ref=<sha>
```

Repository metadata returned canonical `full_name=actions/<repository>`, owner
login `actions`, and owner type `Organization`. Release enumeration was
filtered to exact semantic versions in the retained major with both
`draft=false` and `prerelease=false`, then sorted descending by semantic
version. The selected identities were:

| Official repository | Stable releases in retained major | Selected release | Published UTC | Commit SHA | Commit tree | `action.yml` blob | Bytes |
| --- | ---: | --- | --- | --- | --- | --- | ---: |
| `actions/checkout` | 14 | `v4.3.1` | `2025-11-17T16:06:48Z` | `34e114876b0b11c390a56381ad16ebd13914f8d5` | `aea96b3e80c21c26a319652e510e7b0429d019a8` | `6842eb843b7258993656f41f9c358f5c5331fbe7` | 4,593 |
| `actions/setup-python` | 8 | `v5.6.0` | `2025-04-24T02:50:16Z` | `a26af69be951a213d495a4c3e4e4022e16d87065` | `568c6310706725a8b725497dbe6b3b909cbcf6cd` | `efa8de904209196588db1453bdb44079b3c393d7` | 2,364 |
| `actions/upload-artifact` | 18 | `v4.6.2` | `2025-03-19T17:47:02Z` | `ea165f8d65b6e75b540449e92b4886f43607fa02` | `90fba5b2fb462e7dd5b3b810757b73327d2d66bc` | `2a0ecf19e8d0087dd2e5d1785dcf764811e79fae` | 3,159 |

Exact official release pages are:

- `https://github.com/actions/checkout/releases/tag/v4.3.1`;
- `https://github.com/actions/setup-python/releases/tag/v5.6.0`;
- `https://github.com/actions/upload-artifact/releases/tag/v4.6.2`.

An initial sandboxed `ls-remote` failed connectivity and was repeated through
the approved network boundary. A later optional shallow-fetch attempt in bare
repositories below `build/action-pin-verification` encountered DNS failure and
is not used as identity evidence. The official ref, release, repository,
commit-object, and exact-commit contents checks above all completed, so no
verification input remains missing.

All modified occurrences use the identity in the table and its exact release
comment:

```text
.github/workflows/ci.yml:22   actions/checkout ... # v4.3.1
.github/workflows/ci.yml:27   actions/setup-python ... # v5.6.0
.github/workflows/ci.yml:52   actions/checkout ... # v4.3.1
.github/workflows/ci.yml:55   actions/setup-python ... # v5.6.0
.github/workflows/ci.yml:101  actions/checkout ... # v4.3.1
.github/workflows/ci.yml:104  actions/setup-python ... # v5.6.0
.github/workflows/ci.yml:218  actions/upload-artifact ... # v4.6.2
.github/workflows/ci.yml:227  actions/upload-artifact ... # v4.6.2
.github/workflows/heavy-search.yml:61   actions/checkout ... # v4.3.1
.github/workflows/heavy-search.yml:64   actions/setup-python ... # v5.6.0
.github/workflows/heavy-search.yml:195  actions/upload-artifact ... # v4.6.2
```

## EV-003 - Validator behavior and verification

`tools/check_github_action_pins.py` recursively discovers lower-case `.yml`
and `.yaml` paths below `.github/workflows/`, sorts them before validation,
and decodes bytes only as strict UTF-8. It uses no YAML library or new
dependency. The accepted canonical `uses:` value forms are:

- local Action beginning `./`, after dynamic expressions are rejected;
- `owner/repository[/subpath]@<40-lowercase-hex-commit>`;
- `docker://image@sha256:<64-lowercase-hex>` with no mutable tag.

The restricted lexical parser ignores comment-only lines and actual block
scalar content. It fails closed on empty or multiline values, tags, branches,
short or uppercase SHAs, dynamic expressions, Docker tags, non-UTF-8, BOMs,
ambiguous flow/quoted/explicit/tagged/alias mapping keys, and block-scalar
sibling tricks. Block indentation is inferred from the first content line or
derived from an explicit indicator. Every failure is selected in sorted
path/line order, leaves stdout empty, and writes one prefixed stderr line.
Success is buffered until the complete scan and writes one compact sorted JSON
line.

The exact real invocation exited zero with empty stderr and this deterministic
record (the occurrence identities and lines are expanded in EV-002):

```text
python tools/check_github_action_pins.py
{"external_reference_count":11,"ok":true,"workflow_count":2,"workflows":[".github/workflows/ci.yml",".github/workflows/heavy-search.yml"]}
```

The executable's actual JSON additionally contains the sorted
`external_references` array with `workflow`, one-based `line`, normalized
`reference`, `kind`, and, for GitHub Actions, `repository` and `commit`; its
eleven records are exactly the EV-002 occurrence list. The abridgement above
omits only that already-expanded array.

Final required test commands and results were:

```text
python -m pytest -q tests/unit/test_github_action_pins.py
44 passed in 0.39s
exit 0; no failure, skip, or xfail

python -m pytest -q \
  tests/unit tests/differential tests/integration/test_verifier_cli.py
287 passed in 75.77s (0:01:15)
exit 0; no failure, skip, or xfail

$env:EG_CMAKE='C:\msys64\ucrt64\bin\cmake.exe'
$env:EG_CXX='C:\msys64\ucrt64\bin\g++.exe'
$env:EG_NINJA='C:\msys64\ucrt64\bin\ninja.exe'
$env:EG_MAKE='C:\msys64\usr\bin\make.exe'
$env:PATH='C:\msys64\ucrt64\bin;C:\msys64\usr\bin;' + $env:PATH
python -m pytest -q --basetemp build/pytest-root
291 passed in 107.19s (0:01:47)
exit 0; no failure, skip, or xfail
```

The focused tests cover the task's complete positive and negative matrix,
repeated success and failure bytes, sorted discovery, comments and block
scalars, encoded/tagged/explicit bypasses, real repository scanning,
same-repository SHA consistency, exact release comments, and the fast-CI step.
A separate read-only audit first exposed two parser bypass classes, then tested
17 adversarial YAML constructions against the corrected code and found no
remaining HIGH or MEDIUM issue.

Other required terminal checks were:

```text
python -m json.tool REVIEW_STATE.yaml
exit 0; strict JSON records the accepted dde4e6c... baseline/head,
accepted multi-worktree task, current active task, and ordered OPEN follow-ups
RFU-SUPPLY-001 then RFU-ENV-001

python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier
TASK-20260719__pin_github_actions_immutable_shas
exit 0

python tools/validate_schemas.py
{"ok": true, "schemas_checked": ["schemas/benchmark-result.schema.json", "schemas/counterexample.schema.json", "schemas/experiment-manifest.schema.json", "schemas/search-certificate.schema.json", "schemas/search-partition.schema.json", "schemas/surprising-process-outcome.schema.json"]}
exit 0

python tools/verify_upstream_snapshot.py
{"added": [], "changed": [], "expected_file_count": 10, "missing": [], "observed_file_count": 10, "ok": true, "snapshot_path": "third_party/erdos-gyarfas"}
exit 0

python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD
{"base":"dde4e6cbd06be8ebc8192097930f40b06cf2f9f6","head":"dde4e6cbd06be8ebc8192097930f40b06cf2f9f6","ok":true,"range":"dde4e6cbd06be8ebc8192097930f40b06cf2f9f6..dde4e6cbd06be8ebc8192097930f40b06cf2f9f6"}
exit 0
```

## EV-004 - Governance, preservation, scope, cleanup, and limitations

`REVIEW_STATE.yaml` records the already accepted baseline, last reviewed head,
and accepted baseline as
`dde4e6cbd06be8ebc8192097930f40b06cf2f9f6`; verdict
`ACCEPT WITH FOLLOW-UP`; accepted task
`TASK-20260718__support_multi_worktree_whitespace_check`; and this active task.
`RFU-CI-004` is absent. Direct JSON-object comparison with task-start state
confirms that `RFU-SUPPLY-001` and `RFU-ENV-001` retain identical content and
remain ordered first/second and `OPEN`. Supply pinning is pending review;
environment locking remains distinct.

Protected content has identical task-start and closing SHA-256:

| Protected path | SHA-256 |
| --- | --- |
| `.gitattributes` | `3d4fcd555869954eab9bbe5147d04514f8525dc500e8aa301bc20740a104f040` |
| `PROJECT_KNOWLEDGE.md` | `ca4a8764e8a4f50cb92a6412b190147d4568c70c525aefebcdb3c9d58ebde09c` |
| `research/CLAIMS_REGISTRY.yaml` | `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` |
| `research/PRUNING_REGISTRY.md` | `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` |
| `upstream/README.md` | `29daba524345584e837b8b4d396358f0243956e4c7f31b885a874e5003532e0c` |
| `upstream/UPSTREAM_PROVENANCE.json` | `0fbad279d79b61fbdd29a0b9f3fabbdfd09d41a3aaf546a11434ec52413439b5` |
| `upstream/UPSTREAM_REFS.json` | `562a5c8b9faad3fe2f7c80f97e262f14a51332eacc4da1ddc9b0ed0fff619130` |

`git diff --quiet HEAD -- research/CLAIMS_REGISTRY.yaml
research/PRUNING_REGISTRY.md PROJECT_KNOWLEDGE.md third_party` exits zero, and
the independent upstream inventory check passes. Project Git config and index
retain the EV-001 hashes; the closing staged diff is empty. No Git
configuration, ref, commit, or upstream path changed.

The actual final change set is exactly the twelve authorized paths listed in
`TASK_STATUS.md`. No upstream, verifier, graph, schema, manifest, certificate,
benchmark, claim, pruning, or project-knowledge path changed. `RS-001` remains
`NOT STARTED`.

Temporary audit and test directories were resolved and checked beneath the
project `build/` directory before removal:

- `build/action-pin-verification`: absent after cleanup;
- `build/pytest-root`: absent after cleanup.

Residual limitations and trust boundaries are:

- the repository-local pin validator runs after checkout and setup-python in
  its own job, so it detects repository regressions but cannot authenticate
  Actions already used to start that workflow revision;
- full commit pins remove selected-ref mutability but do not freeze the hosted
  runner image, Actions service, operating system, preinstalled packages,
  transitive distributions, or installer archives; this remains
  `RFU-ENV-001`;
- official floating major tags matched the exact releases only at the recorded
  observation time and remain mutable, but workflows do not execute them;
- hosted GitHub Actions execution was not observed by this local task;
- every validator test is bounded engineering evidence and has no mathematical
  implication.

No mathematical claim or pruning status changed.

## EV-005 - Closing file hashes

All rows except the final `EVIDENCE.md` row identify terminal file bytes. A
file cannot contain its own final cryptographic digest without changing that
digest, so the last row explicitly records this evidence file immediately
before EV-005 replaced its placeholder. The final `EVIDENCE.md` digest is
computed after this last edit and reported in the Codex handoff.

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/ci.yml` | 7,780 | `7bfef1f1d09a46bf7b0c1bd85eb19c44cec75071d943ce74dddaa88c17eaf809` |
| `.github/workflows/heavy-search.yml` | 8,572 | `3af7eb1ddf7c12940f2251ac38a30115e29530b75e304e981b254149921cc803` |
| `tools/check_github_action_pins.py` | 15,603 | `34cdb531193f0e46d85c736d12a5d0a67ff47336b8040d2cca369683439f0d77` |
| `tests/unit/test_github_action_pins.py` | 15,149 | `4474418c44cc3d6310a362f753a77bcbf76b3bc8b63f87d2658c270e42536822` |
| `docs/CI.md` | 16,864 | `0ca2957ba48cc1f1737dd9022fe4b6a612234819c881c30be75c49c9a0505742` |
| `research/REPRODUCIBILITY.md` | 17,670 | `dba71c9cd31d92ce012371d8b0c02a84eac0d82e2968dde43a2861a9b2d08b18` |
| `REVIEW_STATE.yaml` | 1,291 | `69619d27039ee841ba96a8bf42ba5287de0bfb07b2898877cd5d65e72c3985b4` |
| `CURRENT_STATUS.md` | 5,476 | `40fa2b3a8b53ad7e2c2990dc55e699293e1081c78f9f3bf53aae047fde5da081` |
| `research/NEXT_RESEARCH_STEPS.md` | 6,198 | `5e03e175176aa3772d7fcef2d7fb8b777ce609321c457d3e1472881648310db4` |
| `TASK_STATUS.md` | 2,707 | `ba4bb26966226b457da6be4360f68d15430707366b2d5dfd2ff35d0ca7d0a9f6` |
| `TASK_LOG.md` | 7,207 | `d624fadc1f2f67d71ae0fe86a08cadfaaa052d4ab82ce1dab02fade20699aa0b` |
| `EVIDENCE.md` immediately before EV-005 | 14,693 | `4e838f749155a2f8260100d426fedb1eddd2df49f923d04e7223ec8eea3a99ad` |
