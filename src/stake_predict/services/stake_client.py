"""Stake client. Wraps the public round feed behind the shared HTTP client."""

from __future__ import annotations

from collections.abc import AsyncIterator

import structlog

from stake_predict.config.settings import Settings
from stake_predict.services.http_client import RateLimitedClient

log = structlog.get_logger(__name__)

_FEED_PATHS = {
    "dice": "/casino/dice/history",
    "limbo": "/casino/limbo/history",
    "keno": "/casino/keno/history",
    "plinko": "/casino/plinko/history",
    "crash": "/casino/crash/history",
}


class StakeClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._http = RateLimitedClient(settings.stake_api_base)

    async def stream_rounds(self) -> AsyncIterator[tuple[str, dict[str, object]]]:
        import asyncio

        while True:
            for game in self._settings.games:
                try:
                    blob = await self._http.get_json(
                        _FEED_PATHS[game], count=50
                    )
                except Exception as exc:  # noqa: BLE001 — feed is best-effort
                    log.warning("feed_error", game=game, err=str(exc))
                    continue
                for row in blob.get("data", []):  # type: ignore[union-attr]
                    yield game, row
            await asyncio.sleep(self._settings.poll_interval_ms / 1000)

    async def aclose(self) -> None:
        await self._http.aclose()