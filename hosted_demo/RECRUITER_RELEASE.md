# Governed RAG synthetic recruiter release v1.0

Target: a browser-runnable, phone-friendly synthetic demonstration of inspectable
retrieval and supervised release. This is a public JavaScript miniature, not the
authenticated Python service and not an independent enterprise-policy study.

## Demonstrated flow

Create a draft, inspect ranked evidence and cited IDs, then simulate approval or
rejection. Drafts begin withheld; approval reveals an answer, rejection does not.
Known injection and conflicting-cadence examples cannot be approved. Choosing a
new case or changing inputs resets the review state. Reloading the tab discards it.
Downloadable JSON records the synthetic case, sources, heuristic score, release
state and simulated events. No timestamps are invented as human reviewer timing.

All policy texts are authored examples. There are no uploads, credentials,
provider calls, server review persistence or authenticated roles. Any visitor can
click the simulated review controls; these are explicitly labeled as a simulation.
Inputs and traces stay in the tab unless the visitor downloads a trace.

## Validation

Nine Node contract tests cover withholding/release, no-answer abstention, conflict
evidence, question/document injection fixtures, terminal review, input bounds,
isolated histories and a documented lexical-overlap limitation.

The Playwright mobile smoke checks the rendered approval/rejection flow,
blocked conflict/injection controls, trace export, safe text rendering, invalid
input handling, reload isolation, horizontal layout bounds and browser errors.
CI runs these checks before merge. The Pages build also reruns contract tests.
Consult the Synthetic recruiter release workflow for the exact tested revision.

## Evidence limits

The lexical scorer differs from the Python TF-IDF retriever. NFCorpus scores and
failures remain separate evidence for that retriever and are not this demo's
accuracy scores. Regex fixtures do not prove complete injection protection.
Lexical overlap can still select a source that does not answer a question: the
cafeteria-applicability case deliberately retains that limitation. Simulated
approval is not independent policy judgment, measured reviewer time, or security.

This release can be validated for its stated synthetic demonstration scope.
Organizational production readiness remains pending in the portfolio release
manifest. No gate is closed by relabeling these authored cases as real-policy data.
