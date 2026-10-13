# Contributing to stake-casino-prediction-bot

Thanks for wanting to push the tater forward. This repo is a Windows desktop
prediction tool that ingests live Stake game rounds, runs them through a
pattern engine, and surfaces probability-weighted suggestions in a local UI.

## Ground rules

- Python 3.11+ only. We use `match` statements and `tomllib`.
- Every PR must keep `pytest -q` green and `ruff check .` clean.
- No network calls outside `src/stake_predict/services/`. All HTTP goes
  through the shared `http_client` wrapper so we can rate-limit and log.
- New prediction strategies go in `src/stake_predict/core/strategies/` and
  must register through the `@register_strategy` decorator.

## Branch flow

1. Fork, branch off `main` as `feat/<short-name>` or `fix/<short-name>`.
2. Add tests under `tests/` mirroring the module path.
3. Open PR with a short description of the signal you're adding and the
   historical hit-rate you measured on the bundled sample set.

## Style

- Type hints everywhere. `mypy --strict` is enforced in CI.
- Dataclasses over dicts for anything crossing a module boundary.
- Log via `structlog`, never `print()`.

## Reporting issues

Include the Stake game (Dice, Limbo, Keno, Plinko, Crash), the seed hash you
captured, and the last 200 rounds as a JSON dump. Without seeds we can't
reproduce.