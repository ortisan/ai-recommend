from loguru import logger
import sys

from ai_recommend.infrastructure.observability.logger.logger import ILogger

class Loguru(ILogger):
    """
    Loguru logger implementation.
    This class provides methods to log messages at different levels.
    """
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logger

        self.logger.add(
            sink= sys.stdout,
            level=log_level,
            serialize=True
        )

    def log(self, message: str) -> None:
        """Log a message at the INFO level."""
        logger.info(message)

    def error(self, message: str) -> None:
        """Log a message at the ERROR level."""
        logger.error(message)

    def warn(self, message: str) -> None:
        """Log a message at the WARNING level."""
        logger.warning(message)

    def debug(self, message: str) -> None:
        """Log a message at the DEBUG level."""
        logger.debug(message)
