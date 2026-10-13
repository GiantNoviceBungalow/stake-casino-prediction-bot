"""Dice strategy: fade long under/over streaks using a Laplace-smoothed shift."""

from __future__ import annotations

from stake_predict.core.registry import register_strategy
from stake_predict.core.signal import Signal
from stake_predict.models.round import Round


@register_strategy
class DiceStreakStrategy:
    name = "dice_streak"

    def evaluate(self, game: str, rounds: list[Round]) -> Signal | None:
        if game != "dice":
            return None
        recent = [r for r in rounds[-40:] if r.outcome is not None]
        if len(recent) < 30:
            return None
        rolls = [float(r.outcome) for r in recent]
        mean = sum(rolls) / len(rolls)
        # Laplace-style shrink toward 50 so a hot streak doesn't over-fire.
        shrunk = 0.7 * mean + 0.3 * 50.0
        if shrunk >= 55.0:
            return Signal(
                game=game,
                strategy=self.name,
                confidence=min(0.9, (shrunk - 50.0) / 25.0),
                target="under 50.00",
                rationale=f"40-roll mean {mean:.2f} shrunk to {shrunk:.2f}",
            )
        if shrunk <= 45.0:
            return Signal(
                game=game,
                strategy=self.name,
                confidence=min(0.9, (50.0 - shrunk) / 25.0),
                target="over 50.00",
                rationale=f"40-roll mean {mean:.2f} shrunk to {shrunk:.2f}",
            )
        return None