# Environments

Branch-to-environment mapping: `../../docs/BRANCHING_AND_RELEASE.md` in the project folder.

## GitHub environment variables (set in `dev` and `itg`)

| Name | Type | Value |
|---|---|---|
| `AZURE_TENANT_ID` | variable | Tenant ID |
| `AZURE_SUBSCRIPTION_ID` | variable | Subscription ID |
| `AZURE_CLIENT_ID` | variable | `gh-pokedex-backend-<env>` client ID |
| `AZURE_RESOURCE_GROUP` | variable | `rg-pokedex-<env>` |
| `AZURE_ACR_NAME` | variable | `crpokedex<env><suffix>` |
| `AZURE_CONTAINERAPP_NAME` | variable | `ca-backend-pokedex-<env>` |
| `AGENT_CONTAINERAPP_NAME` | variable | `ca-agent-pokedex-<env>` (used to find the agent's internal URL) |
| `AGENT_APP_SCOPE` | variable | Scope of the agent app, `api://<agent-app-client-id>/.default`. Open item, see ARCHITECTURE.md |
| `UI_ORIGIN` | variable | UI origin for CORS, for example `https://swa-pokedex-<env>-<suffix>.azurestaticapps.net` |

The deploy job sets `AZURE_TENANT_ID`, `AUTH_AUDIENCE` (`api://pokedex-api`), `AGENT_APP_URL` (resolved at deploy time), `AGENT_APP_SCOPE`, `ALLOWED_ORIGINS`, and `AGENT_TIMEOUT_S` on the Container App.

## Runtime

- External ingress on port 8000. The UI calls it.
- The container uses the backend managed identity (`AZURE_CLIENT_ID` is set by Bicep).
- Only `/healthz` is public. `/api/v1/chat` requires a user token.
