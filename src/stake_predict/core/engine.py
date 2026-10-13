"""Prediction engine. Consumes the round store, emits scored suggestions."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import structlog

from stake_predict.config.settings import Settings
from stake_predict.core.registry import STRATEGIES, Strategy
from stake_predict.core.signal import Signal
from stake_predict.models.round import Round
from stake_predict.services.round_store import RoundStore

log = structlog.get_logger(__name__)


class PredictionEngine:
    """Runs every registered strategy over the rolling window and yields signals."""

    def __init__(self, store: RoundStore, settings: Settings) -> None:
        self._store = store
        self._settings = settings
        self._strategies: list[Strategy] = [cls() for cls in STRATEGIES.values()]
        self._queue: asyncio.Queue[Signal] = asyncio.Queue(maxsize=256)

    async def run_forever(self) -> None:
        while True:
            await self.tick()
            await asyncio.sleep(self._settings.poll_interval_ms / 1000)

    async def tick(self) -> None:
        for game in self._settings.games:
            rounds = await self._store.recent(game, self._settings.history_window)
            if len(rounds) < 50:
                continue
            for strategy in self._strategies:
                signal = strategy.evaluate(game, rounds)
                if signal and signal.confidence >= self._settings.min_confidence:
                    await self._queue.put(signal)
                    log.info("signal_emitted", **signal.as_log_fields())

    async def signals(self) -> AsyncIterator[Signal]:
        while True:
            yield await self._queue.get()

    def recent_signals(self, limit: int = 20) -> list[Signal]:
        out: list[Signal] = []
        while not self._queue.empty() and len(out) < limit:
            out.append(self._queue.get_nowait())
        for s in out:
            self._queue.put_nowait(s)
        return out[-limit:]

    @staticmethod
    def round_from_row(row: dict[str, object]) -> Round:
        return Round.model_validate(row)