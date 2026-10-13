"""Settings loader. Env > local.yaml > defaults. Refuses to boot on leaked keys."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LOCAL_YAML = _REPO_ROOT / "config" / "local.yaml"

_BLOCKED_SUBSTRINGS = ("sk_live_", "AKIA", "-----BEGIN PRIVATE KEY-----")


@dataclass(slots=True, frozen=True)
class Settings:
    db_path: Path
    log_dir: Path
    log_level: str = "INFO"
    poll_interval_ms: int = 1500
    games: tuple[str, ...] = ("dice", "limbo", "keno", "plinko", "crash")
    stake_api_base: str = "https://stake.com/_api"
    session_token: str | None = None
    min_confidence: float = 0.62
    history_window: int = 500
    extra: dict[str, object] = field(default_factory=dict)


def _load_yaml(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open("rb") as fh:
        return yaml.safe_load(fh) or {}


def _reject_secrets(blob: dict[str, object]) -> None:
    flat = " ".join(str(v) for v in blob.values())
    for needle in _BLOCKED_SUBSTRINGS:
        if needle in flat:
            raise RuntimeError(
                f"Refusing to boot: hardcoded secret marker {needle!r} in local.yaml"
            )


def load_settings() -> Settings:
    raw = _load_yaml(_LOCAL_YAML)
    _reject_secrets(raw)

    data_root = Path(os.getenv("STAKE_PREDICT_DATA", str(_REPO_ROOT / "data")))
    data_root.mkdir(parents=True, exist_ok=True)

    return Settings(
        db_path=Path(os.getenv("STAKE_PREDICT_DB", str(data_root / "rounds.sqlite3"))),
        log_dir=Path(os.getenv("STAKE_PREDICT_LOG_DIR", str(_REPO_ROOT / "logs"))),
        log_level=os.getenv("STAKE_PREDICT_LOG_LEVEL", str(raw.get("log_level", "INFO"))),
        poll_interval_ms=int(raw.get("poll_interval_ms", 1500)),
        session_token=os.getenv("STAKE_SESSION_TOKEN"),
        min_confidence=float(raw.get("min_confidence", 0.62)),
        history_window=int(raw.get("history_window", 500)),
    )