"""Async client for a remote opencode serve HTTP API."""
from __future__ import annotations
import logging
from typing import Any
import httpx
from config import Settings

logger = logging.getLogger("opencode_bridge.client")

class OpenCodeError(RuntimeError):
    pass

class OpenCodeClient:
    def __init__(self, settings: Settings):
        self.base_url = settings.opencode_url.rstrip("/")
        self.auth = (settings.opencode_username, settings.opencode_password) if settings.opencode_password else None
        self.timeout = settings.opencode_timeout_s

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, auth=self.auth, timeout=httpx.Timeout(self.timeout, connect=10.0))

    async def health(self) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.get("/global/health")
            resp.raise_for_status()
            return resp.json()

    async def create_session(self, title: str | None = None) -> str:
        payload: dict[str, Any] = {}
        if title:
            payload["title"] = title
        async with self._client() as client:
            resp = await client.post("/session", json=payload)
            resp.raise_for_status()
            data = resp.json()
            session_id = data.get("id") or data.get("sessionID")
            if not session_id:
                raise OpenCodeError(f"Unexpected session creation response: {data}")
            return session_id

    async def send_message(self, session_id: str, prompt: str, agent: str | None = None, model: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"parts": [{"type": "text", "text": prompt}]}
        if agent: payload["agent"] = agent
        if model: payload["model"] = model
        async with self._client() as client:
            resp = await client.post(f"/session/{session_id}/message", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def get_diff(self, session_id: str) -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get(f"/session/{session_id}/diff")
            if resp.status_code == 404: return []
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else []

    async def abort(self, session_id: str) -> bool:
        async with self._client() as client:
            resp = await client.post(f"/session/{session_id}/abort")
            if resp.status_code == 404: return False
            resp.raise_for_status()
            return bool(resp.json())
