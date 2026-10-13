"""Limbo strategy: gap analysis on multiplier distribution."""

from __future__ import annotations

import math

from stake_predict.core.registry import register_strategy
from stake_predict.core.signal import Signal
from stake_predict.models.round import Round


@register_strategy
class LimboGapStrategy:
    name = "limbo_gap"

    def evaluate(self, game: str, rounds: list[Round]) -> Signal | None:
        if game != "limbo":
            return None
        recent = [r for r in rounds[-120:] if r.outcome is not None]
        if len(recent) < 60:
            return None
        mults = [float(r.outcome) for r in recent]
        low_band = sum(1 for m in mults if m < 2.0) / len(mults)
        # Expected P(<2x) under a fair 1% house edge is ~0.495.
        z = (low_band - 0.495) / math.sqrt(0.495 * 0.505 / len(mults))
        if z < -2.0:
            return Signal(
                game=game,
                strategy=self.name,
                confidence=min(0.88, abs(z) / 4.0),
                target="cash out @ 2.00x",
                rationale=f"low-band share {low_band:.3f}, z={z:.2f}",
            )
        return None