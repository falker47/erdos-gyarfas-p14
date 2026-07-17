# TASK-20260717__establish_review_state — Evidence

## EV-001 — Exact Git baseline and clean startup state

- Question: Does the current checkout match the required repository, branch,
  HEAD, and clean-worktree precondition?
- Method or exact commands:
  - `git rev-parse --show-toplevel`
  - `git branch --show-current`
  - `git rev-parse HEAD`
  - `git status --short --branch`
  - `git log --oneline --decorate -5`
  - `git remote -v`
- Output summary: repository root resolved to the requested checkout; branch was
  `main`; HEAD and `origin/main` were
  `164d6756fd2f6725f2de0bedbe13f1e8c444ba0c`; status was
  `## main...origin/main` with no changes; the only remote was the requested
  GitHub repository.
- Interpretation: the task baseline matched exactly and modification was
  permitted.
- Limitations: the sandbox owner check required a process-local
  `safe.directory` environment override. The first attempt failed before
  producing Git state; no persistent configuration changed.
- Classification: `EMPIRICAL_OBSERVATION`.
- Linked log entry: `2026-07-17T09:12:50Z — Startup and baseline audit`.

## EV-002 — Accepted bootstrap review state

- Question: Is the accepted bootstrap baseline and verdict represented without
  changing its bounded claim classification?
- Method or exact command: inspect the accepted commit, prior dossier,
  `REVIEW_STATE.yaml`, `CURRENT_STATUS.md`, `RESEARCH_LOG.md`, and the
  `BOOTSTRAP-BASELINE` registry entry.
- Output summary: all new state records identify commit
  `164d6756fd2f6725f2de0bedbe13f1e8c444ba0c`, verdict
  `ACCEPT WITH FOLLOW-UP`, and accepted task
  `TASK-20260715__bootstrap_reproducible_baseline`.
- Interpretation: review provenance is synchronized while
  `BOOTSTRAP-BASELINE` remains `VERIFIED_BOUNDED_COMPUTATION` and no
  mathematical target advances.
- Limitations: this governance record does not re-run hosted CI or add
  mathematical evidence.
- Classification: `DECISION` plus existing `VERIFIED_BOUNDED_COMPUTATION` scope.
- Linked log entry: `2026-07-17T09:12:50Z — Governance synchronization drafted`.

## EV-003 — Persistent cumulative-review design and open follow-ups

- Question: Are future reviews anchored to a machine-readable accepted baseline
  with rejected-fix and follow-up semantics preserved?
- Method or exact command: inspect `CHATGPT_REVIEW_PROTOCOL.md`, parse
  `REVIEW_STATE.yaml`, and compare follow-up paths with the actual workflows,
  benchmark runner, integration test, and container definition.
- Output summary: the protocol defines repository-first cumulative review over
  `review_base_commit..HEAD`, unchanged baseline after rejection, advancement
  only to an accepted existing HEAD, exceptional commands, verdict criteria,
  mandatory output, and the next Codex prompt. Six stable `OPEN` follow-ups map
  to the inspected technical paths.
- Interpretation: the next review has a durable baseline and the accepted
  bootstrap limitations remain explicit rather than implicitly resolved.
- Limitations: the current task records but intentionally does not correct any
  technical follow-up.
- Classification: `DECISION`.
- Linked log entry: `2026-07-17T09:12:50Z — Governance synchronization drafted`.

## EV-004 — Required verification and final scope audit

- Question: Do all required checks pass with only authorized documentation and
  governance changes?
- Method or exact commands:
  - `python -m json.tool REVIEW_STATE.yaml`
  - `python tools/validate_schemas.py`
  - `python tools/verify_upstream_snapshot.py`
  - `python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py`
  - `git diff --check`
  - `git status --short --branch`
  - `git diff --stat`
  - `git diff -- AGENTS.md start.md CHATGPT_REVIEW_PROTOCOL.md REVIEW_STATE.yaml CURRENT_STATUS.md RESEARCH_LOG.md DECISION_LOG.md research/NEXT_RESEARCH_STEPS.md research/CLAIMS_REGISTRY.yaml ops/TASK-20260717__establish_review_state`
  - `git status --porcelain=v1 --untracked-files=all` compared with the exact
    12-path allowlist;
  - `git diff --quiet` checks for `.github/workflows/`,
    `third_party/erdos-gyarfas/`, `upstream/`, and the closed bootstrap dossier;
  - targeted diff/search checks for claim statuses, affirmative mathematical
    language, reading order, stale Git state, RS-001 state, SHA consistency,
    follow-up status, and trailing whitespace in new files.
- Output summary:
  - `REVIEW_STATE.yaml` parsed as JSON and retained the exact accepted SHA in
    all three baseline/head fields;
  - all five Draft 2020-12 project schemas passed;
  - upstream verification reported `ok: true`, with 10 expected and 10 observed
    files and no added, changed, or missing path;
  - pytest reported `59 passed in 4.07s`;
  - `git diff --check` exited `0` with no output;
  - the exact scope audit found 12/12 authorized changed paths and no others;
  - workflows, upstream records/snapshot, and the bootstrap dossier were
    unchanged;
  - no claim `status` line changed; all identity, reading-order, RS-001,
    claim-language, and new-file whitespace audits passed;
  - status, stat, the complete tracked diff, and every untracked new file were
    inspected.
- Interpretation: the governance-only change set meets its required local
  verification and remains inside the authorized scope. It is
  `READY_FOR_REVIEW`.
- Limitations: `git diff --stat` and ordinary `git diff` do not include
  untracked files; their content was reviewed through full reads and their exact
  paths through `git status --porcelain=v1 --untracked-files=all`. Git emitted a
  sandbox-only warning about the inaccessible user-global ignore file, and the
  read-only Git commands used a process-local `safe.directory` override; no Git
  configuration changed. Hosted CI, Docker, benchmarks, and searches were not
  run and are outside this task.
- Classification: `VERIFIED_BOUNDED_COMPUTATION` for the stated engineering
  checks only; no mathematical claim follows.
- Linked log entry: `2026-07-17T09:19:19Z — Verification and handoff`.
