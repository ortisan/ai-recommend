from loguru import logger

from ai_recommend.infrastructure.observability.logger.logger import ILogger


class Loguru(ILogger):
    """
    Loguru logger implementation.
    This class provides methods to log messages at different levels.
    """
    def __init__(self):
        self.logger = logger

    def log(self, message: str) -> None:
        """Log a message at the INFO level."""
        logger.info(message)

    def error(self, message: str) -> None:
        """Log a message at the ERROR level."""
        logger.error(message)

    def debug(self, message: str) -> None:
        """Log a message at the DEBUG level."""
        logger.debug(message)
