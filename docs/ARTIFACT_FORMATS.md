# Artifact formats

All current schemas use JSON Schema Draft 2020-12 and live under `schemas/`.
Schema validation checks representation, required fields, simple value ranges,
and some cross-field constraints. It does not prove graph semantics, hash
correctness, partition coverage, pruning soundness, or a mathematical claim.

## Canonical graph and counterexample artifact

`schemas/counterexample.schema.json` wraps the verifier's canonical graph
payload:

```json
{
  "schema_version": "1.0",
  "vertices": [0, 1, "x"],
  "edges": [[0, 1], [1, "x"]]
}
```

Integer labels sort before string labels. Each edge stores its lower canonical
endpoint first, and edges are lexicographically sorted. Strings use the ASCII
identifier grammar in the schema. The graph digest is SHA-256 over the compact
UTF-8 canonical payload plus one LF, excluding artifact metadata and the hash
field itself.

The counterexample envelope additionally records source, target, mode, `k`,
generator environment, and verification status. The semantic verifier must
still check vertex count, endpoints, loops, duplicate undirected edges,
ordering, graph hash, minimum degree, induced-path absence, and the relevant
simple-cycle predicate.

## Experiment manifest

`schemas/experiment-manifest.schema.json` records every field required by the
verification protocol. Paths are repository-relative. `artifacts` and the keys
of `artifact_sha256` must denote the same files; `tools/verify_manifest.py`
checks that semantic equality and recomputes the hashes.

Unknown measurements are `null` only where the schema allows it. A refused or
not-run scaffold has `completed: false`, `search_mode: scaffold-only`, and
`verifier_result: not-run`. A failed, timed-out, or interrupted run remains a
material manifest and must not be rewritten as completed.

## File inventories

`tools/hash_artifacts.py tree` emits individual SHA-256 values and an inventory
digest. The inventory digest hashes records in ascending POSIX relative-path
order. Each record is the UTF-8 path, one NUL byte, the lowercase ASCII file
digest, and one LF byte. File content is read without newline conversion.
Symbolic links are rejected so an inventory cannot depend on a target outside
the recorded tree.

## Benchmark result

`schemas/benchmark-result.schema.json` is emitted by
`tools/run_benchmark.py`. It hashes the case, executable, stdout, and stderr;
captures command, `k`, compiler, flags, platform, architecture, CPU/thread
counts, timestamps, wall time, exit status, and available CPU/memory metrics;
and labels the artifact kind `engineering_benchmark`. Its claim classification
is the allowed class `EMPIRICAL_OBSERVATION`.

Benchmark results measure process behavior only. They do not establish output
semantics or exhaustive coverage.

## Search partitions

`schemas/search-partition.schema.json` is version `0.1-provisional`. It records
a parent configuration, canonical root-state path/hash, partition identity,
program identity, lifecycle state, counters, output, and verifier result.
Neither schema validity nor a collection of completed partition files proves
that the partition mapping is total or disjoint.

## Search certificate scaffold

`schemas/search-certificate.schema.json` is deliberately constrained to:

- `provisional: true`;
- `certifying_use_permitted: false`;
- `artifact_kind: search_certificate_scaffold`;
- `classification: ENGINEERING_ASSUMPTION`;
- `status: provisional_non_certifying`;
- unaccepted totality and disjointness proofs;
- an independent verifier result of `not-run`.

It is an interface-review artifact, not a usable certificate. A future
certifying format requires a separate schema version and acceptance under
`research/VERIFICATION_PROTOCOL.md`.
