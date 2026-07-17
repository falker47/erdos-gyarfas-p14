# Bootstrap trust boundary

## In scope

The bootstrap engineering checks trust:

- the checked-out project files and recorded upstream provenance;
- the operating system, filesystem, Python interpreter, C++ compiler, CMake,
  Make, Git, and installed dependencies used for a recorded run;
- SHA-256 as implemented by the runtime;
- JSON parsing and the `jsonschema` implementation for structural validation;
- the Python verifier source for candidate-level small-graph predicates;
- the test-local brute-force oracles only for their documented bounded domain;
- the human reviewer who compares manifests, commands, code, and claims.

Exact versions and environment details belong in each material run manifest.
Ordinary CI images and major-version-pinned actions are not immutable research
environments.

## Explicitly outside the trusted conclusion

The following are not accepted as certifying components during bootstrap:

- upstream search correctness or completeness;
- any upstream pruning rule;
- the informal minimal-counterexample invariant;
- output or exit-code semantics as mathematical evidence;
- partition coverage or disjointness;
- the provisional certificate schema;
- a generator validating its own output;
- passing tests outside their stated fixture or bounded enumeration domain;
- timing or benchmark results;
- GitHub Actions success by itself.

The preserved upstream program is a generator/reference implementation. Its
source remains byte-identical to the acquired snapshot, but provenance does
not imply correctness.

## Separation

The independent verifier must not call upstream graph-predicate functions.
Critical parsing, degree, induced-path, cycle, and counterexample checks are
implemented independently. Test-local oracles deliberately favor simple
enumeration over shared production logic.

Manifest generation and manifest verification are separate commands. The
bootstrap verifier recomputes artifact hashes, but full certificate replay and
partition coverage checking do not yet exist. JSON Schema is a syntax layer,
not an independent semantic verifier.

## Claim boundary

At bootstrap, successful builds, tiny executions, unit tests, and bounded
differential agreement support only engineering observations or explicitly
bounded verification. There is no new theorem, counterexample, exhaustive
search, computer-certified result, or independent reproduction.
