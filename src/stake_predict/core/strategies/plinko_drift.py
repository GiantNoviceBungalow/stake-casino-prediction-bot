"""Plinko strategy: bin-drift detection on the 16-row board."""

from __future__ import annotations

from stake_predict.core.registry import register_strategy
from stake_predict.core.signal import Signal
from stake_predict.models.round import Round

_CENTER_BINS = {7, 8}


@register_strategy
class PlinkoDriftStrategy:
    name = "plinko_drift"

    def evaluate(self, game: str, rounds: list[Round]) -> Signal | None:
        if game != "plinko":
            return None
        recent = [r for r in rounds[-80:] if r.bin_index is not None]
        if len(recent) < 50:
            return None
        center_hits = sum(1 for r in recent if int(r.bin_index) in _CENTER_BINS)
        share = center_hits / len(recent)
        # Fair share for bins 7+8 on a 16-row board is ~0.35.
        if share < 0.22:
            return Signal(
                game=game,
                strategy=self.name,
                confidence=min(0.75, (0.22 - share) * 4.0),
                target="high risk / 16 rows",
                rationale=f"center share {share:.3f} over {len(recent)} drops",
            )
        return None