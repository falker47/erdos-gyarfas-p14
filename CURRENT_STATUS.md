# CURRENT_STATUS - erdos-gyarfas-p14

Last updated: 2026-07-19 UTC

## Current state

- Current phase: pinning GitHub Action supply-chain identities before
  research.
- Active task: `TASK-20260719__pin_github_actions_immutable_shas`.
- Task status: `READY_FOR_REVIEW`.
- Repository: Git worktree for `falker47/erdos-gyarfas-p14`.
- Working branch: `main`.
- Accepted review baseline:
  `dde4e6cbd06be8ebc8192097930f40b06cf2f9f6`.
- Task-start HEAD: `dde4e6cbd06be8ebc8192097930f40b06cf2f9f6`.
- Last reviewed candidate HEAD:
  `dde4e6cbd06be8ebc8192097930f40b06cf2f9f6`.
- Last review verdict: `ACCEPT WITH FOLLOW-UP`.
- Accepted task: `TASK-20260718__support_multi_worktree_whitespace_check`.
- Next review: the cumulative range from the accepted baseline through the
  current immutable-pin candidate; the candidate SHA is intentionally
  resolved from Git by the reviewer.

The multi-worktree whitespace candidate at the current accepted baseline was
accepted with follow-up, so `RFU-CI-004` is resolved. This task addresses only
`RFU-SUPPLY-001`: mutable external Action tags are replaced by verified commit
identities and a repository-local regression validator. It does not broaden
the mathematical or search scope.

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

## Immutable Action pin candidate and open follow-ups

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

Local terminal verification passes 44 focused tests, the 287-test bounded
suite, and the 291-test complete suite with no failure, skip, or xfail. Strict
JSON, canonical task resolution, the real pin validator, all schemas, upstream
snapshot verification, and committed-range whitespace validation also pass.
Independent read-only adversarial review found and then confirmed closure of
encoded-key and block-scalar bypasses before the final suites.

The two pending follow-ups remain ordered and `OPEN`:

- `RFU-SUPPLY-001`: immutable Action references, pending review of this
  candidate;
- `RFU-ENV-001`: complete environment and system-package locking, unchanged.

`RFU-SUPPLY-001` is not closed before review. Hosted GitHub Actions execution
was not observed locally. A commit pin fixes the Action source identity but
does not freeze the `ubuntu-24.04` hosted image, runner service, operating
system packages, or installed package archives; those are the distinct
`RFU-ENV-001` boundary.

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
