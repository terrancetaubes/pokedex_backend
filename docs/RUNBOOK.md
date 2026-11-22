# Runbook

## Users get 401

1. Check that the UI's `apiScope` matches `api://pokedex-api/access_as_user`.
2. Check that the API app registration has token version 2 (`requestedAccessTokenVersion`).
3. Check the token's issuer. It must match `https://login.microsoftonline.com/<tenant>/v2.0`.

## Users get 403

The token has no `access_as_user` scope. Check admin consent for the UI app.

## Users get 502 or 504

The agent app is unreachable or slow. Check `AGENT_APP_URL`, the agent's revision health, and `AGENT_TIMEOUT_S`. A 502 is also expected while the agent returns 501 (orchestration not built yet).

## Deploy fails at "Resolve agent app URL"

The agent app does not exist in this environment yet. Run the platform deployment in `pokedex_infra` first.

## Roll back

`az containerapp update --name <app> --resource-group <rg> --image <acr>.azurecr.io/pokedex-backend:<previous-sha>`, then revert the commit.
