from dependency_injector import containers, providers


class LoggerContainer(containers.DeclarativeContainer):
    logging = providers.Resource(
        logging.basicConfig,
        stream=sys.stdout,
        level=config.log.level,
        format=config.log.format,
    )
