"""Logging configuration and utilities."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import sys


def setup_logger(
    name: str = "coursera_scraper",
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 3
) -> logging.Logger:
    """Set up structured logging with file rotation."""

    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / f"{name}.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    logger_name = name if name else "coursera_scraper"
    return logging.getLogger(logger_name)


class LoggerMixin:
    """Mixin class to add logging capability to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


# Progress logging utilities
def log_api_request(logger: logging.Logger, method: str, url: str, status_code: Optional[int] = None):
    """Log API request details."""
    if status_code:
        logger.info(f"{method} {url} -> {status_code}")
    else:
        logger.info(f"{method} {url}")


def log_download_progress(logger: logging.Logger, filename: str, progress: float, total_size: int):
    """Log download progress."""
    logger.debug(f"Downloading {filename}: {progress:.1f}% ({total_size} bytes)")


def log_scraping_progress(logger: logging.Logger, course_name: str, modules_done: int, total_modules: int):
    """Log course scraping progress."""
    progress = (modules_done / total_modules) * 100 if total_modules > 0 else 0
    logger.info(f"Course '{course_name}': {modules_done}/{total_modules} modules ({progress:.1f}%)")