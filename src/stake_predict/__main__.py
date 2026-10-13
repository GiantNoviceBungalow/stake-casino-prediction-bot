"""Bootstrap entry point. Wires config -> engine -> UI and runs the loop."""

from __future__ import annotations

import asyncio
import sys

from stake_predict.app import StakePredictApp
from stake_predict.config.settings import load_settings
from stake_predict.utils.logging import configure_logging


def main() -> int:
    settings = load_settings()
    configure_logging(settings.log_level, settings.log_dir)

    app = StakePredictApp(settings)
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())