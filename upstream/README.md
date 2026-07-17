# Preserved Upstream Baseline

This directory records provenance for an exact, read-only snapshot of
[`rbsandeep/Erdos-Gyarfas`](https://github.com/rbsandeep/Erdos-Gyarfas).
The snapshot itself is under `third_party/erdos-gyarfas/`.

## Selected source

- Requested ref: `refs/heads/main`
- Resolved commit: `27d9cb22705905fac32314c5e95addf6e11ce283`
- Git tree: `35707222c62e2bc14b90f385f593a66799405eba`
- Design-time observed commit: `27d9cb22705905fac32314c5e95addf6e11ce283`
- License: MIT, preserved as `third_party/erdos-gyarfas/LICENSE`

The independently resolved bootstrap commit matches the design-time
observation. `UPSTREAM_REFS.json` records all six requested branch refs; no
branch was merged into the main snapshot.

## Acquisition

The source was acquired without placing nested Git metadata in the project:

```text
git ls-remote --heads https://github.com/rbsandeep/Erdos-Gyarfas.git main cilk tests logs special-graphs 4-8-cycles
git clone --bare https://github.com/rbsandeep/Erdos-Gyarfas.git C:\tmp\eg-upstream-bootstrap-27d9cb2.git
git -C C:\tmp\eg-upstream-bootstrap-27d9cb2.git rev-parse "27d9cb22705905fac32314c5e95addf6e11ce283^{tree}"
git -c core.autocrlf=false -C C:\tmp\eg-upstream-bootstrap-27d9cb2.git archive --format=tar --output=C:\tmp\eg-upstream-bootstrap-27d9cb2-raw.tar 27d9cb22705905fac32314c5e95addf6e11ce283
tar -xf C:\tmp\eg-upstream-bootstrap-27d9cb2-raw.tar -C third_party\erdos-gyarfas
```

The paths under `C:\tmp` are acquisition-time temporary paths, not runtime or
build dependencies. The machine-readable record is
`UPSTREAM_PROVENANCE.json`.

## Integrity definition

`snapshot_sha256` is the platform-stable file-inventory digest emitted by:

```text
python tools/hash_artifacts.py tree third_party/erdos-gyarfas
```

The digest byte stream consists, for each POSIX-style relative path in sorted
order, of `path UTF-8`, a NUL byte, its lowercase raw-file SHA-256 in ASCII,
and a line-feed byte. `file_sha256` records those ten constituent file hashes.
This representation is independent of tar implementation and host line-ending
configuration.

Disabling `core.autocrlf` was essential during extraction on Windows. An
initial archive attempt inherited the user's global `core.autocrlf=true`,
converted LF bytes to CRLF, and was rejected before handoff. Its
environment-specific archive hash is retained separately in provenance as an
acquisition audit record, not as `snapshot_sha256`. The final raw Git archive
was generated with conversion disabled, and `git hash-object --no-filters`
matched all ten extracted files to the selected Git tree's blob IDs. Neither
temporary archive is committed.

The snapshot is immutable project input. Do not build the original Makefile in
place, because it writes `out/` below the source directory. Tests copy the
snapshot to a temporary directory first. Any future workaround or correction
must live outside the snapshot and be documented under `patches/`.

## Build interfaces

The original upstream build remains byte-for-byte preserved:

```text
make clean
make
./out/a.out <k>
```

It compiles every `src/*.cpp` file with `g++`, C++17, `-Wall -Wextra -O3` and
writes into the copied snapshot's `out/` directory.

The project CMake wrapper names the same three source files explicitly, uses
C++17, adds only warning options, and writes generated files outside the
snapshot:

```text
cmake --preset release
cmake --build --preset release
./build/release/bin/eg-upstream-serial <k>
```

Debug uses the analogous `debug` preset and path. CMake Release selects the
toolchain's standard release optimization flags; the wrapper adds no source,
algorithm, or output-semantic changes.

The `Dockerfile` pins the Ubuntu 24.04 image index by digest, installs the
compiler, CMake, Ninja, Python, and test dependencies, builds as an unprivileged
`researcher` user, and defaults to the bounded test suite. Ubuntu archive
package versions are resolved at image-build time because the public archive
does not retain every superseded version; this remaining dependency pinning
limitation must be captured by the image build log. `.dockerignore` excludes
local builds, caches, Git metadata, and generated benchmark JSON from the
container context.

## Observed CLI exit semantics

These are source-code observations, not mathematical conclusions:

- missing or extra CLI arguments print usage and return `1`;
- `k < 3` prints a message and returns `0`;
- a discovered candidate counterexample is printed and the process exits
  `100`;
- ordinary return after recursive exploration prints elapsed microseconds and
  returns `0`.

Integration smoke tests accept only the documented terminal codes `0` and
`100` for tiny valid inputs and require termination within ten seconds. They
capture stdout and stderr but do not interpret an ordinary exit as proof of
search completeness or of any theorem.

## Scientific boundary

Acquisition, hashing, compilation, or a tiny execution is engineering
evidence only. The snapshot has no project-reviewed invariant proof,
certifying pruning rule, completeness certificate, checkpoint protocol, or
independent search replay. No P13 or P14 result follows from this baseline.
