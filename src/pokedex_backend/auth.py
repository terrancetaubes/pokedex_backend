"""Entra ID access token validation for user tokens."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from pokedex_backend.config import Settings

REQUIRED_SCOPE = "access_as_user"
_bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=4)
def _jwks_client(jwks_uri: str) -> jwt.PyJWKClient:
    # PyJWKClient caches the signing keys and refreshes them when needed.
    return jwt.PyJWKClient(jwks_uri)


def verify_token(token: str, settings: Settings) -> dict:
    """Return the verified claims, or raise jwt.PyJWTError."""
    signing_key = _jwks_client(settings.jwks_uri).get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.auth_audience,
        issuer=settings.issuer,
        options={"require": ["exp", "aud", "iss", "oid"]},
    )


def require_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    settings: Settings = request.app.state.settings
    try:
        claims = verify_token(credentials.credentials, settings)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    scopes = str(claims.get("scp", "")).split()
    if REQUIRED_SCOPE not in scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return claims
