# Portfolio evidence review — 25 September 2026

## Scope and method

This review covers the five GitHub repositories available to the account and the two projects nested in the public monetary simulator repository. The checks below used the proposed audit branches, not production deployments. All sample documents, benchmark questions, stress distributions, and monetary shocks are authored fixtures. No independent user study, real transaction dataset, or real translation quality dataset was supplied.

## Reproducible code checks

| Project | Command | Observed result | What the result establishes |
|---|---|---:|---|
| Monetary simulator and recruiter demo | `python -m pytest -q` | 11 passed | Current deterministic unit checks pass, including invalid scenario inputs |
| ArgusLoop | `PYTHONPATH=src python -m pytest -q` | 6 passed | Current policy and coordinate tests pass |
| EvidenceWeave | `PYTHONPATH=src python -m pytest -q` | 6 passed | Current synthetic pipeline and scoring tests pass |
| Governed RAG core | `python -m pytest -q` | 6 passed | Current retrieval and risk flag tests pass |
| Governed RAG demo | `python -m pytest -q` | 4 passed | Current sample benchmark and reproducibility tests pass |
| Governed RAG model lab v2 | `python -m pytest -q` | 4 passed | Current retrieval comparison tests pass |
| Polyglot Relay | `node --test tests/models.test.js`; `npm run build` | 3 passed; build passed | Numerical model tests and a Vite production build pass |

The command results are observations on these versions, not evidence of production security, accessibility, or deployment uptime. The Polyglot test suite does not exercise browser interactions.

## Targeted findings and corrections

1. The small RAG demo previously answered “What is the vacation policy?” from an unrelated legal-policy section. A minimum of two distinct matching query terms now gates its answer. Its four authored benchmark cases now return four expected outcomes, including abstention. This gate can still miss paraphrases and accept coincidental overlap.
2. Polyglot Relay previously showed the input text after an adapter-required label for unsupported translation. It now returns an explicit unavailable message and does not speak that message. Language pairs other than listed English sample phrases remain unsupported.
3. The monetary simulator previously treated an explicit empty agent list as defaults. It now rejects empty, duplicate, malformed-share, and unknown-shock inputs. The default run still uses illustrative parameters.
4. The RAG core now rejects `k < 1` and matches risk terms at word boundaries, avoiding substring hits such as “legalized.” Its confidence formula is uncalibrated.
5. The ArgusLoop action-contract table called planner confidence calibrated. It is self-reported, as its limitations section already explained. The table now says so.

## Synthetic benchmark results

The RAG demo v1 has 4/4 expected outcomes after the abstention fix on four authored questions. In demo v2, Jaccard and TF-IDF each obtain top-1 accuracy 0.80, MRR 0.84, and Hit@3 0.80; trigram and hybrid each obtain 1.00 on all three metrics. These numbers describe only five questions written around five sample sections. They cannot rank models on an external corpus.

## Monetary sensitivity experiment

For each of 100 deterministic seeds 0–99, the model was run for 15 years with default shocks and with no shocks. Final-year model shares below are percentages within the simulation, reported as minimum / median / maximum across seeds:

| Network | Default shocks | No shocks |
|---|---:|---:|
| US / USD | 16.448 / 18.050 / 20.377 | 40.451 / 43.095 / 47.037 |
| BRICS settlement | 26.439 / 29.323 / 35.074 | 15.779 / 17.673 / 21.782 |
| Europe / EUR | 13.939 / 16.353 / 18.204 | 14.288 / 16.426 / 18.102 |

This large scenario difference shows sensitivity to assumed shocks. These are relative modeled attractiveness shares, not observed settlement shares, reserve shares, probabilities, or forecasts. Changing the parameters changes the results; the experiment does not validate the shock sizes.

## Claims that remain unproven

- **Demand:** No interviews, user tasks, retention, willingness-to-pay, or comparative workflow data. Each project has an intended use, but product-market fit has not been shown.
- **External quality:** The RAG and EvidenceWeave fixtures are synthetic. Gather independently labeled held-out questions, sources, contradictions, and negative examples; publish citation precision, abstention errors, false alerts, and reviewer time.
- **Polyglot translation and accessibility:** Recruit bilingual reviewers and test browser speech and keyboard/screen-reader flows across supported devices. The model’s quality and latency numbers are assumptions.
- **ArgusLoop safety:** Conduct supervised tests in a disposable desktop environment with adversarial screens, independent task completion checks, and measured false approvals. Unit policy checks do not prove safe live automation.
- **Monetary forecasting:** Calibrate the baseline and shock model against defined historical settlement indicators, document source dates and uncertainty, and backtest held-out periods before any predictive claim.

The accurate portfolio positioning today is **working prototypes and inspectable methods with synthetic demonstrations**. None of these test results establishes real-world effectiveness or commercial need.
