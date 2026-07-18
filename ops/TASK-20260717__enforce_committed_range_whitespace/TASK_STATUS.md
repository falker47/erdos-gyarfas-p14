# TASK-20260717__enforce_committed_range_whitespace — Status

- Mode: STRICT
- Objective: replace false clean-worktree coverage of committed whitespace
  with a deterministic read-only check of
  `REVIEW_STATE.yaml:review_base_commit..HEAD`.
- Repository: `falker47/erdos-gyarfas-p14`
- Working branch: `main`
- Accepted review baseline:
  `e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`
- Task-start HEAD: `e33c3bf121d5bb81b4c63adf704ca9b4ecfea970`
- Previous verdict: `ACCEPT WITH FOLLOW-UP`
- Previous accepted task:
  `TASK-20260717__bind_heavy_workflow_task_identity`
- Follow-up addressed: `RFU-CI-003` (`OPEN` pending review)
- Status: `READY_FOR_REVIEW`

## Scope and claim boundary

Only the twelve prompt-authorized paths may change. This task changes CI and
repository-governance behavior only. It does not change graph predicates,
search or certificate semantics, mathematical claims, pruning rules, the
heavy workflow, the accepted resolver, upstream content, or earlier dossiers.

## Verification state

The corrective gate resolved the exact root, branch, accepted baseline/HEAD,
ancestry, twelve-path allowlist, and empty staged state. The previously blocked
canonical-state test was reproduced failing because it compared the resolver's
correct active-task output with a task-specific synthetic constant inherited
from the accepted prior task.

The authorized test now derives its canonical expectation independently from
UTF-8 `REVIEW_STATE.yaml` via `json.loads`, validates the top-level object,
task-ID type and literal canonical pattern, requires the active dossier status
file, and retains exact stdout/stderr assertions. A separate synthetic test
places distinct accepted and active IDs in state, creates only the active
dossier, and requires the active ID alone.

JSON parsing, canonical resolver/range commands, schema validation, upstream
snapshot verification, 35 resolver tests, 36 whitespace tests, the 195-test
bounded suite, and the 199-test complete suite all pass with no failures or
skips. All session-created basetemps were removed. Protected claims, pruning,
heavy workflow, production resolver, prior dossier, upstream snapshot,
manifest tooling, schemas, and templates remain unchanged.

Hosted GitHub Actions behavior is not locally observed. All evidence remains
bounded engineering evidence; `RS-001` remains `NOT STARTED`.

## Final status

`READY_FOR_REVIEW`
