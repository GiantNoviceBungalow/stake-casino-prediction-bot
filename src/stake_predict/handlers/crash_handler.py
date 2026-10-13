"""Crash handler: normalizes bust multipliers."""

from __future__ import annotations

from stake_predict.models.round import Round


def normalize(payload: dict[str, object]) -> Round:
    return Round(
        id=str(payload["id"]),
        game="crash",
        outcome=float(payload["bust"]),
        target="cash-out",
        timestamp_ms=int(payload["time"]),
    )