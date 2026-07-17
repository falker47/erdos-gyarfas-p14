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
- `git diff --check` and a clean post-test working tree detect accidental
  source modifications.

CI does not run `k=13`, `k=14`, the P13 C4/C8 search, a retained or substantive
performance benchmark, or a certifying search. Passing CI establishes
engineering confidence and bounded test agreement, not a theorem.

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

The last two job steps use `actions/upload-artifact@v4` to upload the complete
contents of `artifacts/counterexamples/` and `benchmarks/results/`. Artifact
names include compiler, GitHub run ID, and run attempt, preventing GCC/Clang or
rerun collisions. A missing directory payload after an unrelated failure is an
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

Official actions are major-version pinned (`actions/checkout@v4`,
`actions/setup-python@v5`, and `actions/upload-artifact@v4`). A future release
hardening task may pin immutable action commit SHAs.

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
