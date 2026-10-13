"""Limbo handler: extracts the bust multiplier from a limbo round payload."""

from __future__ import annotations

from stake_predict.models.round import Round


def normalize(payload: dict[str, object]) -> Round:
    return Round(
        id=str(payload["id"]),
        game="limbo",
        outcome=float(payload["multiplier"]),
        target="cash-out",
        timestamp_ms=int(payload["time"]),
    )