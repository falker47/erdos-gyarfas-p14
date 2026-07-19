# CURRENT_STATUS - erdos-gyarfas-p14

Last updated: 2026-07-19 UTC

## Current state

- Current phase: aligning accepted GitHub Action pin documentation before
  research.
- Active task: `TASK-20260719__align_action_pin_documentation`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `265c1474da9e2b91b6779281289eb23129edac33`.
- Task-start HEAD: `265c1474da9e2b91b6779281289eb23129edac33`.
- Last reviewed candidate HEAD:
  `265c1474da9e2b91b6779281289eb23129edac33`.
- Last review verdict: `ACCEPT WITH FOLLOW-UP`.
- Accepted task: `TASK-20260719__pin_github_actions_immutable_shas`.
- Next review: the cumulative range from the accepted baseline through the
  current documentation-alignment candidate; the candidate SHA is
  intentionally resolved from Git by the reviewer.

The immutable Action pin candidate at the current baseline was accepted with
follow-up. `RFU-SUPPLY-001` is therefore resolved. This task addresses only
`RFU-DOC-001`: it aligns one stale descriptive sentence in `docs/CI.md` with
the accepted upload-artifact commit pin. It changes no workflow behavior and
does not broaden the mathematical or search scope.

## Accepted bootstrap scope

- All six requested upstream refs resolved; none is absent or unresolved.
- The ten-file raw `main` snapshot and upstream MIT license are preserved and
  match the selected Git tree and recorded SHA-256 inventory.
- Original Make and project CMake Debug/Release builds completed in the tested
  MSYS2 environment without changing the snapshot.
- Tiny upstream `k=3` and `k=4` processes terminated within ten-second test
  timeouts.
- The independent Python graph verifier, machine-JSON CLI, fixtures, unit
  tests, bounded differential oracles, and CLI integration tests are present.
- The accepted bootstrap suite covered the exact 1,100-graph bounded
  differential domain on orders zero through five.
- Five JSON Schemas, manifest/hash validation, a benchmark harness, fast CI,
  and a manual non-certifying heavy-workflow scaffold are present.

These are bounded engineering and predicate checks only. The accepted verdict
does not convert them into an upstream reproduction, exhaustive computation,
certificate, or mathematical proof.

## Accepted immutable Action pins and open follow-ups

All eleven external Action occurrences in the two workflow files now use one
of three verified identities, with no major upgrade:

- `actions/checkout` release `v4.3.1` at
  `34e114876b0b11c390a56381ad16ebd13914f8d5`;
- `actions/setup-python` release `v5.6.0` at
  `a26af69be951a213d495a4c3e4e4022e16d87065`;
- `actions/upload-artifact` release `v4.6.2` at
  `ea165f8d65b6e75b540449e92b4886f43607fa02`.

The exact release and floating major refs pointed to the same official commit
object in each `actions/<name>` repository, and `action.yml` exists at every
selected commit. Release comments beside the full SHA are non-operative.

`tools/check_github_action_pins.py` scans all workflow `.yml` and `.yaml` files
in deterministic path order using only the Python standard library. It accepts
local `./` references, full lowercase GitHub commit SHAs, and full lowercase
Docker `sha256` digests without tags. Mutable, short, uppercase, dynamic,
multiline, encoded, tagged, alias-based, or ambiguous forms fail closed with
empty stdout; success is one deterministic JSON line. Block-scalar content is
distinguished from sibling mapping keys by actual or explicit YAML content
indentation.

The accepted pin task passed 44 focused tests, the 287-test bounded suite, and
the 291-test complete suite with no failure, skip, or xfail. Its strict JSON,
canonical task resolution, real pin validator, schemas, upstream snapshot,
and range-whitespace checks also passed. This task rechecks the accepted pin
behavior without modifying workflows, validator code, or tests.

Terminal verification for the documentation candidate passes strict JSON,
canonical dossier resolution, the exact documentation assertion, the real
pin validator, 44 focused tests, all 291 collected tests with the documented
MSYS2 toolchain, six-schema validation, upstream snapshot verification, and
worktree whitespace checks. Protected workflow, validator, test, upstream,
project-knowledge, claim, and pruning bytes remain unchanged.

Follow-up state is now:

- `RFU-SUPPLY-001`: resolved by accepted commit
  `265c1474da9e2b91b6779281289eb23129edac33` and no longer pending;
- `RFU-DOC-001`: `OPEN` until review of this documentation correction;
- `RFU-ENV-001`: `OPEN` and unchanged; complete environment and
  system-package locking remains separate.

Hosted GitHub Actions execution is not observed locally by this task. A commit
pin fixes the Action source identity but does not freeze the `ubuntu-24.04`
hosted image, runner service, operating system packages, or installed package
archives; those remain the distinct `RFU-ENV-001` boundary.

## Current mathematical claim boundary

No P13 or P14 research run has started. This task introduces no mathematical
result and no new theorem, counterexample, exhaustive search,
computer-certified result, reproduced upstream result, certifying pruning
rule, or accepted search certificate. All mathematical target statuses remain
unchanged. Action identities, validator behavior, and tests are bounded
supply-chain engineering evidence only.

## Remaining scientific and engineering obligations

- The upstream generation invariant and every pruning proof remain unaudited.
- Search partition coverage, replay, certificate semantics, and independent
  search verification remain provisional or unimplemented.
- The verifier is intentionally exponential and intended for small candidates,
  not search-completeness certification.
- Hosted runner and package-environment immutability remains open under
  `RFU-ENV-001`.
- `RS-001` is `NOT STARTED`.
