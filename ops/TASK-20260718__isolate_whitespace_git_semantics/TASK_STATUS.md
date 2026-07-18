# TASK-20260718__isolate_whitespace_git_semantics — Status

- Mode: STRICT
- Objective: make the canonical committed-range whitespace verdict independent
  of mutable Git configuration and non-versioned attribute sources while
  preserving checked-in `.gitattributes`.
- Repository: `falker47/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`
- Task-start HEAD: `ac9c4c4d18e8b0d01038215e25ba37cdbf1449e4`
- Previous verdict: `REJECT`
- Previous rejected task:
  `TASK-20260717__enforce_committed_range_whitespace`
- Accepted task:
  `TASK-20260717__bind_heavy_workflow_task_identity`
- Follow-up addressed: `RFU-CI-003` (`OPEN` pending review)
- Status: `READY_FOR_REVIEW`

## Scope and claim boundary

Only the ten prompt-authorized paths may change. This correction retains the
rejected candidate in the cumulative review history and does not modify either
workflow, the task-ID resolver, checked-in `.gitattributes`, earlier dossiers,
claims, pruning, upstream content, graph code, manifests, or search behavior.

Exact task allowlist:

- `tools/check_review_range_whitespace.py`
- `tests/unit/test_review_range_whitespace.py`
- `docs/CI.md`
- `research/REPRODUCIBILITY.md`
- `REVIEW_STATE.yaml`
- `CURRENT_STATUS.md`
- `research/NEXT_RESEARCH_STEPS.md`
- `ops/TASK-20260718__isolate_whitespace_git_semantics/TASK_STATUS.md`
- `ops/TASK-20260718__isolate_whitespace_git_semantics/TASK_LOG.md`
- `ops/TASK-20260718__isolate_whitespace_git_semantics/EVIDENCE.md`

The task is CI/governance engineering only. It creates no mathematical result,
reproduction, exhaustive computation, certificate, counterexample, theorem,
or proof. `RS-001` remains `NOT STARTED`.

## Trust boundary

The intended Git whitespace policy is explicit:
`blank-at-eol,space-before-tab,blank-at-eof`. Neutralizable system, global,
process, and repository-local configuration plus global/system attributes are
isolated for child Git commands. Checked-in `.gitattributes` remains active.
A non-versioned repository attribute source that Git cannot safely ignore
without also losing checked-in attributes is rejected deterministically before
the committed range is evaluated.

## Verification state

Startup Git gate, complete cumulative-diff inspection, mandatory repository
reads, and installed Git 2.45.1 documentation inspection are complete. The 63
focused tests, 222-test bounded suite, and 226-test complete suite pass without
failures, skips, or xfails. Strict JSON, canonical task resolution, schema
validation, upstream inventory, real cumulative checker invocation, diff
hygiene, scope, preservation, and cleanup checks pass.

An independent adversarial review reproduced local and per-worktree diff-driver
bypasses during implementation; both are now fail-closed and covered through
direct and included config files. The final independent review reports no
remaining static-config blocker. Concurrent hostile filesystem replacement
during the Git subprocess remains outside the read-only atomicity boundary and
is documented as a limitation. Hosted GitHub Actions was not executed.

## Final status

`READY_FOR_REVIEW`
