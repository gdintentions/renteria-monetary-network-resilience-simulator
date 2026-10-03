# Hosted Demo-Safe Showcase

This directory is the static browser-hosted presentation layer for selected Renteria AI Systems portfolio projects.

## Included interactive demos

- Governed RAG — evidence ranking, abstention, heuristic confidence, and safe/review/block routing
- Polyglot Relay — controlled phrase translation with explicit unsupported and review states
- Context Atlas — explainable synthetic knowledge graph with explicit and missing links
- Monetary Network Resilience Simulator — deterministic synthetic browser scenario model

## Privacy and IP boundary

The hosted site is intentionally independent from the private working repositories. It contains:

- synthetic fixtures only
- reduced client-side logic
- no credentials or API keys
- no uploads
- no personal records
- no private prompts
- no provider integrations
- no database or persistence

The site demonstrates engineering patterns without publishing the fuller private implementations.

## Hosting

GitHub Actions workflow: `.github/workflows/pages-demo-safe.yml`

The workflow verifies the static site, packages `hosted_demo/` as a GitHub Pages artifact, and deploys it after GitHub Pages is enabled for the repository with **GitHub Actions** as the publishing source.

Expected GitHub Pages URL after activation:

`https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/`

## Local preview

Any static web server can serve the directory, for example:

```bash
python -m http.server 8000 --directory hosted_demo
```

Then open `http://127.0.0.1:8000/`.
