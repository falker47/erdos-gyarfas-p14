# Certified Computational Study of the Erdős–Gyárfás Conjecture for P14-Free Graphs

This repository is an independent research workspace for reproducible,
auditable computation concerning the Erdős–Gyárfás conjecture. Its primary
open target is the following statement:

> Every finite simple P14-free graph of minimum degree at least 3 contains a
> simple cycle whose length is a power of 2.

An independently verifiable counterexample is an equally valid outcome. A
separate intermediate target asks whether every finite simple P13-free graph
of minimum degree at least 3 contains C4 or C8.

## Current boundary

This bootstrap repository contains engineering infrastructure and bounded
small-graph checks only. It contains no new theorem, no counterexample, no
exhaustive P13 or P14 search, and no certified mathematical result. Published
P13 and P12 results are external results and have not been independently
certified here.

The preserved source under `third_party/erdos-gyarfas/` is an exact snapshot of
the upstream project. Its presence does not endorse its correctness. The
project's Python verifier is independent of the upstream predicates, but at
bootstrap it validates small graphs and individual candidates only; it does
not certify search coverage.

## Start here

Read, in order:

1. `AGENTS.md` — repository operating contract;
2. `start.md` — project identity and canonical reading order;
3. `CURRENT_STATUS.md` — current task and verification state;
4. `research/PROBLEM_STATEMENT.md` — exact mathematical definitions;
5. `research/VERIFICATION_PROTOCOL.md` — evidence requirements;
6. `upstream/UPSTREAM_PROVENANCE.json` — snapshot identity.

## Fast local workflow

Python 3.11 or newer, CMake, a C++17 compiler, GNU Make, and pytest are
required. Exact commands that have been exercised locally are maintained in
`research/REPRODUCIBILITY.md`; development details are in
`docs/DEVELOPMENT.md`.

Typical commands are:

```text
python -m pip install -e ".[test]"
cmake --preset debug
cmake --build --preset debug
python -m pytest
python tools/validate_schemas.py
```

Heavy workflows are manual-only and currently refuse certifying P13/P14
claims. See `docs/CI.md`.

## Licensing and citation

Project-authored material is licensed under the repository `LICENSE`.
Vendored upstream material retains its own license at
`third_party/erdos-gyarfas/LICENSE`. Citation metadata is in `CITATION.cff`.
