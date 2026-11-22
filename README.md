# pokedex_backend

The API between `pokedex_ui` and `pokedex_agent_app`. It is a FastAPI service in Azure Container Apps.

## Routes

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/healthz` | None | Health probe |
| POST | `/api/v1/chat` | Bearer token, scope `access_as_user` | Send a question to the agents |

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
pytest
```

Copy `.env.example` to `.env` for local settings. Never commit `.env`.

## Deploy

- Merge to `develop`: CI, then deploy to `dev`.
- Push to `release/<n>`: CI, then deploy to `itg`.

The deploy is a reusable workflow (`deploy.yml`). Settings come from the GitHub environment. See `docs/ENVIRONMENTS.md`.

See `docs/ARCHITECTURE.md`, `docs/RUNBOOK.md`, and `SECURITY.md`.
