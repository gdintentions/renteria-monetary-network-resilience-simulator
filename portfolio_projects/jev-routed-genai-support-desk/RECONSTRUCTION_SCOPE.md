# JEV runnable clean-room reconstruction (separate from original v0.1.1)

This branch adds `reconstructed_router.py` and reproducible synthetic regression tests.
The original `Jev_Routed_GenAI_Support_Desk_v0.1.1.zip` and historical exact R29/R30 inputs were **not located** in the accessible GitHub project. No archive recovery, integration, or performance improvement over the historical 33/35 has been demonstrated.

## Safe scope

- Local deterministic routing, no live Jev/Groq adapter, model inference, refund, account access or customer delivery
- Tracking and exchange paraphrases lead to guarded candidate dispositions
- Human/sensitive cases have precedence; mixed intents abstain
- Synthetic verification flags are not authentication
- Draft guard only allows *agent review*, never delivery or automatic factual certification
- All preexisting historical runs and the old original specification remain untouched

## Verification and follow-up

Run: `cd portfolio_projects/jev-routed-genai-support-desk && python -m unittest discover -s . -p 'test_reconstructed_router.py' -v`.

Do not compare its authored tests numerically with the archived 35-case baseline. Obtain the original archive and exact historical inputs first; pin source hashes; run original router unchanged; apply a separately reviewed patch; compare route and handoff quality on identical old fixtures and a genuinely fresh blinded set; retain raw failures and human sign-off. See [issue #27](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/issues/27).

## CI result — November 16, 2026

[Reconstructed Router Tests, run #43834358157](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43834358157): **passed** (10 authored Python unittest test methods). An earlier run #43834235395 failed two checks: the guard did not hold the wording "refund is guaranteed," and the handler did not escalate "card was stolen." Both checks passed after explicit regex updates. Preserve the failed workflow and before/after commits in GitHub history.

This establishes testable local routing behavior only; it cannot replace the unavailable original v0.1.1 source, its exact R29/R30 ticket texts, or an independent human review. No safe delivery channel exists and no production usage is authorized.
