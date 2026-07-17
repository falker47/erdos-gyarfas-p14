# Canonical Problem Statement

## 1. Graph conventions

Unless explicitly stated otherwise:

- graphs are finite;
- graphs are simple;
- graphs are undirected;
- `V(G)` is the vertex set;
- `E(G)` is the edge set;
- `delta(G)` is the minimum degree;
- `P_t` is the path on `t` vertices;
- `C_t` is the cycle on `t` vertices;
- a cycle is simple but need not be induced.

A graph `G` is `P_t`-free when no induced subgraph of `G` is isomorphic to
`P_t`.

A power-of-two cycle is a cycle `C_(2^j)` for an integer `j >= 2`. In a simple
graph the relevant lengths begin with 4, 8, 16, 32, and so on.

## 2. General Erdős–Gyárfás conjecture

### Claim ID: EG-GENERAL

Every finite simple graph `G` satisfying

`delta(G) >= 3`

contains a cycle whose length is a power of 2.

Classification in this project: `CONJECTURE` (external and open).

This project does not attempt the unrestricted conjecture directly.

## 3. Primary target

### Claim ID: EG-P14

For every finite simple graph `G`,

if

- `delta(G) >= 3`, and
- `G` is `P14`-free,

then `G` contains a cycle whose length is a power of 2.

Classification at bootstrap: `OPEN_QUESTION`.

A valid proof may combine exact mathematics with a certified finite or
well-founded search, provided every computational step satisfies
`research/VERIFICATION_PROTOCOL.md`.

## 4. Counterexample target

### Claim ID: CE-P14

A counterexample to `EG-P14` is a finite simple graph `G` such that:

1. `delta(G) >= 3`;
2. `G` has no induced `P14`;
3. `G` has no cycle of length `2^j` for any integer `j >= 2` with
   `2^j <= |V(G)|`.

A claimed counterexample is accepted only when:

- serialized in a canonical documented graph format;
- assigned a SHA-256 hash;
- independently checked for simplicity;
- independently checked for minimum degree;
- independently checked for induced-P14 absence;
- independently checked for absence of every relevant power-of-two cycle;
- manually inspectable;
- accompanied by environment and command metadata.

Finding a graph candidate is not sufficient until independent verification
passes.

Classification at bootstrap: `OPEN_QUESTION`; no candidate is recorded.

## 5. Intermediate stronger target

### Claim ID: EG-P13-C4C8

For every finite simple graph `G`,

if

- `delta(G) >= 3`, and
- `G` is `P13`-free,

then `G` contains `C4` or `C8`.

Classification at bootstrap: `OPEN_QUESTION`.

This is stronger than the power-of-two-cycle conclusion for `P13`-free graphs.

The published computer-assisted result currently establishes the analogous
statement for `P12`-free graphs. That result remains external until reproduced
or independently verified here.

## 6. Search formulations

### 6.1 Full self-contained route to EG-P14

A self-contained implementation of the upstream minimal-counterexample method
would establish `EG-P14` by completing and certifying the required searches for
every relevant `k` from 3 through 14.

### 6.2 Route using the external P13-free theorem

One may instead combine:

- an accepted proof of the published P13-free result; and
- a certified search handling the new `k = 14` layer.

This route is logically valid only when the published P13-free conclusion is
cited as an external computational result and its role is explicit.

### 6.3 Internal reproduction route

The preferred project route is to reproduce the prior `k <= 13` computations
before treating `k = 14`, because reproduction:

- validates the build;
- validates instrumentation;
- supplies regression baselines;
- reveals resource scaling;
- tests certificate machinery on known cases.

Reproduction does not by itself constitute independent certification.

## 7. Search completeness question

The upstream algorithm is based on the following conceptual invariant:

- a current labelled graph is compatible with an induced prefix of a minimal
  counterexample;
- all possible missing neighbors of the newest vertex are enumerated;
- if the current graph is still `P_k`-free and has a low-degree vertex, a new
  vertex is attached to a canonical low-degree anchor;
- a minimal-counterexample argument shows that some branch follows any actual
  minimal counterexample.

The project must formalize this invariant independently.

The following are separate obligations:

1. mathematical correctness of the invariant;
2. correctness of the implementation;
3. completeness of subset enumeration;
4. soundness of pruning;
5. completion of every partition;
6. correctness of the resulting certificate;
7. correctness of the independent verifier.

None may be inferred solely from the others.

## 8. Cycle predicates

For the primary target, forbidden cycles during a counterexample search are all
simple cycles of lengths:

`4, 8, 16, ..., 2^floor(log2(|V(G)|))`.

For the intermediate `C4/C8` target, only `C4` and `C8` are forbidden.

These are distinct search modes and must not share ambiguous configuration.

## 9. Non-goals of the bootstrap phase

The bootstrap phase does not:

- prove `EG-P14`;
- disprove `EG-P14`;
- reproduce `k = 13`;
- run `k = 14`;
- prove `EG-P13-C4C8`;
- certify upstream;
- select an optimal parallelization;
- establish practical termination;
- claim that upstream pruning is complete;
- produce benchmark comparisons unless actual measurements are made.

## 10. Result wording

Permitted examples:

- “The upstream executable was reproduced for `k = 5` under environment X.”
- “The independent verifier confirms that graph H has minimum degree 3.”
- “All partitions listed in manifest M completed and verifier V accepted the
  coverage certificate.”
- “No counterexample was found in the explicitly described heuristic search.”

Forbidden examples unless fully justified:

- “The conjecture is proved because the program terminated.”
- “The search is exhaustive” without a certificate.
- “The pruning is safe” because bounded tests passed.
- “The upstream result is certified” because the same code reproduced it.
