# Environment Trust Boundary

This document interprets the canonical machine-readable inventory at
`research/ENVIRONMENT_LOCK_INVENTORY.json`. Both artifacts describe the
environment interfaces inspected at project commit
`41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d`. They inventory current state and
open obligations; they do not implement an environment lock, execute a
research run, or change any mathematical evidence level.

## Terms

**Locked** means that the outcome-relevant selector is fixed by repository
bytes at the inspected commit and, for acquired content, names a cryptographic
content identity. A version family, package name, executable path, image label,
or service name alone is not locked. The Action source commits and Docker image
index digest are locked selectors, while their runners, runtimes, platform
selection, and later acquisitions are separate records
(`ENV-006-GHA-ACTION-CHECKOUT`, `ENV-007-GHA-ACTION-SETUP-PYTHON`,
`ENV-008-GHA-ACTION-UPLOAD-ARTIFACT`, `ENV-033-DOCKER-BASE-INDEX`).

**Captured** means that a run records the effective observed identity and value
with enough command, version, platform, byte-hash, timestamp, and source
context to audit it. Capture reports what ran; it does not make the component
repository-controlled or guarantee that it can be reacquired. Local tools and
hosted preinstalled tools are capture obligations
(`ENV-013-GHA-NATIVE-GCC`, `ENV-014-GHA-NATIVE-CLANG`,
`ENV-051-LOCAL-PYTHON-RUNTIME`, `ENV-052-LOCAL-MSYS2-CMAKE`,
`ENV-053-LOCAL-MSYS2-GCC`, `ENV-054-LOCAL-MSYS2-NINJA`,
`ENV-055-LOCAL-MSYS2-MAKE`).

**Externally trusted** means that an outcome depends on a service or host
boundary whose implementation and active bytes cannot be pinned by this
repository. Its role must be named, minimized, and explicitly accepted for the
intended evidence level. The GitHub control plane, GitHub-supplied JavaScript
runtime, Python package services, and Ubuntu archive are such boundaries
(`ENV-005-GHA-CONTROL-PLANE`, `ENV-009-GHA-ACTION-NODE20-RUNTIME`,
`ENV-030-PYPI-SERVICE`, `ENV-038-DOCKER-APT-SERVICE`).

`VERSION_PIN_ONLY` fixes a version expression but not a distribution artifact.
`MUTABLE_RESOLUTION` permits a repository or service to choose a value at run
or build time. `CAPTURE_REQUIRED` identifies a value that can be observed but
is not presently recorded with sufficient identity. These conditions remain
open under `RFU-ENV-001`.

## Boundary conclusions

Repository-controlled bytes include the workflow text, exact Action commit
selectors, Dockerfile, base-image index digest, Python direct dependency
versions, CMake configuration, tests, and preserved upstream snapshot. GitHub
still controls runner assignment, runner images, Action orchestration, the
Node runtime, caches, and artifact transport
(`ENV-001-GHA-RUNNER-WHITESPACE`, `ENV-002-GHA-RUNNER-PYTHON`,
`ENV-003-GHA-RUNNER-CPP`, `ENV-004-GHA-RUNNER-HEAVY`,
`ENV-005-GHA-CONTROL-PLANE`, `ENV-009-GHA-ACTION-NODE20-RUNTIME`). An Action
commit pin therefore freezes selected Action source bytes, not the hosted
runner or the runtime that executes those bytes.

The Docker `FROM` digest fixes a multi-platform index, but the implicit build
platform selects a child manifest, `apt-get update` reads mutable repository
state, and eight unversioned packages resolve later. The base digest therefore
does not freeze the selected architecture, APT indexes, package archives,
compiler, standard library, CMake, Ninja, Git, Python, pip, or virtual
environment (`ENV-034-DOCKER-PLATFORM-CHILD`, `ENV-037-DOCKER-APT-INDEX`,
`ENV-039-DOCKER-APT-BUILD-ESSENTIAL`,
`ENV-040-DOCKER-APT-CA-CERTIFICATES`, `ENV-041-DOCKER-APT-CMAKE`,
`ENV-042-DOCKER-APT-GIT`, `ENV-043-DOCKER-APT-NINJA`,
`ENV-044-DOCKER-APT-PYTHON3`, `ENV-045-DOCKER-APT-PYTHON3-PIP`,
`ENV-046-DOCKER-APT-PYTHON3-VENV`, `ENV-047-DOCKER-NATIVE-TOOLCHAIN`,
`ENV-048-DOCKER-PYTHON-RUNTIME`). The builder and local context also affect
the resulting image (`ENV-035-DOCKER-ENGINE`,
`ENV-036-DOCKER-BUILD-CONTEXT`, `ENV-050-DOCKER-EXECUTION-ENVIRONMENT`).

Direct `==` Python requirements constrain distribution versions but do not
hash-lock wheels, source distributions, transitive packages, build outputs,
pip, indexes, or caches (`ENV-023-PYTHON-BUILD-BACKEND`,
`ENV-024-PYTHON-DIRECT-SETUPTOOLS`, `ENV-025-PYTHON-DIRECT-JSONSCHEMA`,
`ENV-026-PYTHON-DIRECT-PYTEST`, `ENV-027-PYTHON-PIP-INSTALLER`,
`ENV-028-PYTHON-TRANSITIVE-DISTRIBUTIONS`,
`ENV-029-PYTHON-DISTRIBUTION-ARTIFACTS`). Likewise, setup-python `3.11` and
`3.12` name interpreter families rather than exact distribution bytes
(`ENV-010-GHA-PYTHON-311-SELECTOR`,
`ENV-011-GHA-PYTHON-312-SELECTOR`,
`ENV-012-GHA-PYTHON-DISTRIBUTIONS`).

Native source-level choices are committed, but a CMake lower bound and tool
names do not identify the active binaries (`ENV-015-GHA-NATIVE-CMAKE`,
`ENV-016-GHA-NATIVE-NINJA`, `ENV-017-GHA-NATIVE-MAKE`,
`ENV-018-GHA-NATIVE-GIT`, `ENV-019-GHA-SHELL-UTILITIES`,
`ENV-031-CMAKE-COMPATIBILITY`, `ENV-032-NATIVE-BUILD-CONFIGURATION`). CPU,
operating-system, filesystem, resource, PATH, locale, timezone, Git
configuration, and environment-variable inputs also remain explicit capture
boundaries (`ENV-020-GHA-PLATFORM-RESOURCES`,
`ENV-021-GHA-EXECUTION-ENVIRONMENT`, `ENV-056-LOCAL-MSYS2-RUNTIME-UTILITIES`,
`ENV-057-LOCAL-GIT-CONFIGURATION`, `ENV-058-LOCAL-PLATFORM-RESOURCES`).

The accepted local MSYS2 paths are tool-discovery selectors, not artifact
pins. Their documented versions do not supply accepted compiler target,
standard-library/runtime-DLL, package database, installer, mirror, dependency,
or artifact-hash provenance. The project-wide Python compatibility lower bound
has the same version-versus-artifact distinction
(`ENV-022-PYTHON-COMPATIBILITY`).

## Evidence levels

For V1 engineering checks, sufficient environment evidence is the exact
project revision, command, bounded test domain, exit status, relevant output,
and anomalies, plus enough observed interpreter/tool/platform detail to make
the check understandable. A complete immutable environment is not required to
say that the specified tests passed in the observed environment. V1 still
cannot establish search completeness or any broader mathematical conclusion.
This is why unresolved records have `V1=false` while retaining stronger
blockers.

Before a V3 upstream reproduction, the project additionally needs an exact
upstream and project revision, exact interpreter and native toolchain,
standard-library/runtime identity, platform/architecture, dependency lock and
artifact hashes, package/index resolution, effective environment variables,
commands, outputs, and hashes. Any unavoidable service dependency must be
named and reviewed. The current `V3=true` records show that this environment
evidence is not yet complete.

V4 certification has the stronger obligation to use an accepted trust
boundary covering generator, independent verifier, complete manifests,
executable and input hashes, deterministic configuration, platform/resources,
all dependency artifacts, and every external service or capture-only
assumption. The current `V4=true` records remain blockers to treating this
inventory as that boundary; inventorying them does not resolve them.

A tiny exploratory execution before full locking may be preserved only as an
`EMPIRICAL_OBSERVATION` when its exact revision, command, available environment
facts, outputs, hashes, exit state, and limitations are recorded. It cannot be
presented as V3 or V4 evidence and has no mathematical implication.

The `required_next_action` fields below specify evidence gaps, not an accepted
implementation design. A later atomic task must choose and review any concrete
locking, capture, attestation, or execution mechanism.

## Inventory interpretation

Each heading is the stable machine ID from the JSON inventory. The JSON entry
is canonical for exact source locations, selector text, evidence, external
dependencies, and required action.

### ENV-001-GHA-RUNNER-WHITESPACE

The whitespace job uses the mutable `ubuntu-24.04` runner label.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `NOT_REPOSITORY_CONTROLLED`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-002-GHA-RUNNER-PYTHON

The Python matrix uses the mutable `ubuntu-24.04` runner label.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `NOT_REPOSITORY_CONTROLLED`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-003-GHA-RUNNER-CPP

The native compiler matrix uses the mutable `ubuntu-24.04` runner label.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `NOT_REPOSITORY_CONTROLLED`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-004-GHA-RUNNER-HEAVY

The heavy-workflow scaffold uses the mutable `ubuntu-24.04` runner label.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `NOT_REPOSITORY_CONTROLLED`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-005-GHA-CONTROL-PLANE

GitHub supplies orchestration, contexts, cache, artifact, and runner services.

- Classification: `EXTERNAL_SERVICE_TRUST`
- Repository lockability: `NOT_REPOSITORY_CONTROLLED`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-006-GHA-ACTION-CHECKOUT

The checkout Action source is pinned to the accepted full commit.

- Classification: `IMMUTABLE_PIN`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=false`, `V4=false`

### ENV-007-GHA-ACTION-SETUP-PYTHON

The setup-python Action source is pinned to the accepted full commit.

- Classification: `IMMUTABLE_PIN`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=false`, `V4=false`

### ENV-008-GHA-ACTION-UPLOAD-ARTIFACT

The upload-artifact Action source is pinned to the accepted full commit.

- Classification: `IMMUTABLE_PIN`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=false`, `V4=false`

### ENV-009-GHA-ACTION-NODE20-RUNTIME

Pinned metadata requests node20, while GitHub supplies the runtime bytes.

- Classification: `EXTERNAL_SERVICE_TRUST`
- Repository lockability: `NOT_REPOSITORY_CONTROLLED`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-010-GHA-PYTHON-311-SELECTOR

The `3.11` input is a major/minor selector, not a distribution hash.

- Classification: `VERSION_PIN_ONLY`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-011-GHA-PYTHON-312-SELECTOR

The `3.12` input is a major/minor selector, not a distribution hash.

- Classification: `VERSION_PIN_ONLY`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-012-GHA-PYTHON-DISTRIBUTIONS

Interpreter patch/build, architecture, download, and tool-cache state resolve dynamically.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-013-GHA-NATIVE-GCC

Hosted GCC, target, standard library, and linker identities require capture.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-014-GHA-NATIVE-CLANG

Hosted Clang, target, standard library, and linker identities require capture.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-015-GHA-NATIVE-CMAKE

The hosted CMake executable is selected by an unversioned PATH name.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-016-GHA-NATIVE-NINJA

The hosted Ninja executable is selected by generator/tool name.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-017-GHA-NATIVE-MAKE

The integration test resolves hosted Make from PATH.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-018-GHA-NATIVE-GIT

Hosted Git and its effective configuration are not artifact-locked.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-019-GHA-SHELL-UTILITIES

Hosted bash and shell/core utilities are unversioned runner inputs.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-020-GHA-PLATFORM-RESOURCES

Runner architecture, kernel, libc, CPU, memory, filesystem, and locale require capture.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `NOT_REPOSITORY_CONTROLLED`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-021-GHA-EXECUTION-ENVIRONMENT

Explicit workflow variables coexist with externally supplied contexts and inherited environment.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-022-PYTHON-COMPATIBILITY

The `>=3.11` compatibility bound does not select one interpreter distribution.

- Classification: `VERSION_PIN_ONLY`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-023-PYTHON-BUILD-BACKEND

The backend name and direct version do not hash-lock backend artifacts.

- Classification: `VERSION_PIN_ONLY`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-024-PYTHON-DIRECT-SETUPTOOLS

Setuptools is version-pinned without a wheel or source-distribution hash.

- Classification: `VERSION_PIN_ONLY`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-025-PYTHON-DIRECT-JSONSCHEMA

jsonschema is version-pinned without a wheel or source-distribution hash.

- Classification: `VERSION_PIN_ONLY`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-026-PYTHON-DIRECT-PYTEST

pytest is version-pinned without a wheel or source-distribution hash.

- Classification: `VERSION_PIN_ONLY`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-027-PYTHON-PIP-INSTALLER

Each route uses the selected interpreter's unpinned pip implementation.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-028-PYTHON-TRANSITIVE-DISTRIBUTIONS

No exact transitive dependency resolution is repository-locked.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-029-PYTHON-DISTRIBUTION-ARTIFACTS

Direct and transitive wheel/source artifacts and cache contents lack hashes.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-030-PYPI-SERVICE

Package index and artifact delivery remain external service dependencies.

- Classification: `EXTERNAL_SERVICE_TRUST`
- Repository lockability: `NOT_REPOSITORY_CONTROLLED`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-031-CMAKE-COMPATIBILITY

CMake 3.25 is a minimum version, not an exact executable identity.

- Classification: `VERSION_PIN_ONLY`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-032-NATIVE-BUILD-CONFIGURATION

The inspected commit fixes language mode, generator, build types, and source-level flags.

- Classification: `IMMUTABLE_PIN`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=false`, `V4=false`

### ENV-033-DOCKER-BASE-INDEX

The Ubuntu multi-platform image index is selected by full digest.

- Classification: `IMMUTABLE_PIN`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=false`, `V4=false`

### ENV-034-DOCKER-PLATFORM-CHILD

The builder platform implicitly selects an unrecorded child manifest.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-035-DOCKER-ENGINE

Docker/BuildKit/frontend/runtime identity is unavailable until a recorded build.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-036-DOCKER-BUILD-CONTEXT

`COPY .` can include any nonignored dirty or untracked context bytes.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-037-DOCKER-APT-INDEX

APT source/index state is resolved at image-build time without a snapshot identity.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-038-DOCKER-APT-SERVICE

Ubuntu archive, mirror, and signing infrastructure are externally trusted.

- Classification: `EXTERNAL_SERVICE_TRUST`
- Repository lockability: `NOT_REPOSITORY_CONTROLLED`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-039-DOCKER-APT-BUILD-ESSENTIAL

`build-essential` is an unversioned meta-package selector.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-040-DOCKER-APT-CA-CERTIFICATES

`ca-certificates` is an unversioned package selector.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-041-DOCKER-APT-CMAKE

`cmake` is an unversioned package selector.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-042-DOCKER-APT-GIT

`git` is an unversioned package selector.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-043-DOCKER-APT-NINJA

`ninja-build` is an unversioned package selector.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-044-DOCKER-APT-PYTHON3

`python3` is an unversioned interpreter package selector.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-045-DOCKER-APT-PYTHON3-PIP

`python3-pip` is an unversioned installer package selector.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-046-DOCKER-APT-PYTHON3-VENV

`python3-venv` is an unversioned environment package selector.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-047-DOCKER-NATIVE-TOOLCHAIN

Compiler, standard libraries, linker, and build-tool identities require a resolved package capture.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-048-DOCKER-PYTHON-RUNTIME

Container Python/pip/venv build, ABI, and executable identities require capture.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-049-DOCKER-PIP-INSTALL-ROUTE

The Docker editable install performs live unhashed dependency resolution.

- Classification: `MUTABLE_RESOLUTION`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-050-DOCKER-EXECUTION-ENVIRONMENT

Build arguments, inherited PATH, shell, user, locale, and process variables need an effective capture.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `REPOSITORY_PINNABLE`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-051-LOCAL-PYTHON-RUNTIME

The local Python version observation lacks distribution, executable, package, and artifact provenance.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-052-LOCAL-MSYS2-CMAKE

The accepted CMake path/version lacks package, installer, dependency, and artifact-hash provenance.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-053-LOCAL-MSYS2-GCC

The accepted GCC path/version lacks target, standard-library/runtime, package, and artifact provenance.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-054-LOCAL-MSYS2-NINJA

The accepted Ninja path/version lacks package, dependency, and artifact provenance.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-055-LOCAL-MSYS2-MAKE

The accepted Make path/version lacks shell/coreutils, package, and artifact provenance.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-056-LOCAL-MSYS2-RUNTIME-UTILITIES

Inherited PATH, runtime DLLs, bash/coreutils, locale, and loader choices remain uncaptured.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-057-LOCAL-GIT-CONFIGURATION

Local Git binary, configuration, attributes, and filesystem inputs remain capture-only.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`

### ENV-058-LOCAL-PLATFORM-RESOURCES

Local OS, architecture, CPU, ABI, resources, filesystem, locale, timezone, and environment remain capture-only.

- Classification: `CAPTURE_REQUIRED`
- Repository lockability: `CAPTURE_ONLY`
- Evidence blockers: `V1=false`, `V3=true`, `V4=true`
