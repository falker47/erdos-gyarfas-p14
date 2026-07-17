# Known External Results and Upstream Claims

This file records literature and upstream claims.

It does not record project-generated results.
A result listed here is not automatically reproduced or independently verified.

## Classification legend

- `EXTERNAL_THEOREM`:
  a theorem stated in an identifiable mathematical source.
- `EXTERNAL_COMPUTATIONAL_RESULT`:
  a published conclusion whose proof materially relies on computation.
- `EMPIRICAL_OBSERVATION`:
  behavior or scope claimed by the upstream repository.
- Project verification status:
  whether this project has reproduced or independently checked the claim.

## KR-001 — General Erdős–Gyárfás conjecture

- Classification: `CONJECTURE` (external, open)
- Statement:
  every finite graph of minimum degree at least 3 contains a cycle whose length
  is a power of 2.
- Primary historical source:
  Paul Erdős, “Some old and new problems in various branches of
  combinatorics,” Discrete Mathematics 165–166, 227–231, 1997.
- Project verification status:
  not applicable; the general conjecture remains open.

## KR-002 — P8-free C4-or-C8 theorem

- Classification: `EXTERNAL_THEOREM`
- Statement:
  every P8-free graph of minimum degree at least 3 contains C4 or C8.
- Source:
  Y. Gao and S. Shan,
  “Erdős–Gyárfás conjecture for P8-free graphs,”
  Graphs and Combinatorics 38, article 168, 2022;
  arXiv:2109.01277.
- Project verification status:
  not reproduced.

## KR-003 — P10-free C4-or-C8 theorem

- Classification: `EXTERNAL_THEOREM`
- Statement:
  every P10-free graph of minimum degree at least 3 contains C4 or C8.
- Source:
  Z. Hu and C. Shen,
  “The Erdős–Gyárfás conjecture holds for P10-free graphs,”
  Discrete Mathematics 347(12), 114175, 2024;
  arXiv:2308.05675.
- Project verification status:
  not reproduced.

## KR-004 — P13-free power-of-two-cycle result

- Classification: `EXTERNAL_COMPUTATIONAL_RESULT`
- Statement:
  every P13-free graph of minimum degree at least 3 contains a cycle whose
  length is a power of 2.
- Source:
  A. S. Hegde, R. B. Sandeep, P. Shashank,
  “Erdős–Gyárfás conjecture on graphs without long induced paths,”
  arXiv:2410.22842v2, 2025, Theorem 1.
- Reported method:
  a backtracking search based on a minimal-counterexample extension lemma.
- Project verification status:
  not reproduced and not independently certified.

## KR-005 — P12-free C4-or-C8 result

- Classification: `EXTERNAL_COMPUTATIONAL_RESULT`
- Statement:
  every P12-free graph of minimum degree at least 3 contains C4 or C8.
- Source:
  Hegde–Sandeep–Shashank, arXiv:2410.22842v2, Theorem 2.
- Reported implementation:
  a variant forbidding only cycles of lengths 4 and 8.
- Reported repository location:
  branch named `4-8-cycles`.
- Project verification status:
  not reproduced; the branch ref resolved during bootstrap, but its source was
  not imported or audited.

## KR-006 — Upstream search algorithm

- Classification: `EMPIRICAL_OBSERVATION`
- Repository:
  `https://github.com/rbsandeep/Erdos-Gyarfas`
- Inspected main commit:
  `27d9cb22705905fac32314c5e95addf6e11ce283`
- Observed implementation:
  C++17 recursive backtracking over labelled graphs.
- Observed graph representation:
  adjacency sets stored in an unordered map keyed by integer vertex labels.
- Observed predicates:
  recursive simple-cycle search and recursive induced-path search.
- Observed counterexample handling:
  print graph and terminate with exit code 100.
- Project verification status:
  exact source snapshot acquired and bounded local build/smoke checks passed;
  no published mathematical result has been reproduced or certified.

## KR-007 — Reported upstream performance

- Classification: `EXTERNAL_COMPUTATIONAL_RESULT`
- Source:
  Hegde–Sandeep–Shashank, arXiv:2410.22842v2.
- Reported machine:
  2.6 GHz CPU, 72 cores.
- Reported general-search serial times:
  below 0.2 seconds for `k <= 9`, 2 seconds for `k = 10`,
  32 seconds for `k = 11`, 31 minutes 32 seconds for `k = 12`,
  and 11 hours 56 minutes for `k = 13`.
- Reported Cilk time for `k = 13`:
  17 minutes 17 seconds.
- Reported `k = 14` Cilk outcome:
  terminated for out-of-memory.
- Project verification status:
  not reproduced.
- Warning:
  these numbers are environment-specific and are not project benchmarks.

## KR-008 — Upstream correctness testing

- Classification: `EXTERNAL_COMPUTATIONAL_RESULT`
- Reported checks:
  agreement with the P10-free result, manual execution inspection for
  `3 <= k <= 5`, unit tests on a separate branch, and checks involving known
  special cubic graphs.
- Project verification status:
  these reported checks were not reproduced or independently inspected during
  bootstrap; only the named branch refs were resolved.
- Interpretation:
  useful validation evidence, not a project-independent certificate.

## KR-009 — Upstream branches

Observed or source-referenced branches include:

- `main`
- `cilk`
- `tests`
- `logs`
- `special-graphs`
- `4-8-cycles`

Project bootstrap observation (`EMPIRICAL_OBSERVATION`): all six requested refs
resolved on 2026-07-17. Exact SHAs and resolution methods are recorded only in
`upstream/UPSTREAM_REFS.json`. This does not import or validate non-main branch
code.

## KR-010 — License

- Classification: `EMPIRICAL_OBSERVATION`
- Upstream license:
  MIT License, copyright 2024 rbsandeep.
- Consequence:
  source may be preserved and modified subject to retaining the license and
  copyright notice.
- Project verification status:
  bootstrap provenance records the copied license hash; legal interpretation
  is not a project mathematical result.

## Important non-results

After bootstrap, none of the following is known from this project:

- whether the upstream program compiles in the unbuilt pinned container;
- whether any published boundary case reproduces under a recorded research
  environment;
- whether branch behavior agrees;
- whether all subset states are enumerated exactly once;
- whether the implementation matches the paper invariant;
- whether the current output is sufficient for certification;
- whether the P14 search terminates;
- whether the P14 statement is true;
- whether the P13 C4/C8 statement is true.
