"""Signal dataclass — the unit the engine emits and the UI renders."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True, frozen=True)
class Signal:
    game: str
    strategy: str
    confidence: float
    target: str
    rationale: str
    emitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, object] = field(default_factory=dict)

    def as_log_fields(self) -> dict[str, object]:
        return {
            "game": self.game,
            "strategy": self.strategy,
            "confidence": round(self.confidence, 4),
            "target": self.target,
        }