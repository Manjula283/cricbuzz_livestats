"""
utils/logger.py

Centralized logging configuration. Call setup_logging() once, at
app startup (app.py). Every module's `logging.getLogger(__name__)`
calls throughout the project then inherit this configuration
automatically — no per-file setup needed.

Without this, Python's logging defaults to WARNING-level, console-only,
unformatted output — meaning most of our logger.info()/error() calls
in services/api/database modules were silently going nowhere useful.
"""
import logging
import sys
from pathlib import Path


def setup_logging(log_to_file: bool = True, level: int = logging.INFO) -> None:
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_to_file:
        log_dir = Path(__file__).resolve().parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        handlers.append(logging.FileHandler(log_dir / "app.log"))

    logging.basicConfig(level=level, format=log_format, handlers=handlers, force=True)
