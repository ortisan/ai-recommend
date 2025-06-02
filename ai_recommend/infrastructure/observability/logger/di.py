from dependency_injector import containers, providers

from ai_recommend.infrastructure.observability.logger.loguru.loguru import Loguru

class LoggerContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging = providers.Factory(
        Loguru,
        log_level=config.from_env("LOG_LEVEL"), default="INFO"
    )
