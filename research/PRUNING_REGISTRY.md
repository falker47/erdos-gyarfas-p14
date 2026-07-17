# Pruning Registry

No certifying project pruning rule is currently accepted. The three observed
upstream rules are `UPSTREAM_UNAUDITED` review items and have operational
status `DISABLED`; they cannot be enabled in an evidentiary run.

## Status vocabulary

Every rule has exactly one operational status:

- CERTIFYING:
  proved correct, reviewed, tested, and usable in certified runs.
- HEURISTIC_ONLY:
  usable only for exploration; never supports an exhaustive conclusion.
- DISABLED:
  retained for history but not active.
- RETRACTED:
  previously accepted rule found invalid.

`PROPOSED` and `UPSTREAM_UNAUDITED` are review labels, not operational
statuses. A rule with either label must have operational status `DISABLED`.

## PR-UP-001 — Reject an edge that already creates a forbidden cycle

- Origin: upstream
- Audit label: UPSTREAM_UNAUDITED
- Operational status: DISABLED
- Informal rule:
  when considering an edge incident to the newest vertex, if adding that edge
  already creates a forbidden cycle, do not include that edge in any later
  neighbor subset.
- Intended justification:
  adding more edges cannot remove an already existing cycle.
- Required proof:
  formalize the current-state semantics and show that forbidden-cycle existence
  is monotone under edge addition.
- Required tests:
  compare pruned and unpruned subset enumeration on bounded small states.
- Certifying use: forbidden until accepted.

## PR-UP-002 — Stop a branch when the current graph contains an induced P_k

- Origin: upstream
- Audit label: UPSTREAM_UNAUDITED
- Operational status: DISABLED
- Informal rule:
  do not extend a graph that already contains an induced P_k.
- Risk:
  adding edges can destroy inducedness, so monotonicity is not automatic under
  arbitrary edge addition.
- Required analysis:
  prove from the construction invariant that edges between already completed
  old vertices will never be added later in a way that could destroy the
  detected induced path.
- Required tests:
  explicitly search for bounded states where later allowed operations could
  affect the witness.
- Certifying use: forbidden until the invariant proof closes this point.

## PR-UP-003 — Choose only the highest-labelled low-degree anchor

- Origin: upstream and associated minimal-counterexample lemma
- Audit label: UPSTREAM_UNAUDITED
- Operational status: DISABLED
- Informal rule:
  when extending, attach the next vertex only to the highest-labelled vertex
  whose current degree is below 3.
- Required proof:
  reconstruct the relabelling argument used in the minimal-counterexample
  lemma and align it with implementation details.
- Required tests:
  compare with a branching version over all low-degree anchors on bounded
  cases.
- Certifying use: forbidden until accepted.

## Project rules

Every new pruning proposal must receive:

- a new stable ID;
- exact source predicate;
- proof;
- applicable search modes;
- code location;
- verifier treatment;
- regression tests;
- benchmark evidence;
- acceptance commit.

Passing tests alone never changes a rule to CERTIFYING.
