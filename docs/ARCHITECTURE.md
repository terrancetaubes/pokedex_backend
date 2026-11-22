# Architecture

## Is a backend needed?

Yes. The UI cannot call the agents directly, for these reasons:

1. **Credentials.** A managed identity works only on the server. A browser cannot use it. The agent app needs a server-side identity to call the data services.
2. **Trust boundary.** Browser code is public. Anything in it can be read or changed by a user. Token checks, request limits, and tool-call limits must run on the server.
3. **Stable contract.** The backend gives the UI one API. The agent internals can change without a UI release.
4. **Cross-cutting concerns.** Logging, rate limits, audit records, and later streaming responses belong on the server.

## Options

| Option | Strength | Trade-off |
|---|---|---|
| **Separate backend** (chosen, this repository) | Clear boundary, independent scaling and release, one place for auth and limits | One more service to build, deploy, and monitor |
| Merge into `pokedex_agent_app` (expose an HTTP API there) | Fewer services, lower cost, faster MVP | The agent repo becomes both API and agent logic. Auth and agent code change together. |
| Azure API Management in front of the agents | Built-in throttling, keys, policies, developer portal | Higher cost and setup time. Overkill for an MVP. |
| Call the agents directly from the UI | Least code | Not acceptable. Exposes the agent endpoint and breaks the trust boundary. |

## Decision

Keep the separate backend. It costs one small Container App. It keeps authentication and limits in one place. If the team later wants fewer services, merge it into the agent app and keep this repository's routes and tests.

## Request flow

1. UI signs the user in with MSAL and gets a token for `api://pokedex-api`.
2. UI calls `POST /api/v1/chat` with the token.
3. Backend verifies the token and the `access_as_user` scope.
4. Backend gets a managed identity token for the agent app and calls `POST /v1/chat`.
5. Backend returns the answer and sources to the UI.

## Open item

The agent app has no HTTP endpoint yet. The contract `POST /v1/chat` with body `{"message": str}` and response `{"answer": str, "sources": [str]}` is the assumption in `agent_client.py`. Build it in `pokedex_agent_app` before the first end-to-end test. The agent app must also validate the managed identity token.
