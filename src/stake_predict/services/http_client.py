"""Shared async HTTP client. All outbound calls go through here."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import httpx
import structlog

log = structlog.get_logger(__name__)


class RateLimitedClient:
    """Wraps httpx.AsyncClient with a token-bucket limiter (default 5 rps)."""

    def __init__(self, base_url: str, rps: float = 5.0, timeout: float = 10.0) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._interval = 1.0 / rps
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def _throttle(self) -> None:
        async with self._lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            wait = self._interval - (now - self._last)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last = loop.time()

    async def get_json(self, path: str, **params: object) -> dict[str, object]:
        await self._throttle()
        resp = await self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def stream_sse(self, path: str) -> AsyncIterator[dict[str, object]]:
        import json

        async with self._client.stream("GET", path) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data:"):
                    yield json.loads(line[5:].strip())

    async def aclose(self) -> None:
        await self._client.aclose()