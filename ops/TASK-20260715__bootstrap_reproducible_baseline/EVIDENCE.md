# TASK-20260715__bootstrap_reproducible_baseline — Evidence

## EV-001 — Supplied repository state

- Question: What is the baseline Git/worktree state and does unrelated work
  block the task?
- Method or exact commands:
  - `git rev-parse --show-toplevel`
  - `git status --short --branch`
  - `git rev-parse HEAD`
  - `git branch --show-current`
  - `git log -5 --oneline --decorate`
  - `git remote -v`
  - `rg --files -g '!*.pyc' | Sort-Object`
  - `Get-ChildItem -Force`
- Output summary: Git reported “not a git repository” for every Git query.
  The directory contained only the supplied project design/memory skeleton.
- Interpretation: there is no baseline HEAD, branch, remote, or Git worktree to
  dirty. Existing files are directly related to this explicitly requested
  bootstrap, so the unrelated-change stop condition does not apply.
- Limitations: without `.git`, later `git diff`, tracked-file, and commit-based
  integrity checks are unavailable.
- Classification: `ENGINEERING_ASSUMPTION` supported by filesystem inspection.
- Linked log entry: `2026-07-17T07:27:00Z — Startup audit`.

## EV-002 — Exact upstream branch refs

- Question: Which commits do the six required upstream refs resolve to?
- Method or exact command:
  `git ls-remote --heads https://github.com/rbsandeep/Erdos-Gyarfas.git main cilk tests logs special-graphs 4-8-cycles`
- Output summary:
  - `main`: `27d9cb22705905fac32314c5e95addf6e11ce283`
  - `cilk`: `baf9004e54f3af82e4a79c4aaf04710fd1c92592`
  - `tests`: `cc608b9311c79d15c8471d3f208f46f4a48951ee`
  - `logs`: `13a2ebe79d67b030fef0b30ea33563b9ed9f028e`
  - `special-graphs`: `f7bea75afecb07dab552047ece2d551722f32272`
  - `4-8-cycles`: `fa72f40dbbc8fdb1f5bc8ba78376bd89202619ed`
- Interpretation: every requested ref was accessible and resolved; `main`
  agrees with the design-time observation. None is absent or unresolved.
- Limitations: ref identity alone does not validate source correctness or
  snapshot integrity; those require separate evidence.
- Classification: `EMPIRICAL_OBSERVATION`.
- Linked log entry: `2026-07-17T07:30:00Z — Upstream ref resolution`.

## EV-003 — Initial toolchain availability

- Question: Can required native builds run from the initial Windows `PATH`?
- Method or exact commands:
  - `python --version`
  - `cmake --version`
  - `g++ --version`
  - `clang++ --version`
  - `make --version`
  - `where.exe cmake cl g++ clang++ make mingw32-make ninja docker wsl`
  - `wsl.exe --status`
  - recursive read-only checks under `C:\msys64` and standard Visual Studio
    paths
- Output summary: Python 3.14.3 is present. The compiler/build tools are not on
  `PATH`; WSL has no distro. A bare MSYS2 installation exists.
- Interpretation: native build verification needs a discovered or approved
  toolchain before it can pass.
- Limitations: this is an environment observation, not yet a task blocker;
  toolchain installation and container alternatives remain possible.
- Classification: `EMPIRICAL_OBSERVATION`.
- Linked log entry: `2026-07-17T07:35:33Z — Local environment audit`.

## EV-004 — Upstream snapshot integrity

- Question: Is `third_party/erdos-gyarfas/` an exact raw snapshot of resolved
  upstream `main`, with reproducible identity and preserved license?
- Method or exact commands:
  - `git clone --bare https://github.com/rbsandeep/Erdos-Gyarfas.git C:\tmp\eg-upstream-bootstrap-27d9cb2.git`
  - `git -C C:\tmp\eg-upstream-bootstrap-27d9cb2.git rev-parse 27d9cb22705905fac32314c5e95addf6e11ce283^{tree}`
  - `git -c core.autocrlf=false -C C:\tmp\eg-upstream-bootstrap-27d9cb2.git archive --format=tar --output=C:\tmp\eg-upstream-bootstrap-27d9cb2-raw.tar 27d9cb22705905fac32314c5e95addf6e11ce283`
  - `tar -xf C:\tmp\eg-upstream-bootstrap-27d9cb2-raw.tar -C third_party\erdos-gyarfas`
  - `python tools/hash_artifacts.py tree third_party/erdos-gyarfas`
  - selected-tree `git ls-tree`/`git cat-file blob` byte comparison for each
    imported path
  - `python tools/verify_upstream_snapshot.py`
- Output summary: commit `27d9cb22705905fac32314c5e95addf6e11ce283`,
  tree `35707222c62e2bc14b90f385f593a66799405eba`, ten expected files,
  no missing/extra/mismatched blob, inventory SHA-256
  `6fcd2f09dae6618b968a3981748c5cc16f8321478cee6f6b831071463ec7756c`,
  and license SHA-256
  `6c87527a065e12d3be189d606cf243b10dc97445a0b3e436ea1605062968be74`.
- Interpretation: the final metadata-free snapshot matches the selected raw
  Git tree and contains the upstream MIT license.
- Limitations: provenance establishes identity, not algorithm correctness. An
  initial `core.autocrlf=true` archive was rejected; its hash and reason remain
  in `UPSTREAM_PROVENANCE.json`.
- Classification: `EMPIRICAL_OBSERVATION`.
- Linked log entry: `2026-07-17T07:34:12Z — Upstream acquisition`.

## EV-005 — Original Make, CMake wrapper, and tiny upstream processes

- Question: Do both documented build routes work without modifying the
  snapshot, and do tiny inputs terminate under a bound?
- Method or exact commands:
  - `cmake --preset debug`
  - `cmake --build --preset debug`
  - `cmake --preset release`
  - `cmake --build --preset release`
  - `python -m pytest tests/integration/test_upstream_build.py -q --basetemp build/pytest-upstream-raw-final`
  - the integration test runs `make clean`, `make`, and CMake in temporary
    directories and invokes `k=3` and `k=4` with ten-second timeouts
- Output summary: original Make build passed in a copied tree; Debug and
  Release CMake targets built; both tiny processes returned `0` with nonempty
  elapsed-time stdout; four integration tests passed; snapshot re-audit passed;
  GCC emitted no warnings.
- Interpretation: both build interfaces and the documented tiny process paths
  function in the tested environment.
- Limitations: exit `0` is upstream ordinary completion, not mathematical
  certificate semantics. No `k=13`/`k=14` run occurred. Docker was unavailable
  and the Docker image was not built. Original Make is Unix-tool-specific;
  MinGW executables require their runtime DLL directory.
- Classification: `VERIFIED_BOUNDED_COMPUTATION` (engineering only).
- Linked log entry: `2026-07-17T07:48:00Z — Build setup and bounded upstream checks`.

## EV-006 — Python verifier and bounded differential tests

- Question: Do the independent graph predicates and CLI satisfy their stated
  small-input contracts and agree with deliberately simple oracles on the
  exact bounded domain?
- Method or exact commands:
  - `python -m pytest tests/unit -q`
  - `python -m pytest tests/differential -q`
  - `python -m pytest tests/integration/test_verifier_cli.py -q`
  - `python -m pytest -q --basetemp build/pytest-root`
  - repeated `python -m egverify graph tests/fixtures/disconnected.json`
- Output summary: 48 unit, 1 differential, and 10 verifier CLI tests passed;
  the full suite including four upstream integration checks passed 63 tests.
  The differential domain contained exactly 1,100 graphs with order counts
  `1, 1, 2, 8, 64, 1024`. Repeated CLI graph output was byte-identical.
- Interpretation: production degree/path/cycle predicates agree with test-local
  edge-list/permutation oracles on all labelled simple graphs of orders 0–5;
  parser, target reports, hashes, and exit codes behave as tested.
- Limitations: predicates are deliberately exponential; bounded agreement is
  not a general proof. No fixture satisfies a counterexample predicate. The
  verifier does not establish generator/search completeness. An earlier
  sandboxed full-suite attempt could not access a pre-existing Windows pytest
  temp directory; the repository-local-base rerun is the accepted result.
- Classification: `VERIFIED_BOUNDED_COMPUTATION`.
- Linked log entry: `2026-07-17T07:57:00Z — Independent verifier implementation`.

## EV-007 — Schemas and manifest semantic checks

- Question: Are the five artifact schemas well formed, does the unexecuted
  template validate without invented values, and are artifact hashes
  independently checked?
- Method or exact commands:
  - `python tools/validate_schemas.py`
  - `python tools/validate_schemas.py --schema experiment-manifest --instance _TEMPLATES/EXPERIMENT_MANIFEST_TEMPLATE.json`
  - `python tools/verify_manifest.py tests/fixtures/manifest-valid-hash.json`
  - `python tools/verify_manifest.py tests/fixtures/manifest-invalid-hash.json`
- Output summary: all five Draft 2020-12 schemas and the template passed. The
  valid fixture verified one artifact; the deliberately wrong digest returned
  exit `1` with `artifact SHA-256 mismatch`.
- Interpretation: schema shape and implemented artifact-set/hash/timestamp/mode
  semantics work on positive and negative fixtures.
- Limitations: schemas do not prove graph semantics, pruning, partition
  coverage, certificate correctness, or search completeness. The certificate
  schema is constrained to provisional non-certifying use.
- Classification: `VERIFIED_BOUNDED_COMPUTATION`.
- Linked log entry: `2026-07-17T08:02:00Z — Schemas, benchmark tooling, and workflows`.

## EV-008 — Benchmark runner and result schema

- Question: Does the tiny case runner capture required metadata and validate
  an actually executed result without committing fabricated measurements?
- Method or exact commands:
  - `python tools/run_benchmark.py benchmarks/cases/upstream-small-k.json --output benchmarks/results/bootstrap-harness-check.json`
  - `python tools/validate_schemas.py --schema benchmark-result --instance benchmarks/results/bootstrap-harness-check.json`
- Output summary: the runner invoked `k=3`, returned runner success with child
  exit `0`, captured nonempty stdout, hashes, compiler/flags, Windows/AMD64,
  thread setting, timestamps, and unavailable CPU/memory fields as `null`; the
  result validated. The JSON and two stream files were then removed and
  `benchmarks/results/` contains only `.gitkeep`.
- Interpretation: the runner and schema handle one actual tiny engineering
  execution and Windows runtime-path capture.
- Limitations: the measurement was ephemeral, is not accepted benchmark data,
  and carries no mathematical meaning. CPU time and peak memory were
  unavailable on this platform.
- Classification: `EMPIRICAL_OBSERVATION`.
- Linked log entry: `2026-07-17T08:10:00Z — Root verification pass`.

## EV-009 — CI and safe heavy-workflow scaffold

- Question: Are the workflow files syntactically plausible, bounded, and
  unable to launch or claim an uncertified P13/P14 result?
- Method or exact commands:
  - Python `yaml.BaseLoader` parse of both workflow files
  - Python JSON parse of schemas, presets, templates, benchmark case, and
    upstream records
  - local `tools/make_manifest.py` and `tools/verify_manifest.py` checks for
    not-run and refused scaffold configurations
  - manual source review of every workflow trigger, guard, command, and upload
- Output summary: both YAML files parsed; ten JSON documents parsed; fast CI is
  push/PR/manual with Python 3.11/3.12 and GCC/Clang bounded jobs. Heavy search
  is manual-only, records original inputs, refuses non-scaffold targets/modes
  and `k >= 13`, launches no search executable, emits a non-certifying manifest
  and log, and uploads them with `if: always()`.
- Interpretation: the checked scaffold cannot accidentally run a P13/P14
  search or emit `COMPUTER_CERTIFIED_RESULT` through its exposed path.
- Limitations: GitHub Actions was not executed locally and no actionlint binary
  was available; this is syntax plus manual semantic review. Major action tags
  are not immutable commit pins.
- Classification: `ENGINEERING_ASSUMPTION` supported by static inspection.
- Linked log entry: `2026-07-17T08:02:00Z — Schemas, benchmark tooling, and workflows`.

## EV-010 — Final file-set and claim-boundary audit

- Question: Is the handoff tree complete, clean of generated products, still
  byte-exact upstream, and conservative in its scientific claims?
- Method or exact commands:
  - `python tools/verify_upstream_snapshot.py`
  - `python tools/validate_schemas.py`
  - required-path comparison against the task structure
  - `rg --files -uu -g '!.agents/**' -g '!.git/**'`
  - `rg -n --hidden -g '!.agents/**' -g '!.git/**' -g '!third_party/**' -g '!upstream/UPSTREAM_PROVENANCE.json' -g '!upstream/README.md' -g '!ops/**' '[A-Za-z]:\\(?:Users|tmp|msys64|Program Files|Windows)' .`
  - targeted case-insensitive searches for affirmative P14 proof,
    counterexample, exhaustive-coverage, and certified-result language
  - recursive checks for `build`, `out`, pytest/bytecode caches, native object
    files, executables, and retained benchmark/run artifacts
  - `git status --short --branch`
  - `git diff --check`
  - per-file `git diff --no-index --check -- NUL <path>` for all 103
    non-vendored files; the byte-preserved upstream subtree is excluded from
    this textual audit and marked `-diff` by `.gitattributes`
- Output summary: all 54 required paths exist; the 113-file handoff inventory,
  all five schemas, and the 10/10 snapshot inventory pass; no generated product
  or retained measurement is present; artifact leaves contain only `.gitkeep`;
  no runtime/build setting
  embeds a local absolute path; project claim language remains negative or
  properly classified. Project-authored whitespace passes. The upstream raw
  files retain their original whitespace and exact hashes. Normal Git commands
  report “not a git repository”; the no-index file audit is the available
  bootstrap substitute.
- Interpretation: the file-level bootstrap is internally consistent and ready
  for manual review. The user must establish Git metadata before a normal
  staged diff, `git diff --check`, and commit can exist.
- Limitations: Docker and GitHub Actions were not run; static workflow review is
  not a hosted execution. The unexplained empty `.git` directory has no files
  and no attributable task command. File hygiene and schema conformance do not
  establish any mathematical proposition or search completeness.
- Classification: `VERIFIED_BOUNDED_COMPUTATION` for engineering checks only.
- Linked log entry: `2026-07-17T08:24:54Z — Final hygiene and handoff`.
