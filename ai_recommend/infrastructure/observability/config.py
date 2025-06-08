from pydantic import BaseModel

from ai_recommend.infrastructure.observability.logger.config import LogConfig


class ObservabilityConfig(BaseModel):
    """
    Configuration for observability settings.
    """

    service_name: str
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True
    logConfig: LogConfig
