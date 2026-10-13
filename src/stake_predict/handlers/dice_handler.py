"""Dice-specific handler: normalizes Stake dice payloads into Round rows."""

from __future__ import annotations

from stake_predict.models.round import Round


def normalize(payload: dict[str, object]) -> Round:
    return Round(
        id=str(payload["id"]),
        game="dice",
        outcome=float(payload["roll"]),
        target=str(payload.get("target", "50.00")),
        timestamp_ms=int(payload["time"]),
    )