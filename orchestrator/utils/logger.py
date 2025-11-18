"""Logging configuration for AI-CI-CD Orchestrator."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
import colorlog


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class ColoredFormatter(colorlog.ColoredFormatter):
    """Colored log formatter for console output."""

    def __init__(self):
        super().__init__(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s - %(message)s",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )


def setup_logging(
    level: str = "INFO",
    log_format: str = "json",
    output: str = "both",
    log_file: Optional[str] = None,
    max_file_size: int = 10485760,
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type (json, text, colored)
        output: Where to log (console, file, both)
        log_file: Path to log file
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep

    Returns:
        Configured root logger
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Create formatters
    if log_format == "json":
        formatter = JSONFormatter()
    elif log_format == "colored":
        formatter = ColoredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Console handler
    if output in ("console", "both"):
        console_handler = logging.StreamHandler(sys.stdout)
        if log_format == "colored":
            console_handler.setFormatter(ColoredFormatter())
        else:
            console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if output in ("file", "both") and log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Use rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds extra fields to log records."""

    def process(self, msg, kwargs):
        """Add extra fields to log record."""
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        # Add context from adapter
        if self.extra:
            kwargs["extra"]["extra_fields"] = self.extra

        return msg, kwargs


def get_contextual_logger(name: str, **context) -> LoggerAdapter:
    """
    Get a logger with additional context.

    Args:
        name: Logger name
        **context: Additional context fields to include in all log messages

    Returns:
        Logger adapter with context
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, context)
