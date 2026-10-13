"""Small statistical helpers used by strategies."""

from __future__ import annotations

import math


def laplace_shift(mean: float, prior: float, weight: float) -> float:
    """Shrink `mean` toward `prior` by `weight` in [0, 1]."""
    if not 0.0 <= weight <= 1.0:
        raise ValueError("weight must be in [0, 1]")
    return (1.0 - weight) * mean + weight * prior


def z_score(sample_share: float, expected: float, n: int) -> float:
    """One-sample z for a binomial share under H0: p = expected."""
    if not 0.0 < expected < 1.0:
        raise ValueError("expected must be in (0, 1)")
    if n <= 0:
        raise ValueError("n must be positive")
    return (sample_share - expected) / math.sqrt(expected * (1 - expected) / n)


def exp_hazard(samples: list