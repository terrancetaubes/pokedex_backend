"""Calls the agent app with this service's managed identity.

Contract (assumed, to be built in pokedex_agent_app):
  POST {AGENT_APP_URL}/v1/chat   body: {"message": str}
  200 response:                  {"answer": str, "sources": [str]}
"""

from __future__ import annotations

import asyncio
from functools import lru_cache

import httpx
from azure.identity import DefaultAzureCredential

from pokedex_backend.config import Settings
from pokedex_backend.models import ChatResponse


@lru_cache(maxsize=1)
def _credential() -> DefaultAzureCredential:
    # Uses AZURE_CLIENT_ID to pick the user-assigned managed identity in Azure.
    return DefaultAzureCredential()


async def ask_agent(
    client: httpx.AsyncClient, settings: Settings, message: str, user_oid: str
) -> ChatResponse:
    # get_token is blocking, so run it in a worker thread.
    token = await asyncio.to_thread(
        lambda: _credential().get_token(settings.agent_app_scope).token
    )
    response = await client.post(
        f"{settings.agent_app_url}/v1/chat",
        json={"message": message},
        headers={
            "Authorization": f"Bearer {token}",
            # Audit only. The agent app must not use this for authorization.
            "X-Requesting-User-Oid": user_oid,
        },
        timeout=settings.agent_timeout_s,
    )
    response.raise_for_status()
    return ChatResponse.model_validate(response.json())
