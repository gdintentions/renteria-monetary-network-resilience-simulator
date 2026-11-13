# JEV-Routed GenAI Support Desk

**Portfolio specification · November 12, 2026 Pacific**  
**Readiness:** Offline prototype with historical synthetic development evidence. Live-provider evaluation, personal technical ownership, observed human workflow, independent review, selected-host validation, operator acceptance, and production readiness are open.

## 1. System concept and source

The support desk is a synthetic retail workflow for order status, product questions, returns or exchanges, and complaints. A typed decision model supplies routing signals. Application rules choose between an order lookup, a small-model draft, a larger-model draft, human handoff, and a clarifying question. A second check screens generated drafts against approved facts and policy. The portfolio prototype gives a support agent a review queue and records decisions locally.

The original concept comes from @DataScienceBrain’s tutorial for **Kumkum Home**, a fictional home-decor store. The tutorial sends each ticket to TypeSafe Jev for intent, complexity, and a human-request signal. Plain code chooses the route. Groq-hosted language models draft catalog and policy responses. A second Jev call checks unauthorized promises, invented facts, and whether the draft answers the customer. The tutorial shows a send-or-hold branch. It reports that the guard held a correct return reply when it had to infer that five days falls within seven, so the tutorial moved the date comparison into code. That example and the tutorial’s model versions, scores, thresholds, and timings belong to its author.

The original 16 supplied images match the checksums in the prototype’s source manifest. The last supplied image is marked **16/17**. The original images are retained privately. The supplied pages preview a Jev-versus-LLM routing comparison. Any results on later pages are unverified. The portfolio implementation uses its own fictional retailer data, local prechecks, read-only lookup, agent previews, and recorded review decisions. Approval creates a local receipt. The prototype has no customer delivery, refund, payment, or order-write channel.

## 2. Routing and dispositions

The v0.1.1 intake applies explicit human-request and selected account/billing rules before provider calls. It validates order references and simulated account ownership. Ambiguous references and recognized mixed intents lead to clarification. For remaining cases, the classifier returns intent, intent confidence, complexity, and a human-request score. The application applies the human-request threshold first, then the unclear-intent check, then the complexity threshold, then the evidence requirements for the selected route.

| Route | Evidence and authority | Expected disposition |
| --- | --- | --- |
| Order lookup | One verified order associated with the simulated requester account | Return the known status through a read-only lookup. Unknown and other-account references receive the same generic clarification. |
| Small-model draft | One matching catalog record with the requested fact in scope | Preview for agent review after draft checks. Ask for clarification when the product or requested fact lacks support. |
| Larger-model draft | Return policy with a computed date-window fact when relevant, or complaint policy for a straightforward complaint | Preview for agent review after draft checks. A general policy question can use policy alone. An order-specific question requires a verified order. |
| Human handoff | Explicit request for a person, recognized sensitive account or billing issue, high complexity, or unavailable classifier | Record a pending handoff with a reason and a brief acknowledgement. Avoid promises about outcome or response time. |
| Clarification | Unclear intent, incomplete or ambiguous information, or insufficient evidence | Ask one focused question. Withhold order details and any unsupported answer. |

The archived development settings are **0.55** minimum intent confidence, **0.70** for a classified human request, and complexity **above 1.10** for a handoff. The draft guard holds when either risk score reaches **0.75** or responsiveness falls below **0.55**. These are development cutoffs defined in code. Calibration is pending. The offline mode uses rules and templates. Optional TypeSafe Jev and Groq adapters are documented and covered by fixtures. Live model versions, behavior, costs, latency, and the choice of operating thresholds remain unvalidated.

## 3. Evidence, policy, and abstention

- **Authority.** Use the approved catalog record, fictional return or complaint policy, and verified order data for their respective routes. Compute days since delivery in application code. For the fictional policy, delivery day and day seven are inside the window, day eight is outside, and an undelivered order has no started window. An in-window result establishes timing eligibility for review. Item condition and tags still matter, and refunds require a separate decision.
- **Draft verification.** Bind each draft to the supplied evidence IDs. The prototype checks draft size, known identifier patterns, and the exact set of supplied source IDs before screening for unauthorized commitments, unsupported facts, and responsiveness. The source-ID check verifies which evidence accompanied the draft. Claim-level support for free-form live output requires separate evaluation.
- **Abstention.** Ask for clarification when a missing detail could resolve the request. Hand off sensitive cases or classifier failures. Hold generated text when evidence IDs are wrong, the writer or guard fails, or the guard flags a factual or policy problem. Keep held text out of the requester response. Only a guard-passed draft can receive an approval receipt. Rejection and handling can close appropriate review work locally.
- **Proposed organizational controls.** A policy owner approves source versions, effective dates, applicability, and precedence. If policy is missing, expired, or unresolved after a conflict, withhold the affected claim and hand off with a reason. Carry source version, rule version, reason code, and disposition into a reviewable audit record. Use role-scoped previews and redacted logs. Existing demo account selectors and operator aliases are synthetic, and pattern-based minimization covers only selected identifiers. Authentication, role enforcement, retention, and broader data handling require validation on the intended host.

## 4. Defensive tests and failure evidence

Use synthetic tickets, policies, and provider fixtures. Record the expected and actual route, disposition, evidence IDs, reason code, and whether requester-visible text exposed a draft or unsupported claim. Record which stages ran and retain failed cases alongside passing ones.

| Case | Expected behavior | Evidence status |
| --- | --- | --- |
| Authorized lookup, ambiguous references, or another account’s order | Return status only for the authorized lookup. Missing and other-account orders get the same public clarification. | Archived local fixtures cover these paths. Real identity and access control remain open. |
| Product evidence missing, or return at day 0, 7, or 8 | Clarify when product evidence is absent. Compute the window deterministically and avoid promising refunds or credits. | Archived local fixtures. Real policy interpretation remains open. |
| Bad evidence ID, unsupported refund promise, or irrelevant draft | Hold the draft and show only a neutral next step. A matching source ID cannot clear an unsupported claim. | Archived controlled output and guard fixtures. Live false holds and unsafe drafts that pass the guard are unmeasured. |
| Prompt injection in a ticket, evidence passage, or generated draft | Treat instruction-like text as data. Check that it cannot override policy, disclose out-of-scope data, or make a held draft approvable. Use a clean control for each surface to detect unnecessary holds. | Proposed dedicated injection suite. Archived draft and citation checks provide related control evidence. |
| Missing, stale, or conflicting policy, or an invalid delivery date | Withhold the affected answer. Record the unresolved evidence or invalid date and route the case for review. | Date validation has a local fixture. Policy conflict and stale-policy handling are proposed. |
| Classifier, writer, or guard times out or returns malformed output | Hand off on classifier failure. Hold writer and guard failures. Record the failing stage. On a selected host, verify retry bounds and watch for duplicate provider work. | Archived provider failure and response-shape fixtures. Live provider and selected-host resilience remain open. |

### Historical results from the prototype archive

The November 11, 2026 Pacific offline comparison used the same **35 developer-authored synthetic tickets** across all three columns. The revision was tuned after inspecting the first run. The comparison measures final routing on those fixtures.

| Measure | Frozen keyword baseline | v0.1.0 | v0.1.1 |
| --- | ---: | ---: | ---: |
| Correct final route | 15/35 | 30/35 | 33/35 |
| Required human handoffs caught | 1/8 | 6/8 | 8/8 |
| Unnecessary human handoffs | 0/27 | 1/27 | 0/27 |

Keep the original runs and failure register. v0.1.0 incorrectly escalated a delayed shipment with negative sentiment (R19). v0.1.1 corrected that regression and two missed handoffs. A tracking paraphrase (R29) and an exchange paraphrase (R30) still went to clarification. The archive separately reports 25 local Python tests and a disposable SQLite restore drill. This specification adds no test execution or measurements. The raw run JSONs pin v0.1.0 to `8bdb1cb64986f7deb8c9c50735f93f23c6b1628f` and v0.1.1 to `5ffd646aa5b7f5395d8bb8a69f1a214f3b324aa8`. See the source record below.

## 5. Restore and replay

The archived local drill backed up a disposable SQLite database, removed the test source, opened the snapshot, checked integrity, and verified that a pending handoff and a prior review decision survived. A separate archived concurrency check reports one stored receipt for 24 identical submissions across eight workers. Identical concurrent requests can still compute before a receipt wins, so duplicate provider calls remain possible.

**Proposed selected-host drill.** Record the revision, configuration, snapshot timestamp, and pre-backup receipt and review counts. Exercise interrupted writes and submissions around the snapshot boundary. Restore into an isolated instance, verify integrity and the recovered queue, replay a matching receipt ID, reject a conflicting reuse, and check that a held draft stays withheld. Account for missing post-snapshot records and duplicate provider work. Record actual recovery time, recoverable data loss, failed checks, and rollback outcome. The intended operator must set and approve recovery time and recovery point targets before the drill.

## 6. Validation and readiness gates

| Gate | Current status | Evidence required |
| --- | --- | --- |
| Bounded development and local restore | Historical synthetic evidence available | Retain both pinned runs, fixtures, local verification, recovery procedure, and unresolved failures. Attribute results to their original scope. |
| Personal technical ownership | Open | The project owner explains the deterministic return calculation and guard boundary, diagnoses one open paraphrase miss, implements a bounded fix with a regression test, and explains the outcome. Record AI assistance and preserve the original failure. |
| Observed human workflow | Open | Have a participant complete lookup, clarification, draft approval or rejection, handoff, and receipt replay on synthetic tickets. Record task outcomes, errors, interruptions, elapsed time if measured, and prompts or assistance. Label scripted or AI-operated demonstrations accordingly. |
| Live provider evaluation | Open | Use approved synthetic tickets and record exact model versions, configurations, request counts, failures, latency, and costs. For a router comparison, hold downstream routing rules, writers, and guard fixed. Keep live results distinct from the offline development comparison. |
| Independent review | Open | A qualified reviewer who did not build the prototype labels a fresh holdout before seeing system outputs. Freeze the rubric and cases before tuning. Include supported and unsupported answers, paraphrases, explicit handoffs, mixed intents, policy conflicts, and the defensive tests above. Preserve labels, disagreements, failed cases, and the reviewer’s signed findings. |
| Deployment, load, and recovery | Open | On the selected environment, verify authenticated roles, access separation, TLS where applicable, secrets and retention, realistic traffic and resource limits, dependency failures, monitoring and alert ownership, restore and rollback. Record actual results and any deviations from pre-agreed limits. |
| Operator and organizational acceptance | Open | A named operator and authorized organizational decision-maker record an accept, reject, or conditional decision for the selected environment. Record permitted users and data, escalation coverage, policy ownership, incident responsibility, rollback authority, and unresolved risks. |
| Production readiness | Open | Requires scoped validation evidence, closure of the preceding gates, and an authorized release decision for the intended use. |

For the independent review, report final-route accuracy, required-handoff recall, false handoffs, supported-claim precision, correct abstention, false holds, and unsafe drafts that pass the guard. Give counts and denominators for each metric, including unscorable cases and provider failures. Agree on release thresholds and blocking failures before the run. Any observed unauthorized disclosure, policy-bypassing action, or release of a held draft should block promotion until corrected and retested. This is a proposed acceptance rule.

## 7. Portfolio placement

This specification is indexed in [Start Here](../../START_HERE.md#project-map) and the [recruiter snapshots](../../docs/PORTFOLIO_PROJECT_SNAPSHOTS.md#project-specifications). The [validation queue](../../docs/VALIDATION_NEXT_SESSION_2026-11-06.md#november-12-2026-pacific--jev-support-desk) records the open JEV work. The November 7 evidence register is the historical inventory for that date.

[Open the recruiter browser demo](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/jev-support-desk/) to inspect six recorded synthetic scenarios from the offline prototype. Each shows the routing outcome, customer-facing text, and available evidence. The examples run as a static walkthrough in the browser.

Any future public source release should use synthetic fixtures and redacted summaries. Original slide images, credentials, private operational traces, and reviewer identities stay outside the public snapshot.

### Source record

- **Original concept:** @DataScienceBrain’s user-supplied tutorial images, `IMG_2191.jpeg` through `IMG_2206.jpeg`, checked against `docs/slide-source.sha256`.
- **Prototype record:** `Jev_Routed_GenAI_Support_Desk_v0.1.1.zip`. Within the archive, see `docs/project-charter.md`, `docs/architecture.md`, `reports/before-after/v0.1.1.md`, `reports/failure-register.md`, `reports/local-verification.md`, `deploy/restore-drill.md`, `validation/protocol.md`, and the two November 11 JSON runs in `benchmarks/runs/`.
- **Portfolio conventions:** [Portfolio entry point](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/main/START_HERE.md) · [November 7 evidence register](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/main/docs/CURRENT_EVIDENCE_2026-11-07.md) · [Recruiter snapshots](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/main/docs/PORTFOLIO_PROJECT_SNAPSHOTS.md) · [Production rollout](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/main/docs/PRODUCTION_ROLLOUT.md) · [Validation queue](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/main/docs/VALIDATION_NEXT_SESSION_2026-11-06.md).
