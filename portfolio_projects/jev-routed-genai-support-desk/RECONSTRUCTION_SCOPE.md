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
