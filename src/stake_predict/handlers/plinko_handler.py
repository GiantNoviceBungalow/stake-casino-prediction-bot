"""Plinko handler: maps a landed peg column to a bin index."""

from __future__ import annotations

from stake_predict.models.round import Round


def normalize(payload: dict[str, object]) -> Round:
    return Round(
        id=str(payload["id"]),
        game="plinko",
        outcome=float(payload["multiplier"]),
        bin_index=int(payload["bin"]),
        target=f"rows {payload.get('rows', 16)}",
        timestamp_ms=int(payload["time"]),
    )