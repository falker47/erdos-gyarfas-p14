# Continuous integration

## Fast workflow

`.github/workflows/ci.yml` runs for pushes, pull requests, and manual dispatch.
It is intentionally bounded:

- Python 3.11 and 3.12 run the verifier unit and differential suite;
- GCC and Clang configure and build the C++17 wrapper on Ubuntu;
- integration tests build the original Makefile in a temporary copy and run
  only tiny upstream parameters under explicit timeouts, requiring ordinary
  process completion with exit `0` for both `k=3` and `k=4`;
- each compiler job makes one ephemeral `k=3` engineering measurement to test
  the benchmark runner, exact accepted-outcome contract, and result schema; the
  value is not committed or used as mathematical evidence;
- every JSON Schema is checked against Draft 2020-12;
- deterministic graph serialization is covered by the Python tests;
- the per-file upstream inventory is checked before and after tests;
- complete tiny-surprise and benchmark artifacts are uploaded from each
  compiler job when any job step fails;
- a repository-local validator scans every workflow for immutable external
  Action references;
- one dedicated full-history job checks whitespace in the canonical committed
  review range;
- post-test `git diff --check` and clean-worktree checks detect only accidental
  changes created in each matrix worktree.

CI does not run `k=13`, `k=14`, the P13 C4/C8 search, a retained or substantive
performance benchmark, or a certifying search. Passing CI establishes
engineering confidence and bounded test agreement, not a theorem.

## Committed range versus test-created worktree

The `committed-range-whitespace` job checks out complete Git history with
`fetch-depth: 0` and invokes:

```text
python tools/check_review_range_whitespace.py --state REVIEW_STATE.yaml --head HEAD
```

The helper derives the repository root from its own checked-in path, parses the
state as strict UTF-8 JSON, and accepts only schema version `1.0` with a
lowercase 40-character `review_base_commit`. The sentinel `ROOT` is explicitly
unsupported. It resolves both endpoints to commits, requires the baseline to
be an ancestor of the requested head, and then runs an isolated equivalent of:

```text
git \
  -c core.whitespace=blank-at-eol,space-before-tab,blank-at-eof,tabwidth=8 \
  -c core.attributesFile=<platform-null-device> \
  --attr-source=<head> --no-pager diff \
  --no-ext-diff --no-textconv --no-color --check <base>..<head> --
```

The explicit policy checks blank-at-EOL/trailing whitespace,
space-before-tab in initial indentation, and blank lines added at EOF, with
the default tab width fixed at eight. Repository-local `core.whitespace` cannot
weaken it. The child environment ignores system and global Git configuration,
removes process-level configuration injection including `GIT_CONFIG_COUNT`,
its key/value family, and `GIT_CONFIG_PARAMETERS`, and selects null global and
system configuration files. These changes affect only each child process; the
parent environment and Git configuration are not modified.

Git has no switch that skips only repository-local config. The checker safely
overrides the local `core.whitespace` and `core.attributesFile` values it
needs, then queries the remaining effective stack once with:

```text
git config --includes --name-only --get-regexp '^[dD][iI][fF][fF]\.'
```

The query has no explicit scope option. After system, global, and inherited
process configuration have been neutralized, Git always loads the shared
repository-local config and automatically loads the current worktree's
`config.worktree` only when `extensions.worktreeConfig` is enabled. Direct,
conditional, and nested includes remain part of those effective sources.
Only exit `1` with empty stdout and stderr means that no key matched; a parse,
include, or query error is fatal. Any remaining `diff.*` key fails closed.
Such keys can otherwise combine with a checked-in diff driver to mark a text
file binary and suppress whitespace diagnostics. This condition has empty
stdout and the deterministic error:

```text
check_review_range_whitespace: error: repository-local diff configuration is not permitted
```

The checker deliberately does not invoke `git config --worktree`
unconditionally. The installed Git 2.45.1 documentation describes that option
as equivalent to `--local` when the extension is disabled, but the installed
binary rejects it with exit `128` once a repository has multiple worktrees and
the extension is absent or false. Reading the effective stack avoids that
layout-dependent failure while still observing a real per-worktree scope when
Git enables it.

Global attributes selected by `core.attributesFile` are redirected to the
platform null device, and system attributes are disabled in the child. The
attribute source is the resolved head commit, so a dirty worktree
`.gitattributes` cannot alter the verdict. Checked-in `.gitattributes` remains
effective reviewable policy, including
`third_party/erdos-gyarfas/** -diff`.

Git gives non-versioned `$GIT_DIR/info/attributes` higher precedence than
checked-in attributes and offers no supported switch that ignores only that
source. The helper therefore checks the path before and after the diff. An
absent or zero-byte regular file is harmless; a nonempty, unreadable,
nonregular, or symlink source fails closed with this deterministic diagnostic:

```text
check_review_range_whitespace: error: non-versioned Git attributes are not permitted: $GIT_DIR/info/attributes
```

Both fail-closed rules apply even to a clean range because the range is not
evaluated under unreviewed diff configuration or repository attributes.
Missing objects, malformed state, invalid ancestry, Git errors, committed
whitespace errors, and either fail-closed condition are fatal. A successful
deterministic JSON line reports the two full commit IDs and exact range. The
helper uses no shell interpolation and does not write the worktree, index,
configuration, refs, objects, or repository attributes.

Focused tests use real temporary repositories rather than mocked Git
subprocesses. They cover a single clean worktree with the extension absent;
multiple worktrees with the extension absent or false, clean and bad ranges,
and invocation from both the main and a linked worktree; enabled worktree
configuration with and without direct or included `diff.*`; direct and
included local `diff.*`; and hostile `diff.*` injected through neutralized
system, global, and process sources. Each new multi-worktree case repeats the
checker byte-for-byte and compares both worktrees, indexes, refs, objects,
configuration, environment, and attributes before and after invocation.

The identically named `Check test-created worktree whitespace` steps in the
Python and C++ matrix jobs intentionally retain endpoint-free
`git diff --check`. They run after tests and inspect only changes those tests
may have created in that checkout. A clean checkout makes those worktree checks
empty; it does not make them evidence about already committed changes. The
dedicated full-history job and the post-test worktree checks therefore enforce
separate boundaries and are not substitutes for one another.

## Tiny process-outcome contract

The known tiny cases have one ordinary successful outcome: child-process
`termination_reason: "exited"` paired with `exit_code: 0`. A timeout, spawn
failure, signal, or any other exit code fails. The upstream command,
executable identity, and repository/upstream provenance are collected before
the child starts. An ordinary exit `0` creates no surprising-outcome artifact.

For every other outcome, the integration path performs this exact ordering:

1. write stdout and stderr as byte-preserving `.bin` files beneath the
   configured `artifacts/counterexamples/` directory;
2. close the files and recompute their byte counts and SHA-256 hashes from
   disk;
3. write an immutable deterministic `surprising_process_outcome` JSON record
   with classification `EMPIRICAL_OBSERVATION` and inspection state
   `not_started` or `not_applicable`;
4. only for exact exit `100`, start the independent inspector.

The record and its separate inspection record conform to
`schemas/surprising-process-outcome.schema.json`. Paths inside the bundle are
relative basenames, and existing evidence is never overwritten. Log output
retains only bounded prefixes, sizes, hashes, and artifact paths; it is a quick
diagnostic, not a substitute for the complete raw files.

Upstream exit `100` is not an alternative smoke-test success. It means that the
upstream process printed a candidate graph and is treated as a surprising path.
The inspector runs as a direct child process under a five-second timeout that
is separate from the upstream process's ten-second timeout. It uses Python
process APIs available on Windows and POSIX; on timeout the parent kills,
drains, and waits for the direct child. The inspector reads and verifies the
already-frozen file sizes and hashes before any decoding or predicate work:

- a project-authored interface adapter parses the complete upstream
  adjacency-list output without importing upstream parsing or predicates;
- the adapter rejects malformed syntax, duplicate declarations or neighbors,
  loops, asymmetric adjacency, undeclared endpoints, and noncanonical labels;
- the project-authored `egverify.graph.Graph` and independent verifier
  predicates check simple-graph construction, minimum degree at least 3,
  induced-`P_k` absence, and every relevant power-of-two cycle length;
- successful parsing reports the canonical graph serialization, its SHA-256,
  and every predicate result.

The parent writes a separate deterministic inspection JSON with status
`completed`, `timeout`, or `error`. Parsing or predicate failure is a completed
inspection; timeout, inspector spawn/nonzero exit, and malformed inspector
protocol are explicit machine-readable non-completions. None can delete or
rewrite the original streams or outcome record through the supported path. The
parent pins the outcome-record hash before launch, independently rechecks that
record and both raw streams after the child exits, and owns every source-bound
field in the final schema-validated inspection envelope. The integration test
still fails after parsing failure, predicate failure, all-predicate success,
timeout, or error. If every independent predicate passes, the output is only a
surprising frozen result requiring a separate task. No branch is counterexample
acceptance or certification.

Each benchmark case declares a required nonempty `accepted_outcomes` array of
exact `(termination_reason, exit_code)` objects. Reasons and codes are not
separate lists, so unintended Cartesian-product pairs cannot pass. The runner
returns `0` only for an exact declared pair. It returns `3` after an attempted
execution whose actual pair is unaccepted, but only after preserving and
schema-validating the result JSON and captured stdout/stderr. Configuration,
schema, or artifact failures return `1`.

CI lets a nonzero integration or runner status fail its step directly. If the
benchmark producer ran, an `always()` step checks that its result JSON exists
and schema-validates it even after runner failure. The upstream inventory and
final hygiene checks also use `always()`. Failure-only diagnostics print
bounded, JSON-escaped prefixes with byte counts and SHA-256 hashes.

The last two compiler-job steps use the official `actions/upload-artifact`
release `v4.6.2`, pinned to commit
`ea165f8d65b6e75b540449e92b4886f43607fa02`, to upload the complete contents
of `artifacts/counterexamples/` and `benchmarks/results/`. The adjacent
`# v4.6.2` release comment is explanatory and non-operative; GitHub selects
the Action from the repository and commit before that comment. Artifact names
include compiler, GitHub run ID, and run attempt, preventing GCC/Clang or rerun
collisions. A missing directory payload after an unrelated failure is an
explicit warning; hidden `.gitkeep` files do not count as produced evidence.
There is no `continue-on-error` or status suppression, so post-failure checks
and successful uploads cannot turn the original failed step green.

Hosted-job cancellation, whole-job timeout, runner loss, or artifact-service
failure can still prevent a final upload. Hosted GitHub Actions execution was
not observed by this local task and is not represented as passed.

When `EG_SURPRISING_OUTCOME_DIR` is unset, local integration tests use a pytest
temporary directory. CI sets the variable to a deterministic
repository-relative directory so a failure-only upload can collect the frozen
files.

## Immutable external Action references

Every external Action used by either workflow is pinned to a complete
lowercase commit SHA. The selected identities are:

| Repository | Exact stable release | Commit SHA |
| --- | --- | --- |
| `actions/checkout` | `v4.3.1` | `34e114876b0b11c390a56381ad16ebd13914f8d5` |
| `actions/setup-python` | `v5.6.0` | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `actions/upload-artifact` | `v4.6.2` | `ea165f8d65b6e75b540449e92b4886f43607fa02` |

Each `uses:` line retains the exact release tag as an end-of-line comment,
for example:

```yaml
uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
```

The comment is explanatory only. GitHub executes the commit named before the
comment; changing the comment cannot change the selected Action. Release and
commit identities were resolved from the official `actions/<name>` repository,
including the exact release ref, floating major ref, commit object, and
`action.yml` at that commit. Detailed commands and observations are in
`ops/TASK-20260719__pin_github_actions_immutable_shas/EVIDENCE.md`.

The full-history fast-CI job also runs:

```text
python tools/check_github_action_pins.py
```

The standard-library-only validator reads every `.yml` and `.yaml` below
`.github/workflows/` as strict UTF-8 in sorted path order. It accepts a local
Action only when the reference begins `./`. A GitHub-hosted external Action
must use canonical `owner/repository[/subpath]@ref` syntax with a lowercase
40-character commit SHA. A remote Docker Action must use
`docker://image@sha256:<64-lowercase-hex>` without a mutable image tag. Branches,
major or release tags, short or uppercase SHAs, dynamic expressions, missing
refs, and noncanonical, multiline, quoted-key, explicit-key, or flow-style
`uses:` forms fail closed. Block scalar bodies such as `run: |` are treated as
script text rather than workflow keys.

Success is one deterministic JSON line containing the sorted workflow list and
every normalized external occurrence. Failure writes no stdout and emits one
deterministic diagnostic on stderr. This check is read-only and has no YAML or
other new runtime dependency.

The validator runs only after the checkout and Python setup Actions in the same
job have already executed. It is therefore a repository-local regression
check, not protection against a malicious Action ref already present in that
workflow revision. Review, protected branches, and any organization-level
GitHub policy remain separate controls.

A full commit pin removes mutability of the selected Git ref. It does not make
the hosted `ubuntu-24.04` runner image, its operating system packages, the
Actions service, or packages installed during a job immutable. Those distinct
environment-locking obligations remain tracked by `RFU-ENV-001`.

## Manual heavy-search scaffold

`.github/workflows/heavy-search.yml` is manual-only. Its accepted mode is
`scaffold-only`; it does not invoke the upstream program or any search. Inputs
record a requested tiny `k`, partition label, time limit, and memory limit so
the interface can be reviewed before execution is enabled.

The workflow rejects P13/P14 and any non-scaffold request, emits a refused or
not-run experiment manifest, validates positive integer resource inputs while
preserving their original strings, and uploads the manifest and log even when
a guard rejects the request. It cannot emit
`COMPUTER_CERTIFIED_RESULT`.

Before the guard or manifest producer runs, the workflow invokes
`tools/resolve_review_task_id.py` on the checked-out `REVIEW_STATE.yaml` with a
required dossier check. The resolver accepts only strict JSON schema version
`1.0`, a canonical `active_task_id`, and a regular non-symlink
`ops/<active_task_id>/TASK_STATUS.md` inside the repository. It has no manual
task-ID input or fallback. Resolution failure fails the job and no substitute
manifest is emitted.

The manifest receives the resolved ID and records its source, the canonical
dossier-status path, and checkout-computed SHA-256 hashes of both
`REVIEW_STATE.yaml` and the resolved `TASK_STATUS.md`. These fields bind the
scaffold record to versioned task-governance files from the same checkout;
schema and hash validation do not establish run semantics or a mathematical
result.

Enabling real work later requires a separate reviewed task covering resource
enforcement, checkpointing, invariant and pruning status, partition coverage,
certificate replay, and failure preservation.
