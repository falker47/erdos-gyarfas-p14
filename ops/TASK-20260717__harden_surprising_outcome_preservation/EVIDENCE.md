# TASK-20260717__harden_surprising_outcome_preservation — Evidence

All evidence is bounded engineering evidence. It establishes no mathematical
claim, upstream reproduction, counterexample, exhaustive coverage, or
certificate.

## EV-001 — Startup gate and baseline

- ROOT:
  `C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`
- Branch: `main`
- Task-start HEAD: `be179265919566b44d40cb1e472cd3db50811502`
- Accepted review baseline:
  `f8271e74509a017d1631dea72aaa652f44d8c3df`
- `git merge-base --is-ancestor <baseline> HEAD`: exit 0.
- Initial `git status --porcelain=v1 --untracked-files=all`: empty.
- The only Git warning concerned unreadable user-global ignore configuration;
  process-local `safe.directory` resolved ownership without any configuration
  write.
- Cumulative pre-edit diff: 14 paths, 1,921 insertions, 93 deletions; it was
  read completely before modification.

## EV-002 — Freeze-first and bounded inspection

`tools/inspect_upstream_candidate.py` performs the following ordered boundary:

1. exact ordinary `(exited, 0)` returns without an artifact directory;
2. every other outcome exclusively writes stdout and stderr bytes;
3. it closes and hashes those files, then schema-validates and writes the
   deterministic outcome JSON;
4. only exact exit `100` starts the independent inspector child;
5. the child rereads the frozen files, checks size/hash, then decodes/parses and
   invokes independent predicates;
6. the parent enforces a finite timeout with `Popen.communicate(timeout)`, then
   `kill()` and a second `communicate()` to drain and reap;
7. the parent rechecks the pinned outcome record and both raw files, binds the
   final envelope from trusted parent data, schema-validates it, and writes it
   exclusively.

Behavioral unit results after final hardening:

```text
python -m pytest -q tests/unit/test_upstream_candidate_inspection.py
.............................                                            [100%]
29 passed in 5.44s
```

The suite includes actual subprocess tests for pre-inspection file/hash
existence, timeout/reap and stopped heartbeat, timeout/error stream survival,
non-UTF-8 byte identity, incomplete protocol conversion, pinned-record
mutation detection, deterministic names/JSON, and every exit-100 failure
disposition.

## EV-003 — Deliberately red synthetic end-to-end timeout proof

An inline Python proof created a temporary `build/eg-p14-timeout-e2e-*`
directory, supplied a synthetic `(exited, 100)` outcome, launched a child that
verified the frozen raw files and hashes before sleeping, enforced a `0.75`
second timeout, printed evidence, exited deliberately with status 1 because
the ordinary test remained failed, and let `TemporaryDirectory` clean up.

Exact command (PowerShell here-string piped to Python):

```powershell
@'
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
from tools.inspect_upstream_candidate import CapturedProcessOutcome, InvocationIdentity, ordinary_completion_failure
repo = Path.cwd()
cleanup_target = None
with tempfile.TemporaryDirectory(prefix='eg-p14-timeout-e2e-', dir=repo / 'build') as temporary:
    root = Path(temporary)
    cleanup_target = root
    artifacts = root / 'artifacts'
    stem = 'tiny-k4-surprising-outcome'
    outcome_path = artifacts / f'{stem}.json'
    marker = root / 'inspector-verified.txt'
    script = """
import hashlib, json, sys, time
from pathlib import Path
record_path = Path(sys.argv[1]); marker = Path(sys.argv[2])
record = json.loads(record_path.read_text(encoding='utf-8'))
for name in ('stdout', 'stderr'):
    metadata = record[name]
    data = (record_path.parent / metadata['path']).read_bytes()
    assert len(data) == metadata['byte_length']
    assert hashlib.sha256(data).hexdigest() == metadata['sha256']
marker.write_text('raw-files-and-hashes-present-before-inspection', encoding='utf-8')
time.sleep(5)
"""
    inspector_command = [sys.executable, '-c', script, str(outcome_path), str(marker)]
    identity = InvocationIdentity(
        command=('synthetic-upstream', '4'),
        executable_path=(repo / 'tools' / 'inspect_upstream_candidate.py').as_posix(),
        executable_sha256=hashlib.sha256((repo / 'tools' / 'inspect_upstream_candidate.py').read_bytes()).hexdigest(),
        project_commit='b' * 40,
        project_revision='synthetic-e2e',
        upstream_commit='c' * 40,
        limitations=('Synthetic end-to-end preservation proof only.',),
    )
    original = CapturedProcessOutcome('exited', 100, bytes([255]) + b'synthetic-candidate\n', bytes([254]) + b'synthetic-stderr\n')
    failure = ordinary_completion_failure(
        outcome=original,
        k=4,
        identity=identity,
        artifact_directory=artifacts,
        upstream_timeout_seconds=10,
        inspection_timeout_seconds=0.75,
        inspector_command=inspector_command,
    )
    paths = {
        'outcome': outcome_path,
        'stdout': artifacts / f'{stem}.stdout.bin',
        'stderr': artifacts / f'{stem}.stderr.bin',
        'inspection': artifacts / f'{stem}.inspection.json',
    }
    inspection = json.loads(paths['inspection'].read_text(encoding='utf-8'))
    evidence = {
        'synthetic_upstream_outcome': ['exited', 100],
        'failure_returned': failure is not None,
        'failure_first_line': failure.splitlines()[0] if failure else None,
        'inspector_marker': marker.read_text(encoding='utf-8'),
        'inspection_status': inspection['status'],
        'inspection_error_code': inspection['error']['code'],
        'source_outcome_preserved': inspection['source_outcome_preserved'],
        'source_streams_preserved': inspection['source_streams_preserved'],
        'artifacts': {
            name: {
                'byte_length': path.stat().st_size,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for name, path in paths.items()
        },
    }
    print(json.dumps(evidence, ensure_ascii=True, sort_keys=True))
print(json.dumps({'cleanup_confirmed': cleanup_target is not None and not cleanup_target.exists(), 'cleanup_target': str(cleanup_target)}, sort_keys=True))
raise SystemExit(1)
'@ | python -
```

Observed JSON before cleanup:

```json
{"artifacts":{"inspection":{"byte_length":1579,"sha256":"ef663c687d3c52c1912ee34f54db3aca8a1e40d0fbdca0c85e97365de182d646"},"outcome":{"byte_length":1594,"sha256":"9e80706e0782507e167977115d41aaee27864bf89acb0ad649029bff442e91f0"},"stderr":{"byte_length":18,"sha256":"b5d9f8a5a6e2ce0dc11f1b4785cc39630bb6423b402746ba93ad5dec82b2b0a2"},"stdout":{"byte_length":21,"sha256":"37197481a2c4162985b8e53cc07c1a27e5122b843247713dad2e9277b205561b"}},"failure_first_line":"tiny upstream invocation did not complete ordinarily: termination_reason=exited exit_code=100","failure_returned":true,"inspection_error_code":"inspection_timeout","inspection_status":"timeout","inspector_marker":"raw-files-and-hashes-present-before-inspection","source_outcome_preserved":true,"source_streams_preserved":true,"synthetic_upstream_outcome":["exited",100]}
```

Cleanup output:

```json
{"cleanup_confirmed":true,"cleanup_target":"C:\\Users\\Falker\\Desktop\\Code\\circle\\erdos-gyarfas-p14\\build\\eg-p14-timeout-e2e-5c25awu6"}
```

The command status was 1 by design. No synthetic artifact remains.

## EV-004 — Benchmark preservation and exact outcome matching

The benchmark runner writes `.stdout.txt` and `.stderr.txt` and hashes both
closed files immediately after `execute()`, before timestamping, outcome
matching, result construction, or predicate-like postprocessing. A regression
test replaces the matcher with a function that raises only after verifying both
files already exist with exact bytes and both file-hash calls already occurred.
The runner retains its public contract: 0 accepted, 3 attempted but
unaccepted with validated artifacts, 1 configuration/schema/artifact error.

```text
python -m pytest -q tests/unit/test_benchmark_outcomes.py
....................................                                     [100%]
36 passed in 0.29s
```

## EV-005 — CI post-failure preservation

`.github/workflows/ci.yml` now provides:

- compiler-specific repository-relative tiny artifact paths;
- `always()` benchmark-result existence/schema validation after the producer;
- `always()` post-test upstream inventory and final hygiene checks;
- bounded failure-log prefixes plus lengths and SHA-256 for quick diagnosis;
- failure-only `actions/upload-artifact@v4` of complete
  `artifacts/counterexamples/` and `benchmarks/results/` directories;
- names containing matrix compiler, `github.run_id`, and
  `github.run_attempt`;
- `if-no-files-found: warn` for unrelated failure paths;
- no `continue-on-error`, `|| true`, or equivalent success conversion.

Local static inspection establishes workflow intent only. Hosted GitHub
Actions and the artifact service were not observed and are not reported as
passed. `RFU-SUPPLY-001` remains `OPEN`.

## EV-006 — Required validators, build, real tiny cases, and tests

Environment:

```text
Python 3.14.3
cmake 3.26.4
g++ 13.1.0 (MSYS2 Rev6)
Ninja 1.11.1
GNU Make 4.4.1
```

Validators:

```text
python -m json.tool REVIEW_STATE.yaml
exit 0; rejected-head/base/task fields and six OPEN follow-ups parsed

python tools/validate_schemas.py
{"ok":true,"schemas_checked":["schemas/benchmark-result.schema.json","schemas/counterexample.schema.json","schemas/experiment-manifest.schema.json","schemas/search-certificate.schema.json","schemas/search-partition.schema.json","schemas/surprising-process-outcome.schema.json"]}

python tools/verify_upstream_snapshot.py
{"added":[],"changed":[],"expected_file_count":10,"missing":[],"observed_file_count":10,"ok":true,"snapshot_path":"third_party/erdos-gyarfas"}
```

Release build:

```text
cmake -S . -B build/release -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
-- Configuring done
-- Generating done

cmake --build build/release --target eg-upstream-serial
ninja: no work to do.
```

Corrected direct tiny observations with MSYS2 runtime directories in `PATH`:

```powershell
$env:PATH='C:\msys64\ucrt64\bin;C:\msys64\usr\bin;' + $env:PATH
@'
import hashlib, json, subprocess
from pathlib import Path
exe = Path('build/release/bin/eg-upstream-serial.exe').resolve()
for k in (3, 4):
    result = subprocess.run([str(exe), str(k)], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=False)
    print(json.dumps({
        'k': k,
        'termination_reason': 'signal' if result.returncode < 0 else 'exited',
        'exit_code': result.returncode,
        'stdout_byte_length': len(result.stdout),
        'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
        'stderr_byte_length': len(result.stderr),
        'stderr_sha256': hashlib.sha256(result.stderr).hexdigest(),
    }, sort_keys=True))
'@ | python -
```

```json
{"exit_code":0,"k":3,"stderr_byte_length":0,"stderr_sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","stdout_byte_length":29,"stdout_sha256":"a5df640ea9e3541cc20c633885fef26a0c635fa5f4789d1cf859a8ce062ff90c","termination_reason":"exited"}
{"exit_code":0,"k":4,"stderr_byte_length":0,"stderr_sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","stdout_byte_length":29,"stdout_sha256":"9fdd1c76a8320268f7911b31ca784812d816939182cd40c4cc2710d432b06455","termination_reason":"exited"}
```

Test results:

```text
python -m pytest -q tests/integration/test_upstream_build.py
4 passed in 5.73s

python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
124 passed in 10.74s

python -m pytest -q --basetemp build/pytest-root
128 passed in 16.38s
```

The integration and final suites used all four explicit MSYS2 tool overrides.
The final output contained no skip or xfail summary; all 128 tests passed.

## EV-007 — Intermediate failures preserved

- Initial inspector fixture: 1 failed/26 passed due to a literal invalid byte
  in Python `-c` source; corrected to `bytes([255])`.
- Direct tiny run without runtime `PATH`: both k values returned
  `3221225781`, stdout/stderr length 0 and empty SHA-256; corrected environment
  produced the two exit-zero observations in EV-006.
- Required integration run without local basetemp: four setup errors with
  `PermissionError: [WinError 5]` under
  `%TEMP%/pytest-of-Falker`; repository-local basetemp rerun passed 4/4.
- `Get-Date -AsUTC` was unsupported; the portable UTC conversion succeeded.

None of these intermediate failures was hidden or represented as a project
pass before correction.

## EV-008 — Final preservation and diff audit

Protected task-start/current Git blob pairs were identical:

```text
research/CLAIMS_REGISTRY.yaml
c770fc2b51c16d575a05fde361403ffbf9c50f22

research/PRUNING_REGISTRY.md
962075aa9f0c48492162bca322195fed802a1a1f

.github/workflows/heavy-search.yml
89275c467e25c14c486b7f0a66d40930d83b0c56
```

`git diff --quiet HEAD -- third_party/erdos-gyarfas` and the corresponding
protected-file diff both returned 0. The snapshot verifier independently
reported 10 expected/observed files and no additions, changes, or omissions.

The task-local delta from task-start HEAD contains exactly nine modified and
six new paths, all 15 in the task allowlist. The two artifact roots contain
only their pre-existing `.gitkeep`; the synthetic timeout directory was
confirmed removed. No persistent benchmark result, raw surprising stream,
measurement artifact, compiled product, or Python cache is part of the
candidate.

Final cumulative commands and results:

```text
git diff --check f8271e74509a017d1631dea72aaa652f44d8c3df --
exit 0, no output

git status --short --branch
branch main; nine modified tracked paths and six allowed untracked files

git diff --stat f8271e74509a017d1631dea72aaa652f44d8c3df --
14 tracked cumulative paths; 1,869 insertions; 101 deletions

git diff --name-status f8271e74509a017d1631dea72aaa652f44d8c3df --
the rejected cumulative candidate paths only; new corrective files are
separately visible in porcelain until the user creates the manual commit

git status --porcelain=v1 --untracked-files=all
nine M entries and six ?? entries, exactly the current-task allowlist
```

The accepted-base-to-task-start cumulative diff was read completely during the
startup gate. The final task-start tracked diff and all six complete new files
were then read, followed by the exact final cumulative diff command. Together
these cover the full next-review range, including untracked corrective content.
Warnings about the unreadable user-global Git ignore file do not affect the
repository status and caused no configuration change.
