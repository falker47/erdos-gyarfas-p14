# TASK-20260717__repair_review_governance — Evidence

## EV-001 — Exact startup gate

- Question: Did the checkout satisfy every immutable startup precondition before
  modification?
- Exact commands:

```powershell
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short --branch
git merge-base --is-ancestor 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c HEAD
if ($LASTEXITCODE -eq 0) { Write-Output "merge-base-exit: 0" } else { Write-Output "merge-base-exit: $LASTEXITCODE" }
```

- First result: the sandbox identity was not the checkout owner, so each Git
  query stopped with Git's `detected dubious ownership` fatal error and the
  ancestry command produced `merge-base-exit: 128`. No repository or Git
  configuration changed.
- Complete successful rerun output under the checkout owner:

```text
C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14
main
d7b28390482ca026aa6180728992fa2c0c816a60
## main...origin/main
merge-base-exit: 0
```

- Interpretation: all five preconditions passed and modification was permitted.
- Classification: `EMPIRICAL_OBSERVATION` about repository state; no claim
  effect.

## EV-002 — Complete required reads and cumulative diff

- Question: Was repository evidence inspected before the governance correction
  was designed?
- Method: full UTF-8 reads of all files named by the task, including all three
  rejected-dossier files, followed by inspection of the complete cumulative
  patch and the real affected tools, tests, workflows, manifests, benchmark
  path, upstream verifier, and Docker definition.
- Exact cumulative-diff commands:

```powershell
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 diff --stat 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c..HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 diff --name-status 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c..HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 log --oneline --decorate 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c..HEAD
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 diff --no-ext-diff --no-color 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c..HEAD
```

- Complete changed-path result: 12 paths, 684 insertions, 72 deletions;
  modified `AGENTS.md`, `CURRENT_STATUS.md`, `DECISION_LOG.md`,
  `RESEARCH_LOG.md`, `research/CLAIMS_REGISTRY.yaml`,
  `research/NEXT_RESEARCH_STEPS.md`, and `start.md`; added
  `CHATGPT_REVIEW_PROTOCOL.md`, `REVIEW_STATE.yaml`, and all three files in
  `ops/TASK-20260717__establish_review_state/`. The sole included commit was
  `d7b2839 docs: establish cumulative review state` at full task-start HEAD
  `d7b28390482ca026aa6180728992fa2c0c816a60`.
- Interpretation: the rejected implementation and its evidence were inspected
  cumulatively from the unchanged accepted baseline.
- Limitations: source inspection and a diff read are review inputs, not
  mathematical verification.
- Classification: `EMPIRICAL_OBSERVATION`; no claim effect.

## EV-003 — Review findings and correction boundaries

- `RGV-001`: the rejected candidate's `AGENTS.md` omitted
  `research/KNOWN_RESULTS.md` and `research/NEXT_RESEARCH_STEPS.md`; its
  `start.md` and `CHATGPT_REVIEW_PROTOCOL.md` omitted
  `research/NEXT_RESEARCH_STEPS.md`. The correction places all twelve canonical
  files exactly once and in order in each isolated section, followed by the
  current/candidate dossier, latest relevant earlier dossiers, and every
  required affected-material category.
- `RGV-002`: the rejected protocol had twelve differently ordered report items
  and did not explicitly require all ten contract categories. The correction
  supplies exactly ten ordered items while preserving all stricter review
  duties elsewhere in the protocol.
- `RGV-003`: the rejected candidate called the accepted baseline the
  `Current HEAD` and did not persist the later reviewed candidate. The
  correction distinguishes accepted baseline, task-start HEAD, last reviewed
  candidate, verdict, and a future candidate resolved from Git.
- `RGV-004`: the rejected dossier remains immutable historical evidence. Its
  `TASK_STATUS.md`, `TASK_LOG.md`, and `EV-004` reported a passing reading-order
  audit, but that audit did not test the complete governing twelve-file
  contract and did not provide the exact assertion command and output. That
  `PASS` therefore demonstrates only a narrower checklist, not canonical-order
  compliance. This dossier records the corrected reproducible audit.
- Scope boundary: the correction itself is a governance `DECISION`. No claim
  status, pruning status, mathematical statement, CI implementation, workflow,
  benchmark, environment, experiment, reproduction, manifest, certificate, or
  search is changed or started.

## EV-004 — Reproducible governance and scope audit

- Question: Do the three isolated canonical sections, the mandatory review
  output, persistent state, unchanged follow-ups, and exact task-local scope
  satisfy the corrective contract?
- First execution result before the line-wrap correction:

```text
AUDIT reading order: PASS - AGENTS.md (12 canonical files plus dossier/artifact tail)
AUDIT reading order: PASS - start.md (12 canonical files plus dossier/artifact tail)
AUDIT reading order: PASS - CHATGPT_REVIEW_PROTOCOL.md (12 canonical files plus dossier/artifact tail)
AUDIT RESULT: FAIL - mandatory-output item 3 lacks ['checks declared by the task']
```

- Interpretation of the first result: the audit detected that the required
  phrase crossed a Markdown source line boundary. The wording was corrected
  without weakening its meaning, and the exact same audit was rerun.
- Exact successful audit command:

```powershell
@'
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

TASK_START = "d7b28390482ca026aa6180728992fa2c0c816a60"
ACCEPTED_BASE = "164d6756fd2f6725f2de0bedbe13f1e8c444ba0c"
ACTIVE_TASK = "TASK-20260717__repair_review_governance"
ACCEPTED_TASK = "TASK-20260715__bootstrap_reproducible_baseline"

CANONICAL = [
    "AGENTS.md",
    "start.md",
    "CHATGPT_REVIEW_PROTOCOL.md",
    "REVIEW_STATE.yaml",
    "CURRENT_STATUS.md",
    "PROJECT_KNOWLEDGE.md",
    "research/PROBLEM_STATEMENT.md",
    "research/KNOWN_RESULTS.md",
    "research/VERIFICATION_PROTOCOL.md",
    "research/CLAIMS_REGISTRY.yaml",
    "research/PRUNING_REGISTRY.md",
    "research/NEXT_RESEARCH_STEPS.md",
]

READING_SECTIONS = {
    "AGENTS.md": "## 4. Required startup protocol",
    "start.md": "## Canonical reading order",
    "CHATGPT_REVIEW_PROTOCOL.md": "## 2. Canonical review input",
}

TAIL_PATTERNS = [
    ("current/candidate task dossier", r"\b(?:current|active|candidate)\s+task\s+dossier\b"),
    ("latest relevant earlier dossiers", r"\b(?:latest\s+)?relevant\s+(?:earlier|prior)\s+dossiers?\b"),
    ("affected workflows", r"\baffected\s+workflows?\b"),
    ("tests", r"\btests?\b"),
    ("manifests", r"\bmanifests?\b"),
    ("certificates", r"\bcertificates?\b"),
    ("benchmarks", r"\bbenchmarks?\b"),
    ("artifacts", r"\bartifacts?\b"),
    ("implementation files", r"\bimplementation\s+files?\b"),
    ("Git history", r"\bGit\s+history\b"),
]

ALLOWED = [
    "AGENTS.md",
    "start.md",
    "CHATGPT_REVIEW_PROTOCOL.md",
    "REVIEW_STATE.yaml",
    "CURRENT_STATUS.md",
    "research/NEXT_RESEARCH_STEPS.md",
    "ops/TASK-20260717__repair_review_governance/TASK_STATUS.md",
    "ops/TASK-20260717__repair_review_governance/TASK_LOG.md",
    "ops/TASK-20260717__repair_review_governance/EVIDENCE.md",
]

FOLLOW_UP_IDS = [
    "RFU-CI-001",
    "RFU-CI-002",
    "RFU-WORKFLOW-001",
    "RFU-CI-003",
    "RFU-SUPPLY-001",
    "RFU-ENV-001",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"AUDIT RESULT: FAIL - {message}")


ROOT = Path.cwd().resolve()
GIT = [
    "git",
    "-c",
    f"safe.directory={ROOT.as_posix()}",
    "-c",
    "core.excludesFile=.gitignore",
]


def git(*args: str) -> str:
    result = subprocess.run(
        [*GIT, *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def section(path: str, heading: str) -> str:
    text = (ROOT / path).read_text(encoding="utf-8")
    match = re.search(
        rf"(?ms)^{re.escape(heading)}[ \t]*\r?\n(.*?)(?=^##[ \t]|\Z)",
        text,
    )
    require(match is not None, f"missing section {heading!r} in {path}")
    return match.group(1)


repo_root = Path(git("rev-parse", "--show-toplevel").strip()).resolve()
require(repo_root == ROOT, f"run from repository root {repo_root}, not {ROOT}")

tick = chr(96)
for path, heading in READING_SECTIONS.items():
    body = section(path, heading)
    previous = -1
    last_token_end = -1
    for canonical_path in CANONICAL:
        token = f"{tick}{canonical_path}{tick}"
        count = body.count(token)
        require(count == 1, f"{path} section has {count} occurrences of {token}")
        position = body.index(token)
        require(position > previous, f"{token} is out of order in {path}")
        previous = position
        last_token_end = position + len(token)

    cursor = last_token_end
    for label, pattern in TAIL_PATTERNS:
        match = re.search(pattern, body[cursor:], flags=re.IGNORECASE)
        require(match is not None, f"{path} lacks post-file-list {label}")
        cursor += match.end()

    print(
        "AUDIT reading order: PASS - "
        f"{path} (12 canonical files plus dossier/artifact tail)"
    )

mandatory = section(
    "CHATGPT_REVIEW_PROTOCOL.md",
    "## 11. Mandatory review output",
)
markers = list(re.finditer(r"(?m)^(\d+)\.\s+", mandatory))
numbers = [int(marker.group(1)) for marker in markers]
require(numbers == list(range(1, 11)), f"mandatory-output item numbers are {numbers}, expected 1..10")

items = {}
for index, marker in enumerate(markers):
    end = markers[index + 1].start() if index + 1 < len(markers) else len(mandatory)
    items[int(marker.group(1))] = mandatory[marker.start():end]

required_phrases = {
    1: ["examined baseline", "HEAD", "cumulative range", "included commits"],
    2: ["effective diff", "real scope"],
    3: [
        "checks performed by the reviewer",
        "checks declared by the task",
        "observed CI",
        "unavailable checks",
    ],
    4: ["findings", "paths", "impact"],
    5: ["mathematical assessment"],
    6: ["engineering assessment"],
    7: ["exactly one verdict"],
    8: ["required persistent-file updates"],
    9: ["exactly one next atomic task"],
    10: ["complete self-contained Codex prompt"],
}

for number, phrases in required_phrases.items():
    folded = items[number].casefold()
    missing = [phrase for phrase in phrases if phrase.casefold() not in folded]
    require(not missing, f"mandatory-output item {number} lacks {missing}")

print("AUDIT mandatory output: PASS - 10 ordered categories")

severity_tokens = [
    f"{tick}{label}{tick}"
    for label in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
]
severity_positions = [items[4].find(token) for token in severity_tokens]
require(all(position >= 0 for position in severity_positions), "mandatory-output item 4 lacks a severity label")
require(severity_positions == sorted(severity_positions), "severity labels are not ordered CRITICAL, HIGH, MEDIUM, LOW")
require(all(items[4].count(token) == 1 for token in severity_tokens), "severity labels must occur exactly once in item 4")

print("AUDIT severity order: PASS - CRITICAL > HIGH > MEDIUM > LOW")

verdict_tokens = [
    f"{tick}{label}{tick}"
    for label in ["ACCEPT", "ACCEPT WITH FOLLOW-UP", "REJECT"]
]
verdict_positions = [items[7].find(token) for token in verdict_tokens]
require(all(position >= 0 for position in verdict_positions), "mandatory-output item 7 lacks an exact verdict string")
require(verdict_positions == sorted(verdict_positions), "verdict strings are not ordered ACCEPT, ACCEPT WITH FOLLOW-UP, REJECT")
require(all(items[7].count(token) == 1 for token in verdict_tokens), "each exact verdict string must occur once in item 7")

print("AUDIT verdict strings: PASS - ACCEPT | ACCEPT WITH FOLLOW-UP | REJECT")

state = json.loads((ROOT / "REVIEW_STATE.yaml").read_text(encoding="utf-8"))
expected_state = {
    "schema_version": "1.0",
    "repository": "falker47/erdos-gyarfas-p14",
    "branch": "main",
    "review_base_commit": ACCEPTED_BASE,
    "accepted_baseline_commit": ACCEPTED_BASE,
    "last_reviewed_head": TASK_START,
    "last_verdict": "REJECT",
    "accepted_task_id": ACCEPTED_TASK,
    "active_task_id": ACTIVE_TASK,
}

for key, expected in expected_state.items():
    require(
        state.get(key) == expected,
        f"REVIEW_STATE.yaml {key}={state.get(key)!r}, expected {expected!r}",
    )

prior_state = json.loads(git("show", f"{TASK_START}:REVIEW_STATE.yaml"))
pending = state.get("pending_follow_ups")
require(isinstance(pending, list), "pending_follow_ups is not a list")

ids = [entry.get("id") for entry in pending]
require(ids == FOLLOW_UP_IDS, f"follow-up IDs/order changed: {ids}")
require(len(set(ids)) == 6, "follow-up IDs are not six unique values")
require([entry.get("status") for entry in pending] == ["OPEN"] * 6, "not all six follow-ups are OPEN")
require(pending == prior_state.get("pending_follow_ups"), "follow-up severity, paths, status, description, or order changed")

utc_format = "%Y-%m-%dT%H:%M:%SZ"
try:
    updated = datetime.strptime(state["updated_at_utc"], utc_format).replace(tzinfo=timezone.utc)
    prior_updated = datetime.strptime(prior_state["updated_at_utc"], utc_format).replace(tzinfo=timezone.utc)
except (KeyError, TypeError, ValueError) as error:
    raise SystemExit(f"AUDIT RESULT: FAIL - invalid updated_at_utc: {error}") from error

require(updated > prior_updated, "updated_at_utc did not advance from the task-start state")
require(updated <= datetime.now(timezone.utc) + timedelta(minutes=5), "updated_at_utc is unreasonably in the future")

print(
    "AUDIT review state: PASS - "
    f"base={ACCEPTED_BASE}; candidate={TASK_START}; "
    f"verdict=REJECT; active={ACTIVE_TASK}; "
    f"updated={state['updated_at_utc']}"
)
print("AUDIT follow-ups: PASS - 6 unique, 6 OPEN, all fields unchanged")

tracked = {
    line
    for line in git("diff", "--name-only", TASK_START, "--").splitlines()
    if line
}
untracked = {
    line
    for line in git("ls-files", "--others", "--exclude-standard").splitlines()
    if line
}
changed = tracked | untracked

require(
    changed == set(ALLOWED),
    "task-local changed paths differ from allowlist; "
    f"changed={sorted(changed)!r}",
)

rejected_prefix = "ops/TASK-20260717__establish_review_state/"
require(
    not any(path.startswith(rejected_prefix) for path in changed),
    "rejected dossier changed",
)

print("AUDIT task-local scope: PASS - exact 9-path allowlist; rejected dossier unchanged")
print("AUDIT changed paths:")
for path in sorted(changed):
    print(f"  {path}")
print("AUDIT RESULT: PASS")
'@ | python -
```

- Complete successful output:

```text
AUDIT reading order: PASS - AGENTS.md (12 canonical files plus dossier/artifact tail)
AUDIT reading order: PASS - start.md (12 canonical files plus dossier/artifact tail)
AUDIT reading order: PASS - CHATGPT_REVIEW_PROTOCOL.md (12 canonical files plus dossier/artifact tail)
AUDIT mandatory output: PASS - 10 ordered categories
AUDIT severity order: PASS - CRITICAL > HIGH > MEDIUM > LOW
AUDIT verdict strings: PASS - ACCEPT | ACCEPT WITH FOLLOW-UP | REJECT
AUDIT review state: PASS - base=164d6756fd2f6725f2de0bedbe13f1e8c444ba0c; candidate=d7b28390482ca026aa6180728992fa2c0c816a60; verdict=REJECT; active=TASK-20260717__repair_review_governance; updated=2026-07-17T10:03:48Z
AUDIT follow-ups: PASS - 6 unique, 6 OPEN, all fields unchanged
AUDIT task-local scope: PASS - exact 9-path allowlist; rejected dossier unchanged
AUDIT changed paths:
  AGENTS.md
  CHATGPT_REVIEW_PROTOCOL.md
  CURRENT_STATUS.md
  REVIEW_STATE.yaml
  ops/TASK-20260717__repair_review_governance/EVIDENCE.md
  ops/TASK-20260717__repair_review_governance/TASK_LOG.md
  ops/TASK-20260717__repair_review_governance/TASK_STATUS.md
  research/NEXT_RESEARCH_STEPS.md
  start.md
AUDIT RESULT: PASS
```

- Interpretation: all twelve canonical paths occur exactly once and in order in
  each isolated section; dossier and affected-material inspection follows;
  all ten output categories, four severities, and three verdict strings are
  explicit; state and all six follow-ups are exact; task scope is the nine-path
  allowlist.
- Classification: governance validation only; no mathematical result follows.

## EV-005 — Required validators, tests, and Git inspection

- Question: Do all task-required local checks pass at the finalized review-state
  values, and what checks remain unavailable?
- Exact Python commands:

```powershell
python -m json.tool REVIEW_STATE.yaml
python tools/validate_schemas.py
python tools/verify_upstream_snapshot.py
python -m pytest -q tests/unit tests/differential tests/integration/test_verifier_cli.py
```

- Complete JSON parse output:

```json
{
    "schema_version": "1.0",
    "repository": "falker47/erdos-gyarfas-p14",
    "branch": "main",
    "review_base_commit": "164d6756fd2f6725f2de0bedbe13f1e8c444ba0c",
    "last_reviewed_head": "d7b28390482ca026aa6180728992fa2c0c816a60",
    "last_verdict": "REJECT",
    "accepted_baseline_commit": "164d6756fd2f6725f2de0bedbe13f1e8c444ba0c",
    "accepted_task_id": "TASK-20260715__bootstrap_reproducible_baseline",
    "active_task_id": "TASK-20260717__repair_review_governance",
    "updated_at_utc": "2026-07-17T10:16:00Z",
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
59 passed in 3.75s
```

- Exact Git commands, using only process-local configuration because the
  sandbox identity does not own the checkout:

```powershell
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile=.gitignore diff --check 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile=.gitignore status --short --branch
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile=.gitignore diff --stat 164d6756fd2f6725f2de0bedbe13f1e8c444ba0c --
git -c safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14 -c core.excludesFile=.gitignore diff --name-only d7b28390482ca026aa6180728992fa2c0c816a60 --
```

- Complete Git results: cumulative diff-check exited 0 with no output; status
  output was:

```text
## main...origin/main
 M AGENTS.md
 M CHATGPT_REVIEW_PROTOCOL.md
 M CURRENT_STATUS.md
 M REVIEW_STATE.yaml
 M research/NEXT_RESEARCH_STEPS.md
 M start.md
?? ops/TASK-20260717__repair_review_governance/
```

- Cumulative diff-stat output was:

```text
 AGENTS.md                                          |  36 ++-
 CHATGPT_REVIEW_PROTOCOL.md                         | 294 +++++++++++++++++++++
 CURRENT_STATUS.md                                  |  97 +++----
 DECISION_LOG.md                                    |  21 +-
 RESEARCH_LOG.md                                    |  10 +
 REVIEW_STATE.yaml                                  |  73 +++++
 .../EVIDENCE.md                                    | 112 ++++++++
 .../TASK_LOG.md                                    |  42 +++
 .../TASK_STATUS.md                                 |  60 +++++
 research/CLAIMS_REGISTRY.yaml                      |   3 +-
 research/NEXT_RESEARCH_STEPS.md                    |  31 ++-
 start.md                                           |  23 +-
 12 files changed, 728 insertions(+), 74 deletions(-)
```

- Task-start tracked-name output was:

```text
AGENTS.md
CHATGPT_REVIEW_PROTOCOL.md
CURRENT_STATUS.md
REVIEW_STATE.yaml
research/NEXT_RESEARCH_STEPS.md
start.md
```

- Interpretation: all four required Python checks and all four required Git
  checks passed. Ordinary Git diff commands do not include the three untracked
  new-dossier files; EV-004 includes those files and proves the exact combined
  nine-path task-local scope. The cumulative stat intentionally includes the
  rejected candidate from the accepted baseline.
- Unavailable checks and limitations: hosted GitHub Actions and Docker were not
  run; no benchmark, reproduction, experiment, search, pruning analysis,
  manifest/certificate execution, or mathematical verification was authorized.
  Their absence is not evidence. No local required check was unavailable.
- Classification: bounded governance and engineering verification only; no
  mathematical result follows.

## EV-006 — Rejected-dossier and claim-registry preservation

- Question: Are the rejected dossier and claim registry unchanged at raw-byte
  level relative to the task-start commit?
- Exact command:

```powershell
$taskStart = 'd7b28390482ca026aa6180728992fa2c0c816a60'
$gitArgs = @('-c','safe.directory=C:/Users/Falker/Desktop/Code/circle/erdos-gyarfas-p14','-c','core.excludesFile=.gitignore')
$paths = @('ops/TASK-20260717__establish_review_state/TASK_STATUS.md','ops/TASK-20260717__establish_review_state/TASK_LOG.md','ops/TASK-20260717__establish_review_state/EVIDENCE.md')
foreach ($path in $paths) {
  $commitSpec = '{0}:{1}' -f $taskStart, $path
  $commitBlob = & git @gitArgs rev-parse $commitSpec
  $worktreeBlob = & git @gitArgs hash-object --no-filters -- $path
  $sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
  Write-Output ("{0}`tcommit_blob={1}`tworktree_blob={2}`tsha256={3}" -f $path,$commitBlob,$worktreeBlob,$sha256)
  if ($commitBlob -ne $worktreeBlob) { throw "raw blob mismatch: $path" }
}
& git @gitArgs diff --quiet $taskStart -- ops/TASK-20260717__establish_review_state
Write-Output "rejected-dossier-diff-exit: $LASTEXITCODE"
if ($LASTEXITCODE -ne 0) { throw 'rejected dossier differs from task-start HEAD' }
& git @gitArgs diff --quiet $taskStart -- research/CLAIMS_REGISTRY.yaml
Write-Output "claims-registry-diff-exit: $LASTEXITCODE"
if ($LASTEXITCODE -ne 0) { throw 'claims registry differs from task-start HEAD' }
```

- Complete output:

```text
ops/TASK-20260717__establish_review_state/TASK_STATUS.md	commit_blob=0aaac8be1d8816e4aa7de9b6c6419012a3df4230	worktree_blob=0aaac8be1d8816e4aa7de9b6c6419012a3df4230	sha256=61eb259cae0521a33d47d985e35704e169f39b62686471041516f816e9bc5bd1
ops/TASK-20260717__establish_review_state/TASK_LOG.md	commit_blob=7ba5696d040d185d9af24d374b6d494e7fd2b52b	worktree_blob=7ba5696d040d185d9af24d374b6d494e7fd2b52b	sha256=546d1c53035eca3fd4acab51fb90b0fbabe0129bae7e38f9253e9cf3b360541a
ops/TASK-20260717__establish_review_state/EVIDENCE.md	commit_blob=8c84572c9a545ad131b144fd05c4c02de1073ee3	worktree_blob=8c84572c9a545ad131b144fd05c4c02de1073ee3	sha256=469e16608452bd3ed7a10fcf42d1ff0139ae2998e1e45fa3e78f589de24d7dbf
rejected-dossier-diff-exit: 0
claims-registry-diff-exit: 0
```

- Interpretation: each rejected-dossier worktree byte stream hashes to the same
  raw Git blob as task-start HEAD, and the claim registry has no task-local
  diff. No claim status, evidence classification, or mathematical statement
  changed.
- Classification: preservation check only; no mathematical result follows.
