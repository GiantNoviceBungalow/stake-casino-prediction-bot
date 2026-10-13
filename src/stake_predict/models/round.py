"""Round model — the canonical shape for a single game outcome."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Round(BaseModel):
    model_config = {"frozen": True, "extra": "ignore"}

    id: str
    game: str
    outcome: float | None = None
    hits: int | None = None
    bin_index: int | None = None
    target: str = ""
    timestamp_ms: int = Field(ge=0)