from pathlib import Path

from loguru import logger

import sys


class Logger:

    @staticmethod
    def setup():

        log_dir = Path(__file__).parent / "logs"

        log_dir.mkdir(exist_ok=True)

        logger.remove()

        # نمایش داخل کنسول
        logger.add(
            sys.stdout,
            level="INFO",
            colorize=True,
            enqueue=True,
            backtrace=True,
            diagnose=True
        )

        # ذخیره داخل فایل
        logger.add(
            log_dir / "{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="30 days",
            encoding="utf8",
            level="INFO",
            enqueue=True,
            backtrace=True,
            diagnose=True
        )

        logger.success("Logger Initialized")