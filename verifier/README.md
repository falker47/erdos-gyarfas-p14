# Independent small-graph verifier

`egverify` is the bootstrap verifier for finite, simple, undirected graphs. It
does not import or call any graph predicate from the preserved upstream search.
The implementation favors direct, auditable algorithms over performance and is
intended for small fixtures and candidate checking. It does **not** verify that
a generator searched an exhaustive domain.

## Canonical graph JSON

A graph document has exactly these fields:

```json
{
  "edges": [[0, 1], [1, "v2"]],
  "schema_version": "1.0",
  "vertices": [0, 1, "v2"]
}
```

Vertex identifiers are JSON integers (booleans are not integers here) or
nonempty ASCII identifiers matching
`[A-Za-z0-9][A-Za-z0-9_.:-]*`, with at most 200 characters. Integer and string identifiers may coexist.
Vertices are sorted with all integers first in numeric order, followed by
strings in code-point order. Each edge is oriented according to that order,
and edges are lexicographically sorted. Loops, duplicate vertices, duplicate
undirected edges, and edges with undeclared endpoints are rejected.

Canonical bytes are UTF-8 encoded compact JSON with keys sorted and one final
LF byte. `Graph.canonical_sha256()` hashes exactly those bytes. Whitespace and
input ordering therefore do not affect the canonical digest.

Counterexample artifact documents may place protocol metadata beside the same
top-level `vertices` and `edges`. If `graph_sha256` is present, the
counterexample command compares it with the canonical graph payload digest;
metadata and the hash field itself are excluded from that digest.
An artifact with metadata is also checked against
`schemas/counterexample.schema.json`, and its declared vertex count, target,
canonical ordering, and graph digest are checked semantically.

## Predicates and target semantics

- `P_k` means a path on exactly `k` vertices, not a path with `k` edges.
- Path detection requires inducedness: selected nonconsecutive path vertices
  may not be adjacent.
- Cycle detection looks for a simple cycle of exactly the requested length;
  the cycle need not be induced and may have chords.
- Relevant power-of-two cycle lengths are `4, 8, 16, ...` up to the graph's
  vertex count.
- The `p14` candidate predicate requires minimum degree at least 3, no induced
  `P14`, and no relevant power-of-two cycle.
- The `p13-c4c8` candidate predicate requires minimum degree at least 3, no
  induced `P13`, and neither a `C4` nor a `C8`.

For the empty graph the API reports minimum degree `0` as an explicit software
convention, so it cannot satisfy either minimum-degree condition.

## CLI

After `python -m pip install -e '.[test]'`:

```text
egverify graph FILE
egverify counterexample --target p14 FILE
egverify counterexample --target p13-c4c8 FILE
egverify manifest FILE [--schema schemas/experiment-manifest.schema.json]
```

Every normal outcome is one compact JSON object on stdout. Keys are sorted.
Exit codes are stable:

- `0`: the requested validation passed;
- `1`: a well-formed object was rejected by a structural, property, schema, or
  integrity check;
- `2`: invocation, file I/O, or JSON decoding failed;
- `3`: an unexpected internal verifier failure occurred.

For `counterexample`, exit `0` means only that this implementation accepts the
single supplied candidate predicate. It is not an exhaustive-search result and
is not by itself a project-accepted counterexample. For `manifest`, JSON Schema
validation checks structure while separate semantic checks recompute hashes of
declared artifacts. Neither establishes search coverage or certificate
correctness.

The direct Python dependencies are pinned in `pyproject.toml` to versions used
by the bootstrap checks. A future fully locked environment must additionally
pin transitive dependencies and the interpreter/container; the package metadata
alone is not a complete environment lock.
