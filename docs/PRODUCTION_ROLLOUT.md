# Portfolio production rollout model — October 5, 2026 UTC

Governed RAG is the first hardened **supervised service candidate**. API v2 adds
named bearer roles, durable evidence/review/audit records, review withholding,
bounded input/rates, known-pattern risk gates, backup tooling, service dependency
pins and container CI. Its PRs [9](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/pull/9)
and [10](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/pull/10)
are merged. The hardening head passed Python CI, dependency audit and container
build/smoke. It is not a completed real-policy production validation or public
service deployment.

## Reusable completion standard

1. State the actual use scope, data authority and prohibited automatic actions.
2. Test the intended trust boundary, identity/roles and data ownership.
3. Retain source/output/version evidence and make approvals auditable.
4. Bound inputs/concurrency and fail without releasing unsupported drafts or
   silently resetting data.
5. Test durable state, backup/recovery and rollback appropriate to the runtime.
6. Preserve independent labels, publish failures and distinguish synthetic,
   controlled, external-domain and real deployment evidence.
7. Verify the selected host, TLS/resource limits, monitoring and incident owner.
8. Record actual acceptance by the intended operator before claiming readiness.

These principles transfer; implementations and quality metrics differ by project.
A simulator is not a RAG assistant, and a static translation prototype cannot gain
a live provider merely by copying API authentication.

## Current project-specific position

| Project | Evidence already available | Remaining completion gate |
|---|---|---|
| Governed RAG | 51 local tests; deployed local smoke; pinned-dependency audit; GitHub container smoke and Python checks; NFCorpus report | Real-policy independent holdout; selected-host capacity/recovery/TLS; operator acceptance |
| Monetary Simulator | 25-run sensitivity; one BIS historical proxy interval; published wrong directions | More historical targets/windows and identifiability; intended-host release/recovery |
| ArgusLoop | 21/21 deterministic controls with fake desktop adapter in disposable CI | Supervised real-GUI completion and false approval/block benchmark; synthetic accounts and isolated desktop |
| EvidenceWeave | ConflictQA structured conflict results: recall 0.4000, 258 misses, 4 false positives | Better normalization/recall on unchanged labels; independently labeled free-text extraction before text-reasoning claims |
| Polyglot Relay | Working static text/speech prototype and placeholder dictionary | Chosen permitted translation/speech provider, backend identity and independent language quality evaluation |
| Context Atlas | Local note graph and tests; recovery/request-boundary hardening PR | Independently judged links/import behavior; supported hosted service if multi-user use is intended |
| Local Model Workbench | Loopback runtime adapter and tests; recovery/request-boundary hardening PR | Actual installed model quality/repeated latency; model/runtime provenance |
| Notes Evidence RAG | Excerpts, citation-ID checks and explicit generated drafts; hardening PR | Actual claim-support review, no-answer/conflict/injection holdout; hosted identity if required |
| Personal Assistant Ledger | Durable local queue/state-machine tests; hardening PR | Multi-day recovery/timezone drill; external delivery remains excluded pending authorized adapters |
| RAG recruiter demos | Synthetic Streamlit examples and separate demo repositories | Version parity, clear synthetic labels and bounded public hosting; no enterprise-policy accuracy inference |

The four local hardening patches add explicit connection closure, private
state/backup creation, verified SQLite backup, socket timeouts, ambiguous/truncated
body rejection and cross-origin session denial. All existing/new local tests
passed: Atlas 14, Workbench 15, Notes RAG 14, Ledger 15. Their PR/CI status is
separate from local test evidence. All four hardening PRs subsequently passed
GitHub CI and were merged. They remain loopback-only single-user prototypes.

## Machine-readable release gates

`RELEASE_GATES.json` tracks ten portfolio components. All production_ready flags
currently remain false because actual domain/operator/host gates remain open.
Run `python release_gates.py` for a factual status report; add `--require-ready`
to fail when any gate is pending. CI checks the manifest and regression tests.

The checker enforces distinct projects, complete gates, evidence references for
passed gates and readiness consistent with recorded status. It does not inspect
the truth of an evidence reference or certify an application. Closing a gate
requires actual evidence and review, not editing a boolean.

## Next independent inputs

The first deployment's use scope determines corpus, reviewer competence, hosting,
privacy and acceptance tests. Synthetic recruiter hosting, personal study documents
and real organizational policy use are different release targets. No provider
accounts, credentials, spending commitments, reviewer identities, policy authority
or operator approval have been assumed.

All existing evaluation reports remain intact. The current reports index measures
specific external/controlled tasks; it must not be renamed as general production
certification.
