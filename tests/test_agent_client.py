"""Tests for the call to the agent app. They use a mock HTTP transport and a fake token, so no Azure call is made."""

import asyncio
import json

import httpx
import pytest

from pokedex_backend import agent_client
from pokedex_backend.config import Settings
from pokedex_backend.models import ChatResponse


def _settings() -> Settings:
    return Settings(
        tenant_id="00000000-0000-0000-0000-000000000000",
        auth_audience="api://pokedex-api",
        agent_app_url="http://agent.internal",
        agent_app_scope="api://agent/.default",
        allowed_origins=("https://ui.example",),
        agent_timeout_s=5,
    )


class _FakeToken:
    token = "agent-token"


class _FakeCredential:
    def get_token(self, scope: str) -> _FakeToken:
        assert scope == "api://agent/.default"
        return _FakeToken()


@pytest.fixture(autouse=True)
def fake_credential(monkeypatch):
    monkeypatch.setattr(agent_client, "_credential", lambda: _FakeCredential())


def _run_ask(handler, message: str = "Who is Pikachu?") -> ChatResponse:
    async def go() -> ChatResponse:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await agent_client.ask_agent(client, _settings(), message, "user-oid-1")

    return asyncio.run(go())


def test_ask_agent_sends_message_with_agent_token_and_parses_answer():
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["oid"] = request.headers["x-requesting-user-oid"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200, json={"answer": "Pikachu is an Electric type.", "sources": ["pokeapi"]}
        )

    result = _run_ask(handler)

    assert seen["url"] == "http://agent.internal/v1/chat"
    assert seen["auth"] == "Bearer agent-token"
    assert seen["oid"] == "user-oid-1"
    assert seen["body"] == {"message": "Who is Pikachu?"}
    assert result == ChatResponse(answer="Pikachu is an Electric type.", sources=["pokeapi"])


def test_ask_agent_raises_when_agent_returns_error():
    # The route maps httpx errors to 502, so an agent error must raise.
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(501, json={"detail": "not implemented"})

    with pytest.raises(httpx.HTTPStatusError):
        _run_ask(handler)
