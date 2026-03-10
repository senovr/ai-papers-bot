"""Logging configuration using structlog."""

import logging
import sys

import structlog
from structlog.processors import JSONRenderer, TimeStamper

from .config import settings


def setup_logging() -> None:
    """Configure structured logging."""

    # Configure standard logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            JSONRenderer() if settings.app_env == "production" else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance."""
    return structlog.get_logger(name)


# Initialize logging on module import
setup_logging()

# Module-level logger
logger = get_logger(__name__)
