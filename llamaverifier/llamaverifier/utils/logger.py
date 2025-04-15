"""
Logging utilities for LlamaVerifier
"""

import logging
import os
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

# Initialize console for rich output
console = Console()

# Default logger level
DEFAULT_LOG_LEVEL = logging.INFO

# Logger instances
_loggers = {}


def setup_logger(
    name: str,
    level: Optional[int] = None,
    log_file: Optional[str] = None,
    console_output: bool = True,
) -> logging.Logger:
    """
    Set up a logger with the specified name and configuration.

    Args:
        name: Name of the logger
        level: Logging level (default: INFO)
        log_file: Path to log file (optional)
        console_output: Whether to output logs to console (default: True)

    Returns:
        Configured logger instance
    """
    if level is None:
        level = DEFAULT_LOG_LEVEL

    if name in _loggers:
        return _loggers[name]

    # Create logger and set level
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Format
    log_format = "%(message)s"
    date_format = "[%Y-%m-%d %H:%M:%S]"

    # Add console handler with rich formatting if requested
    if console_output:
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            show_time=True,
            show_path=False,
        )
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        logger.addHandler(console_handler)

    # Add file handler if log file specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt=date_format,
            )
        )
        logger.addHandler(file_handler)

    # Store logger
    _loggers[name] = logger

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name. If it doesn't exist, create it with default settings.

    Args:
        name: Name of the logger

    Returns:
        Logger instance
    """
    if name in _loggers:
        return _loggers[name]

    return setup_logger(name)


# Set up default logger
logger = setup_logger("llamaverifier")
