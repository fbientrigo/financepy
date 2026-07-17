"""
Centralized logging configuration for FinancePy.
Provides consistent logging across all modules.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    name: str = "financepy",
) -> logging.Logger:
    """
    Setup logging configuration for FinancePy.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If provided, logs to both console and file
        name: Logger name (default: "financepy")

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Format: [LEVEL] [module:function:line] message
    log_format = logging.Formatter(
        fmt="[%(levelname)-8s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")

    return logger


def get_logger(name: str = "financepy") -> logging.Logger:
    """
    Get or create logger with specified name.

    Args:
        name: Logger name (e.g., "financepy.data", "financepy.indicators")

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Global logger for main application
logger = get_logger("financepy")
