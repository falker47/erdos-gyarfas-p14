# TASK-20260717__repair_postcommit_review_state — Evidence

## EV-001 — Immutable startup gate

- Question: Did the checkout satisfy every immutable startup precondition
  before modification?
- Initial exact command:

```powershell
git rev-parse --show-toplevel
```

- Complete initial output:

```text
fatal: detected dubious ownership in repository at 'C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14'
'C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14' is owned by:
	HYCARUS/Falker (S-1-5-21-1203256543-3988785944-36575366-1001)
but the current user is:
	HYCARUS/CodexSandboxOffline (S-1-5-21-1203256543-3988785944-36575366-1006)
To add an exception for this directory, call:

	git config --global --add safe.directory C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
```

- Interpretation: the command failed before returning repository state. No Git
  configuration was changed. The permitted process-local `safe.directory`
  option was used for every successful rerun.
- Exact successful commands:

```powershell
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 rev-parse --show-toplevel
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 branch --show-current
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 rev-parse HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 status --short --branch
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 merge-base --is-ancestor 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 log --oneline --decorate 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c..HEAD
```

- Complete successful output, in command order:

```text
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
main
5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf
## main...origin/main
warning: unable to access 'C:\Users\Falker/.config/git/ignore': Permission denied
warning: unable to access 'C:\Users\Falker/.config/git/ignore': Permission denied
[merge-base exited 0 with no output]
5dbf0d4 (HEAD -> main, origin/main) docs: repair cumulative review governance
d7b2839 docs: establish cumulative review state
```

- Interpretation: the intended repository root, exact `main` branch, exact
  task-start HEAD, clean worktree, accepted-baseline ancestry, and cumulative
  commit set all matched. Modification was permitted.
- Classification: repository-state observation only; no claim effect.

## EV-002 — Required reading, cumulative diff, and history

- Question: Was the correction based on the full repository-defined evidence?
- Method: read in full, in the required order, all twelve canonical files; all
  six files in the two required prior dossiers; the complete cumulative diff
  from the accepted baseline through task-start HEAD; and relevant Git history,
  workflows, tests, benchmark runner, validators, Docker definition, artifact
  inventory, and repository file inventory.
- Exact cumulative inspection commands included:

```powershell
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile=.gitignore remote -v
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile=.gitignore diff --stat 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c..HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile=.gitignore diff --name-status 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c..HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile=.gitignore log --format=fuller --decorate 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c..HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile=.gitignore diff --no-ext-diff --no-color 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c..HEAD -- <each changed path>
```

- Complete remote output:

```text
origin	https://github.com/falker47/erdos-gyarfas-p14.git (fetch)
origin	https://github.com/falker47/erdos-gyarfas-p14.git (push)
```

- Complete cumulative stat output:

```text
 AGENTS.md                                          |  36 +-
 CHATGPT_REVIEW_PROTOCOL.md                         | 294 ++++++++++
 CURRENT_STATUS.md                                  |  97 ++--
 DECISION_LOG.md                                    |  21 +-
 RESEARCH_LOG.md                                    |  10 +
 REVIEW_STATE.yaml                                  |  73 +++
 .../EVIDENCE.md                                    | 112 ++++
 .../TASK_LOG.md                                    |  42 ++
 .../TASK_STATUS.md                                 |  60 ++
 .../EVIDENCE.md                                    | 636 +++++++++++++++++++++
 .../TASK_LOG.md                                    |  70 +++
 .../TASK_STATUS.md                                 | 105 ++++
 research/CLAIMS_REGISTRY.yaml                      |   3 +-
 research/NEXT_RESEARCH_STEPS.md                    |  31 +-
 start.md                                           |  23 +-
 15 files changed, 1539 insertions(+), 74 deletions(-)
```

- Complete cumulative changed-path output:

```text
M	AGENTS.md
A	CHATGPT_REVIEW_PROTOCOL.md
M	CURRENT_STATUS.md
M	DECISION_LOG.md
M	RESEARCH_LOG.md
A	REVIEW_STATE.yaml
A	ops/TASK-20260717__establish_review_state/EVIDENCE.md
A	ops/TASK-20260717__establish_review_state/TASK_LOG.md
A	ops/TASK-20260717__establish_review_state/TASK_STATUS.md
A	ops/TASK-20260717__repair_review_governance/EVIDENCE.md
A	ops/TASK-20260717__repair_review_governance/TASK_LOG.md
A	ops/TASK-20260717__repair_review_governance/TASK_STATUS.md
M	research/CLAIMS_REGISTRY.yaml
M	research/NEXT_RESEARCH_STEPS.md
M	start.md
```

- Complete included-commit identity:

```text
5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf docs: repair cumulative review governance
d7b28390482ca026aa6180728992fa2c0c816a60 docs: establish cumulative review state
```

- Interpretation: the candidate is the cumulative two-commit change from the
  unchanged accepted bootstrap baseline. The full patch and every changed file
  were inspected; the current task does not reinterpret prior cumulative
  changes as task-local scope.
- Limitations: reading source and Git history is governance inspection, not
  mathematical verification.
- Classification: repository-state observation only; no claim effect.

## EV-003 — Post-commit staleness and policy correction

- Finding: `CURRENT_STATUS.md` at task-start HEAD described the preceding
  correction as “uncommitted” and said its future SHA was not stored before it
  existed. The former became false when the user created commit
  `5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf`; the latter was likewise
  temporally fragile current-state wording.
- Correction: canonical state now calls the new work a corrective candidate
  and states that its candidate SHA is intentionally resolved from Git by the
  reviewer. `AGENTS.md` and `CHATGPT_REVIEW_PROTOCOL.md` now require canonical
  current-state language that remains true after manual commit, while allowing
  clearly historical task-local chronology about SHA availability.
- Protected governance: the three twelve-file canonical reading lists, the
  cumulative-baseline semantics, the verdict criteria, and the mandatory
  ten-category review output are not reordered, weakened, or otherwise
  changed.
- Scope boundary: this is a governance `DECISION` only. There is no
  mathematical, CI, benchmark, reproduction, experiment, manifest,
  certificate, search, pruning, or bounded graph-predicate evidence and no
  claim-registry change.

## EV-004 — Reproducible governance and scope audit

- Question: Do the protected governance structures, synchronized state,
  commit-neutral wording, preservation boundaries, and exact eight-path scope
  satisfy all ten required assertions?
- First compact audit output:

```text
AUDIT CONTEXT: root=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 branch=main head=5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf base=164d6756fd2f6725f2de0bedbe13f1e8c444ba0c process_local_git_config=true
FAIL 01: three canonical sections contain exactly the same ordered twelve files
PASS 02: mandatory review output contains exactly ten ordered categories
PASS 03: REVIEW_STATE exact fields/SHAs and strict UTC timestamp '2026-07-17T10:52:45Z'; no future corrective SHA
PASS 04: all six follow-ups unchanged from task-start HEAD; ids=['RFU-CI-001', 'RFU-CI-002', 'RFU-WORKFLOW-001', 'RFU-CI-003', 'RFU-SUPPLY-001', 'RFU-ENV-001']
PASS 05: CURRENT_STATUS and NEXT_RESEARCH_STEPS contain the exact synchronized state
PASS 06: canonical current state is commit-neutral and both durable rules are explicit; hits={} policy={'AGENTS.md': True, 'CHATGPT_REVIEW_PROTOCOL.md': True}
PASS 07: research/CLAIMS_REGISTRY.yaml unchanged from task-start HEAD
PASS 08: both prior evidence files unchanged: ['ops/TASK-20260717__repair_review_governance/EVIDENCE.md', 'ops/TASK-20260717__establish_review_state/EVIDENCE.md']
PASS 09: task-local tracked-plus-untracked paths equal exact eight-file allowlist; actual=['AGENTS.md', 'CHATGPT_REVIEW_PROTOCOL.md', 'CURRENT_STATUS.md', 'REVIEW_STATE.yaml', 'ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md', 'ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md', 'ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md', 'research/NEXT_RESEARCH_STEPS.md']
PASS 10: no workflow/code/schema/Docker/upstream/benchmark/claim/prior-evidence/artifact/manifest/certificate path changed; hits=[]
AUDIT RESULT: FAIL (9/10; failed=[1])
```

- Failure explanation: assertion 1 initially collected every backtick token in
  the full protocol section, including the post-list `ROOT` definition. The
  repository's twelve-file list was correct; the compact audit's extraction
  boundary was too broad. The non-committed audit was corrected to extract
  tokens only from numbered items preceding the task-dossier item. No
  repository content changed in response.
- Exact corrected audit command:

```powershell
@'
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path.cwd().resolve()
TASK = "5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf"
BASE = "164d6756fd2f6725f2de0bedbe13f1e8c444ba0c"
TASK_ID = "TASK-20260717__repair_postcommit_review_state"
GIT = ["git", "-c", f"safe.directory={ROOT.as_posix()}", "-c", "core.excludesFile="]

def git(*args, check=True, text=True):
    result = subprocess.run(GIT + list(args), cwd=ROOT, capture_output=True)
    if check and result.returncode:
        raise SystemExit(
            f"AUDIT ERROR: git {' '.join(args)} exited {result.returncode}: "
            + result.stderr.decode("utf-8", errors="replace")
        )
    return result.stdout.decode("utf-8") if text else result

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def section(path, heading):
    value = read(path)
    match = re.search(
        rf"(?ms)^{re.escape(heading)}[ \t]*\r?\n(.*?)(?=^##[ \t]|\Z)",
        value,
    )
    if not match:
        raise SystemExit(f"AUDIT ERROR: missing {heading!r} in {path}")
    return match.group(1)

failures = []
def check(number, condition, detail):
    label = "PASS" if condition else "FAIL"
    print(f"{label} {number:02d}: {detail}")
    if not condition:
        failures.append(number)

root = Path(git("rev-parse", "--show-toplevel").strip()).resolve()
branch = git("branch", "--show-current").strip()
head = git("rev-parse", "HEAD").strip()
ancestor = git("merge-base", "--is-ancestor", BASE, TASK, check=False, text=False)
print(
    f"AUDIT CONTEXT: root={root.as_posix()} branch={branch} head={head} "
    f"base={BASE} process_local_git_config=true"
)
if root != ROOT or branch != "main" or head != TASK or ancestor.returncode != 0:
    raise SystemExit("AUDIT RESULT: FAIL - preflight mismatch")

def nul_paths(result):
    return [
        item.decode("utf-8").replace("\\", "/")
        for item in result.stdout.split(b"\0")
        if item
    ]

tracked = nul_paths(git("diff", "--name-only", "-z", TASK, "--", text=False))
untracked = nul_paths(
    git("ls-files", "--others", "--exclude-standard", "-z", text=False)
)
changed = sorted(set(tracked + untracked))

canonical = [
    "AGENTS.md", "start.md", "CHATGPT_REVIEW_PROTOCOL.md", "REVIEW_STATE.yaml",
    "CURRENT_STATUS.md", "PROJECT_KNOWLEDGE.md",
    "research/PROBLEM_STATEMENT.md", "research/KNOWN_RESULTS.md",
    "research/VERIFICATION_PROTOCOL.md", "research/CLAIMS_REGISTRY.yaml",
    "research/PRUNING_REGISTRY.md", "research/NEXT_RESEARCH_STEPS.md",
]
read_sections = {
    "AGENTS.md": "## 4. Required startup protocol",
    "start.md": "## Canonical reading order",
    "CHATGPT_REVIEW_PROTOCOL.md": "## 2. Canonical review input",
}
reading = {}
for path, heading in read_sections.items():
    items = re.findall(r"(?m)^\d+\.\s+([^\n]+)$", section(path, heading))
    stop = next(
        (index for index, item in enumerate(items)
         if "task dossier" in item.lower()),
        len(items),
    )
    reading[path] = [
        token
        for item in items[:stop]
        for token in re.findall(r"`([^`]+)`", item)
    ]
check(
    1,
    all(reading[path] == canonical for path in read_sections),
    "three canonical sections contain exactly the same ordered twelve files",
)

mandatory = section("CHATGPT_REVIEW_PROTOCOL.md", "## 11. Mandatory review output")
categories = re.findall(r"(?m)^(\d+)\.\s+\*\*([^*]+)\*\*", mandatory)
expected_categories = [
    "Examined revisions", "Effective diff and real scope",
    "Verification status", "Findings", "Mathematical assessment",
    "Engineering assessment", "Verdict", "Required persistent-file updates",
    "Next atomic task", "Complete Codex prompt",
]
check(
    2,
    [int(number) for number, _ in categories] == list(range(1, 11))
    and [name for _, name in categories] == expected_categories,
    "mandatory review output contains exactly ten ordered categories",
)

state_text = read("REVIEW_STATE.yaml")
state = json.loads(state_text)
expected_keys = {
    "schema_version", "repository", "branch", "review_base_commit",
    "last_reviewed_head", "last_verdict", "accepted_baseline_commit",
    "accepted_task_id", "active_task_id", "updated_at_utc",
    "pending_follow_ups",
}
expected_values = {
    "schema_version": "1.0",
    "repository": "falker47/erdos-gyarfas-p14",
    "branch": "main",
    "review_base_commit": BASE,
    "last_reviewed_head": TASK,
    "last_verdict": "REJECT",
    "accepted_baseline_commit": BASE,
    "accepted_task_id": "TASK-20260715__bootstrap_reproducible_baseline",
    "active_task_id": TASK_ID,
}
timestamp_ok = False
try:
    updated = datetime.strptime(
        state["updated_at_utc"], "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)
    commit_time = datetime.fromtimestamp(
        int(git("show", "-s", "--format=%ct", TASK).strip()), timezone.utc
    )
    timestamp_ok = (
        re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
                     state["updated_at_utc"]) is not None
        and commit_time <= updated <= datetime.now(timezone.utc)
    )
except (KeyError, TypeError, ValueError):
    pass
sha_counts = Counter(re.findall(r"\b[0-9a-f]{40}\b", state_text))
check(
    3,
    set(state) == expected_keys
    and all(state.get(key) == value for key, value in expected_values.items())
    and timestamp_ok
    and sha_counts == Counter({BASE: 2, TASK: 1}),
    f"REVIEW_STATE exact fields/SHAs and strict UTC timestamp "
    f"{state.get('updated_at_utc')!r}; no future corrective SHA",
)

prior_state = json.loads(git("show", f"{TASK}:REVIEW_STATE.yaml"))
followups = state.get("pending_follow_ups")
followup_ids = [item.get("id") for item in followups] if isinstance(followups, list) else []
check(
    4,
    followups == prior_state.get("pending_follow_ups") and len(followup_ids) == 6,
    f"all six follow-ups unchanged from task-start HEAD; ids={followup_ids}",
)

status_flat = " ".join(read("CURRENT_STATUS.md").split())
steps_flat = " ".join(read("research/NEXT_RESEARCH_STEPS.md").split())
status_required = [
    f"Active task: `{TASK_ID}`",
    "Task status: `READY_FOR_REVIEW`",
    f"Accepted review baseline: `{BASE}`",
    f"Task-start HEAD: `{TASK}`",
    f"Last reviewed candidate HEAD: `{TASK}`",
    "Last review verdict: `REJECT`",
    "cumulative from the unchanged accepted review baseline through the "
    "corrective candidate HEAD; the candidate SHA is intentionally resolved "
    "from Git by the reviewer",
]
steps_required = [
    TASK_ID, BASE, TASK, "was rejected",
    "review remains cumulative from that unchanged baseline",
    "remain unchanged and `OPEN`",
    "RFU-CI-001", "RFU-CI-002", "RFU-WORKFLOW-001", "RFU-CI-003",
    "RFU-SUPPLY-001", "RFU-ENV-001",
    "are not started", "RS-001` remains `NOT STARTED",
]
check(
    5,
    all(value in status_flat for value in status_required)
    and all(value in steps_flat for value in steps_required),
    "CURRENT_STATUS and NEXT_RESEARCH_STEPS contain the exact synchronized state",
)

fragile = re.compile(
    r"\buncommitted\b|\bnot\s+(?:yet\s+)?committed\b|"
    r"\b(?:does|do)\s+not\s+(?:yet\s+)?exist\b|"
    r"\bbefore\s+it\s+exists\b|"
    r"\bfuture\s+(?:corrective\s+|candidate\s+)?commit\b|"
    r"\bnon[- ]?existent\b|\b(?:pending|awaiting)\s+(?:a\s+|the\s+)?"
    r"(?:manual\s+)?commit\b",
    re.IGNORECASE,
)
fragile_hits = {
    path: fragile.findall(read(path))
    for path in [
        "CURRENT_STATUS.md", "REVIEW_STATE.yaml",
        "research/NEXT_RESEARCH_STEPS.md",
    ]
    if fragile.search(read(path))
}
policy_terms = [
    "cannot know the final sha", "canonical current-state files",
    "remains true after", "resolved from git by the reviewer",
    "must not describe", "uncommitted", "not yet committed", "nonexistent",
    "task-local dossier chronology", "historical",
]
policy_ok = {
    path: all(
        term in " ".join(read(path).lower().split())
        for term in policy_terms
    )
    for path in ["AGENTS.md", "CHATGPT_REVIEW_PROTOCOL.md"]
}
check(
    6,
    not fragile_hits and all(policy_ok.values()),
    f"canonical current state is commit-neutral and both durable rules are "
    f"explicit; hits={fragile_hits} policy={policy_ok}",
)

claims = "research/CLAIMS_REGISTRY.yaml"
claims_result = git("diff", "--quiet", TASK, "--", claims, check=False, text=False)
check(
    7,
    claims not in changed and claims_result.returncode == 0,
    "research/CLAIMS_REGISTRY.yaml unchanged from task-start HEAD",
)

prior_evidence = [
    "ops/TASK-20260717__repair_review_governance/EVIDENCE.md",
    "ops/TASK-20260717__establish_review_state/EVIDENCE.md",
]
prior_ok = all(
    path not in changed
    and git("diff", "--quiet", TASK, "--", path, check=False, text=False).returncode == 0
    for path in prior_evidence
)
check(8, prior_ok, f"both prior evidence files unchanged: {prior_evidence}")

allowed = {
    "AGENTS.md", "CHATGPT_REVIEW_PROTOCOL.md", "REVIEW_STATE.yaml",
    "CURRENT_STATUS.md", "research/NEXT_RESEARCH_STEPS.md",
    "ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md",
    "ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md",
    "ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md",
}
check(
    9,
    set(changed) == allowed and len(changed) == 8,
    f"task-local tracked-plus-untracked paths equal exact eight-file allowlist; "
    f"actual={changed}",
)

protected = [
    path for path in changed
    if path.startswith((
        ".github/workflows/", "tests/", "tools/", "verifier/", "schemas/",
        "upstream/", "third_party/", "benchmarks/", "artifacts/",
    ))
    or path in {
        "Dockerfile", "CMakeLists.txt", "CMakePresets.json", "pyproject.toml",
        claims, *prior_evidence,
    }
]
check(
    10,
    not protected,
    f"no workflow/code/schema/Docker/upstream/benchmark/claim/prior-evidence/"
    f"artifact/manifest/certificate path changed; hits={protected}",
)

if failures:
    print(f"AUDIT RESULT: FAIL ({10-len(failures)}/10; failed={failures})")
    sys.exit(1)
print("AUDIT RESULT: PASS (10/10 assertions)")
'@ | python -B -
```

- Complete corrected output:

```text
AUDIT CONTEXT: root=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 branch=main head=5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf base=164d6756fd2f6725f2de0bedbe13f1e8c444ba0c process_local_git_config=true
PASS 01: three canonical sections contain exactly the same ordered twelve files
PASS 02: mandatory review output contains exactly ten ordered categories
PASS 03: REVIEW_STATE exact fields/SHAs and strict UTC timestamp '2026-07-17T10:52:45Z'; no future corrective SHA
PASS 04: all six follow-ups unchanged from task-start HEAD; ids=['RFU-CI-001', 'RFU-CI-002', 'RFU-WORKFLOW-001', 'RFU-CI-003', 'RFU-SUPPLY-001', 'RFU-ENV-001']
PASS 05: CURRENT_STATUS and NEXT_RESEARCH_STEPS contain the exact synchronized state
PASS 06: canonical current state is commit-neutral and both durable rules are explicit; hits={} policy={'AGENTS.md': True, 'CHATGPT_REVIEW_PROTOCOL.md': True}
PASS 07: research/CLAIMS_REGISTRY.yaml unchanged from task-start HEAD
PASS 08: both prior evidence files unchanged: ['ops/TASK-20260717__repair_review_governance/EVIDENCE.md', 'ops/TASK-20260717__establish_review_state/EVIDENCE.md']
PASS 09: task-local tracked-plus-untracked paths equal exact eight-file allowlist; actual=['AGENTS.md', 'CHATGPT_REVIEW_PROTOCOL.md', 'CURRENT_STATUS.md', 'REVIEW_STATE.yaml', 'ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md', 'ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md', 'ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md', 'research/NEXT_RESEARCH_STEPS.md']
PASS 10: no workflow/code/schema/Docker/upstream/benchmark/claim/prior-evidence/artifact/manifest/certificate path changed; hits=[]
AUDIT RESULT: PASS (10/10 assertions)
```

- Final identical rerun after dossier recording and UTC timestamp finalization:

```text
AUDIT CONTEXT: root=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 branch=main head=5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf base=164d6756fd2f6725f2de0bedbe13f1e8c444ba0c process_local_git_config=true
PASS 01: three canonical sections contain exactly the same ordered twelve files
PASS 02: mandatory review output contains exactly ten ordered categories
PASS 03: REVIEW_STATE exact fields/SHAs and strict UTC timestamp '2026-07-17T11:02:13Z'; no future corrective SHA
PASS 04: all six follow-ups unchanged from task-start HEAD; ids=['RFU-CI-001', 'RFU-CI-002', 'RFU-WORKFLOW-001', 'RFU-CI-003', 'RFU-SUPPLY-001', 'RFU-ENV-001']
PASS 05: CURRENT_STATUS and NEXT_RESEARCH_STEPS contain the exact synchronized state
PASS 06: canonical current state is commit-neutral and both durable rules are explicit; hits={} policy={'AGENTS.md': True, 'CHATGPT_REVIEW_PROTOCOL.md': True}
PASS 07: research/CLAIMS_REGISTRY.yaml unchanged from task-start HEAD
PASS 08: both prior evidence files unchanged: ['ops/TASK-20260717__repair_review_governance/EVIDENCE.md', 'ops/TASK-20260717__establish_review_state/EVIDENCE.md']
PASS 09: task-local tracked-plus-untracked paths equal exact eight-file allowlist; actual=['AGENTS.md', 'CHATGPT_REVIEW_PROTOCOL.md', 'CURRENT_STATUS.md', 'REVIEW_STATE.yaml', 'ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md', 'ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md', 'ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md', 'research/NEXT_RESEARCH_STEPS.md']
PASS 10: no workflow/code/schema/Docker/upstream/benchmark/claim/prior-evidence/artifact/manifest/certificate path changed; hits=[]
AUDIT RESULT: PASS (10/10 assertions)
```

- Interpretation: after correcting the audit boundary, all ten required
  assertions passed. The exact eight task-local paths are the only changed
  paths, including all three untracked dossier files.
- Classification: governance validation only; no mathematical result follows.

## EV-005 — Required validators, tests, and Git inspections

- Exact required Python commands:

```powershell
python -m json.tool REVIEW_STATE.yaml
python tools/validate_schemas.py
python tools/verify_upstream_snapshot.py
python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
```

- Complete final JSON parse output:

```json
{
    "schema_version": "1.0",
    "repository": "falker47/erdos-gyarfas-p14",
    "branch": "main",
    "review_base_commit": "164d6756fd2f6725f2de0bedbe13f1e8c444ba0c",
    "last_reviewed_head": "5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf",
    "last_verdict": "REJECT",
    "accepted_baseline_commit": "164d6756fd2f6725f2de0bedbe13f1e8c444ba0c",
    "accepted_task_id": "TASK-20260715__bootstrap_reproducible_baseline",
    "active_task_id": "TASK-20260717__repair_postcommit_review_state",
    "updated_at_utc": "2026-07-17T11:02:13Z",
    "pending_follow_ups": [
        {
            "id": "RFU-CI-001",
            "severity": "HIGH",
            "affected_paths": [
                ".github/workflows/ci.yml",
                "tests/integration/test_upstream_build.py"
            ],
            "status": "OPEN",
            "description": "Make tiny known-completion CI cases require exit 0 and validate any exit 100 candidate separately."
        },
        {
            "id": "RFU-CI-002",
            "severity": "HIGH",
            "affected_paths": [
                ".github/workflows/ci.yml",
                "tools/run_benchmark.py"
            ],
            "status": "OPEN",
            "description": "Make benchmark CI fail unless the recorded child process outcome matches the case's accepted exit and termination semantics."
        },
        {
            "id": "RFU-WORKFLOW-001",
            "severity": "MEDIUM",
            "affected_paths": [
                ".github/workflows/heavy-search.yml"
            ],
            "status": "OPEN",
            "description": "Remove the bootstrap task ID hardcoded into manifests emitted by the manual heavy-workflow scaffold."
        },
        {
            "id": "RFU-CI-003",
            "severity": "MEDIUM",
            "affected_paths": [
                ".github/workflows/ci.yml"
            ],
            "status": "OPEN",
            "description": "Run whitespace validation over the committed comparison range instead of only the clean checkout worktree."
        },
        {
            "id": "RFU-SUPPLY-001",
            "severity": "MEDIUM",
            "affected_paths": [
                ".github/workflows/ci.yml",
                ".github/workflows/heavy-search.yml"
            ],
            "status": "OPEN",
            "description": "Replace mutable major-tag GitHub Action references with reviewed immutable commit SHAs."
        },
        {
            "id": "RFU-ENV-001",
            "severity": "MEDIUM",
            "affected_paths": [
                ".github/workflows/ci.yml",
                ".github/workflows/heavy-search.yml",
                "Dockerfile"
            ],
            "status": "OPEN",
            "description": "Complete environment locking for hosted runners and archive-installed system packages, recording resolved versions and immutable provenance."
        }
    ]
}
```

- Complete schema-validation output:

```json
{"ok": true, "schemas_checked": ["schemas/benchmark-result.schema.json", "schemas/counterexample.schema.json", "schemas/experiment-manifest.schema.json", "schemas/search-certificate.schema.json", "schemas/search-partition.schema.json"]}
```

- Complete upstream-snapshot output:

```json
{"added": [], "changed": [], "expected_file_count": 10, "missing": [], "observed_file_count": 10, "ok": true, "snapshot_path": "third_party/erdos-gyarfas"}
```

- Complete pytest output:

```text
...........................................................              [100%]
59 passed in 3.68s
```

- Interpretation: JSON parsing, all five schemas, the 10/10 preserved upstream
  inventory, and all 59 required unit/differential/verifier-CLI tests passed.
- Unavailable checks and limitations: hosted GitHub Actions and Docker were not
  run; no benchmark, reproduction, material experiment, search, pruning
  analysis, manifest/certificate execution, or mathematical verification was
  authorized. Their absence is not evidence. No required local check was
  unavailable.
- Classification: bounded governance and engineering verification only; no
  mathematical result follows.

## EV-006 — Preservation and exact task-local scope

- Question: Are the claim registry and both prior evidence files unchanged at
  raw-byte level, and do the required Git inspections confirm the exact
  task-local scope?
- Exact raw preservation command:

```powershell
$taskStart = '5dbf0d4a54eef1cac90deb0dd04d7251f609f9cf'
$gitArgs = @('-c','safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14','-c','core.excludesFile=')
$paths = @(
  'research/CLAIMS_REGISTRY.yaml',
  'ops/TASK-20260717__repair_review_governance/EVIDENCE.md',
  'ops/TASK-20260717__establish_review_state/EVIDENCE.md'
)
foreach ($path in $paths) {
  $commitSpec = '{0}:{1}' -f $taskStart, $path
  $commitBlob = & git @gitArgs rev-parse $commitSpec
  $worktreeBlob = & git @gitArgs hash-object --no-filters -- $path
  $sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
  Write-Output ("{0}`tcommit_blob={1}`tworktree_blob={2}`tsha256={3}" -f $path,$commitBlob,$worktreeBlob,$sha256)
  if ($commitBlob -ne $worktreeBlob) { throw "raw blob mismatch: $path" }
}
& git @gitArgs diff --quiet $taskStart -- research/CLAIMS_REGISTRY.yaml
Write-Output "claims-registry-diff-exit: $LASTEXITCODE"
if ($LASTEXITCODE -ne 0) { throw 'claims registry differs from task-start HEAD' }
& git @gitArgs diff --quiet $taskStart -- ops/TASK-20260717__repair_review_governance/EVIDENCE.md
Write-Output "repair-governance-evidence-diff-exit: $LASTEXITCODE"
if ($LASTEXITCODE -ne 0) { throw 'repair-governance evidence differs from task-start HEAD' }
& git @gitArgs diff --quiet $taskStart -- ops/TASK-20260717__establish_review_state/EVIDENCE.md
Write-Output "establish-review-state-evidence-diff-exit: $LASTEXITCODE"
if ($LASTEXITCODE -ne 0) { throw 'establish-review-state evidence differs from task-start HEAD' }
```

- Complete preservation output:

```text
research/CLAIMS_REGISTRY.yaml	commit_blob=c770fc2b51c16d575a05fde361403ffbf9c50f22	worktree_blob=c770fc2b51c16d575a05fde361403ffbf9c50f22	sha256=0329bcf07a4f9a4f8baab351bf039641c9af6cbfe9a0612833c6ecd680cc3b2c
ops/TASK-20260717__repair_review_governance/EVIDENCE.md	commit_blob=8a353d5572a2627fed3bf6d703ef83f088d83f53	worktree_blob=8a353d5572a2627fed3bf6d703ef83f088d83f53	sha256=b123fb5f86845f0d35d8f196c6b7ca90074aaa506747f19dac84fd47c9ac169d
ops/TASK-20260717__establish_review_state/EVIDENCE.md	commit_blob=8c84572c9a545ad131b144fd05c4c02de1073ee3	worktree_blob=8c84572c9a545ad131b144fd05c4c02de1073ee3	sha256=469e16608452bd3ed7a10fcf42d1ff0139ae2998e1e45fa3e78f589de24d7dbf
claims-registry-diff-exit: 0
repair-governance-evidence-diff-exit: 0
establish-review-state-evidence-diff-exit: 0
```

- Exact required Git commands, with process-local configuration only:

```powershell
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --check 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= status --short --branch
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --stat 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --name-status 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= diff --no-ext-diff --no-color 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= status --porcelain=v1 --untracked-files=all
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile= ls-files --others --exclude-standard
```

- Complete diff-check output: no output; exit `0`.
- Complete status output:

```text
## main...origin/main
 M AGENTS.md
 M CHATGPT_REVIEW_PROTOCOL.md
 M CURRENT_STATUS.md
 M REVIEW_STATE.yaml
 M research/NEXT_RESEARCH_STEPS.md
?? ops/TASK-20260717__repair_postcommit_review_state/
```

- Complete cumulative diff-stat output:

```text
 AGENTS.md                                          |  46 +-
 CHATGPT_REVIEW_PROTOCOL.md                         | 304 ++++++++++
 CURRENT_STATUS.md                                  |  99 ++--
 DECISION_LOG.md                                    |  21 +-
 RESEARCH_LOG.md                                    |  10 +
 REVIEW_STATE.yaml                                  |  73 +++
 .../EVIDENCE.md                                    | 112 ++++
 .../TASK_LOG.md                                    |  42 ++
 .../TASK_STATUS.md                                 |  60 ++
 .../EVIDENCE.md                                    | 636 +++++++++++++++++++++
 .../TASK_LOG.md                                    |  70 +++
 .../TASK_STATUS.md                                 | 105 ++++
 research/CLAIMS_REGISTRY.yaml                      |   3 +-
 research/NEXT_RESEARCH_STEPS.md                    |  31 +-
 start.md                                           |  23 +-
 15 files changed, 1561 insertions(+), 74 deletions(-)
```

- Complete cumulative name-status output:

```text
M	AGENTS.md
A	CHATGPT_REVIEW_PROTOCOL.md
M	CURRENT_STATUS.md
M	DECISION_LOG.md
M	RESEARCH_LOG.md
A	REVIEW_STATE.yaml
A	ops/TASK-20260717__establish_review_state/EVIDENCE.md
A	ops/TASK-20260717__establish_review_state/TASK_LOG.md
A	ops/TASK-20260717__establish_review_state/TASK_STATUS.md
A	ops/TASK-20260717__repair_review_governance/EVIDENCE.md
A	ops/TASK-20260717__repair_review_governance/TASK_LOG.md
A	ops/TASK-20260717__repair_review_governance/TASK_STATUS.md
M	research/CLAIMS_REGISTRY.yaml
M	research/NEXT_RESEARCH_STEPS.md
M	start.md
```

- Complete cumulative patch result: exit `0`; 1,814 output lines were inspected.
  The cumulative patch intentionally contains the two previously rejected
  commits plus the five tracked current-task edits. Ordinary Git diff omits the
  three untracked dossier files; their full contents were inspected separately
  and their paths are covered by the following two commands and `EV-004`.
- Complete porcelain output:

```text
 M AGENTS.md
 M CHATGPT_REVIEW_PROTOCOL.md
 M CURRENT_STATUS.md
 M REVIEW_STATE.yaml
 M research/NEXT_RESEARCH_STEPS.md
?? ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md
?? ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md
?? ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md
```

- Complete untracked-file output:

```text
ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md
ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md
ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md
```

- Exact untracked-dossier whitespace command:

```powershell
@'
from pathlib import Path

paths = [
    Path("ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md"),
    Path("ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md"),
    Path("ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md"),
]
for path in paths:
    data = path.read_bytes()
    text = data.decode("utf-8")
    trailing = [
        number
        for number, line in enumerate(text.splitlines(), start=1)
        if line.endswith((" ", "\t"))
    ]
    if trailing:
        raise SystemExit(f"FAIL {path.as_posix()}: trailing whitespace lines {trailing}")
    if not data.endswith(b"\n"):
        raise SystemExit(f"FAIL {path.as_posix()}: missing final newline")
    print(f"PASS {path.as_posix()}: UTF-8, no trailing whitespace, final newline")
print("UNTRACKED DOSSIER WHITESPACE: PASS")
'@ | python -B -
```

- Complete whitespace output:

```text
PASS ops/TASK-20260717__repair_postcommit_review_state/TASK_STATUS.md: UTF-8, no trailing whitespace, final newline
PASS ops/TASK-20260717__repair_postcommit_review_state/TASK_LOG.md: UTF-8, no trailing whitespace, final newline
PASS ops/TASK-20260717__repair_postcommit_review_state/EVIDENCE.md: UTF-8, no trailing whitespace, final newline
UNTRACKED DOSSIER WHITESPACE: PASS
```

- Interpretation: raw blobs for the claim registry and both prior evidence
  files match task-start HEAD; cumulative whitespace passes; and the exact
  task-local union is five tracked files plus three untracked dossier files,
  matching the eight-path allowlist.
- Classification: preservation and governance-scope verification only; no
  mathematical result follows.
