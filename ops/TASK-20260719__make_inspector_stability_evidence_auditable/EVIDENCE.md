# TASK-20260719__make_inspector_stability_evidence_auditable - Evidence

All evidence in this dossier is review-governance and bounded engineering-test
evidence. It establishes no upstream reproduction, exhaustive coverage,
certificate, counterexample, theorem, proof, mathematical claim, or pruning
rule.

`STABILITY_EVIDENCE.json` is the canonical record of the 27 required
executions. This Markdown file summarizes and cross-references that report;
it will not transcribe the individual run records.

## EV-001 - Startup gate

Successful read-only Git commands used only:

```text
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
```

They established:

```text
root=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
origin=https://github.com/falker47/erdos-gyarfas-p14.git
branch=main
HEAD=c71d66995ae6a36620a2aa8f938faf6d84fe1af7
review_base=a7066e70b92d80be2d1772127f329c24222c1b41
review_base_type=commit
review_base_is_ancestor=true
worktree_entries=0
index_entries=0
```

Plain Git first exited `1` for sandbox dubious ownership. No configuration was
added or modified. The owner-global ignore warning produced no status entry.

## EV-002 - Review finding and cumulative boundary

The cumulative committed range
`a7066e70b92d80be2d1772127f329c24222c1b41..c71d66995ae6a36620a2aa8f938faf6d84fe1af7`
contains one commit, `c71d669`, with seven changed paths, 996 insertions, and
89 deletions. The rejected dossier tree contains only `TASK_STATUS.md`,
`TASK_LOG.md`, and `EVIDENCE.md`.

The test redesign was statically sound, but its stated 25 focused passes and
two complete-suite passes were supported only by Markdown transcription. No
raw output, JUnit result, machine-readable run bundle, CI artifact, or other
independently checkable execution record was present. The accepted baseline
therefore remains unchanged, and the next review remains cumulative from it.

## EV-003 - Initial authorized-path state

The four existing authorized paths began as:

| Path | Bytes | Initial SHA-256 |
| --- | ---: | --- |
| `tools/validate_schemas.py` | 3,256 | `c9849f75db7c45786cb7ddbb3ac6de0f44eb23d7d90331d5d2797fa0ff5fb5dd` |
| `REVIEW_STATE.yaml` | 2,210 | `101b5f70993a8740c99bb12a0609c554ffcd3d9c6de3e16ccd57cf5e66b9077c` |
| `CURRENT_STATUS.md` | 6,829 | `49342fc55d7c044b3ac13c07db52df71576daf096b4dfb890db338b55229d7c0` |
| `research/NEXT_RESEARCH_STEPS.md` | 6,370 | `f1745e08aaa2405bf2154795aab4aa6286ba8684c306d9f472f38685f6ac6b03` |

These eight authorized paths were initially absent:

- `schemas/inspector-timeout-stability-evidence.schema.json`
- `tools/run_inspector_timeout_stability.py`
- `tools/verify_inspector_timeout_stability.py`
- `tests/unit/test_inspector_timeout_stability_evidence.py`
- task `TASK_STATUS.md`
- task `TASK_LOG.md`
- task `EVIDENCE.md`
- task `STABILITY_EVIDENCE.json`

## EV-004 - Initial protected anchors

Critical protected paths began as:

| Path | Bytes | Initial SHA-256 |
| --- | ---: | --- |
| rejected `TASK_STATUS.md` | 5,516 | `84a6077b992df616f3f72564cc7691416a65186b80eb1f84e8ccb264517553cd` |
| rejected `TASK_LOG.md` | 8,751 | `78a4e08a50525ad46df84488099abadbd4ba61bd1891c3074f1ca9340eaf290f` |
| rejected `EVIDENCE.md` | 16,703 | `b0ea48f1d1a3e1d1c817c2d2746e0c6aad20b1b148db8d6182af450d45c3d731` |
| `tests/unit/test_upstream_candidate_inspection.py` | 29,837 | `936dd1463a41905c268c5d07238629bf83980e672c2f76cc0099ec8c98f257ea` |
| `tools/inspect_upstream_candidate.py` | 46,163 | `301c427a768e80065d1219a917ac026168c0ab2e9a5226a8f521009d1a73678f` |
| `research/CLAIMS_REGISTRY.yaml` | 5,495 | `0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c` |
| `research/PRUNING_REGISTRY.md` | 3,160 | `34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a` |
| `research/ENVIRONMENT_LOCK_INVENTORY.json` | 99,971 | `1c51bf98a567c24b2b4058a11c499bb2aebd13a3f18606b15d90d791c401b144` |
| `research/ENVIRONMENT_TRUST_BOUNDARY.md` | 22,469 | `d197fbe8e26b0cc4f19b78af358699438a25ae50122ca634c7931a43040bedd7` |

The canonical protected tracked inventory excludes only the four existing
authorized paths. It serializes ordinal-sorted POSIX records as
`path<TAB>bytes<TAB>sha256<LF>` over raw file bytes:

```text
tracked_file_count=168
protected_file_count=164
protected_total_bytes=1139959
protected_serialized_bytes=17827
protected_inventory_sha256=7ac977493f2f6058e8fd190a36b84ce707ea398ec8787fc815fbab469c7af1ce
```

Git metadata anchors were:

```text
.git/config bytes=308 sha256=212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10
.git/index bytes=19466 sha256=e3150bec1c21965b92231c19519d2695c821106188487d7122b082352f5f4f12
.git/config.worktree=absent
.git/info/attributes=absent
```

The closing audit must reproduce every protected value and separately compare
the union of tracked modifications and untracked paths against the authorized
allowlist. `git diff --name-status` alone is insufficient because it omits
untracked files.

## EV-005 - Governance transition

`REVIEW_STATE.yaml` keeps `review_base_commit` and
`accepted_baseline_commit` equal to
`a7066e70b92d80be2d1772127f329c24222c1b41`. It records last reviewed HEAD
`c71d66995ae6a36620a2aa8f938faf6d84fe1af7`, verdict `REJECT`, accepted task
`TASK-20260719__define_environment_trust_boundary`, this active task, and the
actual state-write time `2026-07-19T12:22:54Z`.

`RFU-TEST-001` remains `MEDIUM` and `OPEN`. The complete `RFU-ENV-001` object
remains unchanged and `OPEN`. Current state and research priority record the
rejected review occurrence `2026-07-19T11:58:09Z`, immutable rejected dossier,
cumulative next-review boundary, and commit-neutral candidate-SHA wording.

## EV-006 - Implemented schema, runner, verifier, and tests

The authorized implementation provides:

- a strict recursively closed-world schema and registered schema validator;
- one standard-library runner for exactly 25 focused plus two complete-suite
  executions, in that order, serially, with no retry and stop-on-first-failure;
- canonical partial-report persistence after completed attempts, complete
  Base64 stdout/stderr bytes, sizes, hashes, timestamps, commands, pytest
  outcomes, and positively owned basetemp cleanup;
- a deterministic 170-file execution-source inventory and fingerprint;
- an independent verifier that does not import the runner, does not trust
  summary totals, and separately parses stream and pytest facts;
- portable core verification of recorded absolute executable identities plus
  opt-in same-host Python/tool rehashing with `--rehash-environment`;
- fake-subprocess tests for success, partial failure, interruption, no retry,
  environment isolation, source/stream integrity, malformed records, exact
  counts, portability, and bounded cleanup.

The report classification is `EMPIRICAL_OBSERVATION`. Its explicit V1 and
non-mathematical limitations are schema-constrained.

## EV-007 - Single actual evidence execution

Exactly one actual evidence-runner command was invoked:

```text
python tools/run_inspector_timeout_stability.py --eg-cmake C:\msys64\ucrt64\bin\cmake.exe --eg-cxx C:\msys64\ucrt64\bin\g++.exe --eg-ninja C:\msys64\ucrt64\bin\ninja.exe --eg-make C:\msys64\usr\bin\make.exe
```

It exited `0`, starting at `2026-07-19T13:31:35.919158Z` and finishing at
`2026-07-19T13:37:40.838505Z`. Aggregate facts recomputed from the canonical
report are:

```text
completed=true
recorded_run_count=27
focused_run_count=25
focused_passes_each=31
full_suite_run_count=2
full_suite_passes_each=333
successful_run_count=27
failed_run_count=0
retries=0
failed=0
errors=0
skipped=0
xfailed=0
xpassed=0
cleanup_removed=27
cleanup_remaining=0
cleanup_root_absent=true
```

No attempt failed or was interrupted, no partial-failure record was produced,
and no retry occurred. The JSON report retains the complete 27-record detail;
this Markdown evidence intentionally does not duplicate those rows.

The artifact identity is:

```text
path=ops/TASK-20260719__make_inspector_stability_evidence_auditable/STABILITY_EVIDENCE.json
byte_length=93644
sha256=b370e24312b69423c757a69368860f0316added6f86af4c9c7fe7fddc9c484f1
source_file_count=170
source_fingerprint_sha256=415ef1d6ab427a28f5c437371364f181fc3a489f228b2b87cbba80887400f26a
```

## EV-008 - Independent verification

The exact same-host closing command was:

```text
python tools/verify_inspector_timeout_stability.py --rehash-environment ops/TASK-20260719__make_inspector_stability_evidence_auditable/STABILITY_EVIDENCE.json
```

It exited `0`. The verifier independently accepted canonical serialization,
the schema instance, all 170 current source files, the recorded Python and four
tool byte identities, Git object and ancestry requirements, all complete
streams, parsed pytest summaries, exact ordering and counts, timestamps,
no-retry semantics, cleanup, and limitations. Its result returned:

```text
ok=true
report_byte_length=93644
report_sha256=b370e24312b69423c757a69368860f0316added6f86af4c9c7fe7fddc9c484f1
source_fingerprint_sha256=415ef1d6ab427a28f5c437371364f181fc3a489f228b2b87cbba80887400f26a
focused_runs=25
focused_passes_each=31
full_suite_runs=2
full_suite_passes_each=333
```

## EV-009 - Validation gates

| Command | Exit | Result |
| --- | ---: | --- |
| `python tools/resolve_review_task_id.py --state REVIEW_STATE.yaml --require-dossier` | 0 | strict JSON parsed; active task and dossier resolved |
| `python tools/validate_schemas.py --schema inspector-timeout-stability-evidence --instance ops/TASK-20260719__make_inspector_stability_evidence_auditable/STABILITY_EVIDENCE.json` | 0 | report instance and all registered schemas accepted |
| `python tools/validate_schemas.py` | 0 | all registered schemas and instances accepted |
| `python -m pytest -q tests/unit/test_inspector_timeout_stability_evidence.py` | 0 | 34 passed |
| `python -m pytest -q tests/unit` | 0 | 318 passed |
| `python tools/check_github_action_pins.py` | 0 | 11 immutable references in two workflows |
| `python tools/verify_upstream_snapshot.py` | 0 | expected and observed upstream file counts both 10 |
| process-local-safe `git diff --check` | 0 | no whitespace error |
| process-local-safe `git diff --cached --name-only` | 0 | empty index |

The exact pytest gates in this table ran outside the sandbox because the
sandbox denied pytest's default user temporary directory.

## EV-010 - Development-only harness anomalies

Before source finalization and before the one actual evidence command, a
pre-final all-unit harness attempt encountered an outer 60-second shell
timeout/OSError. An invalid inherited Windows stdin handle was separately
eliminated by passing `subprocess.DEVNULL` for child stdin. Sandbox denial of
pytest's default user temporary directory was handled by running the required
exact validation gates outside the sandbox.

These events belong to development and test-harness validation. None invoked
the evidence runner or created an evidence report. They are not failed,
interrupted, partial, or retried evidence attempts. The single actual evidence
report records uninterrupted success and zero retries.

## EV-011 - Frozen inputs, protected state, and cleanup

After source finalization, all 170 report-fingerprinted inputs were frozen.
The independent verifier's source and tool rehash passed against those bytes.

The closing changed-path union contained exactly 11 paths, all authorized.
The complete protected tracked inventory reproduced the startup convention and
values exactly:

```text
protected_file_count=164
protected_total_bytes=1139959
protected_serialized_bytes=17827
protected_inventory_sha256=7ac977493f2f6058e8fd190a36b84ce707ea398ec8787fc815fbab469c7af1ce
```

Every critical protected row in EV-004 remained byte-identical, including the
rejected dossier, production inspector, stabilized timeout-test file, claims,
pruning, and both environment-boundary artifacts. `.git/config` remained 308
bytes with SHA-256
`212a9e15a304b461f9c9512a98f39abb94a20fb492ec232b00981b5c459c3c10`;
`.git/index` remained 19,466 bytes with SHA-256
`e3150bec1c21965b92231c19519d2695c821106188487d7122b082352f5f4f12`.
`.git/config.worktree` and `.git/info/attributes` remained absent. No
task-owned basetemp or basetemp root remained.

Final post-edit complete-diff inspection, exact changed-path allowlisting,
protected-inventory comparison, UTF-8/LF and trailing-whitespace hygiene, and
`git diff --check` all pass. This dossier is `READY_FOR_REVIEW`.

## EV-012 - Current claim boundary

The completed report is bounded V1 engineering-test evidence classified as
`EMPIRICAL_OBSERVATION`. Local verifier success does not accept the cumulative
candidate. `RFU-TEST-001` remains `OPEN` pending independent review;
`RFU-ENV-001` remains unchanged and `OPEN`; `RS-001` remains `NOT STARTED`.
Claims, pruning, production inspector behavior, environment controls, and all
mathematical target statuses remain unchanged. No upstream reproduction,
exhaustive coverage, certificate, theorem, proof, counterexample, mathematical
claim, or pruning result is asserted.
