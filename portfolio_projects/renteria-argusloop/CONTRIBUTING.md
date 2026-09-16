# Contributing

1. Create a focused branch.
2. Do not include API keys, screenshots, audit logs, or personal data.
3. Add tests for behavior changes.
4. Run `python -m ruff check .` and `python -m pytest`.
5. Explain any change to the policy boundary in the pull request.

Safety controls should fail closed. New action types require schema validation, policy rules,
execution tests, threat-model updates, and documentation.

