# Verifier fixture inventory

These files exercise local verifier behavior only. None is claimed to be a
counterexample, a search certificate, or evidence of exhaustive coverage.

## Canonical graph fixtures

- `empty.json`: zero vertices and edges; the verifier's explicit minimum-degree
  convention returns zero.
- `path-p4.json`, `path-p13.json`, `path-p14.json`: paths on the stated number
  of vertices (not that number of edges).
- `chorded-p4.json`: a four-vertex path ordering with a chord, so it is not an
  induced `P4`.
- `c3.json`, `c4.json`, `c5.json`, `c8.json`, `c16.json`: simple cycle graphs.
- `complete-k4.json`, `complete-k5.json`: complete graphs with minimum degrees
  three and four, respectively.
- `disconnected.json`: a triangle, a separate edge, and an isolated vertex.

`malformed-loop.json`, `malformed-duplicate-edge.json`,
`malformed-duplicate-key.json`,
`malformed-endpoint.json`, `malformed-nonfinite.json`, and `malformed-json.json` are deliberate negative
parser cases.

## Manifest-integrity fixtures

`manifest-hash-target.txt` is a fixed 27-byte LF-terminated payload.
`manifest-valid-hash.json` declares its actual SHA-256. The otherwise
structurally valid `manifest-invalid-hash.json` deliberately declares an all-zero
digest. Both manifests are `scaffold-only`, incomplete, engineering fixtures;
neither records an executed experiment. Run-only values such as timestamps,
host platform, command, and wall time are null or empty rather than invented.

## Differential domain

`tests/differential/test_small_graph_oracles.py` generates, rather than stores,
every labelled simple graph on vertex sets `{0, ..., n-1}` for `0 <= n <= 5`.
The counts are `1, 1, 2, 8, 64, 1024`, totaling exactly 1,100 graphs. Bounded
agreement with the test-local permutation oracles is not a proof for arbitrary
graphs and is not search-completeness evidence.
