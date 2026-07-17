# Engineering benchmarks

Benchmarks in this directory measure process behavior and performance. They
are not evidence that a search is correct or exhaustive and cannot support a
mathematical claim.

## Layout

- `cases/` contains reviewed, machine-readable command definitions.
- `results/` is intentionally empty in the bootstrap commit. Generated result
  JSON and captured streams belong here only when the run was actually made,
  the result validates, and its provenance is recorded in a task dossier.

The bootstrap case `cases/upstream-small-k.json` invokes the preserved serial
implementation with a tiny parameter and a ten-second timeout. It is intended
only for build/smoke timing. Ordinary CI tests termination separately and does
not commit measurements.

## Running a case

Configure and build the release preset first. Then run:

```text
python tools/run_benchmark.py benchmarks/cases/upstream-small-k.json --output benchmarks/results/upstream-serial-k3.json
python tools/validate_schemas.py --schema benchmark-result --instance benchmarks/results/upstream-serial-k3.json
```

The runner:

- executes an argument vector directly, without a shell;
- requires the executable and upstream provenance to exist;
- records the project commit or a deterministic dirty-tree description;
- hashes the case, executable, stdout, and stderr;
- derives stream filenames from the requested result filename so separate runs
  cannot silently overwrite one another's captured streams;
- refuses to overwrite an existing result or captured stream;
- reads compiler metadata from the CMake cache when available;
- records case environment overrides and the enforced thread setting; on
  Windows it prepends the recorded compiler directory to the child `PATH` so
  the matching runtime libraries can be resolved;
- applies the case timeout;
- records unavailable CPU or memory measurements as `null` with a limitation;
- validates the result before writing it.

Platform timing and peak-memory APIs differ. Compare results only after
reviewing their `limitations`, compiler, flags, architecture, and environment.
Do not compare a timeout or failed process as though it were a completed run.
