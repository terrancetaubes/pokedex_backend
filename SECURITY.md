# Security policy

## Reporting a vulnerability

Do not open a public issue. Contact the repository owner directly through a private channel.

## Rules

- Every route except `/healthz` requires an Entra ID access token with the `access_as_user` scope.
- Tokens are verified for signature (JWKS), issuer, audience, and expiry.
- The service calls the agent app with its own managed identity. It never forwards user tokens.
- CORS allows only the origins in `ALLOWED_ORIGINS`.
- Inputs are length-limited and typed with Pydantic.
- Logs contain the user object ID and request ID, not message text or tokens.
- Container runs as a non-root user.
