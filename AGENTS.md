# AGENTS.md — Erdős–Gyárfás P14 Operating Contract

## 0. Project configuration

- Project name: `erdos-gyarfas-p14`
- Project title: Certified Computational Study of the Erdős–Gyárfás Conjecture for P14-Free Graphs
- Project type: independent computational mathematics research
- Primary target:
  prove by a reproducible and independently verifiable computation that every
  finite simple P14-free graph of minimum degree at least 3 contains a cycle
  whose length is a power of 2.
- Alternative target:
  produce an independently verifiable counterexample.
- Intermediate target:
  determine whether every finite simple P13-free graph of minimum degree at
  least 3 contains C4 or C8.
- Upstream reference:
  `https://github.com/rbsandeep/Erdos-Gyarfas`
- Reference workflow only:
  `https://github.com/falker47/ringmin-squared`
- Default execution mode: STANDARD
- Required mode for mathematical claims, pruning rules, exhaustive searches,
  certification, artifact formats, or heavy experiments: STRICT
- Repository memory is authoritative. Chat history is not authoritative.
- The user performs all commits and pushes manually.

Project-specific rules in this file override generic agent behavior.

## 1. Agent role

Codex is a repository-local executor for one bounded task.

Codex may:

- inspect repository files and Git history;
- implement code and tests;
- run local commands;
- create documentation and machine-readable artifacts;
- perform bounded experiments explicitly included in the task;
- update the current task dossier and canonical state files.

Codex must not:

- decide the long-term research direction beyond the current task;
- silently expand scope;
- turn empirical evidence into a theorem;
- claim exhaustive coverage without the required certificate;
- introduce a mathematical pruning rule without an accepted proof;
- modify the preserved upstream snapshot;
- perform Git writes reserved to the user.

ChatGPT, in a separate project chat, acts as scientific reviewer, architect,
and orchestrator. Codex acts as executor.

## 2. One task per session

One fresh Codex session corresponds to one atomic task.

The first prompt defines:

- objective;
- allowed files;
- required verification;
- acceptance criteria;
- explicit out-of-scope work.

Codex must not start the next task in the same session.

A task should prepare one coherent commit. Corrective work discovered after the
task has reached handoff belongs to a new task unless the current task has not
yet been submitted for review.

## 3. Git policy

Codex must not run:

- `git add`;
- `git commit`;
- `git push`;
- `git merge`;
- `git rebase`;
- `git reset`;
- history rewriting;
- remote creation or modification.

Read-only Git commands are allowed, including:

- `git status`;
- `git diff`;
- `git diff --check`;
- `git log`;
- `git show`;
- `git rev-parse`;
- `git remote -v`;
- `git ls-files`.

The user reviews and commits manually.

Successful modified work ends in `READY_FOR_REVIEW`.

## 4. Required startup protocol

At the start of every task:

1. locate the repository root;
2. read this `AGENTS.md`;
3. read `start.md`;
4. read `CHATGPT_REVIEW_PROTOCOL.md`;
5. read `REVIEW_STATE.yaml`;
6. read `CURRENT_STATUS.md`;
7. read `PROJECT_KNOWLEDGE.md`;
8. read `research/PROBLEM_STATEMENT.md`;
9. read `research/VERIFICATION_PROTOCOL.md`;
10. read `research/CLAIMS_REGISTRY.yaml`;
11. read `research/PRUNING_REGISTRY.md` when search or pruning is relevant;
12. read the active task dossier;
13. inspect relevant prior dossiers and decisions;
14. inspect the actual Git status and current HEAD;
15. require a clean working tree unless the prompt explicitly concerns existing
    uncommitted work;
16. inspect actual source, tests, manifests, and artifacts before reasoning from
    documentation.

If required files are missing during the initial bootstrap task, create them as
part of that task.

## 5. Durable memory

The filesystem is durable project memory.

Use:

- `AGENTS.md` for operating rules;
- `start.md` for project identity and reading order;
- `CHATGPT_REVIEW_PROTOCOL.md` for cumulative scientific-review procedure;
- `REVIEW_STATE.yaml` for the machine-readable accepted review baseline;
- `PROJECT_KNOWLEDGE.md` for stable project-internal facts;
- `CURRENT_STATUS.md` for current state only;
- `RESEARCH_LOG.md` for concise global chronology;
- `DECISION_LOG.md` for decisions;
- `research/KNOWN_RESULTS.md` for external mathematical results;
- `research/CLAIMS_REGISTRY.yaml` for claim status;
- `research/NEGATIVE_RESULTS.md` for failed approaches;
- task dossiers for task-local chronology and evidence;
- manifests for experiment and search-run truth.

Do not duplicate a theorem or computational result across multiple global files.
Choose one canonical source and link to it.

Do not place command transcripts in global files.

## 6. Claim classes

Every material claim must use one of these classes:

- DEFINITION
- EXTERNAL_THEOREM
- EXTERNAL_COMPUTATIONAL_RESULT
- PROJECT_PROOF
- COMPUTER_CERTIFIED_RESULT
- VERIFIED_BOUNDED_COMPUTATION
- REPRODUCED_UPSTREAM_RESULT
- EMPIRICAL_OBSERVATION
- ENGINEERING_ASSUMPTION
- HEURISTIC
- CONJECTURE
- IDEA
- NEGATIVE_RESULT
- OPEN_QUESTION
- DISPROVED
- RETRACTED
- SUPERSEDED
- DECISION

A claim is not upgraded merely because tests pass.

`COMPUTER_CERTIFIED_RESULT` requires satisfaction of
`research/VERIFICATION_PROTOCOL.md`.

`REPRODUCED_UPSTREAM_RESULT` means only that a stated upstream execution was
reproduced under recorded conditions. It does not automatically certify the
mathematical conclusion.

## 7. Mathematical scope

All graphs are finite, simple, and undirected unless the canonical problem
statement says otherwise.

A cycle means a simple cycle and need not be induced.

A power-of-two cycle has length `2^j` for an integer `j >= 2`, hence possible
lengths are 4, 8, 16, and so on.

`P_t` means the path on `t` vertices.

`P_t`-free means no induced subgraph is isomorphic to `P_t`.

Definitions in `research/PROBLEM_STATEMENT.md` are authoritative.

## 8. Upstream policy

The preserved upstream snapshot is read-only.

For every imported upstream component record:

- repository URL;
- branch or ref;
- commit SHA;
- tree SHA when available;
- acquisition date;
- file hashes or archive hash;
- license;
- local path;
- any missing or unresolved refs.

Do not silently fix upstream code inside the snapshot.

An upstream bug must be handled by:

1. preserving the original behavior;
2. adding a minimal failing regression outside the snapshot;
3. recording the issue;
4. implementing a clearly separated patch or replacement;
5. comparing patched and original behavior on bounded cases.

No upstream result is treated as internally verified until reproduced and
reviewed under this repository's protocol.

## 9. Search completeness

The absence of a counterexample has mathematical meaning only when all of the
following are available:

- exact search domain;
- root states;
- proof of the generation invariant;
- complete list of pruning rules;
- proof status of each pruning rule;
- exact partitioning scheme;
- evidence that partitions are disjoint;
- evidence that partitions cover the full domain;
- deterministic program version;
- compiler and runtime environment;
- command-line arguments;
- completion status of every partition;
- counts or digests sufficient to detect omitted work;
- hashes of logs, manifests, checkpoints, and certificates;
- independent verification of the certificate.

A completed process with exit code zero is not by itself a certificate of
exhaustiveness.

## 10. Pruning rules

Every pruning rule must have a stable ID in
`research/PRUNING_REGISTRY.md`.

A pruning rule has exactly one operational status:

- CERTIFYING
- HEURISTIC_ONLY
- DISABLED
- RETRACTED

A rule may be CERTIFYING only when its correctness is proved from the search
invariant and the proof has been reviewed.

HEURISTIC_ONLY rules must never be enabled in a run used for a certified
negative result.

Tests are required but do not replace the proof of a pruning rule.

## 11. Generator and verifier separation

The search generator and the independent verifier must not share critical
predicate implementations unless the shared component is explicitly included
in the trust base.

At minimum, independently implement or cross-check:

- graph parsing;
- simplicity;
- degree calculation;
- induced-path detection;
- power-of-two-cycle detection;
- counterexample validation;
- manifest hashes;
- partition coverage;
- certificate replay.

Test-only brute-force oracles should favor simplicity over performance.

## 12. Experiments

Every material experiment requires a machine-readable manifest containing:

- schema version;
- task ID;
- project commit or dirty-tree hash;
- upstream commit;
- target statement;
- search mode;
- parameters;
- enabled pruning rule IDs;
- seeds;
- partition ID;
- start and end timestamps;
- environment;
- compiler;
- dependencies;
- exit status;
- counts;
- artifact paths;
- SHA-256 hashes;
- result classification;
- known limitations.

Do not commit invented benchmark values or placeholder hashes.

Failed and interrupted experiments are evidence and must be recorded.

## 13. Determinism

Prefer deterministic:

- vertex ordering;
- neighbor ordering;
- partition ordering;
- output serialization;
- JSON formatting;
- random seeds;
- artifact names.

Where upstream behavior is nondeterministic, normalize output or record the
source of nondeterminism.

Performance measurements may vary. Mathematical outputs must not.

## 14. Tests and CI

Fast CI should include:

- clean build;
- compiler warnings;
- unit tests;
- independent predicate tests;
- differential tests on small graphs;
- manifest and schema validation;
- upstream smoke tests for very small `k`;
- counterexample verifier tests;
- deterministic-output checks;
- formatting or static checks;
- `git diff --check`.

Heavy searches must not run in ordinary pull-request CI.

Heavy workflows must be manually dispatched and must emit manifests and
artifacts even when interrupted.

## 15. Task dossiers

Each nontrivial task uses:

`ops/TASK-YYYYMMDD__short_description/`

with:

- `TASK_STATUS.md`;
- `TASK_LOG.md`;
- `EVIDENCE.md`.

`TASK_STATUS.md` contains current truth for the task.

`TASK_LOG.md` is append-only.

`EVIDENCE.md` records independently understandable checks.

A closed dossier is not reused for a later correction. A correction receives a
new task and links to the superseded dossier.

## 16. Completion protocol

Before handing work to the user:

1. run all checks required by the task;
2. record exact commands and results;
3. update the task dossier;
4. update `PROJECT_KNOWLEDGE.md` only with stable verified knowledge;
5. update `CURRENT_STATUS.md`;
6. update `research/CLAIMS_REGISTRY.yaml` for every changed claim;
7. update logs or decisions only when required;
8. inspect `git status`;
9. inspect the complete diff;
10. run `git diff --check`;
11. confirm no out-of-scope files changed;
12. set task status to `READY_FOR_REVIEW`;
13. stop.

The final report must include:

- task objective;
- baseline HEAD;
- files changed;
- commands run;
- test results;
- claim classifications;
- mathematical limitations;
- engineering risks;
- unresolved issues;
- suggested manual commit message;
- one proposed next atomic task.

Do not begin that next task.
