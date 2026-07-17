# ChatGPT Cumulative Review Protocol

## 1. Purpose and authority

This protocol governs repository reviews performed by ChatGPT for
`falker47/erdos-gyarfas-p14`. Repository state is the source of truth. Chat
history can help locate context but cannot replace committed files, Git objects,
task dossiers, manifests, artifacts, or recorded commands.

This document supplements `AGENTS.md` and cannot weaken it or
`research/VERIFICATION_PROTOCOL.md`. When rules conflict, the stricter
repository rule applies.

## 2. Canonical review input

Before reviewing, read in this order:

1. `AGENTS.md`;
2. `start.md`;
3. `CHATGPT_REVIEW_PROTOCOL.md`;
4. `REVIEW_STATE.yaml`;
5. `CURRENT_STATUS.md`;
6. `PROJECT_KNOWLEDGE.md`;
7. `research/PROBLEM_STATEMENT.md`;
8. `research/KNOWN_RESULTS.md`;
9. `research/VERIFICATION_PROTOCOL.md`;
10. `research/CLAIMS_REGISTRY.yaml`;
11. `research/PRUNING_REGISTRY.md` when search or pruning is relevant;
12. the candidate task dossier and relevant earlier dossiers and decisions;
13. the actual changed source, tests, workflows, manifests, and artifacts.

`ROOT` means the top-level directory of the reviewed checkout, exactly as
resolved by `git rev-parse --show-toplevel`. Repository paths in review output
are relative to `ROOT`. A similarly named directory, archive, pasted diff, or
subdirectory is not `ROOT`.

## 3. Quick command and revision resolution

The ordinary user command is:

```text
Nuovo commit
```

For that command, ChatGPT must:

1. identify the repository declared by `REVIEW_STATE.yaml`;
2. resolve the stored `branch` and its visible HEAD;
3. read `review_base_commit` from `REVIEW_STATE.yaml`;
4. verify that both commits exist and record their full SHAs;
5. verify whether the baseline is an ancestor of HEAD;
6. inspect the cumulative diff `review_base_commit..HEAD`;
7. inspect every changed file in full where meaning cannot be established from
   the diff alone;
8. run or evaluate the task-required verification at HEAD;
9. issue one verdict under section 9.

The branch, HEAD, and baseline must never be inferred from a chat label alone.
If Git state and canonical files disagree, the discrepancy is a review finding.
If the baseline is not an ancestor of HEAD, ordinary review stops with
`REJECT` unless the user explicitly requests an exceptional range review.

The cumulative range is intentional. If a candidate commit was rejected and a
later commit attempts a fix, `review_base_commit` remains unchanged. The next
review therefore covers the rejected commit, every fix, and all intervening
changes together. A fix commit is never reviewed as if the rejected content
had already been accepted.

## 4. Exceptional commands

- `Nuovo commit <SHA>`: use the explicit full or uniquely resolvable SHA as
  HEAD, retain the stored baseline, record branch reachability, and review the
  cumulative baseline-to-SHA diff.
- `Nuovo commit su <branch>`: resolve the named branch HEAD, retain the stored
  baseline, record the branch and ancestry result, and review the cumulative
  diff.
- `Rianalizza <base>..<head>`: use exactly the two explicit endpoints and
  explain any difference from `REVIEW_STATE.yaml`. This is an exceptional
  range review; it changes the accepted baseline only if the user explicitly
  submits that range for a normal verdict and the acceptance rule is satisfied.
- `Solo audit`: inspect and report the requested state or range without an
  acceptance verdict and without changing or proposing a baseline transition.

An ambiguous SHA, missing object, unavailable branch, or inaccessible
repository blocks a definitive review. ChatGPT must report the exact missing
input rather than substituting another revision.

## 5. Required inspection

A commit message, task summary, patch excerpt, green check, or prior chat report
is not sufficient. ChatGPT must inspect:

- `git diff --stat` and the complete effective diff for the review range;
- the changed-file list, including renames, deletions, modes, and binary files;
- each changed implementation and its relevant callers or consumers;
- tests and fixtures relevant to the changed behavior;
- workflows, schemas, manifests, hashes, and dossier evidence affected by the
  change;
- Git status and any evidence that generated or uncommitted files influenced
  the reported result;
- claim-registry and pruning-registry consequences.

Review commands and their results must be reproducible. A skipped check needs a
specific reason and a stated consequence for the verdict.

## 6. Evidence levels and surprising results

The review must keep these categories distinct:

- a **test** checks stated behavior on its exact test domain;
- a **benchmark** measures an implementation in a recorded environment;
- a **reproduction** repeats an upstream result with pinned provenance;
- a **certification** satisfies the exhaustive-computation and independent
  verification requirements of `research/VERIFICATION_PROTOCOL.md`;
- a **proof** supplies a mathematically valid argument, possibly using an
  accepted certificate when explicitly stated.

Passing tests do not establish performance, reproduction, certification, or a
theorem. A benchmark does not establish correctness. Re-running the same
upstream implementation does not supply independent certification.

Every surprising result—including an unexpected exit code, counterexample,
large count change, speedup, slowdown, warning, timeout, hash change, verifier
disagreement, or empty output—must be treated as unresolved until independently
explained. Preserve the relevant output and environment. Do not normalize the
surprise away, silently rerun until it disappears, or upgrade a claim from it.

## 7. Provenance and independent verification checks

For every material run, inspect the applicable manifest and confirm, rather
than merely assume:

- schema and semantic validation;
- exact project and upstream commits;
- dirty-tree state;
- commands, parameters, search mode, seeds, partitions, and pruning IDs;
- timestamps, exit status, completion status, and termination reason;
- compiler, dependencies, operating system, architecture, resource limits,
  and other outcome-relevant environment fields;
- artifact paths and SHA-256 hashes;
- partition coverage and disjointness when claimed;
- verifier identity, result, and trust boundary.

The generator and verifier must not share critical predicates unless that
sharing is explicitly admitted and reviewed as part of the trust base. A
manifest with missing, invented, stale, or contradictory provenance blocks any
claim that depends on it.

## 8. Pruning review

Each pruning rule must have a stable ID and exactly one operational status:

- `CERTIFYING`;
- `HEURISTIC_ONLY`;
- `DISABLED`;
- `RETRACTED`.

Only reviewed rules with an accepted correctness proof may be `CERTIFYING`.
`HEURISTIC_ONLY` rules cannot appear in a certifying run. `DISABLED` and
`RETRACTED` rules cannot be treated as active support for coverage. Tests and
performance gains never substitute for a pruning proof. Any run/registry/source
mismatch is a blocking review finding for an exhaustive or certified claim.

## 9. Verdict criteria

Exactly one verdict is issued for a normal review.

### ACCEPT

Use `ACCEPT` only when all of the following hold:

- the requested scope and acceptance criteria are fully satisfied;
- no correctness, safety, provenance, reproducibility, claim-boundary, or
  scope violation remains;
- every required check passes in the required environment, or an explicitly
  allowed equivalent is justified by the task;
- documentation, code, tests, manifests, hashes, dossiers, and canonical state
  agree;
- no unresolved issue requires follow-up from this candidate.

### ACCEPT WITH FOLLOW-UP

Use `ACCEPT WITH FOLLOW-UP` only when all `ACCEPT` conditions hold except the
last one, and every residual issue is demonstrably non-blocking for the exact
accepted scope. Each residual issue must receive a stable ID, severity,
affected paths, status `OPEN`, and a concrete description in persistent state.
No mathematical or certification obligation can be downgraded to follow-up if
the accepted claim depends on it.

### REJECT

Use `REJECT` when any of the following applies:

- a required test or validation fails;
- an acceptance criterion is unmet;
- the diff contains unauthorized or unexplained scope;
- a material implementation, manifest, artifact, hash, environment, or dossier
  is missing or contradictory;
- a claim exceeds its evidence level;
- a pruning, coverage, independence, or certificate obligation required by the
  claim is unproved or unverified;
- a high-severity correctness, safety, or provenance issue remains within the
  candidate's accepted scope or supporting evidence;
- the effective revisions or ancestry cannot be established.

A rejection must identify the blocking findings and keep the prior accepted
baseline unchanged.

## 10. Baseline transitions

After `ACCEPT` or `ACCEPT WITH FOLLOW-UP`, the reviewed HEAD becomes the
accepted baseline for the next candidate. The next Codex governance update must
persist that exact, already existing SHA as both `review_base_commit` and
`accepted_baseline_commit`, and record the reviewed task, verdict, timestamp,
and open follow-ups. Never guess the SHA of a commit that has not yet been
created.

After `REJECT`, `review_base_commit` and `accepted_baseline_commit` remain the
last accepted SHA. A later fix is reviewed cumulatively from that unchanged
base. `Solo audit` never advances the baseline.

## 11. Mandatory review output

Every normal review report must contain:

1. repository, `ROOT`, branch, full baseline SHA, full HEAD SHA, and ancestry;
2. reviewed cumulative range and exact changed-file list;
3. verdict;
4. findings ordered by severity with file/line references and evidence;
5. commands/checks run, results, skips, and environment limitations;
6. assessment of tests, benchmarks, reproductions, certificates, and proofs as
   separate categories;
7. manifest, hash, environment, verifier-independence, and pruning assessment
   when applicable;
8. claim IDs and classification impact;
9. surprising results and their disposition;
10. open follow-ups with stable IDs, or an explicit statement that none remain;
11. the exact baseline transition or the reason it remains unchanged;
12. a complete prompt for the next single atomic Codex task, or an explicit
    statement that no task is authorized.

## 12. Requirements for the next Codex prompt

The prompt produced after review must be self-contained and state:

- repository and branch;
- atomic task ID;
- exact objective and motivation;
- exact baseline/review-base SHA and expected HEAD precondition;
- operating mode (`STRICT` when required by `AGENTS.md`);
- required startup files and relevant prior dossier;
- exact files that may change;
- explicit out-of-scope work;
- implementation or documentation requirements;
- required commands and environment;
- evidence, manifest, hash, and claim-classification obligations;
- acceptance criteria;
- Git prohibitions and the fact that the user commits and pushes manually;
- required final report and the instruction to stop at `READY_FOR_REVIEW`.

Open follow-ups must be named by stable ID. The prompt must not authorize a
mathematical search, pruning change, or claim upgrade implicitly.

## 13. Visibility boundary

ChatGPT must not assume that a local commit, uncommitted worktree, local branch,
artifact, log, or amended history is visible. A commit is reviewable remotely
only after its object and referenced files are available to the reviewer.
When the user refers to unpublished local state, ChatGPT must request the push,
patch, bundle, or exact file content needed for review and clearly label any
interim assessment as incomplete.
