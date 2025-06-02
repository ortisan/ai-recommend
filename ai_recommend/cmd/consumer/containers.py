from dependency_injector import containers, providers

from ai_recommend.adapter.input.e_commerce.e_commerce_events_consumer import ECommerceEventsConsumer
from ai_recommend.infrastructure.kafka.config import KafkaConsumerConfig
from ai_recommend.infrastructure.observability.logger.loguru.loguru import Loguru


class CmdContainer(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["config.yaml"])

    logger = providers.Factory(
        Loguru,
        log_level=config.logger.level,
    )

    kafka_consumer_config = providers.Factory(
        KafkaConsumerConfig,
        bootstrap_servers=config.kafka.broker_servers,
        consumer_group=config.kafka.consumer_group,
        auto_offset_reset=config.kafka.auto_offset_reset,
        schema_registry_url=config.kafka.schema_registry_url,
        topic=config.kafka.e_commerce.products_viewed_topic,
        poll_timeout_ms=config.kafka.pool_timeout_ms,
        enable_auto_commit=config.kafka.enable_auto_commit,
    )

    e_commerce_events_consumer = providers.Singleton(
        ECommerceEventsConsumer,
        config=kafka_consumer_config,
        logger=logger,
    )

