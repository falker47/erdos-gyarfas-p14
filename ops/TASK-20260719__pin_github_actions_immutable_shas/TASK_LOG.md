# TASK-20260719__pin_github_actions_immutable_shas - Log

Append-only task chronology. Times are UTC when shown.

## 2026-07-19T01:20:55Z - Startup gate and mandatory inspection

- Plain Git reported dubious ownership. No Git configuration changed. Every
  successful project Git read used process-local
  `-c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`.
- The gate resolved the expected root and origin, branch `main`, exact HEAD and
  review base `dde4e6cbd06be8ebc8192097930f40b06cf2f9f6`, successful ancestry,
  an empty worktree, and an empty index.
- Read all mandatory governance, research, prior-dossier, workflow, CI,
  reproducibility, test-configuration, relevant workflow/governance test, and
  Git-history inputs before modification. Exactly two workflow YAML files and
  eleven active external `uses:` occurrences were present.
- Recorded task-start hashes for project Git config and index, attributes,
  workflows, claims, pruning, project knowledge, and upstream provenance.

## 2026-07-19T01:20:55Z - Official action release resolution

- Queried official `actions/checkout`, `actions/setup-python`, and
  `actions/upload-artifact` Git refs and GitHub release/repository/content
  endpoints. No third-party source supplied an identity.
- Selected the newest exact non-draft, non-prerelease release within each
  already-used major: checkout `v4.3.1`, setup-python `v5.6.0`, and
  upload-artifact `v4.6.2`.
- For each action, the exact release tag and floating major tag resolved to the
  same lightweight-tag commit; the GitHub Git object type was `commit`, the
  repository owner was the `actions` organization, and `action.yml` existed at
  the exact commit.
- An initial sandboxed remote query failed connectivity and was rerun through
  the approved network boundary. A later optional shallow-fetch attempt in a
  temporary bare repository encountered DNS failure; it is not used as
  evidence because official ref and GitHub object/content checks completed.

## 2026-07-19T01:20:55Z - Persistent-state transition

- `REVIEW_STATE.yaml` now records the already accepted baseline/head
  `dde4e6cbd06be8ebc8192097930f40b06cf2f9f6`, verdict
  `ACCEPT WITH FOLLOW-UP`, accepted multi-worktree task, and this active task.
- Removed resolved `RFU-CI-004`. `RFU-SUPPLY-001` remains first and `OPEN`
  pending review of this candidate; `RFU-ENV-001` remains second, unchanged,
  and `OPEN`.

## 2026-07-19T01:56:23Z - Implementation and initial focused verification

- Replaced all eleven floating external Action occurrences with one full
  lowercase commit SHA per official Action and added the exact verified release
  tag as a non-operative end-of-line comment. No major version changed and no
  external Action was added.
- Added `tools/check_github_action_pins.py`, a standard-library-only,
  deterministic, read-only scanner for every workflow `.yml` and `.yaml` path.
  It buffers output until the full scan succeeds, accepts only canonical local,
  GitHub commit, or Docker digest forms, and otherwise fails with empty stdout.
- Added synthetic positive, negative, deterministic-output, real-workflow,
  consistency, comment, and fast-CI tests. The first focused implementation
  passed 33 tests in 0.46 seconds.
- Added one fast-CI step invoking the exact repository-local command. The step
  runs after checkout and Python setup and is not represented as pre-execution
  authentication of those Actions.

## 2026-07-19T01:56:23Z - Independent parser audits and corrections

- A first read-only audit found that escaped/tagged/explicit YAML key forms
  could materialize an active mutable `uses` key without the literal form
  recognized by the restricted parser. The validator now fails closed on
  noncanonical mapping-key mechanisms, including flow explicit forms.
- A second audit found that tracking only a block-scalar header's leading
  indentation could hide a less-indented sibling `uses` key. The validator now
  derives the mapping-key indentation and either infers actual content
  indentation or applies an explicit `|2`, `|4`, `>2-`, or `>4-` indicator.
- Workflow discovery now sorts paths before any validation error is selected,
  and UTF-8 BOMs are rejected so the first key cannot be hidden.
- Added regression cases for every discovered bypass and deterministic
  first-failure ordering. Final focused verification passed 44 tests in 0.39
  seconds. An independent 17-case adversarial YAML corpus found no remaining
  HIGH or MEDIUM bypass.

## 2026-07-19T01:56:23Z - Broad and complete verification

- The first bounded suite, before the parser corrections, passed 276 tests in
  76.09 seconds. After every correction, the final required bounded suite
  passed 287 tests in 75.77 seconds.
- The complete final suite used explicit documented MSYS2 CMake, GCC, Ninja,
  and Make executables plus matching UCRT64/Unix runtime paths. It passed 291
  tests in 107.19 seconds. No final run reported a failure, skip, or xfail.
- Strict state JSON, canonical active-task resolution, the real pin validator,
  six-schema validation, upstream snapshot verification, and committed-range
  whitespace validation each exited zero on terminal implementation state.

## 2026-07-19T01:56:23Z - Documentation and cleanup

- Updated CI and reproducibility documentation with exact Action identities,
  resolution method, validator rules, local/Docker handling, non-operative
  comments, and the distinction between ref immutability and `RFU-ENV-001`.
- Updated current status and research priority without changing mathematical
  claims: `RS-001` remains `NOT STARTED` and `RFU-SUPPLY-001` remains `OPEN`
  pending review.
- The failed optional shallow-fetch audit repositories were created only below
  `build/action-pin-verification`; their resolved parent was verified beneath
  `build/`, removed, and confirmed absent. The complete-suite basetemp was
  similarly verified below `build/pytest-root`, removed, and confirmed absent.

## 2026-07-19T02:00:57Z - Closing audit and result classification

- Exact set comparison found the seven modified tracked paths and five
  untracked implementation/test/dossier paths equal to the twelve-path
  allowlist, with no missing or extra path. The tracked diff stat is 215
  insertions and 111 deletions before the five new files are counted.
- `git diff --check` exited zero and the staged diff is empty. A separate
  all-twelve-file byte audit reports strict UTF-8, final LF, zero NUL bytes,
  and zero trailing-whitespace lines for every tracked and untracked path.
- All eleven real `uses:` lines are full lowercase SHAs with their exact
  release comments. The final validator still reports two workflows and
  eleven normalized external occurrences.
- Claims, pruning, project knowledge, upstream, attributes, project Git config,
  and index retain their task-start hashes. Both task-created temporary
  directories remain absent.
- The task creates only bounded supply-chain engineering evidence. It does not
  create or upgrade any mathematical claim, proof, reproduction, exhaustive
  result, certificate, counterexample, or pruning rule. Final status is
  `READY_FOR_REVIEW`; no next task is started.
