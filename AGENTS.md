# AGENTS.md: pokedex_backend

Read the parent `../AGENTS.md` first. Its rules apply here.

## Purpose

The API between the UI and the agents. It validates user tokens, applies request limits, and forwards questions to `pokedex_agent_app`. It runs in Azure Container Apps with external ingress. The agent app is internal.

## Layout

| Path | Contents |
|---|---|
| `src/pokedex_backend/config.py` | Settings from environment variables |
| `src/pokedex_backend/auth.py` | Entra ID token validation and scope check |
| `src/pokedex_backend/agent_client.py` | Calls the agent app with the managed identity |
| `src/pokedex_backend/models.py` | Request and response models |
| `src/pokedex_backend/main.py` | FastAPI app and routes |
| `tests/` | pytest tests. They must not call Azure or the agent app. |
| `Dockerfile` | Container image |
| `.github/workflows/` | CI and deploy |
| `docs/ARCHITECTURE.md` | Why this service exists, and the alternatives |

## Rules for agents

- Every route except `/healthz` must require a valid Entra token with the `access_as_user` scope. Do not add an unauthenticated route without a human decision.
- Validate the token issuer, audience, signature, and expiry. Never decode a token without verifying it.
- Limit message length (2000 characters, already in `models.py`). Keep the limit.
- Call the agent app with a managed identity token for `AGENT_APP_SCOPE`. Do not forward the user's token to the agent app.
- Do not log message text or tokens. Log the user object ID (`oid`) and the request ID.
- Keep CORS origins in `ALLOWED_ORIGINS`. Never use a wildcard origin.
- Add a test for every route and every new auth rule.
- Log every change in `AGENT_CHANGELOG.md`.
