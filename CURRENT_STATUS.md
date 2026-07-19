# CURRENT_STATUS - erdos-gyarfas-p14

Last updated: 2026-07-19 UTC

## Current state

- Current phase: environment trust-boundary candidate ready for cumulative
  review before any upstream research execution.
- Active task: `TASK-20260719__define_environment_trust_boundary`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d`.
- Task-start HEAD:
  `41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d`.
- Last reviewed candidate HEAD:
  `41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d`.
- Last review verdict: `ACCEPT WITH FOLLOW-UP`.
- Accepted task: `TASK-20260719__align_action_pin_documentation`.
- Accepted review occurrence: `2026-07-19T08:52:08Z`.
- Next review: the cumulative range from the accepted baseline through this
  environment-boundary candidate; the candidate SHA is intentionally resolved
  from Git by the reviewer.

The documentation-alignment task is accepted at the exact baseline above.
`RFU-DOC-001` is resolved and no longer pending. The current task only
inventories and interprets existing environment selectors and trust
dependencies. It changes no workflow, Docker, dependency, build, verifier,
generator, or search behavior.

## Canonical environment boundary candidate

`research/ENVIRONMENT_LOCK_INVENTORY.json` is the canonical machine-readable
inventory tied to the task-start commit. Its 58 stable IDs distinguish:

- four mutable `ubuntu-24.04` runner occurrences and the external GitHub
  control-plane/runtime boundary;
- three immutable Action source commit identities, separately from the
  GitHub-supplied node20 runtime;
- Python 3.11/3.12 selectors, interpreter distributions, pip, direct versions,
  transitive distributions, wheel/sdist artifacts, caches, and package
  services;
- the Docker image-index digest, implicit platform child, builder and context,
  APT index/service, all eight unversioned packages, native toolchain, Python,
  pip route, and execution environment;
- hosted and container compilers, standard libraries, CMake, Ninja, Make, Git,
  shells and utilities;
- accepted local MSYS2 paths, plus their missing package, installer,
  dependency-DLL, runtime, artifact-hash, PATH, platform, and resource
  provenance.

`schemas/environment-lock-inventory.schema.json` constrains the inventory
shape and closed vocabularies. The deliberately simple regression test at
`tests/unit/test_environment_lock_inventory.py` compares the inventory against
the actual workflows, Action-pin validator subprocess output, Dockerfile, and
`pyproject.toml`, and checks deterministic JSON and Markdown agreement.

`research/ENVIRONMENT_TRUST_BOUNDARY.md` defines locked, captured, and
externally trusted state; explains the Action/runner, Docker/APT, and
Python-version/artifact separations; and states the distinct V1, V3, V4, and
exploratory-observation boundaries.

No implementation-level environment lock is accepted. Inventorying a gap does
not resolve it. Hosted services and runners, interpreter and package artifacts,
container platform/APT/toolchain state, local MSYS2 provenance, platform
resources, and execution-affecting environment variables remain open under
`RFU-ENV-001`.

## Accepted engineering baseline

- The exact upstream `main` snapshot and license remain byte-preserved under
  recorded commit, tree, and SHA-256 provenance.
- The independent Python verifier, strict schemas, bounded fixtures, unit and
  differential tests, native build wrappers, fast CI, and non-executing heavy
  scaffold remain the accepted bootstrap engineering interface.
- All eleven external Action occurrences remain pinned to the accepted
  checkout `v4.3.1`, setup-python `v5.6.0`, and upload-artifact `v4.6.2`
  commits.

These are bounded engineering facts only. They do not establish an upstream
reproduction, exhaustive computation, certificate, theorem, or proof.

## Follow-up state

- `RFU-DOC-001`: resolved by accepted commit
  `41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d` and no longer pending.
- `RFU-ENV-001`: `OPEN`; its canonical scope is the unresolved locking,
  capture, and external-service trust obligations catalogued in
  `research/ENVIRONMENT_LOCK_INVENTORY.json` and interpreted by
  `research/ENVIRONMENT_TRUST_BOUNDARY.md`.

## Current mathematical claim boundary

No P13 or P14 research run has started. This task creates no mathematical
result, theorem, counterexample, exhaustive search, computer-certified result,
reproduced upstream result, certifying pruning rule, or accepted search
certificate. `research/CLAIMS_REGISTRY.yaml` and
`research/PRUNING_REGISTRY.md` remain byte-identical. All mathematical target
statuses remain unchanged.

## Remaining scientific and engineering obligations

- Review the current environment-boundary candidate against the accepted
  baseline; the candidate SHA is intentionally resolved from Git by the
  reviewer.
- Resolve or explicitly accept every relevant environment lock, capture, and
  external-service dependency before using that interface for V3 or V4
  evidence.
- Audit the upstream generation invariant and every pruning proof separately.
- Define and prove search partition coverage, certificate semantics, replay,
  and verifier independence before any certifying execution.
- `RS-001` remains `NOT STARTED`.
