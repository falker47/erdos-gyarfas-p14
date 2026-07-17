# TASK-20260715__bootstrap_reproducible_baseline — Status

- Mode: STRICT
- Objective: create one reviewable, reproducible repository baseline for later
  certified-computation research without making a mathematical claim.
- Baseline HEAD: `NO_GIT_REPOSITORY`
- Working branch: none
- Final status: `READY_FOR_REVIEW`

## Scope completed

- durable repository memory, governance, templates, and this dossier;
- exact read-only upstream `main` snapshot, provenance, refs, and license;
- preserved Make build plus project CMake and container interfaces;
- independent small-graph Python verifier and machine-JSON CLI;
- bounded unit, differential, integration, determinism, and schema tests;
- manifest, benchmark, partition, and provisional certificate data formats;
- fast CI and a manual safe heavy-workflow scaffold;
- explicit claim, trust, pruning, and verification boundaries.

## Out of scope preserved

No P13/P14 search, upstream optimization or semantic fix, invariant proof,
certifying pruning, partition proof, certificate acceptance, publication,
upstream issue/PR, Git initialization, commit, or push occurred.

## Actual upstream identity

- Repository: `https://github.com/rbsandeep/Erdos-Gyarfas`
- Requested ref: `main`
- Resolved commit: `27d9cb22705905fac32314c5e95addf6e11ce283`
- Resolved tree: `35707222c62e2bc14b90f385f593a66799405eba`
- Design-time observation: the same `main` commit
- Canonical snapshot inventory SHA-256:
  `6fcd2f09dae6618b968a3981748c5cc16f8321478cee6f6b831071463ec7756c`
- Additional refs resolved: `cilk`, `tests`, `logs`, `special-graphs`, and
  `4-8-cycles`; exact SHAs are in `upstream/UPSTREAM_REFS.json`.
- Unresolved requested refs: none.

## Files created or normalized

- Governance and memory: `README.md`, `LICENSE`, `CITATION.cff`, `.gitignore`,
  `.gitattributes`, `start.md`, `PROJECT_KNOWLEDGE.md`, `CURRENT_STATUS.md`,
  `RESEARCH_LOG.md`, canonical research files, and `_TEMPLATES/`.
- Upstream: `third_party/erdos-gyarfas/`, `upstream/README.md`, both upstream
  JSON records, and `upstream/patches/README.md`.
- Build: `CMakeLists.txt`, `CMakePresets.json`, `Dockerfile`, `.dockerignore`,
  `pyproject.toml`, and build/reproducibility documentation.
- Verifier: `verifier/egverify/` and `verifier/README.md`.
- Tests: unit, differential, verifier-CLI, upstream-build integration tests,
  and documented fixtures under `tests/`.
- Schemas and tools: five schemas plus manifest, hash, snapshot, schema, and
  benchmark utilities under `schemas/` and `tools/`.
- CI and benchmarks: both workflow files, benchmark case/runner documentation,
  and empty retained artifact/result leaves containing only `.gitkeep`.
- Dossier: this status, append-only task log, and evidence register.

## Verification completed

- Exact upstream ref resolution and raw-blob snapshot audit: PASS.
- Original Make build; CMake Debug and Release configure/build: PASS.
- Tiny upstream `k=3` and `k=4` timeout-bounded smoke tests: PASS.
- Unit/differential/verifier-CLI/upstream integration suite: PASS, 63 tests.
- Differential domain: PASS, all 1,100 labelled simple graphs on 0–5 vertices.
- Five schemas, manifest template, valid/invalid artifact hashes: PASS.
- Deterministic verifier serialization and stable CLI exit behavior: PASS.
- Actual ephemeral benchmark execution and benchmark schema: PASS; outputs
  reviewed and removed rather than retained as evidence.
- Workflow YAML/embedded shell static checks and heavy guard review: PASS.
- Required structure, no generated products, no retained run artifacts,
  absolute-path review, and mathematical-claim audit: PASS.
- Upstream inventory after all testing and cleanup: PASS, 10/10 files.
- Project-file no-index whitespace check: PASS. Normal `git diff --check` is
  unavailable because the supplied directory has no valid Git repository.
- Complete no-index handoff inventory/stat review: PASS, 113 files.

## Claim impact

- `UPSTREAM-MAIN-RESOLVED`: `EMPIRICAL_OBSERVATION`.
- `UPSTREAM-SNAPSHOT-PRESERVED`: `EMPIRICAL_OBSERVATION`.
- `VERIFIER-SMALL-GRAPH-AGREEMENT`: `VERIFIED_BOUNDED_COMPUTATION` on the
  documented 1,100-graph domain only.
- `BOOTSTRAP-BASELINE`: `VERIFIED_BOUNDED_COMPUTATION` for engineering checks
  only.
- No mathematical target was upgraded.

## Limitations and blockers

There is no blocker to file-level review. Before a manual commit, the user must
initialize or restore Git metadata and perform the normal status/diff review;
Codex was prohibited from doing so. An empty `.git` directory appeared during
execution but contains no metadata, is not commit-visible, and has unresolved
origin.

Docker was unavailable, GitHub Actions did not execute, and `actionlint` was
unavailable. Local Python was 3.14.3 rather than the configured CI 3.11/3.12
matrix. MSYS2 package installation reported stale-mirror and certificate
post-install warnings, although direct tool versions and all native checks
passed. Search completeness, upstream correctness, certifying pruning,
partition coverage, and certificate semantics remain unverified.

## Next atomic action

The user reviews this one bootstrap change set, initializes or restores Git,
runs the documented checks and normal Git diff checks, and manually commits it
if accepted. No subsequent research task is started in this dossier.
