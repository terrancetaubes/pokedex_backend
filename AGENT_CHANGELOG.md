# Agent change log: pokedex_backend

Each entry records one change made by an agent. Newest entries first.

| Date | Change | Reason | Files |
|---|---|---|---|
| 2026-11-21 | Replaced the deprecated `@app.on_event("shutdown")` hook with a FastAPI `lifespan` handler that closes the shared HTTP client. Behavior is unchanged. Tests run with no deprecation warnings from app code. | FastAPI deprecates `on_event`. | `src/pokedex_backend/main.py`, `AGENT_CHANGELOG.md` |
| 2026-11-21 | Fixed three `ruff check` findings that CI would fail on with the current ruff (B008 on `Depends` defaults in `auth.py` and `main.py`, UP037 quoted annotation in `config.py`). `Depends` now uses `Annotated[...]`, which is the FastAPI form. Behavior is unchanged. Added `tests/test_agent_client.py`, which tests the call to the agent app (URL, agent token, `X-Requesting-User-Oid` header, response parsing, error on agent error) with a mock transport and no Azure call. Test count: 7 to 9. | Lint gate was red. The agent call had no test. | `src/pokedex_backend/auth.py`, `src/pokedex_backend/main.py`, `src/pokedex_backend/config.py`, `tests/test_agent_client.py`, `AGENT_CHANGELOG.md` |
| 2026-11-21 | Corrected this entry's date from 2026-11-22 to today's date (2026-11-21). The date was wrong. No content change. | Date must match the work session. | `AGENT_CHANGELOG.md` |
| 2026-11-21 | Replaced workflows with `ci-cd.yml` (CI, then reusable `deploy.yml` to dev on develop and itg on release/**). Deploy resolves the agent URL at run time and sets all app settings from GitHub environment variables. Added environment and runbook docs. | Release pattern; no hard-coded settings | `.github/workflows/*`, `README.md`, `docs/*` |
| 2026-11-21 | Created FastAPI backend with Entra token validation, chat route, tests, and CI/CD | Initial setup | All files |
