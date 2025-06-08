from pydantic import BaseModel


class LogConfig(BaseModel):
    """
    Configuration for log settings.
    """

    logging_level: str = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
