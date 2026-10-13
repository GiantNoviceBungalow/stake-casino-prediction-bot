"""Crash strategy: hazard-rate estimate from recent bust multipliers."""

from __future__ import annotations

import math

from stake_predict.core.registry import register_strategy
from stake_predict.core.signal import Signal
from stake_predict.models.round import Round


@register_strategy
class CrashMultiplierStrategy:
    name = "crash_multiplier"

    def evaluate(self, game: str, rounds: list[Round]) -> Signal | None:
        if game != "crash":
            return None
        recent = [r for r in rounds[-100:] if r.outcome is not None]
        if len(recent) < 60:
            return None
        mults = [max(1.0, float(r.outcome)) for r in recent]
        # Exponential MLE on log(mult) gives the hazard rate for P(bust > k).
        lam = 1.0 / (sum(math.log(m) for m in mults) / len(mults))
        target_mult = 1.5
        p_survive = math.exp(-lam * math.log(target_mult))
        if p_survive > 0.68:
            return Signal(
                game=game,
                strategy=self.name,
                confidence=min(0.85, p_survive - 0.5),
                target=f"cash out @ {target_mult:.2f}x",
                rationale=f"hazard lam={lam:.3f}, P(>{target_mult}x)={p_survive:.3f}",
            )
        return None