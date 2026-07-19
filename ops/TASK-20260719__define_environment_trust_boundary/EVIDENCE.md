# TASK-20260719__define_environment_trust_boundary - Evidence

All evidence in this dossier is environment/reproducibility specification,
review-governance, and bounded engineering evidence. It establishes no
mathematical result, upstream reproduction, exhaustive coverage, certificate,
counterexample, theorem, proof, or pruning rule.

## EV-001 - Startup gate

Plain Git first exited `1` with its dubious-ownership diagnostic. No
`safe.directory` entry or other configuration was added. Successful read-only
Git commands used only the process-local option
`-c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`.
They established:

```text
git rev-parse --show-toplevel
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
exit 0

git remote -v
origin  https://github.com/falker47/erdos-gyarfas-p14.git (fetch/push)
exit 0

git branch --show-current
main
exit 0

git rev-parse HEAD
41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d
exit 0

git merge-base --is-ancestor \
  41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d HEAD
<no stdout>
exit 0

git status --short --untracked-files=all
<no entries; sandbox warning for inaccessible owner-global ignore file>
exit 0

git diff --cached --name-only
<no entries>
exit 0
```

The task-supplied review base equals exact task-start HEAD. The state file's
historical prior baseline was the expected commit-neutral input to the
explicit accepted-review transition, not a competing task gate value.

## EV-002 - Mandatory input and source inspection

The required governance and research files were read completely in the
specified order. The new dossier was confirmed absent, followed by complete
inspection of:

- the accepted documentation-alignment status, log, and evidence;
- the accepted Action-pin status and evidence;
- `research/REPRODUCIBILITY.md`, `Dockerfile`, `.dockerignore`, both workflow
  files, `pyproject.toml`, `CMakePresets.json`, `CMakeLists.txt`, and
  `tools/validate_schemas.py`;
- existing schema conventions and schema-validation tests;
- `tests/integration/test_upstream_build.py` and the preserved upstream
  `Makefile`, because they contain local/native selectors;
- task-start Git history and the complete accepted
  `265c1474...41fb0a9` transition.

Direct source inspection found four `runs-on: ubuntu-24.04` occurrences,
eleven full-SHA external Action occurrences, setup-python selectors `3.11` and
`3.12`, eight unversioned APT package names, one digest-qualified Docker base
index, one live Docker pip route, and three direct Python requirements.

Official raw `action.yml` bytes at the exact accepted commits report
`runs.using: node20` for checkout, setup-python, and upload-artifact. These
metadata bytes are content-selected by the Action SHAs; the runtime executable
is separately supplied by GitHub and is not treated as content-pinned.

Relevant Git history established:

```text
41fb0a9 docs: align upload-artifact pin documentation
265c147 ci: pin GitHub Actions to immutable SHAs
dde4e6c ci: support multi-worktree whitespace validation
...
164d675 chore: bootstrap certified Erdos-Gyarfas P14 research baseline
```

Commit `41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d` changes exactly the seven
accepted documentation-alignment paths. Dockerfile history has only the
bootstrap commit; environment-related workflow/reproducibility history was
also inspected through the Action-pin and earlier CI-governance commits.

## EV-003 - Accepted review and follow-up transition

The accepted review occurred at `2026-07-19T08:52:08Z`. At observed state-write
time `2026-07-19T09:15:11Z`, `REVIEW_STATE.yaml` was advanced to:

- review base, last reviewed head, and accepted baseline:
  `41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d`;
- verdict: `ACCEPT WITH FOLLOW-UP`;
- accepted task: `TASK-20260719__align_action_pin_documentation`;
- active task: `TASK-20260719__define_environment_trust_boundary`.

`RFU-DOC-001` was removed because the accepted commit resolves it.
`RFU-ENV-001` remains `MEDIUM`, `OPEN`, and refined to the canonical inventory,
interpretation, and every identified interface layer. The accepted dossier is
protected historical chronology; its statement that the documentation issue
was open pending its then-future review remains byte-identical.

## EV-004 - Task-start hashes and protected inventory

The four existing authorized files had these task-start bytes and SHA-256.
All seven task-created paths were absent.

| Authorized existing path | Initial bytes | Initial SHA-256 |
| --- | ---: | --- |
| `research/REPRODUCIBILITY.md` | 17,670 | `dba71c9cd31d92ce012371d8b0c02a84eac0d82e2968dde43a2861a9b2d08b18` |
| `REVIEW_STATE.yaml` | 1,249 | `c04e7becbd5f984f8becf809027adc3131d644ccf19a299e02c23b2bf75164fb` |
| `CURRENT_STATUS.md` | 5,929 | `862bf3296550bfdb6ddf56cab20e6a7d71db2a136c23ab4c4a5ec1fa5eb4890d` |
| `research/NEXT_RESEARCH_STEPS.md` | 5,831 | `dec299c222e5a001505761bad8327c4759d1efc80a3b279313efb7c9aafe3152` |

Initially absent:

- `research/ENVIRONMENT_TRUST_BOUNDARY.md`
- `research/ENVIRONMENT_LOCK_INVENTORY.json`
- `schemas/environment-lock-inventory.schema.json`
- `tests/unit/test_environment_lock_inventory.py`
- `ops/TASK-20260719__define_environment_trust_boundary/TASK_STATUS.md`
- `ops/TASK-20260719__define_environment_trust_boundary/TASK_LOG.md`
- `ops/TASK-20260719__define_environment_trust_boundary/EVIDENCE.md`

Required protected anchors were:

| Protected path | Initial bytes | Initial SHA-256 |
| --- | ---: | --- |
| `.github/workflows/ci.yml` | 7,780 | `7bfef1f1d09a46bf7b0c1bd85eb19c44cec75071d943ce74dddaa88c17eaf809` |
| `.github/workflows/heavy-search.yml` | 8,572 | `3af7eb1ddf7c12940f2251ac38a30115e29530b75e304e981b254149921cc803` |
| `Dockerfile` | 1,289 | `812ac741b6b80eff545b88a837c83068e5443c3d2ebb244e542cbedf0f5038ff` |
| `.dockerignore` | 359 | `46d98cdd7a0c19863214d704b6eb7b1a8b1f993a0ee40cb48969f6d309a5c08b` |
| `pyproject.toml` | 794 | `c247d389d0c72c5c9ecdfff39ab6197ecc96526d0a87859eb5248700812a9243` |
| `CMakeLists.txt` | 1,076 | `4163b6957f68d05f316e1242c355d6d9a7fd9e585034cb48cc3c318f1021b71f` |
| `CMakePresets.json` | 1,240 | `f23b0b5fb32333424e1540a8e0b4f638774225e0737a1fad452739fb5be016c1` |
| `tools/validate_schemas.py` | 3,256 | `c9849f75db7c45786cb7ddbb3ac6de0f44eb23d7d90331d5d2797fa0ff5fb5dd` |
| `tools/check_github_action_pins.py` | 15,603 | `34cdb531193f0e46d85c736d12a5d0a67ff47336b8040d2cca369683439f0d77` |
| `PROJECT_KNOWLEDGE.md` | 4,836 | `ca4a8764e8a4f50cb92a6412b190147d4568c70c525aefebcdb3c9d58ebde09c` |
| `research/CLAIMS_REGISTRY.yaml` | 5,495 | `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` |
| `research/PRUNING_REGISTRY.md` | 3,160 | `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` |
| `upstream/README.md` | 5,188 | `29daba524345584e837b8b4d396358f0243956e4c7f31b885a874e5003532e0c` |
| `upstream/UPSTREAM_PROVENANCE.json` | 4,468 | `0fbad279d79b61fbdd29a0b9f3fabbdfd09d41a3aaf546a11434ec52413439b5` |
| `upstream/UPSTREAM_REFS.json` | 1,528 | `562a5c8b9faad3fe2f7c80f97e262f14a51332eacc4da1ddc9b0ed0fff619130` |
| `upstream/patches/README.md` | 612 | `9efd90b3d75ebbb45c841ef9b23d0f650b9ea5e6aa738c3f466993491e55bbaa` |
| accepted align `TASK_STATUS.md` | 4,025 | `f1c321916f252cb0c5dc53d94a2d8159b3de94cee4e8c8b40111b9662f1ef7ab` |
| accepted align `TASK_LOG.md` | 8,494 | `bc5aaad24b63276f0ef7d87d5f30654d6445d674476a03bcaedd3b21ac030e1e` |
| accepted align `EVIDENCE.md` | 17,112 | `2679b44c1c7bec40fe6e95d573691957ab6efa5858258ddd0fe7a5e836145355` |
| `.gitattributes` | 193 | `3d4fcd555869954eab9bbe5147d04514f8525dc500e8aa301bc20740a104f040` |
| `.git/config` | 308 | `212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10` |
| `.git/index` | 18,104 | `ff3b8d380e6f89d380566a432760f337b37471768784acdeef9c26181f264372` |

`.git/config.worktree` and `.git/info/attributes` were absent. Canonical
protected tracked inventory, excluding the four authorized existing paths:

```text
file_count=154
total_bytes=904336
serialized_bytes=16553
inventory_sha256=9502eeec910a0b34040d2857cf5716a911a791a67e986b1cb63ca376d6ce0eca
```

Additional directory inventory digests used canonical sorted
`path<TAB>bytes<TAB>sha256<LF>` records:

| Protected group | Files | Initial inventory SHA-256 |
| --- | ---: | --- |
| existing tests excluding the authorized new test | 47 | `0edbe7b07cdb6db641a4271634b4c190023d93cf2a44034f0b085bfe61b86726` |
| existing schemas excluding the authorized new schema | 6 | `f4c61f67858035dbfe946cb41745d2ba27f92f8c40d253edd71e4ea6601d7eed` |
| `tools/` | 17 | `b1ae05b7a99cecad8d357dbb72df584f30aa4b6fd7a894618d80a9eb70655e68` |
| `verifier/` | 15 | `2d5eafc71fdfcb3977f742b8a58a908a75c8f98675b3f1f074cdf461d5c323e0` |
| `third_party/` | 10 | `56fe3d40bbceb84ad3f5d1c7eb96ad4f8ffe754b34cbbca93510cf0133c0ec0b` |
| `upstream/` | 4 | `ed29ebe37c67654039f9750f85303235c66d1605aa4ef9705eed6846cc84d91e` |
| existing `artifacts/`, `benchmarks/`, `_TEMPLATES/` | 13 | `f9152f0232a024221215aeb1c6b9f3e790a7026f59b3da12118565f4e498c1bd` |

The first aggregate script attempted unavailable older PowerShell/.NET APIs
and produced no usable digest; the portable retry generated the values above.
One separate compact pipeline attempt had a parser error before execution and
was immediately replaced with a valid read-only form. Neither diagnostic
changed repository state.

## EV-005 - Inventory coverage and interpretation

The strict deterministic inventory contains 58 unique lexicographically
ordered IDs. Required coverage maps as follows:

| Required current boundary | Stable inventory IDs |
| --- | --- |
| each `runs-on: ubuntu-24.04` | `ENV-001` through `ENV-004` full IDs |
| GitHub runner/control plane | `ENV-005-GHA-CONTROL-PLANE`, `ENV-020-GHA-PLATFORM-RESOURCES` |
| each Action repository and commit | `ENV-006-GHA-ACTION-CHECKOUT` through `ENV-008-GHA-ACTION-UPLOAD-ARTIFACT` |
| GitHub-supplied JavaScript runtime | `ENV-009-GHA-ACTION-NODE20-RUNTIME` |
| setup-python 3.11 and 3.12 | `ENV-010-GHA-PYTHON-311-SELECTOR`, `ENV-011-GHA-PYTHON-312-SELECTOR` |
| interpreter/tool-cache artifacts | `ENV-012-GHA-PYTHON-DISTRIBUTIONS` |
| hosted compilers/native/build/Git/shell tools | `ENV-013` through `ENV-019` full IDs |
| Python backend and direct pins | `ENV-023` through `ENV-026` full IDs |
| pip, transitive distributions/artifacts/services | `ENV-027` through `ENV-030` full IDs |
| Docker base digest and platform child | `ENV-033-DOCKER-BASE-INDEX`, `ENV-034-DOCKER-PLATFORM-CHILD` |
| Docker builder/context | `ENV-035-DOCKER-ENGINE`, `ENV-036-DOCKER-BUILD-CONTEXT` |
| APT index/service and every unversioned package | `ENV-037` through `ENV-046` full IDs |
| container compiler/stdlib/build tools | `ENV-047-DOCKER-NATIVE-TOOLCHAIN` |
| container Python and pip install route | `ENV-048-DOCKER-PYTHON-RUNTIME`, `ENV-049-DOCKER-PIP-INSTALL-ROUTE` |
| CPU/platform selectors and environment variables | `ENV-020`, `ENV-021`, `ENV-034`, `ENV-050`, `ENV-058` full IDs |
| accepted local MSYS2 paths and missing provenance | `ENV-052` through `ENV-056` full IDs |
| local Python, Git, OS/platform/resources | `ENV-051`, `ENV-057`, `ENV-058` full IDs |

The JSON distinguishes the five closed classification values and three closed
lockability values. It contains source path/range/expression records, observed
state, outcome relevance, external dependencies, evidence, next action, and
V1/V3/V4 blockers for every entry. No unavailable resolved package version,
runner image identity, interpreter build identity, or artifact hash is
invented.

The Markdown document defines locked, captured, and externally trusted state;
separates Action source from runner/runtime, image index from platform/APT, and
direct versions from transitive/artifact hashes; states V1/V3/V4 obligations;
and permits only `EMPIRICAL_OBSERVATION` wording for a tiny pre-lock execution.
Every JSON ID appears as one ordered interpretation heading with exact
classification, lockability, and blocker values.

## EV-006 - Focused verification and preserved anomalies

Initial strict checks passed:

```text
python -m json.tool research/ENVIRONMENT_LOCK_INVENTORY.json
exit 0

python tools/validate_schemas.py \
  --schema environment-lock-inventory \
  --instance research/ENVIRONMENT_LOCK_INVENTORY.json
ok=true; seven schemas checked; instance accepted
exit 0
```

The first focused run exited `1` with three test failures: an off-by-one source
locator; `WinError 6` from `capture_output=True` under the local pytest handle
environment; and an ID regex that matched the `ENV-001` suffix inside
`RFU-ENV-001`. Corrections used the exact source line, the existing repository
`DEVNULL`/binary-`PIPE` subprocess pattern, and a prefix-aware ID regex. The
second run exited `1` on one remaining exact source-expression mismatch in a
broad accepted-dossier range. The expression was replaced with the exact
in-range source phrase without changing inventory semantics.

Terminal focused result:

```text
python -m pytest -q tests/unit/test_environment_lock_inventory.py \
  --basetemp build/pytest-root-env-boundary
...... [100%]
6 passed in 0.20s
exit 0; no failure, skip, or xfail
```

Complete required commands, full-suite result, final byte/scope audit,
protected-state comparison, cleanup, and closing hashes are recorded only
after their terminal execution.

## EV-007 - Current classification and limitations

The inventory and documents are reproducibility specifications and bounded
source observations. They do not implement a lock, attest hosted/container
execution, reproduce an upstream result, certify a search, or alter any
mathematical claim. Unresolved entries deliberately report `V3=true` and
`V4=true` blockers while allowing exact bounded V1 checks to be described in
their observed environment.

`RFU-ENV-001` remains open. `RS-001` remains `NOT STARTED`.
`research/CLAIMS_REGISTRY.yaml` and `research/PRUNING_REGISTRY.md` have no
authorized change.

## EV-008 - Required verification and complete-suite chronology

Terminal required command results are:

| Command | Exit | Relevant terminal result |
| --- | ---: | --- |
| `python -m json.tool REVIEW_STATE.yaml` | 0 | strict JSON accepted |
| `python -m json.tool research/ENVIRONMENT_LOCK_INVENTORY.json` | 0 | strict JSON accepted |
| `python tools/validate_schemas.py` | 0 | `ok=true`; all seven schemas accepted |
| `python tools/validate_schemas.py --schema environment-lock-inventory --instance research/ENVIRONMENT_LOCK_INVENTORY.json` | 0 | explicit instance accepted against the new schema |
| `python -m pytest -q tests/unit/test_environment_lock_inventory.py --basetemp build/pytest-root-env-boundary` | 0 | 6 passed in 0.22 seconds; no failure, skip, or xfail |
| `python tools/check_github_action_pins.py` | 0 | `ok=true`; 2 workflows and 11 external references |
| `python tools/verify_upstream_snapshot.py` | 0 | `ok=true`; expected and observed file counts both 10 |
| `python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD` | 0 | `ok=true`; base and head both `41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d` |
| process-local-safe `git diff --check` | 0 | no output |
| process-local-safe `git diff --cached --name-only` | 0 | empty index |

The required complete suite used exactly the documented `EG_CMAKE`, `EG_CXX`,
`EG_NINJA`, and `EG_MAKE` path overrides. Its full chronology is preserved:

1. First run: 296 passed and 1 new-contract failure in 105.40 seconds. The
   failure exposed a stale reproducibility source locator after canonical text
   movement. Exact inspection corrected all affected ranges; an all-entry
   audit then reported `source_locator_mismatches=0`.
2. Second run: 296 passed and 1 protected timing-test failure in 104.30
   seconds. The inspector child did not create its marker before the existing
   0.75-second Windows timeout. No protected file changed.
3. Exact timing-test retry: 1 passed in 1.16 seconds.
4. Terminal complete retry: 297 passed in 99.16 seconds, exit `0`, with no
   failure, skip, or xfail.

## EV-009 - Final scope, byte audit, and protected-state proof

The closing status contains exactly the allowlist: four modified tracked paths
and seven untracked task-created paths. `git diff --name-status` names only the
four tracked modifications because Git does not include untracked files in
that output; `git status --short --untracked-files=all` names all eleven. The
index is empty, branch is `main`, and HEAD remains the task-start SHA.

Every authorized file passed a raw-byte audit for strict UTF-8 decoding, no
BOM, no NUL, final LF, no trailing whitespace, and no bare CR. The inventory
also equals the canonical bytes produced by `json.dumps(..., ensure_ascii=True,
indent=2) + "\\n"`. Its 58 records have these closed-vocabulary totals:

```text
classification: CAPTURE_REQUIRED=16, EXTERNAL_SERVICE_TRUST=4,
  IMMUTABLE_PIN=5, MUTABLE_RESOLUTION=25, VERSION_PIN_ONLY=8
lockability: CAPTURE_ONLY=18, NOT_REPOSITORY_CONTROLLED=9,
  REPOSITORY_PINNABLE=31
blockers: V1=0, V3=53, V4=53
```

All protected path hashes in EV-004 match their task-start values, including
both workflows, Docker/build/dependency inputs, project knowledge, claims,
pruning, upstream metadata, the accepted dossier, `.gitattributes`,
`.git/config`, and `.git/index`. The two initially absent Git configuration
paths remain absent. The stronger protected tracked inventory is unchanged:

```text
file_count=154
total_bytes=904336
serialized_bytes=16553
inventory_sha256=9502eeec910a0b34040d2857cf5716a911a791a67e986b1cb63ca376d6ce0eca
```

All directory inventory digests also exactly equal EV-004: existing tests
excluding the authorized new test, existing schemas excluding the new schema,
`tools/`, `verifier/`, `third_party/`, `upstream/`, and the combined existing
artifact/benchmark/template group. The final upstream verifier independently
reports 10 expected and 10 observed preserved files.

The first closing group-comparison wrapper incorrectly captured its
human-readable label together with the digest scalar and therefore exited `1`
with seven false mismatches. The corrected read-only wrapper returned only the
digest value and reported `protected_group_failures=0`, with every count and
digest exactly matching EV-004. Neither command modified a repository file.

## EV-010 - Cleanup and final disposition

Only task-created basetemp directories were targeted after their absolute
paths were verified beneath the repository `build/` directory.
`build/pytest-root` was removed and `build/pytest-root-env-boundary` was already
absent. The sandbox denied access to
`build/pytest-root-timeout-retry`; approved removal of that one exact path then
succeeded. All three are absent. Pre-existing build output was preserved.

The dossier and `CURRENT_STATUS.md` end at `READY_FOR_REVIEW`.
`RFU-ENV-001` remains `OPEN`, `RS-001` remains `NOT STARTED`, and no later task
has begun.

## EV-011 - Closing file hashes

Terminal byte counts and SHA-256 values are:

| Closing path | Bytes | SHA-256 |
| --- | ---: | --- |
| `research/ENVIRONMENT_TRUST_BOUNDARY.md` | 22,469 | `d197fbe8e26b0cc4f19b78af358699438a25ae50122ca634c7931a43040bedd7` |
| `research/ENVIRONMENT_LOCK_INVENTORY.json` | 99,971 | `1c51bf98a567c24b2b4058a11c499bb2aebd13a3f18606b15d90d791c401b144` |
| `schemas/environment-lock-inventory.schema.json` | 6,568 | `cafe394bdb2d2a9636ec9f4d7f775cdbb331b92f9593ce34ee70859127ed6ea0` |
| `tests/unit/test_environment_lock_inventory.py` | 15,601 | `a850aa43b1d83cb116aa70fec52017cd00c9bca823382e42599690d1791cf046` |
| `research/REPRODUCIBILITY.md` | 20,872 | `2c3f5dccebf613134fa9bb2bf02a2e6505461d5c3aa10676252babef78fbeb62` |
| `REVIEW_STATE.yaml` | 1,702 | `ca9b965a1d3c4dacc759d2021298cfe05e811169a2d25daaac510d23c4639c37` |
| `CURRENT_STATUS.md` | 5,368 | `f227c736216ab609b70adee6696ad6a83efec2a00ab35fdee9852b2b68e18245` |
| `research/NEXT_RESEARCH_STEPS.md` | 6,120 | `4fa2dd31e7601faa1de7d9036ebee9512ca18c06c2ff0cdafe26faccaaa128a2` |
| task `TASK_STATUS.md` | 6,010 | `d883e2fa2e62ddc445dd373a3b9594d3eb1b69cc490bbe9d6a13cb0436de9f64` |
| task `TASK_LOG.md` | 8,193 | `b2840fca3138e898f783e1dc10fac6587bca8566cd12707a47a8c65bb018dbd5` |

Immediately before this section was populated, this evidence file had 18,860
bytes and SHA-256
`ab48d18afb931b665d4238ddc3f182a3021062b2976f4af052e994511aa1daf7`.
Its actual post-edit digest is reported externally at handoff rather than
fabricated recursively inside its own contents.
