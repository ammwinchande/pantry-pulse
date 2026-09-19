"""
Centralized logging configuration for PantryPulse.

Call ``setup_logging()`` once at process start (the composition root in
``main.py`` does this before any adapters are built). It:

* installs a uniform, human-readable format across the whole console,
* re-styles uvicorn's own loggers so server + application lines look alike,
* silences uvicorn's per-request access log (the REST adapter emits a richer
  request log with duration instead, so each request is logged exactly once),
* optionally writes to a rotating log file when ``LOG_FILE`` is set
  (useful for App Runner / production where stdout is captured but a file
  gives you retention + rotation for free).

The function is idempotent — safe to call more than once (e.g. under
``uvicorn --reload`` where the app module is imported in a worker process).
"""
import logging
import logging.config
import logging.handlers
import os

from src.config import settings

# One consistent line shape for every logger in the process:
#   2025-01-01 12:00:00 | INFO     | PantryPulseService | message here
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Max size per log file before rotation (5 MB) and how many backups to keep.
_MAX_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 3


def _resolve_level(level: str | None) -> int:
    """Map a level name to a numeric level, falling back to INFO if unknown."""
    name = (level or settings.log_level or "INFO").upper()
    numeric = getattr(logging, name, None)
    if not isinstance(numeric, int):
        return logging.INFO
    return numeric


def setup_logging(level: str | None = None, log_file: str | None = None) -> None:
    """Configure process-wide logging. Idempotent."""
    numeric_level = _resolve_level(level)
    file_path = (log_file if log_file is not None else settings.log_file) or ""

    handlers: dict = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }
    }
    if file_path:
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": file_path,
            "maxBytes": _MAX_BYTES,
            "backupCount": _BACKUP_COUNT,
            "encoding": "utf-8",
        }

    handler_names = list(handlers)

    config = {
        "version": 1,
        # Keep uvicorn's already-configured loggers alive; we re-style them below.
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": LOG_FORMAT, "datefmt": DATE_FORMAT},
        },
        "handlers": handlers,
        "root": {"level": numeric_level, "handlers": handler_names},
        "loggers": {
            # Re-style uvicorn so server lines match application lines.
            "uvicorn": {"level": numeric_level, "handlers": handler_names, "propagate": False},
            "uvicorn.error": {"level": numeric_level, "handlers": handler_names, "propagate": False},
            # Silence uvicorn's access log — the REST request-logging middleware
            # emits a single, richer line per request (with duration).
            "uvicorn.access": {"level": "WARNING", "handlers": handler_names, "propagate": False},
        },
    }

    logging.config.dictConfig(config)
