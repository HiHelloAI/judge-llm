"""Singleton logger for Judge LLM framework"""

import logging
import sys
from typing import Optional


class LoggerSingleton:
    """Singleton logger instance for the framework"""

    _instance: Optional[logging.Logger] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = logging.getLogger("judge_llm")
            cls._setup_logger()
            cls._initialized = True
        return cls._instance

    @classmethod
    def _setup_logger(cls):
        """Set up the logger with default configuration"""
        if cls._instance is None:
            return

        cls._instance.setLevel(logging.INFO)
        cls._instance.propagate = False

        if not cls._instance.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            cls._instance.addHandler(handler)

    @classmethod
    def set_level(cls, level: str):
        """Set the logging level

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if cls._instance is None:
            cls()

        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        log_level = level_map.get(level.upper(), logging.INFO)
        cls._instance.setLevel(log_level)

        for handler in cls._instance.handlers:
            handler.setLevel(log_level)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the singleton logger instance

        Returns:
            Logger instance
        """
        if cls._instance is None:
            cls()
        return cls._instance


def get_logger() -> logging.Logger:
    """Get the singleton logger instance

    Returns:
        Logger instance
    """
    return LoggerSingleton.get_logger()


def set_log_level(level: str):
    """Set the logging level

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    LoggerSingleton.set_level(level)
