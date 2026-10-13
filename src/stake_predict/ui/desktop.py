"""CustomTkinter desktop shell. Renders live signals in a scrollable list."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import customtkinter as ctk
import structlog

from stake_predict.config.settings import Settings
from stake_predict.core.engine import PredictionEngine
from stake_predict.services.round_store import RoundStore

log = structlog.get_logger(__name__)


@dataclass(slots=True)
class DesktopShell:
    engine: PredictionEngine
    store: RoundStore
    settings: Settings

    async def serve(self) -> None:
        ctk.set_appearance_mode("dark")
        root = ctk.CTk()
        root.title("stake-casino-prediction-bot")
        root.geometry("720x520")

        header = ctk.CTkLabel(
            root,
            text=f"Stake Predictor v{self.settings.min_confidence:.2f} min-conf",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        header.pack(pady=8)

        feed = ctk.CTkTextbox(root, width=680, height=440, wrap="word")
        feed.pack(padx=16, pady=8)

        async def pump() -> None:
            async for signal in self.engine.signals():
                feed.insert(
                    "end",
                    f"[{signal.game}] {signal.strategy} conf={signal.confidence:.2f} "
                    f"-> {signal.target}\n",
                )
                feed.see("end")

        root.after(0, lambda: asyncio.create_task(pump()))
        await asyncio.to_thread(root.mainloop)