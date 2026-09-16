# Model card

## Intended use

Research, education, document comparison, evidence triage, and recruiter demonstrations using
public or synthetic material.

## Out of scope

EvidenceWeave must not autonomously decide medical care, legal rights, employment, credit,
insurance, policing, or financial transactions. The score is a prioritization aid, not proof.

## Known limitations

- Lexical cosine retrieval does not capture every paraphrase.
- Contradiction detection currently compares explicit subject–predicate values.
- Source authority and freshness are configured inputs and can encode human bias.
- Vision and table extraction errors can propagate into claims.
- A high Evidence Integrity Score does not establish real-world truth.

## Evaluation targets

Track retrieval Hit@k, citation precision, conflict recall, claim exact match, score calibration
(Brier score / expected calibration error), latency, and abstention quality.

