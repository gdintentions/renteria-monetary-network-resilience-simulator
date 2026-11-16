# EvidenceWeave: semantic graph development comparison — November 16, 2026

**Purpose:** reproducible, opt-in engineering experiment. This file does not replace the prior schema-challenger negative report or original ConflictQA baseline.

## CI evidence

- [EvidenceWeave Tests successful run #43834418688](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43834418688)
- [Semantic challenger replay and benchmark successful run #43834418512](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43834418512)
- Exact code: `src/evidenceweave/semantic_challenger.py`, `semantic_development_eval.py`, and `tests/test_semantic_*.py`.
- Generated artifact: `artifacts/semantic-challenger-development.json` in the CI run's uploaded artifact (not committed as a new permanent benchmark dataset).

## Measured paired developer fixtures only

Eight fictional, author-labeled synthetic cases: three configured conflicts and five controls.

| Method | TP | FP | TN | FN | Sensitivity on fixture conflicts | False positive count |
|---|---:|---:|---:|---:|---:|---:|
| Current direct-key ClaimGraph rule | 1 | 2 | 3 | 2 | 1/3 | 2/5 controls |
| New explicit-equivalence/inverse challenger | 3 | 0 | 5 | 0 | 3/3 | 0/5 controls |

This positive result **does not establish general accuracy**: fixtures were chosen and authored for these rule capabilities. The unchanged external ConflictQA baseline remains 172 TP / 4 FP / 426 TN / 258 FN and recall 0.4000. An earlier functional-schema challenger failed to recover any of the 258 historical exposed misses; see `SCHEMA_CHALLENGER_NEGATIVE_RESULT_2026-11-15.md`. The new mechanism has not been validated on an unseen external conflict corpus.

## Algorithm limitations

Only explicit `same_as` equivalence chains and configured inverse predicates can affect the comparison. No automatic entailment, text parsing, time-scoped truth inference, trust adjudication, authorized ontology mapping, or calibrated truth probability is claimed. User-provided equivalences can themselves be incorrect; a qualified reviewer must control their scope. This code is not wired into main `ClaimGraph.conflicts()` or the public answer-release path.

## Release decision

Keep experimental PR #25 in draft. Before a production or independent-validation label: permission-cleared fresh relation-diverse benchmark, blinded labels including negatives, immutable inputs, domain-approved functional rules and aliases, paired TP/FP/TN/FN plus CIs, failure review, user workflow and selected-host acceptance. Do not tune on the evaluation holdout.
