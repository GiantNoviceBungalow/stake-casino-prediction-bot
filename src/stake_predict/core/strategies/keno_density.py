"""Keno strategy: hit-density drift across the last N draws."""

from __future__ import annotations

from stake_predict.core.registry import register_strategy
from stake_predict.core.signal import Signal
from stake_predict.models.round import Round


@register_strategy
class KenoDensityStrategy:
    name = "keno_density"

    def evaluate(self, game: str, rounds: list[Round]) -> Signal | None:
        if game != "keno":
            return None
        recent = [r for r in rounds[-60:] if r.hits is not None]
        if len(recent) < 40:
            return None
        hits = [int(r.hits) for r in recent]
        avg = sum(hits) / len(hits)
        expected = 4.0
        if avg <= expected - 0.9:
            return Signal(
                game=game,
                strategy=self.name,
                confidence=min(0.8, (expected - avg) / 3.0),
                target="pick 8 / medium risk",
                rationale=f"60-draw hit avg {avg:.2f} vs expected {expected:.2f}",
            )
        return None