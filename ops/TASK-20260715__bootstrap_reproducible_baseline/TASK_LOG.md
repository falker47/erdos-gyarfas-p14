# TASK-20260715__bootstrap_reproducible_baseline — Log

Append-only task chronology. Times are UTC.

## 2026-07-17T07:27:00Z — Startup audit

- Located the supplied workspace at
  `C:\Users\Falker\Desktop\Code\circle\erdos-gyarfas-p14`.
- Read the operating contract and all available canonical startup documents.
- `git rev-parse`, `git status`, `git log`, and `git remote -v` each reported
  that the directory is not a Git repository; no HEAD or branch exists.
- Enumerated the existing files. They form a task-related design skeleton; no
  source, tests, manifests, artifacts, or active dossier existed.
- Normalized canonical filename case and corrected
  `research/PROBLEM_STATEMEMNT.md` to `research/PROBLEM_STATEMENT.md`.
- Evidence: `EV-001`.

## 2026-07-17T07:30:00Z — Upstream ref resolution

- A sandboxed `git ls-remote` failed because network access was blocked.
- Repeated the same read-only query with approved network access.
- Resolved all requested branch refs exactly; `main` matches the design-time
  observation.
- Snapshot acquisition, tree SHA, file-tree hash, and license hash delegated to
  the upstream/build workstream.
- Evidence: `EV-002`.

## 2026-07-17T07:35:33Z — Local environment audit

- Recorded Python 3.14.3 and Windows PowerShell 5.1.26100.8875.
- `cmake`, `g++`, `clang++`, and `make` were not on `PATH`; WSL is enabled but
  has no installed distribution.
- Found a bare MSYS2 installation at `C:\msys64`; the build workstream is
  checking whether a narrowly scoped package install can provide the required
  toolchain.
- Evidence: `EV-003`.

## 2026-07-17T07:36:00Z — Governance and research baseline

- Added project README, license, citation metadata, ignore rules, dossier and
  decision templates, manifest template, search-model boundary, negative-result
  register, and bibliography.
- Removed the decorative proposed-tree document after canonical paths existed.
- No run result or mathematical conclusion was added.

## Pending append-only entries

Upstream acquisition, build setup, verifier implementation, tests, CI and
schemas, final verification, and handoff will be appended only after their
actions occur.

## 2026-07-17T07:34:12Z — Upstream acquisition

- Cloned upstream read-only into a temporary bare repository, resolved the
  selected commit/tree, and extracted exactly ten regular files without nested
  Git metadata.
- Detected that an initial Git-for-Windows archive inherited
  `core.autocrlf=true`; rejected that CRLF-transformed archive, regenerated
  with conversion disabled, and preserved the failed attempt in provenance.
- Compared every final snapshot file byte-for-byte with its raw selected-tree
  Git blob and recorded per-file plus aggregate inventory SHA-256 values.
- Evidence: `EV-004`.

## 2026-07-17T07:48:00Z — Build setup and bounded upstream checks

- Added the C++17 CMake wrapper, Debug/Release Ninja presets, pinned-base
  Dockerfile, Docker context exclusions, and an integration test that builds
  the original Makefile only in a temporary copy.
- Installed the narrow MSYS2 GCC/CMake/Ninja/Make packages after the initial
  Windows PATH had no native toolchain; preserved package-manager warnings and
  verified the functional versions directly.
- Original Make and both CMake configurations built without compiler warnings.
  Tiny `k=3` and `k=4` invocations terminated with upstream exit `0` under
  explicit timeouts.
- Evidence: `EV-005`.

## 2026-07-17T07:57:00Z — Independent verifier implementation

- Added canonical graph JSON, strict parsing, deterministic serialization,
  independent small-graph predicates, both candidate validators, manifest
  hash checking, and a machine-JSON CLI with exit codes 0–3.
- Added graph, malformed-input, manifest-hash, path/cycle, complete, and
  disconnected fixtures plus unit and CLI integration tests.
- No verifier code imports an upstream graph predicate.
- Evidence: `EV-006`.

## 2026-07-17T08:02:00Z — Schemas, benchmark tooling, and workflows

- Added five Draft 2020-12 schemas, manifest/hash utilities, deterministic
  benchmark case/runner, artifact directories, documentation, fast CI, and a
  manual-only heavy-search refusal scaffold.
- Corrected scaffold fields to the permitted claim vocabulary, preserved null
  unknowns for non-runs, and made invalid workflow inputs emit refusal
  manifests without fabricating normalized values.
- Exercised allowed and refused manifest paths and reviewed the workflow guard;
  no heavy/search executable is reachable from the scaffold.
- Evidence: `EV-007`, `EV-008`, and `EV-009`.

## 2026-07-17T08:10:00Z — Root verification pass

- The first sandboxed full-suite attempt encountered a pre-existing Windows
  temporary-directory ACL and could not access seven pytest temp fixtures;
  this was an environment error, not a test assertion failure.
- Repeated with an approved native-toolchain environment and repository-local
  pytest base directory: all 63 tests passed.
- Re-ran snapshot, schemas, manifest semantics, CMake presets, verifier CLI,
  deterministic serialization, and benchmark-result validation.
- The benchmark harness completed `k=3` with exit `0`; its schema-valid local
  JSON/stdout/stderr were inspected and removed, leaving `.gitkeep` only.
- Evidence: `EV-004` through `EV-009`.

## 2026-07-17T08:24:54Z — Final hygiene and handoff

- Removed all generated build products, pytest caches, bytecode caches, and
  ephemeral benchmark/manifest outputs; retained result/artifact leaves contain
  only their intended `.gitkeep` files.
- Rechecked the required structure, all five schemas, snapshot inventory,
  project-authored whitespace, local absolute paths, generated products, and
  mathematical-claim language.
- Normal Git status/diff checks remain unavailable because the supplied
  directory has no valid Git repository. Used a no-index project-file
  whitespace check and preserved upstream whitespace behind `.gitattributes`;
  exact upstream bytes remain governed by the inventory verifier.
- Recorded the unexplained empty `.git` directory without initializing,
  populating, or deleting it. All task-agent command histories report no Git
  writes.
- Updated durable memory and set the task to `READY_FOR_REVIEW`.
- Evidence: `EV-010`.

## 2026-07-17T08:37:12Z — Final post-document audit

- Inspected the complete 113-file no-index handoff inventory and shortstat.
- Confirmed 54/54 required paths, five valid schemas, 10/10 unchanged upstream
  files, 103 clean non-vendored files, zero generated products, and only
  `.gitkeep` in every retained result/artifact leaf.
- Reconfirmed the conservative 12-entry claims registry and found no
  affirmative project P14 proof/counterexample/certification language.
- Normal `git status` and `git diff --check` again failed only because no valid
  Git repository exists; this limitation remains explicit at handoff.
- Evidence: `EV-010`.
