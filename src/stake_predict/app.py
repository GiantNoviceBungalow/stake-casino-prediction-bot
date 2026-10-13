"""Top-level application object. Owns the engine, the ingest loop, and the UI."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import structlog

from stake_predict.config.settings import Settings
from stake_predict.core.engine import PredictionEngine
from stake_predict.services.round_store import RoundStore
from stake_predict.services.stake_client import StakeClient
from stake_predict.ui.desktop import DesktopShell

log = structlog.get_logger(__name__)


@dataclass(slots=True)
class StakePredictApp:
    settings: Settings

    async def run(self) -> None:
        store = await RoundStore.open(self.settings.db_path)
        client = StakeClient(self.settings)
        engine = PredictionEngine(store=store, settings=self.settings)

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._ingest_loop(client, store), name="ingest")
            tg.create_task(engine.run_forever(), name="engine")
            tg.create_task(DesktopShell(engine, store, self.settings).serve(), name="ui")

    async def _ingest_loop(self, client: StakeClient, store: RoundStore) -> None:
        async for game, round_payload in client.stream_rounds():
            await store.append(game, round_payload)
            log.debug("round_ingested", game=game, round_id=round_payload.get("id"))