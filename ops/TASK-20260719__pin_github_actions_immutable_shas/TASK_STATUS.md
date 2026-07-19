# TASK-20260719__pin_github_actions_immutable_shas - Status

- Mode: STRICT
- Objective: replace every mutable external GitHub Action reference with a
  verified immutable commit SHA and add a deterministic repository-local
  regression validator.
- Repository: `falker47/erdos-gyarfas-p14`
- Repository root:
  `C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `dde4e6cbd06be8ebc8192097930f40b06cf2f9f6`
- Task-start HEAD:
  `dde4e6cbd06be8ebc8192097930f40b06cf2f9f6`
- Previous verdict: `ACCEPT WITH FOLLOW-UP`
- Accepted task: `TASK-20260718__support_multi_worktree_whitespace_check`
- Follow-up addressed: `RFU-SUPPLY-001` (`OPEN` pending review)
- Status: `READY_FOR_REVIEW`

## Authorized scope

Exactly these twelve paths may change:

- `.github/workflows/ci.yml`
- `.github/workflows/heavy-search.yml`
- `tools/check_github_action_pins.py`
- `tests/unit/test_github_action_pins.py`
- `docs/CI.md`
- `research/REPRODUCIBILITY.md`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260719__pin_github_actions_immutable_shas/TASK_STATUS.md`
- `ops/TASK-20260719__pin_github_actions_immutable_shas/TASK_LOG.md`
- `ops/TASK-20260719__pin_github_actions_immutable_shas/EVIDENCE.md`

## Claim boundary

This task is supply-chain, CI, and reproducibility engineering only. It creates
no mathematical result, reproduction, exhaustive computation, certificate,
counterexample, theorem, proof, or pruning rule. `RS-001` remains
`NOT STARTED`. Claims, pruning, project knowledge, upstream, verifier,
generator, schemas, manifests, certificates, and benchmarks are out of scope.

## Verification state

All eleven external Action occurrences in the two workflow files use one
consistent SHA for each retained major: checkout `v4.3.1`, setup-python
`v5.6.0`, and upload-artifact `v4.6.2`. Official release, repository, Git ref,
commit-object, and exact-commit `action.yml` checks pass.

The deterministic standard-library validator accepts full lowercase GitHub
commit SHAs, local `./` Actions, and full lowercase Docker digests without
tags. It rejects mutable and ambiguous forms, including encoded/tagged keys
and block-scalar sibling bypass attempts. Final verification passes 44 focused
tests, 287 bounded tests, and 291 complete tests with no failure, skip, or
xfail. State, resolver, real validator, schemas, upstream inventory, range
whitespace, scope, preservation, and cleanup checks pass.

`RFU-SUPPLY-001` remains `OPEN` pending review. `RFU-ENV-001` remains
unchanged and `OPEN`; full Action pins do not freeze hosted runners or package
installation sources.

## Final status

`READY_FOR_REVIEW`
