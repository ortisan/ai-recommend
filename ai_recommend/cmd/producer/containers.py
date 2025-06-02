from dependency_injector import containers, providers

from ai_recommend.adapter.output.e_commerce.e_commerce_events_producer import ECommerceEventsProducer
from ai_recommend.infrastructure.kafka.config import KafkaProducerConfig
from ai_recommend.infrastructure.observability.logger.loguru.loguru import LoggerLoguru


class CmdContainer(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["config.yaml"])

    logger = providers.Factory(
        LoggerLoguru,
        log_level=config.logger.level,
    )

    kafka_producer_config = providers.Factory(
        KafkaProducerConfig,
        bootstrap_servers=config.kafka.broker_servers,
        schema_registry_url=config.kafka.schema_registry_url,
        topic=config.kafka.e_commerce.products_viewed_topic,
    )

    e_commerce_events_producer = providers.Singleton(
        ECommerceEventsProducer,
        config=kafka_producer_config,
        logger=logger,
    )

