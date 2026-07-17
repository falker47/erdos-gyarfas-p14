# TASK-20260717__enforce_process_outcome_semantics — Evidence

## EV-001 — Immutable startup gate

- Question: Did every immutable repository precondition pass before any file
  was modified?
- Initial exact command:

```powershell
git rev-parse --show-toplevel
```

- Complete initial result: Git stopped with `detected dubious ownership`; it
  identified checkout owner `HYCARUS/Falker` and process owner
  `HYCARUS/CodexSandboxOffline`, and suggested a global configuration change.
  No Git configuration or repository file was changed.
- Exact successful commands used only a process-local exception:

```powershell
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 rev-parse --show-toplevel
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 branch --show-current
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 rev-parse HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 status --porcelain=v1 --untracked-files=all
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 merge-base --is-ancestor f8271e74509a017d1631dea72aaa652f44d8c3df HEAD
```

- Complete successful output, in command order:

```text
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
main
f8271e74509a017d1631dea72aaa652f44d8c3df
[status contained no worktree entries; Git emitted only two warnings that the
user-global ignore file was inaccessible to the sandbox identity]
[merge-base exited 0 with no output]
```

- Interpretation: exact root, `main`, task-start HEAD, clean worktree, and
  baseline ancestry passed. Modification was permitted.
- Classification: repository-state observation only; no claim effect.

## EV-002 — Required reading and accepted-baseline diff

- Question: Was the design based on the complete repository-defined evidence
  before editing?
- Method: read all 30 explicitly ordered items in full, including every file
  in the two named earlier dossier directories; inspected relevant benchmark
  documentation, common tooling, schema validation, verifier tests and
  predicate tests; mapped all callers with `rg`; and inspected Git history.
- Exact cumulative commands:

```powershell
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --stat f8271e74509a017d1631dea72aaa652f44d8c3df..HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --name-status f8271e74509a017d1631dea72aaa652f44d8c3df..HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --no-ext-diff --no-color f8271e74509a017d1631dea72aaa652f44d8c3df..HEAD
```

- Complete output: all three commands exited `0` with no output because the
  accepted baseline and task-start HEAD are identical.
- Interpretation: there was no pre-existing candidate patch to account for.
  The implementation is based on repository evidence rather than prior chat.
- Classification: repository-state observation only; no claim effect.

## EV-003 — Implemented process-outcome and trust-boundary semantics

- Tiny integration contract: `k=3` and `k=4` accept only
  `(termination_reason="exited", exit_code=0)`. Timeout, spawn error, signal,
  exit `100`, and every other exit fail with exact byte-stream diagnostics.
- Exit-100 adapter: the test-local, project-authored parser requires complete
  UTF-8 upstream adjacency output with a final LF and exact line grammar. It
  accepts arbitrary declaration order because upstream stores vertices in an
  unordered map, but requires labels exactly `0..n-1`. It rejects malformed
  lines, blank lines, noncanonical numeric labels, duplicate declarations,
  duplicate neighbors, loops, undeclared endpoints, and asymmetry before
  constructing `egverify.graph.Graph`.
- Independent candidate predicates: project-authored `minimum_degree`,
  `find_induced_path`, `relevant_power_of_two_lengths`, and
  `find_exact_cycle` evaluate minimum degree at least 3, induced-`P_k`
  absence, and absence at every relevant power-of-two length. Successful
  parsing records canonical serialization and SHA-256. Exact stdout/stderr
  bytes remain reconstructable from full base64 plus SHA-256 in the failure
  record. No upstream parser or predicate implementation is imported.
- Benchmark case contract: `accepted_outcomes` is required and nonempty; each
  item contains exactly `termination_reason` and `exit_code`; reason/code
  compatibility, boolean exclusion, unknown fields, duplicates, and canonical
  sort order are validated. Matching compares one normalized actual object to
  complete accepted objects, never independent lists.
- Runner/result contract: stdout and stderr are written, hashed, the result is
  schema-validated and written, and a result hash is computed before returning
  status `3` for an unaccepted attempted outcome. Exact acceptance returns `0`;
  configuration/schema/artifact errors return `1`. Structured output uses
  `ok` equal to `outcome_accepted`, so an unexpected child outcome never prints
  `ok: true`.
- CI contract: the runner step fails natively; an `always()` step validates the
  result; a `failure()` step emits bounded JSON-escaped prefixes, byte counts,
  and hashes. No `continue-on-error`, pipeline, `|| true`, or captured shell
  status masks the runner.
- Classification: engineering implementation only. Result classification is
  still `EMPIRICAL_OBSERVATION`; no claim or pruning rule changes.

## EV-004 — Focused synthetic tests and preserved corrections

- Initial focused commands and outputs:

```text
python -m pytest -q tests/unit/test_benchmark_outcomes.py
..............................                                           [100%]
30 passed in 0.09s

python tools/validate_schemas.py
{"ok": true, "schemas_checked": ["schemas/benchmark-result.schema.json", "schemas/counterexample.schema.json", "schemas/experiment-manifest.schema.json", "schemas/search-certificate.schema.json", "schemas/search-partition.schema.json"]}

python -m pytest -q tests/integration/test_upstream_build.py -k "adjacency_parser or candidate_diagnostic or exit_100"
.............                                                            [100%]
13 passed, 4 deselected in 0.05s
```

- A subsequent synthetic full-run test deliberately supplied an unaccepted
  exit `100` and required the result/stdout/stderr to survive. Its first run
  reported `30 passed, 1 failed`; the relevant schema error was:

```text
Additional properties are not allowed ('exit_code', 'termination_reason' were unexpected)
On instance['accepted_outcomes'][0]:
    {'termination_reason': 'exited', 'exit_code': 0}
```

- Cause and correction: `$defs.process_outcome` used
  `additionalProperties: false`, while its fields appeared only inside
  `oneOf`. Declaring the two properties at the same object level corrected the
  schema; the unchanged preservation test then passed with `31 passed`.
- Independent final review found that Python equality equates `True` with `1`.
  Actual-pair normalization was restored, a boolean regression was added, and
  direct synthetic tests now exercise `TimeoutExpired`, `OSError`, and negative
  signal mapping in `execute()`. Raw exit-100 streams replaced text-mode
  capture, and late diagnostic hashing moved inside the guarded artifact path.
- Complete final focused output:

```text
python -m pytest -q tests/unit/test_benchmark_outcomes.py
...................................                                      [100%]
35 passed in 0.21s

python -m pytest -q tests/integration/test_upstream_build.py -k "adjacency_parser or candidate_diagnostic or exit_100"
.............                                                            [100%]
13 passed, 4 deselected in 0.05s
```

- Covered cases: accepted exit `0`; unexpected exit `100`; timeout/null;
  spawn-error/null; signal/negative; malformed, unknown, duplicate, empty, and
  incompatible accepted outcomes; no Cartesian leakage; deterministic
  serialization; exact artifact preservation; well-formed out-of-order
  adjacency; malformed syntax; noncanonical labels; duplicate declarations
  and neighbors; loops; undeclared endpoints; asymmetry; and a K4 diagnostic
  that fails the C4 predicate.
- Classification: `VERIFIED_BOUNDED_COMPUTATION` for these exact synthetic
  engineering cases only.

## EV-005 — Native build and real tiny-process outcomes

- Tool discovery output:

```text
cmake  MISSING on sandbox PATH
g++    MISSING on sandbox PATH
ninja  MISSING on sandbox PATH
make   MISSING on sandbox PATH
FOUND  C:\msys64\ucrt64\bin\cmake.exe
FOUND  C:\msys64\ucrt64\bin\g++.exe
FOUND  C:\msys64\ucrt64\bin\ninja.exe
FOUND  C:\msys64\usr\bin\make.exe
```

- The first exact integration command passed 13 synthetic tests and skipped
  four tool-dependent tests because those tools were absent from PATH. The
  first explicit-tool retry passed 13 and errored four times before execution
  because the sandbox could not access pytest's user temp directory. The first
  in-repository basetemp retry likewise passed 13 and errored four times because
  its parent `build/` did not yet exist. These environment failures occurred
  before a tiny child process started and are not represented as outcome
  passes. Creating the ignored build parent resolved the environment only.
- Exact final integration invocation (the environment variables name the
  located tools and supply an in-repository basetemp while preserving the
  required pytest command):

```powershell
$env:EG_CMAKE='C:\msys64\ucrt64\bin\cmake.exe'
$env:EG_CXX='C:\msys64\ucrt64\bin\g++.exe'
$env:EG_NINJA='C:\msys64\ucrt64\bin\ninja.exe'
$env:EG_MAKE='C:\msys64\usr\bin\make.exe'
$env:PYTEST_ADDOPTS='--basetemp=build/pytest-integration-final'
python -m pytest -q tests/integration/test_upstream_build.py
```

- Complete final output:

```text
.................                                                        [100%]
17 passed in 5.45s
```

- Required release configure command and complete output:

```powershell
cmake -S . -B build/release -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

```text
-- The CXX compiler identification is GNU 13.1.0
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: C:/msys64/ucrt64/bin/c++.exe - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done (2.4s)
-- Generating done (0.0s)
-- Build files have been written to: C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14/build/release
```

- Required release build command and complete output:

```powershell
cmake --build build/release --target eg-upstream-serial
```

```text
[1/4] Building CXX object CMakeFiles/eg-upstream-serial.dir/third_party/erdos-gyarfas/src/lib.cpp.obj
[2/4] Building CXX object CMakeFiles/eg-upstream-serial.dir/third_party/erdos-gyarfas/src/main.cpp.obj
[3/4] Building CXX object CMakeFiles/eg-upstream-serial.dir/third_party/erdos-gyarfas/src/graph.cpp.obj
[4/4] Linking CXX executable bin\eg-upstream-serial.exe
```

- Direct bounded process check deliberately suppressed timing values and
  reported only outcome/stream facts:

```text
k=3 termination_reason=exited exit_code=0 stdout_nonempty=True stderr_empty=True
k=4 termination_reason=exited exit_code=0 stdout_nonempty=True stderr_empty=True
```

- Interpretation: both known tiny cases produced the sole ordinary accepted
  pair. No real exit `100`, malformed output, verifier disagreement, timeout,
  signal, spawn error, or other surprising process outcome occurred.
- Classification: bounded engineering execution only; not an upstream
  reproduction or mathematical result.

## EV-006 — Final real benchmark, schema assertion, hashes, and cleanup

- Exact runner command:

```powershell
python tools/run_benchmark.py benchmarks/cases/upstream-small-k.json --output benchmarks/results/task-process-outcome-check.json
```

- Complete final machine output:

```json
{"accepted_outcomes": [{"exit_code": 0, "termination_reason": "exited"}], "actual_outcome": {"exit_code": 0, "termination_reason": "exited"}, "artifacts": {"result": {"path": "benchmarks/results/task-process-outcome-check.json", "sha256": "ad45ef5dc342d942d779c461c912f86ad44b167d2fa2a92628d7d7dfdbfe2229"}, "stderr": {"path": "benchmarks/results/task-process-outcome-check.stderr.txt", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}, "stdout": {"path": "benchmarks/results/task-process-outcome-check.stdout.txt", "sha256": "a5df640ea9e3541cc20c633885fef26a0c635fa5f4789d1cf859a8ce062ff90c"}}, "case_id": "upstream-serial-k3", "ok": true, "outcome_accepted": true}
```

- Exact schema command and complete output:

```text
python tools/validate_schemas.py --schema benchmark-result --instance benchmarks/results/task-process-outcome-check.json
{"instance_checked": {"instance": "benchmarks/results/task-process-outcome-check.json", "schema": "schemas/benchmark-result.schema.json"}, "ok": true, "schemas_checked": ["schemas/benchmark-result.schema.json", "schemas/counterexample.schema.json", "schemas/experiment-manifest.schema.json", "schemas/search-certificate.schema.json", "schemas/search-partition.schema.json"]}
```

- The required programmatic assertions printed:

```json
{"accepted_outcomes": [{"exit_code": 0, "termination_reason": "exited"}], "exit_code": 0, "outcome_accepted": true, "termination_reason": "exited"}
```

- Independently recomputed hashes before cleanup:

```text
task-process-outcome-check.json        ad45ef5dc342d942d779c461c912f86ad44b167d2fa2a92628d7d7dfdbfe2229
task-process-outcome-check.stdout.txt  a5df640ea9e3541cc20c633885fef26a0c635fa5f4789d1cf859a8ce062ff90c
task-process-outcome-check.stderr.txt  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

- The three explicit paths were resolved beneath `benchmarks/results/`,
  removed non-recursively, and the complete remaining listing was:

```text
Name      Length
.gitkeep       1
```

- Interpretation: the case accepted exactly ordinary exit `0`; actual and
  accepted pairs agree; the emitted result is schema-valid and
  `EMPIRICAL_OBSERVATION`; no generated measurement remains in the candidate.

## EV-007 — Required final validators and test matrix

- Exact commands:

```text
python -m json.tool REVIEW_STATE.yaml
python tools/validate_schemas.py
python tools/verify_upstream_snapshot.py
python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
python -m pytest -q tests/unit/test_benchmark_outcomes.py
python -m pytest -q tests/integration/test_upstream_build.py
python -m pytest -q --basetemp build/pytest-root
```

- `python -m json.tool` exited `0` and printed the full state object. Its exact
  review fields were:

```json
{
  "review_base_commit": "f8271e74509a017d1631dea72aaa652f44d8c3df",
  "accepted_baseline_commit": "f8271e74509a017d1631dea72aaa652f44d8c3df",
  "last_reviewed_head": "f8271e74509a017d1631dea72aaa652f44d8c3df",
  "last_verdict": "ACCEPT WITH FOLLOW-UP",
  "accepted_task_id": "TASK-20260717__repair_postcommit_review_state",
  "active_task_id": "TASK-20260717__enforce_process_outcome_semantics",
  "pending_follow_up_ids": [
    "RFU-CI-001",
    "RFU-CI-002",
    "RFU-WORKFLOW-001",
    "RFU-CI-003",
    "RFU-SUPPLY-001",
    "RFU-ENV-001"
  ],
  "pending_follow_up_statuses": ["OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN"]
}
```

- Complete schema and snapshot outputs:

```text
{"ok": true, "schemas_checked": ["schemas/benchmark-result.schema.json", "schemas/counterexample.schema.json", "schemas/experiment-manifest.schema.json", "schemas/search-certificate.schema.json", "schemas/search-partition.schema.json"]}
{"added": [], "changed": [], "expected_file_count": 10, "missing": [], "observed_file_count": 10, "ok": true, "snapshot_path": "third_party/erdos-gyarfas"}
```

- Complete final pytest outputs:

```text
........................................................................ [ 76%]
......................                                                   [100%]
94 passed in 3.88s

...................................                                      [100%]
35 passed in 0.21s

.................                                                        [100%]
17 passed in 5.45s

........................................................................ [ 64%]
.......................................                                  [100%]
111 passed in 10.38s
```

- The integration and full-suite commands used only the explicit `EG_*`
  MSYS2 tool paths recorded in `EV-005`; the integration command also obtained
  its basetemp through `PYTEST_ADDOPTS`. No test was skipped in either final
  native run.
- Hosted GitHub Actions and Docker were unavailable. They were not run and are
  not represented as passed. Every required local check was available after
  the documented sandbox environment corrections.
- Classification: bounded engineering and predicate verification only.

## EV-008 — Protected preservation and final scope

- The first raw preservation script passed the claims registry and then
  stopped as follows:

```text
PASS claims_registry: files=1 raw_inventory_sha256=a5b757e4cbf9e4cf8d2fa4cf6e15fcbf54b76592f4aac220eb5bfd93f3c280d9
FAIL pruning_registry: raw mismatch research/PRUNING_REGISTRY.md
```

- Diagnostic output established a checkout line-ending representation rather
  than a content change:

```text
baseline_blob=962075aa9f0c48492162bca322195fed802a1a1f
worktree_raw_blob=10a8ec03921553f2a8b66c13d3a600307c55b3d8
worktree_filtered_blob=962075aa9f0c48492162bca322195fed802a1a1f
worktree_sha256=34e821c1fc622dea4ed28cfa32cbcbc1eb1e6ae92c2bb1f3538c27c69db2e22a
git_diff_exit=0
```

- The task permits raw-byte **or Git-blob** preservation checks. The corrected
  audit used filtered Git-blob identity for text checkout paths and required
  both raw and filtered identity for the preserved upstream snapshot. Complete
  successful output:

```text
PASS claims_registry: files=1 mode=filtered-git-blob inventory_sha256=5a504d463b476e5054b446f0358ad1c01fa89da72c22bc37ac9bd39aea7111dc
PASS pruning_registry: files=1 mode=filtered-git-blob inventory_sha256=590d4035c2338705f1312e2117eee1617cbe95e7675c9ab4dada037f04f2792b
PASS all_prior_dossiers: files=12 mode=filtered-git-blob inventory_sha256=d20e34fd3c6daa20fcd574eaf417bdfc2071789689bf95ed8752a90676dc340e
PASS third_party_upstream: files=10 mode=raw+filtered inventory_sha256=2af15c3bd194dbbb45d0bbebb20745ffd5ea2b2a2b99b7e0206086b15eed1178
PASS heavy_workflow: files=1 mode=filtered-git-blob inventory_sha256=55e0ca4c1d0c9ab2764a8ab718d6396aa6cf92ec227398726d79ba040586a443
GIT-BLOB/RAW PRESERVATION: PASS
```

- This proves preservation relative to task-start HEAD for
  `research/CLAIMS_REGISTRY.yaml`, `research/PRUNING_REGISTRY.md`, every one of
  the 12 files in all prior dossiers, all 10 preserved upstream files, and
  `.github/workflows/heavy-search.yml`. `verify_upstream_snapshot.py`
  independently also passed 10/10 raw inventory validation.
- Final Git commands, exact scope output, complete diff inspection, and the
  repeated final untracked UTF-8/newline/trailing-whitespace results are
  recorded below.

### Final exact-scope and state audit

Command: a read-only PowerShell audit using process-local
`git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`
compared the union of tracked and untracked changes with the exact allowlist,
compared the six follow-up objects byte-for-byte after JSON normalization with
the task-start `REVIEW_STATE.yaml`, checked required persistent-state text,
checked all protected paths for changes, and enumerated
`benchmarks/results/`.

Complete output:

```text
ALLOWLIST: PASS (14 exact paths)
REVIEW STATE: PASS (six ordered OPEN follow-ups preserved)
PERSISTENT TEXT: PASS (active READY_FOR_REVIEW; high follow-ups pending; RS-001 NOT STARTED)
PROTECTED SCOPE: PASS
BENCHMARK CLEANUP: PASS (only .gitkeep remains)
```

Commands:

```text
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --check f8271e74509a017d1631dea72aaa652f44d8c3df --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= status --short --branch
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --stat f8271e74509a017d1631dea72aaa652f44d8c3df --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --name-status f8271e74509a017d1631dea72aaa652f44d8c3df --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --no-ext-diff --no-color f8271e74509a017d1631dea72aaa652f44d8c3df --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= status --porcelain=v1 --untracked-files=all
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= ls-files --others --exclude-standard
```

The complete tracked diff was inspected. `diff --check` produced no output and
returned `0`. Final status/name outputs before the final timestamp-only state
refresh were:

```text
## main...origin/main
 M .github/workflows/ci.yml
 M CURRENT_STATUS.md
 M REVIEW_STATE.yaml
 M benchmarks/cases/upstream-small-k.json
 M docs/CI.md
 M research/NEXT_RESEARCH_STEPS.md
 M research/REPRODUCIBILITY.md
 M schemas/benchmark-result.schema.json
 M tests/integration/test_upstream_build.py
 M tools/run_benchmark.py
?? ops/TASK-20260717__enforce_process_outcome_semantics/
?? tests/unit/test_benchmark_outcomes.py

M	.github/workflows/ci.yml
M	CURRENT_STATUS.md
M	REVIEW_STATE.yaml
M	benchmarks/cases/upstream-small-k.json
M	docs/CI.md
M	research/NEXT_RESEARCH_STEPS.md
M	research/REPRODUCIBILITY.md
M	schemas/benchmark-result.schema.json
M	tests/integration/test_upstream_build.py
M	tools/run_benchmark.py

ops/TASK-20260717__enforce_process_outcome_semantics/EVIDENCE.md
ops/TASK-20260717__enforce_process_outcome_semantics/TASK_LOG.md
ops/TASK-20260717__enforce_process_outcome_semantics/TASK_STATUS.md
tests/unit/test_benchmark_outcomes.py
```

The stat at that point was `10 files changed, 908 insertions(+), 93
deletions(-)` for tracked files; ordinary Git diff correctly omitted the four
untracked files. Each untracked file was separately read in full. A strict
UTF-8 decoder plus explicit final-LF and per-line trailing-whitespace checks
returned `PASS` for all four paths. The final post-recording repetition is
reported at handoff because a dossier cannot contain its own final byte hash
without changing that hash.
