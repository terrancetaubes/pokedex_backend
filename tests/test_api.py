import pytest
from fastapi.testclient import TestClient

from pokedex_backend.auth import require_user
from pokedex_backend.config import Settings
from pokedex_backend.main import create_app
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


async def _fake_ask(settings, message, oid):
    return ChatResponse(answer=f"echo: {message}", sources=["test"])


@pytest.fixture
def client():
    app = create_app(settings=_settings(), ask=_fake_ask)
    return TestClient(app)


def test_health_is_public(client):
    assert client.get("/healthz").status_code == 200


def test_chat_requires_token(client):
    response = client.post("/api/v1/chat", json={"message": "hi"})
    assert response.status_code == 401


def test_chat_rejects_bad_token(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "hi"},
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert response.status_code == 401


def test_chat_with_verified_user(client):
    client.app.dependency_overrides[require_user] = lambda: {"oid": "u1", "scp": "access_as_user"}
    response = client.post("/api/v1/chat", json={"message": "Pikachu?"})
    assert response.status_code == 200
    assert response.json() == {"answer": "echo: Pikachu?", "sources": ["test"]}


def test_chat_rejects_empty_and_long_messages(client):
    client.app.dependency_overrides[require_user] = lambda: {"oid": "u1"}
    assert client.post("/api/v1/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/v1/chat", json={"message": "x" * 2001}).status_code == 422


def test_cors_rejects_unknown_origin(client):
    response = client.options(
        "/api/v1/chat",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in response.headers


def test_settings_reject_wildcard_origin(monkeypatch):
    monkeypatch.setenv("AZURE_TENANT_ID", "t")
    monkeypatch.setenv("AUTH_AUDIENCE", "api://x")
    monkeypatch.setenv("AGENT_APP_URL", "http://a")
    monkeypatch.setenv("AGENT_APP_SCOPE", "api://a/.default")
    monkeypatch.setenv("ALLOWED_ORIGINS", "*")
    with pytest.raises(RuntimeError):
        Settings.from_env()
