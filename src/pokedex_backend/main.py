"""FastAPI application factory."""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from pokedex_backend.agent_client import ask_agent
from pokedex_backend.auth import require_user
from pokedex_backend.config import Settings
from pokedex_backend.models import ChatRequest, ChatResponse

log = logging.getLogger("pokedex_backend")

AskFn = Callable[[Settings, str, str], Awaitable[ChatResponse]]


def create_app(settings: Settings | None = None, ask: AskFn | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    http = httpx.AsyncClient()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await http.aclose()

    app = FastAPI(title="Pokedex backend", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=False,
    )

    async def default_ask(s: Settings, message: str, user_oid: str) -> ChatResponse:
        return await ask_agent(http, s, message, user_oid)

    ask_fn: AskFn = ask or default_ask

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["x-request-id"] = rid
        return response

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"status": "ok"}

    @app.post("/api/v1/chat", response_model=ChatResponse)
    async def chat(
        body: ChatRequest, claims: Annotated[dict, Depends(require_user)]
    ) -> ChatResponse:
        oid = str(claims.get("oid", ""))
        try:
            result = await ask_fn(settings, body.message, oid)
        except httpx.TimeoutException:
            log.warning("agent timeout oid=%s", oid)
            raise HTTPException(status_code=504, detail="The agents took too long to answer.")
        except httpx.HTTPError:
            log.exception("agent call failed oid=%s", oid)
            raise HTTPException(status_code=502, detail="The agents are unavailable.")
        log.info("chat ok oid=%s", oid)
        return result

    return app
