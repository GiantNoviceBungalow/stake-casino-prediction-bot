"""Prediction model — persisted record of an emitted signal and its outcome."""

from __future__ import annotations

from pydantic import BaseModel


class Prediction(BaseModel):
    model_config = {"frozen": True}

    signal_id: str
    game: str
    strategy: str
    confidence: float
    target: str
    emitted_at_ms: int
    resolved: bool = False
    hit: bool | None = None