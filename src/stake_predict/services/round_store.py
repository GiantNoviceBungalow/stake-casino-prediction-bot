"""SQLite round store. Append-only, indexed by (game, timestamp_ms)."""

from __future__ import annotations

from pathlib import Path

import aiosqlite

from stake_predict.models.round import Round

_SCHEMA = """
CREATE TABLE IF NOT EXISTS rounds (
    id           TEXT PRIMARY KEY,
    game         TEXT NOT NULL,
    outcome      REAL,
    hits         INTEGER,
    bin_index    INTEGER,
    target       TEXT NOT NULL DEFAULT '',
    timestamp_ms INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rounds_game_ts ON rounds(game, timestamp_ms DESC);
"""


class RoundStore:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    @classmethod
    async def open(cls, db_path: Path) -> "RoundStore":
        conn = await aiosqlite.connect(db_path)
        await conn.executescript(_SCHEMA)
        await conn.commit()
        return cls(conn)

    async def append(self, game: str, payload: dict[str, object]) -> None:
        from stake_predict.handlers import (
            crash_handler,
            dice_handler,
            keno_handler,
            limbo_handler,
            plinko_handler,
        )

        normalizer = {
            "dice": dice_handler.normalize,
            "limbo": limbo_handler.normalize,
            "keno": keno_handler.normalize,
            "plinko": plinko_handler.normalize,
            "crash": crash_handler.normalize,
        }[game]
        row: Round = normalizer(payload)
        await self._conn.execute(
            "INSERT OR REPLACE INTO rounds VALUES (?,?,?,?,?,?,?)",
            (
                row.id,
                row.game,
                row.outcome,
                row.hits,
                row.bin_index,
                row.target,
                row.timestamp_ms,
            ),
        )
        await self._conn.commit()

    async def recent(self, game: str, limit: int) -> list[Round]:
        cur = await self._conn.execute(
            "SELECT id, game, outcome, hits, bin_index, target, timestamp_ms "
            "FROM rounds WHERE game = ? ORDER BY timestamp_ms DESC LIMIT ?",
            (game, limit),
        )
        rows = await cur.fetchall()
        await cur.close()
        cols = ("id", "game", "outcome", "hits", "bin_index", "target", "timestamp_ms")
        return [Round.model_validate(dict(zip(cols, r, strict=True))) for r in rows]

    async def close(self) -> None:
        await self._conn.close()