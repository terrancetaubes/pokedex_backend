"""Settings from environment variables. Holds no secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    tenant_id: str
    auth_audience: str          # for example api://pokedex-api
    agent_app_url: str          # internal URL of pokedex_agent_app
    agent_app_scope: str        # for example api://<agent-app-client-id>/.default
    allowed_origins: tuple[str, ...]
    agent_timeout_s: float

    @property
    def issuer(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"

    @property
    def jwks_uri(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys"

    @classmethod
    def from_env(cls) -> "Settings":
        def required(name: str) -> str:
            value = os.environ.get(name, "").strip()
            if not value:
                raise RuntimeError(f"Missing required setting: {name}")
            return value

        origins = tuple(
            o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()
        )
        if "*" in origins:
            raise RuntimeError("ALLOWED_ORIGINS must not contain a wildcard")

        return cls(
            tenant_id=required("AZURE_TENANT_ID"),
            auth_audience=required("AUTH_AUDIENCE"),
            agent_app_url=required("AGENT_APP_URL").rstrip("/"),
            agent_app_scope=required("AGENT_APP_SCOPE"),
            allowed_origins=origins,
            agent_timeout_s=float(os.environ.get("AGENT_TIMEOUT_S", "30")),
        )
