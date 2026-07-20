# TASK-20260720__bind_stability_evidence_to_exact_worktree - Evidence

All evidence in this dossier is governance or bounded engineering-test
evidence. It has no mathematical implication.

## EV-001 - Startup gate

Process-local-safe Git reads established:

```text
root=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
origin=https://github.com/falker47/erdos-gyarfas-p14.git
branch=main
HEAD=b1eb792a2a771485f37979cd932303f14ab52f56
review_base=a7066e70b92d80be2d1772127f329c24222c1b41
review_base_is_ancestor=true
worktree_entries=0
index_entries=0
```

Plain Git initially exited `1` for sandbox dubious ownership. No Git
configuration was added or modified.

## EV-002 - Initial protected state

The canonical protected tracked inventory excludes the seven existing paths
that the task may modify. It uses ordinal-sorted POSIX records encoded as
`path<TAB>bytes<TAB>sha256<LF>`:

```text
tracked_file_count=176
protected_file_count=169
protected_total_bytes=1282027
protected_serialized_bytes=18552
protected_inventory_sha256=6dc2e78d2ac5bf9416f4854aa7833e09bebf942368ba6f868b9e2c1e412fdb5f
```

Critical protected identities include:

| Path | Bytes | Initial SHA-256 |
| --- | ---: | --- |
| v1 evidence schema | 20,364 | `f49b702e142b95d6b52c0f96cfd78263c11ce8eb45616c81e5c694d757c0ea68` |
| protected timeout test | 29,837 | `936dd1463a41905c268c5d07238629bf83980e672c2f76cc0099ec8c98f257ea` |
| production inspector | 46,163 | `301c427a768e80065d1219a917ac026168c0ab2e9a5226a8f521009d1a73678f` |
| rejected stabilization dossier status | 5,516 | `84a6077b992df616f3f72564cc7691416a65186b80eb1f84e8ccb264517553cd` |
| rejected stabilization dossier log | 8,751 | `78a4e08a50525ad46df84488099abadbd4ba61bd1891c3074f1ca9340eaf290f` |
| rejected stabilization dossier evidence | 16,703 | `b0ea48f1d1a3e1d1c817c2d2746e0c6aad20b1b148db8d6182af450d45c3d731` |
| rejected v1 dossier status | 7,308 | `bc7d48895eeff991d0bfa40dc58b3c369a9bdab52902a3e5ae11a1d3ae1ded71` |
| rejected v1 dossier log | 7,699 | `6a28d4e2ab049a0a9803519473d10c551944935f61dcad99f566138f827d5cec` |
| rejected v1 dossier evidence | 13,053 | `4b82bb678afc0a2ee9392ecaa9efc335fd337da3c05856bc9f6ba698a3d1ad17` |
| rejected v1 JSON report | 93,644 | `b370e24312b69423c757a69368860f0316added6f86af4c9c7fe7fddc9c484f1` |
| claims registry | 5,495 | `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` |
| pruning registry | 3,160 | `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` |

Git metadata anchors started as:

```text
.git/config bytes=308 sha256=212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10
.git/index bytes=20589 sha256=6e1bdc8548a5bb45e397cca7af8cf0150dba647629446333c70dbfc0f380c293
```

## EV-003 - Evidence boundary

The task may create only a v2 `EMPIRICAL_OBSERVATION` for the fixed engineering
test plan. `RFU-TEST-001` and `RFU-ENV-001` remain `OPEN`; `RS-001` remains
`NOT STARTED`. Claims and pruning are protected and byte-identical at startup.

## EV-004 - V2 implementation

The v2 implementation records five exact raw Git probes per snapshot, each
with argv, exit status, complete Base64 stdout and stderr, byte lengths, and
SHA-256 digests:

1. `status --porcelain=v2 -z --untracked-files=all --no-renames`;
2. `ls-files -z`;
3. `ls-files --others --exclude-standard -z`;
4. `ls-files --others --ignored --exclude-standard -z`;
5. `diff --cached --name-only -z --`.

Every Git argv uses the resolved and hashed Git executable plus process-local
`safe.directory` and an empty `core.excludesFile`. Normalization distinguishes
tracked clean, modified, and deleted paths; staged paths; untracked paths;
task-owned ignored basetemps; other ignored paths; task-owned non-execution
artifacts; execution inputs; and unexpected paths. All tracked execution
paths, the authorized untracked v2 schema, and regular files under the ignored
`build/release/**` tree are content-hashed. Every ignored path is also frozen
in the worktree digest.

The runner takes two recorded collection preflights and then permits exactly
25 focused attempts followed by two full-suite attempts. It checks source and
worktree identity immediately before and after every child, uses distinct
task-owned basetemps, stops at the first non-passing outcome, performs no
retry, and atomically preserves a schema-valid partial report after every
attempt. Cleanup is constrained by frozen root, marker, device, and file
identity checks. The verifier does not import the runner and reconstructs Git,
source, collection, pytest, summary, chronology, environment, and cleanup
facts independently.

The v2 schema identity before the real run is:

```text
bytes=24621
sha256=a594a76a3a99a2026bb7f21b176ef32032d919da50fc0f2af6ce6c332d93947b
```

The verifier identity before the independent audit correction was:

```text
bytes=71406
sha256=ef8be88ca89e0ce87d57254b349463ed0a01e3d24e2af21f64a9941a5cb3a48d
```

An independent audit then identified divergent normalization of valid Git
porcelain-v2 unmerged XY states. The verifier now retains the validated raw XY
state just as the runner does, and one synthetic test covers all seven legal
states. Its final pre-run identity is:

```text
bytes=71426
sha256=eaf61bf5efb8e7d5778d4c796b8715512e20b0eec38600e7a3118699f30a05ee
```

## EV-005 - Synthetic and static pre-run checks

Commands actually executed before the real runner invocation include:

```text
python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier
  exit=0; resolved TASK-20260720__bind_stability_evidence_to_exact_worktree

python tools/validate_schemas.py
  exit=0; 9 schemas valid, including the v2 schema

python -m pytest -q tests/unit/test_inspector_timeout_stability_evidence.py
  first sandboxed attempt: exit=1; 51 setup errors because the sandbox could
  not access pytest's user temporary directory
  exact rerun outside that filesystem restriction: exit=0; 51 passed in 16.68s
  first post-audit attempt: exit=1; 51 passed and one test-only helper-name
  failure
  final post-audit rerun: exit=0; 52 passed in 17.76s

python -m pytest -q tests/unit
  pre-audit exit=0; 335 passed in 101.43s
  final post-audit exit=0; 336 passed in 108.77s

python tools/check_github_action_pins.py
  exit=0; 2 workflows and 11 external action references checked

python tools/verify_upstream_snapshot.py
  exit=0; 10/10 upstream files unchanged

git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 diff --check
  exit=0
```

The successful pytest commands used the required local native-tool overrides:

| Tool | Override | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| CMake | `C:/msys64/ucrt64/bin/cmake.exe` | 9,777,292 | `ffca3626caf34f69bdcfb38d5040ff622080d5add3928ee678582d3d92e83bc0` |
| C++ | `C:/msys64/ucrt64/bin/g++.exe` | 2,781,056 | `9e69b6c6d6593d143476ae93098ba8df897835949e5fd6be4f3df919371f4913` |
| Ninja | `C:/msys64/ucrt64/bin/ninja.exe` | 1,318,176 | `de6836289099ec47cc4aa4671b1522eafc73b9b4dd73ac407b8bb7cdd46b60ce` |
| Make | `C:/msys64/usr/bin/make.exe` | 228,832 | `6732605294c9f11ffc9e0ed112786bc63d65c8d8b6a22d14281bcb4e90148f20` |

The final 52-case synthetic suite covers all 28 required families, including
staged and arbitrary untracked inputs, `pytest.ini`, `conftest.py`, an added
test, `sitecustomize.py`, omitted execution sources, malformed or altered raw
Git records, exact collection and count mutations, noncanonical JSON and
streams, partial failure and interruption, source/worktree mutation, cleanup
root replacement, environment identity changes, and all legal porcelain-v2
unmerged states. It constructs synthetic reports and never invokes the real
27-attempt runner plan.

## EV-006 - Pre-run worktree and cleanup state

The final development preflight accepted the current allowlist and source
classification. With task-development basetemps removed, the ignored-path
population returned to the initial 439 entries. The source inventory contains
195 execution-input records after including ignored `build/release/**`
regular files. No report, atomic-report temporary file, or active task-owned
stability basetemp existed before the permitted real invocation.

The last raw Git/source preflight after every implementation and dossier edit
reported:

```text
accepted=true
tracked_clean=170
tracked_modified=6
staged=0
untracked=4
ignored_other=439
ignored_task_basetemps=0
execution_inputs=195
source_record_count=195
unexpected=[]
source_fingerprint_sha256=18b608d925c515cec2edba7781b23b29f166cb0a500a7ea0587848d342028949
execution_state_sha256=36acc12d82df0bdc8f3e05c7120942ef0a38c168862d8190563f10e5564931d0
```

This direct preflight used the runner's snapshot acquisition function only;
it launched no pytest child and was not the real v2 runner invocation.

## EV-007 - The single permitted real invocation

Exactly one real runner command was executed:

```text
python tools/run_inspector_timeout_stability.py \
  --eg-cmake C:/msys64/ucrt64/bin/cmake.exe \
  --eg-cxx C:/msys64/ucrt64/bin/g++.exe \
  --eg-ninja C:/msys64/ucrt64/bin/ninja.exe \
  --eg-make C:/msys64/usr/bin/make.exe
exit=1
```

The report records:

```text
execution_started_at_utc=2026-07-20T09:46:48.207097Z
execution_finished_at_utc=2026-07-20T09:46:48.414933Z
completed=false
stop_reason=failure
failure_detail=Git ignored probe emitted unexpected stderr
recorded_process_count=0
recorded_run_count=0
successful_run_count=0
failed_run_count=0
collection_status=pending
```

The first raw snapshot is labelled `before:1:collect_focused`. Four Git probes
had exit `0` and empty stderr. The ignored-path probe also exited `0`, but its
complete preserved stderr has:

```text
byte_length=792
sha256=e03b5828ea227da73e49f4c4733bcf4c27281c388653bec129cd84050de2ae73
```

Git reported permission denied while opening these nine pre-existing ignored
directories:

```text
build/pytest-benchmark-final/
build/pytest-benchmark-required/
build/pytest-bounded-required/
build/pytest-inspector-required/
build/pytest-integration-final/
build/pytest-integration-harden/
build/pytest-integration-harden-2/
build/pytest-integration-outcomes/
build/pytest-integration-required/
```

The fail-closed runner therefore rejected the snapshot before invoking pytest.
Per the one-invocation rule, no retry was performed and none is permitted in
this task.

## EV-008 - Evidence contained in the partial report

The preserved artifact is
`ops/TASK-20260720__bind_stability_evidence_to_exact_worktree/STABILITY_EVIDENCE.json`:

```text
bytes=30387
sha256=5481b90013d2e20e8e23fb9f21269048749208a0b381381c6eb5b93594b9f348
schema_version=2.0
snapshot_count=1
source_file_count=0
source_fingerprint_sha256=null
worktree_identity_sha256=null
collection_digest_sha256=null
focused_count=null
full_suite_count=null
```

This is a canonical partial failure record, not completed stability evidence.
The source and normalized worktree inventories were intentionally not accepted
after the raw Git acquisition warning, so their report digests remain null.
Collection never began, so its digest and both exact counts also remain null.

Cleanup is complete and identity-verified. The runner created and positively
removed only
`build/TASK-20260720__bind_stability_evidence_to_exact_worktree-basetemps/collection-focused`,
removed its task-owned root, recorded no remaining or unexpected entries, and
confirmed the atomic-report temporary file absent.

## EV-009 - Commands actually executed after the real invocation

```text
python tools/validate_schemas.py --schema inspector-timeout-stability-evidence-v2 \
  --instance ops/TASK-20260720__bind_stability_evidence_to_exact_worktree/STABILITY_EVIDENCE.json
  exit=0; instance valid

python tools/verify_inspector_timeout_stability.py --rehash-environment \
  ops/TASK-20260720__bind_stability_evidence_to_exact_worktree/STABILITY_EVIDENCE.json
  exit=1; valid partial record but not completed evidence

python tools/verify_inspector_timeout_stability.py --rehash-environment \
  --allow-partial \
  ops/TASK-20260720__bind_stability_evidence_to_exact_worktree/STABILITY_EVIDENCE.json
  exit=0; completed=false; evidence_success=false; recorded_runs=0
```

The partial verifier independently decoded and hashed the raw streams,
validated the canonical JSON and closed schema, reconstructed the preserved
failed Git acquisition, rehashed same-host Python, Git, and native tools, and
verified cleanup. Its success means only that the incomplete prefix is
internally consistent.

## EV-010 - Manual verifications

- The real runner command appears exactly once in the task chronology and was
  not retried.
- The report, snapshot label, summary, raw ignored-probe stderr, hashes,
  timestamps, process/run counts, and cleanup fields were inspected directly.
- The report temporary path and task-owned basetemp root are absent after
  cleanup.
- The protected inventory, prior v1 artifacts, claims, pruning, Git index, and
  exact changed-path allowlist are checked again during finalization.

## EV-011 - Verifications not available

- A passing completed-evidence verifier result is unavailable because the
  report is partial.
- No collection node IDs, collection digest, focused count, or full-suite count
  were observed.
- No focused or full-suite stability attempt ran; consequently there is no
  serial 25-plus-2 result and no passing-outcome claim.
- Source/worktree immutability across child brackets was not exercised because
  no child process began.

## EV-012 - Limitations and claim boundary

The partial artifact records one fail-closed engineering failure only. It is
not the requested bounded V1 stability observation and cannot resolve
`RFU-TEST-001`. It is not V3 or V4 evidence, an upstream reproduction, an
exhaustive search, a certificate, a theorem, a proof, a counterexample, a
pruning result, or any other mathematical evidence. The direct pre-run digest
reported in EV-006 is diagnostic preflight output and is not promoted into the
failed report.

## EV-013 - Final protected-state and hygiene audit

Final read-only checks produced:

```text
changed_path_count=11
changed_path_allowlist_delta=[]
staged_status_lines=[]
index_entries=0
tracked_file_count=176
protected_file_count=169
protected_total_bytes=1282027
protected_serialized_bytes=18552
protected_inventory_sha256=6dc2e78d2ac5bf9416f4854aa7833e09bebf942368ba6f868b9e2c1e412fdb5f
utf8_lf_trailing_paths_checked=11
utf8_lf_trailing_failures=[]
git_diff_check_exit=0
cumulative_baseline_diff_check_exit=0
report_temp_exists=false
basetemp_root_exists=false
```

The v1 schema, protected timeout test, production inspector, both rejected
dossiers and the prior v1 report, claims registry, and pruning registry retain
the exact byte lengths and SHA-256 values in EV-002. Git metadata anchors also
remain exact:

```text
.git/config bytes=308 sha256=212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10
.git/index bytes=20589 sha256=6e1bdc8548a5bb45e397cca7af8cf0150dba647629446333c70dbfc0f380c293
```

`RFU-ENV-001` is deep-equal to its task-start object and `OPEN`;
`RFU-TEST-001` is `OPEN`. `review_base_commit` and
`accepted_baseline_commit` remain
`a7066e70b92d80be2d1772127f329c24222c1b41`. No `git add`, `git commit`,
`git push`, rebase, amend, reset, merge, or Git-configuration write was
executed.
