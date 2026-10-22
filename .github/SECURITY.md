# Security policy — public portfolio

## Scope

This repository contains **educational and synthetic demo applications**, source, tests and documentation. Public source does **not** mean a production service is offered, and the hosted browser demonstrations are not authorized to process real confidential data.

## Reporting

Please do **not** post credentials, private user information, exploit payloads against real systems or sensitive findings in public GitHub issues or pull requests.

Use GitHub's **Report a vulnerability** / private vulnerability reporting option for this repository **if available and enabled**. If private vulnerability reporting is unavailable, do not publish sensitive details in a public issue; use a trusted private channel agreed with the repository owner. No private response email or security SLA is published here.

## Protecting credentials and private material

- Never commit secret values, personal records, real confidential corpora, production tokens, or `.env` files.
- Use synthetic fixtures and local mocks for public screenshots and examples.
- Keep original private implementations in their private repositories. Avoid mirroring private Git histories.
- Review Git history, pull request diffs, CI artifacts and published Pages bundles before public releases.
- Rotate and revoke any token that may have been exposed; deleting a commit does not by itself invalidate a credential.
- The [scoped static publication check](../scripts/check_public_release.py) is supplementary and **cannot establish that a repository is secret-free**.

## Support and limitations

The simulations have documented limitations and are not presented as independently validated production security systems. See the [public source guide](../PUBLIC_SOURCE_GUIDE.md) and [release evidence](../docs/RELIABILITY_RELEASE.md).
