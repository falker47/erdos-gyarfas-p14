# Verification Protocol

## 1. Purpose

This document defines the evidence required for mathematical and computational
claims in this repository.

It distinguishes:

- code correctness;
- bounded testing;
- upstream reproduction;
- exhaustive search;
- computer certification;
- independent reproduction;
- counterexample verification.

No other file may weaken these requirements implicitly.

## 2. Verification levels

### V0 — Source inspection

Evidence:

- code or document was read;
- relevant paths and commit were recorded.

Permitted classification:

- `EMPIRICAL_OBSERVATION`

Not permitted:

- `VERIFIED_BOUNDED_COMPUTATION`
- `COMPUTER_CERTIFIED_RESULT`

### V1 — Local functional verification

Evidence:

- unit tests;
- static checks;
- build checks;
- curated fixtures.

Permitted classification:

- `VERIFIED_BOUNDED_COMPUTATION`, restricted to the stated fixtures/checks

Limitation:

V1 does not establish exhaustive search completeness.

### V2 — Differential bounded verification

Evidence:

- optimized or production routine compared with an independent simple oracle;
- exact bounded domain documented;
- all mismatches preserved;
- code paths kept sufficiently independent.

Permitted classification:

- `VERIFIED_BOUNDED_COMPUTATION`

Limitation:

V2 does not prove behavior outside the tested domain.

### V3 — Upstream reproduction

Evidence:

- exact upstream commit;
- exact environment;
- successful build;
- exact command;
- recorded output and hashes;
- result consistent with upstream claim.

Permitted classification:

- `REPRODUCED_UPSTREAM_RESULT`

Limitations:

- the same implementation may reproduce the same bug;
- a reproduced runtime is not a certificate;
- reproduction does not independently prove the mathematical theorem.

### V4 — Certified exhaustive computation

Required evidence:

1. canonical mathematical target;
2. proved search invariant;
3. exact root set;
4. deterministic implementation;
5. complete certifying pruning registry;
6. proved partition coverage and disjointness;
7. complete manifest set;
8. completion of every required partition;
9. artifact hashes;
10. independent certificate verification;
11. accepted trust-boundary document;
12. reproducible commands;
13. successful regression on smaller known cases;
14. no enabled heuristic-only rule;
15. review of all unexpected warnings and partial failures.

Permitted classification:

- `COMPUTER_CERTIFIED_RESULT`

### V5 — Independent reproduction

Evidence:

- a second implementation or research group;
- independently produced or replayed search;
- independently implemented critical predicates;
- matching result;
- separately recorded environment and hashes.

Permitted classification:

- `COMPUTER_CERTIFIED_RESULT`, with V5 independent-reproduction evidence

V5 is preferred for publication but is not required before beginning research.

## 3. Counterexample protocol

A counterexample candidate must be serialized in a documented canonical format.

Required fields:

- schema version;
- graph identifier;
- vertex count;
- sorted edge list;
- graph hash;
- source task;
- source project commit;
- generator command;
- generator environment;
- target claim;
- relevant `k`;
- enabled search mode;
- verification status.

The independent verifier must check:

1. vertex labels are valid and unique;
2. no loops;
3. no parallel edges;
4. adjacency symmetry;
5. every vertex has degree at least 3;
6. no induced `P14`;
7. no cycle of any relevant power-of-two length;
8. serialization hash;
9. canonical reserialization stability.

For the intermediate target, replace step 7 with absence of C4 and C8 and
step 6 with absence of induced P13.

A counterexample is not accepted when only the generator validates it.

## 4. Negative-result protocol

A statement that no counterexample exists in a searched domain requires more
than a completed process.

The project must document:

- the exact mathematical domain;
- why the search representation covers it;
- why every state transition is complete;
- why every pruning rule is sound;
- why every required root was included;
- why all partitions completed;
- why no partition was duplicated or omitted;
- how interruption and restart are handled;
- how artifacts are associated with code and environment;
- how a separate verifier checks the conclusion.

A log line such as `done`, an empty output file, or exit code zero is
insufficient.

## 5. Search invariant review

Before accepting an exhaustive run, the invariant proof must specify:

- meaning of every current graph state;
- which edges are fixed;
- which edges remain undecided;
- relationship between labels and construction order;
- relationship to a hypothetical minimal counterexample;
- definition of a safe-neighbor set;
- completeness of safe-neighbor enumeration;
- anchor-selection rule;
- recursion measure or well-foundedness used by the proof;
- conditions under which a branch is terminal;
- relationship between program return codes and mathematical outcomes.

The proof must match source code, not only pseudocode.

Any semantic code change invalidates the prior invariant review until
reassessed.

## 6. Pruning verification

Every pruning rule record must include:

- stable ID;
- exact predicate;
- search modes where it applies;
- proof;
- code locations;
- tests;
- verifier treatment;
- version introduced;
- status.

A certifying rule must be locally checkable from the search state or justified
by a globally reviewed theorem.

Performance benefit is irrelevant to soundness.

An optimization that merely changes traversal order is not a pruning rule, but
its determinism and checkpoint effects must still be tested.

## 7. Partition protocol

A search partition scheme must define a total mapping:

`search state -> exactly one partition identifier`

for all states at the selected frontier.

Required proof obligations:

- every full search branch reaches exactly one frontier state;
- every frontier state has exactly one partition ID;
- partition IDs are stable under serialization;
- union of partitions equals the intended frontier;
- partitions do not overlap;
- completed partitions cannot be confused with partial ones.

Each partition manifest records:

- partition ID;
- parent search configuration;
- serialized root state;
- root-state hash;
- program commit;
- certificate format version;
- start and completion status;
- state counts;
- output hash;
- verifier result.

A global manifest lists every expected partition and its status.

## 8. Manifest requirements

Every material run manifest must contain at least:

- `schema_version`
- `run_id`
- `task_id`
- `claim_ids`
- `classification`
- `project_commit`
- `working_tree_status`
- `upstream_repository`
- `upstream_commit`
- `executable_sha256`
- `command`
- `parameters`
- `search_mode`
- `k`
- `forbidden_cycle_lengths`
- `pruning_rule_ids`
- `partition_id`
- `seed`
- `started_at_utc`
- `finished_at_utc`
- `exit_code`
- `termination_reason`
- `completed`
- `host`
- `operating_system`
- `architecture`
- `compiler`
- `compiler_flags`
- `runtime_dependencies`
- `cpu_count`
- `memory_limit`
- `peak_memory` when measurable
- `wall_time_seconds`
- `cpu_time_seconds` when measurable
- `counters`
- `artifacts`
- `artifact_sha256`
- `stdout_sha256`
- `stderr_sha256`
- `verifier`
- `verifier_result`
- `limitations`

Unknown fields must be explicit `null` only when the schema allows them.

Do not invent unavailable values.

## 9. Determinism checks

A deterministic search configuration should produce identical:

- canonical root serialization;
- partition list;
- event ordering where required;
- state counts;
- leaf counts;
- rejection counts;
- certificate bytes or normalized certificate hash;
- result classification.

Wall time, process IDs, memory addresses, and timestamps are excluded from
deterministic digests.

When byte-for-byte determinism is impractical, define a normalized semantic
digest.

## 10. Reference-versus-optimized comparison

Before accepting an optimization:

1. preserve a reference implementation;
2. choose a bounded complete comparison domain;
3. run both implementations;
4. compare accepted states, rejected states, leaves, counterexamples, and
   normalized search digest;
5. investigate every mismatch;
6. record before/after benchmark data;
7. state whether the change affects only order, representation, or semantics.

A faster implementation is not accepted merely because final output matches on
one case.

## 11. Independent predicate oracles

The test suite should include simple independent implementations of:

- induced-path detection by explicit vertex-subset and path-order checks for
  very small graphs;
- simple-cycle existence for an exact requested length;
- C4 and C8 detection;
- minimum degree;
- graph serialization;
- counterexample validation.

The brute-force domain must be recorded.

Use exhaustive enumeration of all simple labelled graphs only where bounded
and practical. For larger fixtures use generated and hand-constructed cases.

## 12. CI policy

Ordinary CI:

- builds the preserved upstream baseline;
- builds project code;
- runs unit tests;
- runs bounded differential tests;
- validates schemas;
- runs independent counterexample verifier tests;
- runs tiny upstream smoke cases;
- checks deterministic serialization;
- checks documentation links and diff hygiene.

Ordinary CI must finish predictably.

Heavy workflow:

- manual dispatch only;
- explicit resource settings;
- mandatory manifest;
- periodic checkpoints;
- artifact upload on success, failure, cancellation where supported;
- no automatic theorem claim.

## 13. Environment capture

A reproducible result records:

- operating-system image or container digest;
- compiler version;
- standard library version where relevant;
- build-system version;
- compilation flags;
- Python version;
- exact Python dependency lock;
- CPU architecture;
- core count;
- memory limit;
- environment variables that affect scheduling or hashing;
- command;
- code commit;
- upstream commit.

A Docker tag without digest is not immutable provenance.

## 14. Accepted wording by level

V1:

> Unit tests pass for the documented fixtures.

V2:

> The production predicate agrees with the independent oracle on the exact
> bounded domain D.

V3:

> The upstream result for parameter k was reproduced under environment E.

V4:

> The complete certificate for claim C was accepted by independent verifier V
> under trust boundary T.

Do not shorten V3 into “the theorem is independently verified.”

## 15. Failure handling

On:

- crash;
- timeout;
- out-of-memory;
- signal termination;
- manifest mismatch;
- hash mismatch;
- partition omission;
- verifier disagreement;

the run is not complete.

Preserve:

- partial manifest;
- logs;
- checkpoint;
- environment;
- failure reason;
- relevant hashes.

A resumed run must identify the original run and prove that work was neither
lost nor double-counted.

## 16. Review gate for a mathematical conclusion

Before changing a claim to `COMPUTER_CERTIFIED_RESULT`, the reviewing ChatGPT
must inspect:

- claim statement;
- proof of invariant;
- pruning registry;
- source diff;
- test results;
- CI;
- manifests;
- coverage report;
- certificate hashes;
- independent verifier implementation;
- verifier output;
- trust boundary;
- residual limitations.

Any unresolved high-severity issue blocks acceptance.
