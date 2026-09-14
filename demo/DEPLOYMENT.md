# Public Demo Deployment

The recruiter demo is prepared for Streamlit Community Cloud.

## Deployment configuration

Use these values when creating the Streamlit app:

- GitHub repository: `gdintentions/renteria-monetary-network-resilience-simulator`
- Branch: `main`
- App entrypoint: `demo/recruiter_app.py`
- Python dependencies: root `requirements.txt`
- Streamlit configuration: root `.streamlit/config.toml`

## Deploy

1. Sign in to Streamlit Community Cloud with GitHub.
2. Create a new app.
3. Select the repository above.
4. Select the `main` branch.
5. Set the entrypoint to `demo/recruiter_app.py`.
6. Choose the desired public `streamlit.app` subdomain.
7. Deploy.

No application secrets are required for this demo because the calibration dataset is committed as a small static CSV and the simulation runs locally in the app process.

## Why no live external API calls

The public demo intentionally avoids runtime calls to IMF, BIS, or third-party APIs. This keeps the portfolio build:

- reproducible
- fast to start
- robust to external API outages and schema changes
- free of API keys and secret-management requirements

When the historical anchor file is refreshed, the source URLs and dates should be updated in `demo/data/calibration_reference.csv`.

## After deployment

Add the resulting public `https://<subdomain>.streamlit.app/` address to the repository README and GitHub repository website field.
