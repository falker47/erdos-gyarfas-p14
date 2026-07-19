# TASK-20260719__stabilize_inspector_timeout_test - Evidence

All evidence in this dossier is review-governance and bounded engineering-test
evidence. It establishes no upstream reproduction, exhaustive coverage,
certificate, counterexample, theorem, proof, mathematical claim, or pruning
rule.

## EV-001 - Startup gate

Plain Git first exited `1` with the dubious-ownership diagnostic. No
configuration was added or modified. Successful read-only Git commands used
only:

```text
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
```

They established:

```text
root=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
origin=https://github.com/falker47/erdos-gyarfas-p14.git
branch=main
HEAD=a7066e70b92d80be2d1772127f329c24222c1b41
review_base_type=commit
review_base_is_ancestor=true
worktree_entries=0
index_entries=0
```

The unreadable owner-global ignore file produced warnings only. Exact root,
origin, branch, HEAD, base resolution, ancestry, worktree, and index therefore
matched the immutable task gate before modification.

## EV-002 - Mandatory inspection and initial hashes

All mandatory files were read completely in the specified order. The current
dossier was confirmed absent before its creation. The accepted
environment-boundary dossier, earlier process-outcome and surprising-outcome
dossiers, affected implementation and tests, and relevant Git history were
then inspected.

The four existing authorized paths started as:

| Path | Bytes | Initial SHA-256 |
| --- | ---: | --- |
| `tests/unit/test_upstream_candidate_inspection.py` | 22,074 | `e0ac90849662cdae7447c44b4c3d5fd567c767212fe17cea6f9ccc79be4586dc` |
| `REVIEW_STATE.yaml` | 1,702 | `ca9b965a1d3c4dacc759d2021298cfe05e811169a2d25daaac510d23c4639c37` |
| `CURRENT_STATUS.md` | 5,368 | `f227c736216ab609b70adee6696ad6a83efec2a00ab35fdee9852b2b68e18245` |
| `research/NEXT_RESEARCH_STEPS.md` | 6,120 | `4fa2dd31e7601faa1de7d9036ebee9512ca18c06c2ff0cdafe26faccaaa128a2` |

All three current dossier files were initially absent. The canonical protected
tracked inventory excludes only those four existing authorized paths:

```text
file_count=161
total_bytes=1082408
serialized_bytes=17397
inventory_sha256=8432dfeb225620e369da44a5b9426b665761ee26035ed6eb06852148557629f0
```

Critical protected anchors started as:

| Path | Bytes | Initial SHA-256 |
| --- | ---: | --- |
| `tools/inspect_upstream_candidate.py` | 46,163 | `301c427a768e80065d1219a917ac026168c0ab2e9a5226a8f521009d1a73678f` |
| accepted environment `TASK_STATUS.md` | 6,010 | `d883e2fa2e62ddc445dd373a3b9594d3eb1b69cc490bbe9d6a13cb0436de9f64` |
| accepted environment `TASK_LOG.md` | 8,193 | `b2840fca3138e898f783e1dc10fac6587bca8566cd12707a47a8c65bb018dbd5` |
| accepted environment `EVIDENCE.md` | 20,462 | `bee46b3b44ff20a502c16329e372a87ceab713e54f4307f009e1fa5825a8f135` |
| `research/ENVIRONMENT_LOCK_INVENTORY.json` | 99,971 | `1c51bf98a567c24b2b4058a11c499bb2aebd13a3f18606b15d90d791c401b144` |
| `research/ENVIRONMENT_TRUST_BOUNDARY.md` | 22,469 | `d197fbe8e26b0cc4f19b78af358699438a25ae50122ca634c7931a43040bedd7` |
| `schemas/environment-lock-inventory.schema.json` | 6,568 | `cafe394bdb2d2a9636ec9f4d7f775cdbb331b92f9593ce34ee70859127ed6ea0` |
| `tests/unit/test_environment_lock_inventory.py` | 15,601 | `a850aa43b1d83cb116aa70fec52017cd00c9bca823382e42599690d1791cf046` |
| `research/CLAIMS_REGISTRY.yaml` | 5,495 | `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` |
| `research/PRUNING_REGISTRY.md` | 3,160 | `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` |

The stronger protected inventory includes workflows, Docker/CMake/Python build
inputs, tools, schemas, verifier, upstream snapshot and metadata, manifests,
certificates, benchmarks, and every other tracked protected path.

Git metadata anchors were:

```text
.git/config bytes=308 sha256=212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10
.git/index bytes=19002 sha256=d37bb84289e54dea195af81a554302ac25105cf4b63c33e4fd1d83385a7860ba
.git/config.worktree=absent
.git/info/attributes=absent
```

## EV-003 - Accepted review and follow-up transition

`REVIEW_STATE.yaml` records exact accepted commit
`a7066e70b92d80be2d1772127f329c24222c1b41` as review base, last reviewed
head, and accepted baseline. It records verdict `ACCEPT WITH FOLLOW-UP`,
accepted task `TASK-20260719__define_environment_trust_boundary`, active task
`TASK-20260719__stabilize_inspector_timeout_test`, and actual observed update
time `2026-07-19T10:52:11Z`.

`RFU-TEST-001` is `MEDIUM` and `OPEN`. The complete pre-existing
`RFU-ENV-001` object remains second, byte-for-byte equal in content and order
to its task-start representation, with status `OPEN`. The accepted review
occurrence `2026-07-19T10:24:26Z` is separately recorded in current state and
this dossier.

## EV-004 - Exact flake cause

The old test required the same fresh Python process to complete interpreter
startup, JSON decoding, two file reads, two SHA-256 calculations, and marker
creation within 0.75 seconds before it could prove freeze ordering and then be
timed out. The hardening dossier records that the timeout had already been
raised from 0.15 seconds to 0.75 seconds because cold startup could race.

The accepted environment-boundary dossier preserves the observed signature:

1. a complete suite reported 296 passes and one failure because the marker did
   not exist before the child was killed;
2. the exact test then passed in isolation in 1.16 seconds;
3. the terminal complete retry passed all 297 tests.

The production inspector and its unit file were unchanged between the
hardening commit and task-start HEAD. This evidence identifies a temporal test
false negative, not a distinct production bug.

## EV-005 - Separated test properties

The controlled real-inspector test proves freeze ordering without intending to
expire. It checks the immutable outcome's initial state, absence of the final
inspection artifact, exact stream sizes, and both recorded SHA-256 values,
then emits a unique valid completed protocol under a ten-second bound.

The fake timeout test begins from separately frozen artifacts and records
their bytes and SHA-256 before calling the production timeout orchestration.
Its independent state machine requires this exact lifecycle:

```text
Popen
__enter__
communicate(timeout=0.75) -> TimeoutExpired
kill
communicate() -> distinct drained stdout/stderr and reaped return code 137
returncode read
__exit__
wait
```

The test then validates the written timeout record, drained bytes, exact
return code, `source_outcome_preserved`, `source_streams_preserved`, unchanged
source bytes and SHA-256, and `EMPIRICAL_OBSERVATION` limitation. The fake does
not copy production payload construction. Its late-effect probe can write only
while unreaped and therefore proves no post-return fake effect.

The real-child smoke uses a child that only attempts heartbeat writes and a
late marker. It requires neither startup nor any marker, parsing, file read, or
hash before the timeout. After return, the optional heartbeat state remains
unchanged and the late marker stays absent.

## EV-006 - Focused development runs

Both observed focused attempts passed without failure, skip, or xfail:

```text
python -m pytest -q tests/unit/test_upstream_candidate_inspection.py \
  --basetemp build/pytest-root-inspector-stable
31 passed in 5.94s
exit 0

python -m pytest -q tests/unit/test_upstream_candidate_inspection.py \
  --basetemp build/pytest-root-inspector-stable
31 passed in 4.19s
exit 0
```

The second run followed a stricter fake-lifecycle refinement.

The required serial PowerShell loop stopped on any nonzero status and used
`build/pytest-root-inspector-stable-01` through `-25`. Its complete terminal
result was 25 consecutive exit-zero runs with 31 passes each:

| Run | Pytest time (s) | Exit |
| ---: | ---: | ---: |
| 01 | 5.54 | 0 |
| 02 | 5.09 | 0 |
| 03 | 5.05 | 0 |
| 04 | 5.01 | 0 |
| 05 | 5.14 | 0 |
| 06 | 5.00 | 0 |
| 07 | 5.74 | 0 |
| 08 | 5.12 | 0 |
| 09 | 5.20 | 0 |
| 10 | 5.26 | 0 |
| 11 | 5.35 | 0 |
| 12 | 5.39 | 0 |
| 13 | 5.18 | 0 |
| 14 | 5.11 | 0 |
| 15 | 5.69 | 0 |
| 16 | 5.04 | 0 |
| 17 | 4.91 | 0 |
| 18 | 4.96 | 0 |
| 19 | 5.02 | 0 |
| 20 | 5.29 | 0 |
| 21 | 5.18 | 0 |
| 22 | 4.98 | 0 |
| 23 | 5.09 | 0 |
| 24 | 4.99 | 0 |
| 25 | 5.21 | 0 |

The loop wall time was 187.3 seconds. No attempt failed, so no retry or hidden
temporal anomaly exists in this sequence.

## EV-007 - Two consecutive complete suites

Both commands used exactly:

```text
EG_CMAKE=C:\msys64\ucrt64\bin\cmake.exe
EG_CXX=C:\msys64\ucrt64\bin\g++.exe
EG_NINJA=C:\msys64\ucrt64\bin\ninja.exe
EG_MAKE=C:\msys64\usr\bin\make.exe
```

Results were consecutive, with no intervening patch or verification:

```text
python -m pytest -q --basetemp build/pytest-root-full-1
299 passed in 110.92s (0:01:50)
exit 0

python -m pytest -q --basetemp build/pytest-root-full-2
299 passed in 110.51s (0:01:50)
exit 0
```

Neither suite reported a failure, skip, xfail, or warning summary. The increase
from the accepted baseline's 297 tests is exactly the replacement of one
combined timeout test by three separately scoped tests.

## EV-008 - Validators and committed-range limitation

Terminal preliminary results were:

| Command | Exit | Result |
| --- | ---: | --- |
| `python -m json.tool REVIEW_STATE.yaml` | 0 | strict JSON accepted; both follow-ups `OPEN` |
| `python tools/validate_schemas.py` | 0 | all seven schemas accepted |
| `python tools/check_github_action_pins.py` | 0 | two workflows; eleven immutable external references |
| `python tools/verify_upstream_snapshot.py` | 0 | expected and observed file counts both ten |
| `python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD` | 0 | base and head both exact `a7066e70...`; `ok=true` |
| process-local-safe `git diff --check` | 0 | no output |
| process-local-safe `git diff --cached --name-only` | 0 | empty index |

Before the user's manual commit, the range checker necessarily examines only
the already committed range
`a7066e70b92d80be2d1772127f329c24222c1b41..a7066e70b92d80be2d1772127f329c24222c1b41`.
It does not validate the candidate worktree. `git diff --check`, the strict
byte audit, complete diff inspection, and allowlist audit cover that separate
boundary.

## EV-009 - Protected preservation and follow-up audit

The preliminary closing audit reported:

```text
allowlist_match=true
rfu_env_unchanged=true
follow_ups=RFU-TEST-001:MEDIUM:OPEN,RFU-ENV-001:MEDIUM:OPEN
protected_file_count=161
protected_total_bytes=1082408
protected_serialized_bytes=17397
protected_inventory_sha256=8432dfeb225620e369da44a5b9426b665761ee26035ed6eb06852148557629f0
protected_inventory_matches_initial=true
git_config_sha256=212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10
git_index_sha256=d37bb84289e54dea195af81a554302ac25105cf4b63c33e4fd1d83385a7860ba
config_worktree_exists=false
info_attributes_exists=false
```

The changed-path set was exactly the seven authorized paths. Because the
protected inventory includes every tracked path except the four existing
authorized files, it proves byte preservation of the production inspector,
accepted environment-boundary deliverables and dossier, workflows,
Docker/CMake/Python inputs, verifier, upstream and metadata, schemas, claims,
pruning, manifests, certificates, benchmarks, and all other protected tracked
content.

## EV-010 - Task basetemp cleanup

The 28 verified paths comprised the two complete-suite basetemps, the reused
focused-development basetemp, and 25 numbered stability basetemps. The initial
bounded removal deleted 27 but emitted access denied for exact task path
`build/pytest-root-inspector-stable`; PowerShell left the error non-terminating
and the wrapper exited `0` while explicitly reporting
`remaining_task_basetemps=1`.

A read-only retry proved that exact path was the sole remainder. Bounded
approved removal of only that directory exited `0`. Final enumeration then
reported:

```text
remaining_task_basetemps=0
```

No pre-existing build output was targeted.

## EV-011 - Current claim boundary

This is bounded V1 engineering-test evidence only. `RFU-TEST-001` and
`RFU-ENV-001` remain `OPEN`; `RS-001` remains `NOT STARTED`. Claims, pruning,
production inspector behavior, environment controls, and mathematical target
statuses do not change.

## EV-012 - Authorized-file byte audit chronology

The first strict audit decoded all seven authorized files with a throwing
UTF-8 decoder, rejected BOM/NUL/CR bytes, required a final LF, and checked
every line for trailing spaces or tabs. It exited `1` only because
`research/NEXT_RESEARCH_STEPS.md` retained CR bytes on checkout lines not
replaced by the initial semantic patch. The other six paths passed. This was
recorded rather than hidden by the retry.

The research-priority file was replaced in full through `apply_patch` with the
same ordering and current-task meaning in normalized UTF-8/LF form. The exact
repeated audit then exited `0` and reported `ok=true` for all seven paths. At
that audit point their bytes and SHA-256 were:

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `tests/unit/test_upstream_candidate_inspection.py` | 29,837 | `936dd1463a41905c268c5d07238629bf83980e672c2f76cc0099ec8c98f257ea` |
| `REVIEW_STATE.yaml` | 2,210 | `101b5f70993a8740c99bb12a0609c554ffcd3d9c6de3e16ccd57cf5e66b9077c` |
| `CURRENT_STATUS.md` | 6,806 | `805b887545e8c815f90e69bbb914cf7889ff954922dcdbab2a47b66dc28347ec` |
| `research/NEXT_RESEARCH_STEPS.md` | 6,370 | `f1745e08aaa2405bf2154795aab4aa6286ba8684c306d9f472f38685f6ac6b03` |
| task `TASK_STATUS.md` | 4,901 | `bb9114d49ca14b1feae5a664f717fc3119e8b83eef84ae92200e5b79b734a94f` |
| task `TASK_LOG.md` | 6,224 | `dbf4052aa129c4cd6fea1c879ceabef358372fea36931f51aaf1d85230871ee3` |
| task `EVIDENCE.md` | 12,411 | `f024c2cb5221a6d027b0174bcb5dadd543a0725907c266ffd431c2808728ac4e` |

The dossier files change again when final audit results are appended; terminal
closing hashes are therefore recomputed after dossier closure rather than
misrepresenting these intermediate values as recursive final hashes.

## EV-013 - Final gate and disposition

The terminal pre-handoff validator repetition accepted strict review-state
JSON, all seven schemas, all eleven Action pins in two workflows, and all ten
preserved upstream files. The committed-range checker again returned
`ok=true` for exact committed range `a7066e70...a7066e70`; its pre-commit
worktree limitation remains explicit. `git diff --check` returned no output,
the index listing was empty, and status named exactly four authorized tracked
modifications plus three authorized new dossier files.

The first composite final preservation wrapper failed at JavaScript parse time
because an embedded PowerShell backtick was not escaped. It executed no nested
tool and changed no state. The corrected wrapper exited `0` with:

A subsequent closing-hash wrapper also failed before execution when Markdown
backticks in ready-state string literals terminated its JavaScript template.
Its corrected form removed the ambiguous literals and exited `0`. Neither
parser failure ran a nested command or altered repository state.

After closure, one final read-only reporting wrapper printed the tracked diff
stat (`4 files changed, 345 insertions, 89 deletions`) and then failed to start
its separate `rg` line-locator because a Markdown backtick left the PowerShell
string unterminated. That failed locator ran no repository command and changed
no state. It is retained here as an operational anomaly; it has no effect on
the complete diff inspection or file-path evidence.

```text
root=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
branch=main
head=a7066e70b92d80be2d1772127f329c24222c1b41
allowlist_match=true
follow_ups=RFU-TEST-001:MEDIUM:OPEN,RFU-ENV-001:MEDIUM:OPEN
rfu_env_unchanged=true
byte_audit_ok=true
protected_file_count=161
protected_total_bytes=1082408
protected_serialized_bytes=17397
protected_inventory_sha256=8432dfeb225620e369da44a5b9426b665761ee26035ed6eb06852148557629f0
protected_inventory_matches_initial=true
git_config_sha256=212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10
git_index_sha256=d37bb84289e54dea195af81a554302ac25105cf4b63c33e4fd1d83385a7860ba
config_worktree_exists=false
info_attributes_exists=false
remaining_task_basetemps=0
```

Thus the production inspector, accepted environment-boundary work, claims,
pruning, and every other protected tracked file remain byte-identical. Both
follow-ups remain `OPEN`, `RS-001` remains `NOT STARTED`, and no mathematical
classification changes. The task is `READY_FOR_REVIEW`.
