import json
from pathlib import Path

from loguru import logger

from logger import Logger
from monitor import Monitor


def load_config():

    config_file = Path(__file__).parent / "config.json"

    with open(
        config_file,
        "r",
        encoding="utf-8-sig"
    ) as f:

        return json.load(f)


def main():

    # راه‌اندازی Logger
    Logger.setup()

    logger.info(
        "Loading Config..."
    )

    config = load_config()

    monitor = Monitor(
        config
    )

    monitor.start()


if __name__ == "__main__":

    main()