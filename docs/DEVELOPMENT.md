# Development guide

## Supported bootstrap environment

- Python 3.11 or newer;
- a C++17 compiler;
- CMake with preset support;
- Make for the preserved original build route;
- Git for provenance and diff checks.

Install the Python package and test dependencies into an isolated environment:

```text
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

Generated environments and build directories are not source artifacts and
must remain untracked.

## Build and fast checks

The project wrapper builds the unchanged serial upstream source as
`eg-upstream-serial`:

```text
cmake --preset debug
cmake --build --preset debug
python -m pytest
python tools/validate_schemas.py
python tools/verify_upstream_snapshot.py
git diff --check
```

Use the `release` preset for engineering benchmarks. The original Makefile is
tested only in a temporary copy because running it in place would add build
products beneath the read-only snapshot.

These commands are candidate developer commands until their execution is
recorded in the active task dossier. A passing fast suite establishes local or
bounded behavior only; it does not certify a search.

## Tooling contracts

- `tools/hash_artifacts.py` hashes files or creates a deterministic per-file
  tree inventory.
- `tools/make_manifest.py` records caller-supplied run metadata and hashes
  existing artifacts. It does not execute or classify a search automatically,
  bootstrap tooling refuses to emit `COMPUTER_CERTIFIED_RESULT`, and existing
  manifest files are never overwritten.
- `tools/verify_manifest.py` validates an experiment manifest and independently
  recomputes listed artifact hashes.
- `tools/run_benchmark.py` executes one reviewed bounded benchmark case without
  a shell, captures both streams, and validates the result.

The independent graph verifier under `verifier/egverify` does not import
upstream predicate code. Avoid introducing dependencies between generator and
verifier implementations merely to remove duplication.

## Change discipline

Work belongs to one active task dossier and one proposed manual commit. Do not
edit `third_party/erdos-gyarfas/`; place any later workaround outside the
snapshot and preserve a regression demonstrating the original behavior.

Before handoff, inspect all changed paths, run the task-required checks, search
for accidental absolute paths or generated products, run `git diff --check`,
and update the dossier. The user alone stages, commits, and pushes.
