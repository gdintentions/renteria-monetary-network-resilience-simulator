# No-token, no-local-PC validation program — November 16, 2026

## Resource assumption

This plan is for a project owner without access to a high-storage personal computer or budget for paid LLM API tokens. The authored evidence/regression tests below run on **hosted GitHub Actions runners**, subject to GitHub's applicable Actions permissions, limits and billing settings. None of these authored jobs invokes paid LLM APIs. Public standard-hosted Actions often permit usage without additional usage charges; check account billing settings before adding large downloads, paid runners or long jobs. This is not a claim of unlimited free compute.

Developer-authored cases are useful for repeatable software correctness but **not independently labeled validation**. A hosted CI green check is not real-world model or production verification.

## Priority 1 — EvidenceWeave

- Research branch PR #25 provides opt-in semantic graph conflict candidates via explicit entity equivalences and inverse predicates, plus tests and an eight-case fictional developer comparison.
- The external ConflictQA baseline is **unchanged at recall 0.4000**, with 258 known misses and four false positives.
- The separate-label runner requires the case file, independently obtained label file and fixed domain schema as distinct inputs. Hashes and per-case outputs help reviewers audit any result.
- Next: collect a permission-cleared set of **fresh, non-overlapping**, adjudicated contradiction and noncontradiction cases, including multivalued facts, temporal changes and indirect chains. Freeze the cases, rubric and code before exposing labels. Require independent labels and report counts/denominators, confidence intervals when justified, and false positives. Do not tune on the holdout.
- Actual language-model inference is **optional** for the current explicit-graph rule tests, but claims about free-text semantic extraction or generalization require real-model inference or human judgments.

## Priority 2 — JEV Support Desk

- Research branch PR #28 holds a **clean-room reconstructed router**, not the unavailable archived v0.1.1 system.
- The developer-only routing evaluation uses twelve fictional tickets with labels in a separate file; prior 11/12 missed a sensitive account-lockout phrase, and a guarded regex fix passed a subsequent 12/12 CI run. These numbers **do not supersede** the archived 33/35 result.
- Next: recover source and exact original routing run, freeze a fresh human-labeled ticket set, independently review user-facing clarification and handoff outcomes, and compare identical cases under equivalent downstream rules.
- No real customer order lookup, refund, provider billing, privileged data or customer delivery is permitted in this prototype. Do not claim provider model quality until tested.

## Priority 3 — SourceGate and TraceLens

- PR #29 provides a zero-token offline reviewer-protocol harness, thirteen developer-authored synthetic cases (seven SourceGate, six TraceLens), separate labels and raw per-case results.
- The SourceGate coverage fix is already released to `main`, but source authority and claim truth must still be judged by someone who did not design the system.
- For TraceLens, have an independent reviewer judge evidence relevance and where retrieval failed without seeing the detector's answer; include ambiguous examples and disagreements. Report the reviewer rubric and case exclusions.
- For SourceGate, include stale, empty, forged-looking, contradictory and untrusted evidence plus true/false claim labels. Do not let self-labeled metadata stand in for factual verification.

## Practical independent-review process without local hardware

1. Post a **review rubric** and permission-cleared synthetic cases in a read-only GitHub document or a shareable form. Keep expected answers concealed until reviewers submit their judgments.
2. Invite a qualified third party such as a faculty member, peer contributor or AI governance practitioner. A reviewer must not be the project author or an AI-generated stand-in.
3. Freeze the rubric and case identifiers. Collect classifications, uncertainties, disagreements, sign-off (with consent) and a timestamp. Never expose secret keys or sensitive source material.
4. Run the separately stored case and label files via GitHub Actions; publish the exact dataset hashes, code revision, raw errors, confusion matrices and exceptions.
5. Record independent evaluation and real-provider evaluation as **different gates**. Real-model latency and inference quality remain open when suitable hardware or no-cost model access is unavailable.

## Honest recruiter language

"Built and CI-tested governed AI components with reproducible local logic and transparent negative cases; external human review, broader real-model benchmarking and selected-environment production acceptance remain open."

This document is an execution protocol, not proof that an independent reviewer has been recruited or has evaluated anything.
