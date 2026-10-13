"""Strategy registry. Decorate a class to make the engine pick it up."""

from __future__ import annotations

from typing import Protocol, TypeVar

from stake_predict.core.signal import Signal
from stake_predict.models.round import Round


class Strategy(Protocol):
    name: str

    def evaluate(self, game: str, rounds: list[Round]) -> Signal | None: ...


STRATEGIES: dict[str, type[Strategy]] = {}
_T = TypeVar("_T", bound=type[Strategy])


def register_strategy(cls: _T) -> _T:
    if not getattr(cls, "name", None):
        raise ValueError(f"{cls.__name__} must define a class-level `name`")
    STRATEGIES[cls.name] = cls
    return cls