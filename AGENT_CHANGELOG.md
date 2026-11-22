# Agent change log: pokedex_backend

Each entry records one change made by an agent. Newest entries first.

| Date | Change | Reason | Files |
|---|---|---|---|
| 2026-11-22 | Replaced workflows with `ci-cd.yml` (CI, then reusable `deploy.yml` to dev on develop and itg on release/**). Deploy resolves the agent URL at run time and sets all app settings from GitHub environment variables. Added environment and runbook docs. | Release pattern; no hard-coded settings | `.github/workflows/*`, `README.md`, `docs/*` |
| 2026-11-21 | Created FastAPI backend with Entra token validation, chat route, tests, and CI/CD | Initial setup | All files |
