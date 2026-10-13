"""Keno handler: counts matched numbers against the drawn set."""

from __future__ import annotations

from stake_predict.models.round import Round


def normalize(payload: dict[str, object]) -> Round:
    picked = set(payload.get("picked", []))
    drawn = set(payload.get("drawn", []))
    return Round(
        id=str(payload["id"]),
        game="keno",
        outcome=float(len(picked & drawn)),
        hits=len(picked & drawn),
        target=f"pick {len(picked)}",
        timestamp_ms=int(payload["time"]),
    )