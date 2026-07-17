# Upstream Algorithm Audit Baseline

## Source

Repository:

`https://github.com/rbsandeep/Erdos-Gyarfas`

Design-time inspected and bootstrap-resolved `main` commit:

`27d9cb22705905fac32314c5e95addf6e11ce283`

The read-only bootstrap resolution confirmed this SHA. Its Git tree is
`35707222c62e2bc14b90f385f593a66799405eba`; canonical hashes and acquisition
evidence are recorded in `upstream/UPSTREAM_PROVENANCE.json`.

Associated paper:

A. S. Hegde, R. B. Sandeep, P. Shashank,
“Erdős–Gyárfás conjecture on graphs without long induced paths,”
arXiv:2410.22842v2.

## Observed main-branch structure

- `include/graph.h`
- `include/lib.h`
- `src/graph.cpp`
- `src/lib.cpp`
- `src/main.cpp`
- `Makefile`
- `README.md`
- `CITATION.cff`
- `LICENSE`

No project conclusion is inferred from this list.

## Graph representation

The observed `Graph` class stores:

- integer vertex labels;
- adjacency sets;
- number of vertices `n`;
- target induced-path parameter `k`.

The container is an unordered map from vertex IDs to ordered neighbor sets.

Consequences requiring audit:

- adjacency membership is straightforward;
- graph serialization is not canonical;
- unordered-map iteration may affect printed ordering;
- labelled-isomorphic states are not visibly merged;
- memory overhead may be substantial in a parallel copy-heavy search.

## Forbidden-cycle predicate

The main implementation tests lengths:

`4, 8, 16, ...`

up to the current vertex count.

The cycle search is recursive and searches for a simple closed walk with the
requested number of vertices.

Audit obligations:

- confirm off-by-one semantics;
- confirm marked-state restoration on every return path;
- confirm no false positive from repeated start handling;
- confirm edge-specific cycle checks;
- compare with an independent exact-length-cycle oracle on small graphs.

## Induced-path predicate

The implementation extends a path recursively.

Before adding a new vertex it checks that the vertex has no edge to any already
marked path vertex other than the immediate predecessor.

Audit obligations:

- confirm the path contains exactly `k` vertices;
- confirm state restoration after both success and failure;
- confirm all possible endpoints and extensions are covered;
- investigate the optimization that starts from only `n - 1` vertices;
- compare with an independent induced-subgraph oracle.

## Neighbor-set enumeration

For the newest vertex:

- existing incident edges are marked fixed;
- individually cycle-forbidden edges are marked unavailable;
- remaining candidate edges are enumerated as binary subsets;
- complete candidate subsets are rejected when they create a forbidden cycle.

Audit obligations:

- prove every compatible subset is enumerated;
- prove no subset is skipped by the `-1/0/1` representation;
- prove state is restored after every iteration;
- record the traversal order;
- define deterministic counters;
- prove the individual forbidden-edge pruning is monotone.

## Recursive extension

If the current graph is Pk-free:

- find the highest-labelled vertex of degree below 3;
- if none exists, report a counterexample;
- otherwise add one new vertex adjacent to that anchor;
- recurse;
- remove the new vertex.

The associated paper supplies a minimal-counterexample argument.

Audit obligations:

- restate the invariant independently;
- align every proof condition with actual code;
- confirm the highest-labelled rule matches the lemma;
- define the exact relationship between initial path size and `k`;
- separate termination of a concrete run from theoretical termination for all
  `k`.

## Output behavior

The observed implementation:

- prints a graph on counterexample discovery;
- exits with code 100;
- otherwise prints elapsed microseconds.

Additional bootstrap source observations:

- missing/extra arguments return `1`;
- `atoi` parses the parameter without strict input validation, so malformed
  text is not rejected as a distinct input error;
- `src/main.cpp` does not directly include `<cstdlib>` for `atoi`, although the
  tested GCC environment obtained a declaration transitively;
- output graph order follows an unordered map and is not canonical.

Limitations:

- no canonical graph format;
- no manifest;
- no explicit successful-search certificate;
- no partition summary;
- no checkpoint;
- no artifact hash;
- no machine-readable completion status.

## Build

Observed and locally exercised main build:

- GNU Make;
- `g++`;
- C++17;
- `-Wall -Wextra -O3`.

The bootstrap Windows build used GCC 13.1.0 and GNU Make 4.4.1 through MSYS2
and emitted no compiler warnings. The Makefile assumes Unix `mkdir`/`rm`,
`g++`, and in-source `out/`; integration tests therefore build a temporary
copy. This is a portability observation, not a source defect or correctness
result.

The project-level wrapper must preserve this baseline while adding reproducible
tooling.

## Parallel branch

The inspected `cilk` branch:

- includes a machine-specific absolute header path;
- spawns recursive exploration on graph copies;
- is reported to be faster but memory-intensive;
- reportedly reached out-of-memory for `k = 14`.

It is not an acceptable certifying baseline until:

- dependency discovery is portable;
- ownership and memory are audited;
- scheduling nondeterminism is controlled;
- output and coverage are deterministic or normalized;
- serial equivalence is demonstrated.

## Test and diagnostic branches

The source and paper refer to:

- `tests`: unit tests for major functions;
- `logs`: detailed node/edge mutation logs and visualization;
- `special-graphs`: guided special cases;
- `4-8-cycles`: modified forbidden-cycle target;
- `cilk`: parallel search.

These branches are prior evidence, not automatically part of the preserved
main baseline. All six requested branch names resolved during bootstrap; their
exact SHAs are recorded in `upstream/UPSTREAM_REFS.json`. Only `main` was
imported, and no branch-specific code was merged.

The non-main branch sources and behavior remain unbuilt and unaudited.

## Initial audit verdict

The upstream work provides:

- a mathematically motivated generation method;
- compact source;
- prior successful computations;
- useful branch-specific validation.

It does not yet provide, in the inspected form:

- a project-independent certificate;
- a complete machine-readable execution manifest;
- partition coverage;
- deterministic content-addressed outputs;
- integrated main-branch test and CI infrastructure;
- a portable reproducible parallel environment.

No statement here alleges an actual correctness bug. Successful compilation,
four tiny integration checks, and `k=3`/`k=4` termination are bounded
engineering evidence only; they do not reproduce the published P13 result.
The current status is `REQUIRES INDEPENDENT AUDIT`.
