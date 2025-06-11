from dependency_injector import containers, providers

from ai_recommend.adapter.input.e_commerce.e_commerce_events_consumer import ECommerceEventsConsumer
from ai_recommend.adapter.output.repository.user_product_repository import UserProductRepository
from ai_recommend.infrastructure.kafka.config import KafkaConsumerConfig
from ai_recommend.infrastructure.observability.logger.loguru.loguru import LoggerLoguru
from ai_recommend.infrastructure.observability.meter.meter import Meter
from ai_recommend.infrastructure.observability.trace.trace import Trace
from ai_recommend.infrastructure.db.config import DatabaseConfig
from ai_recommend.infrastructure.db.surreal_db import SurrealDb


class CmdContainer(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["config.yaml"])

    logger = providers.Factory(
        LoggerLoguru,
        log_level=config.logger.level,
    )

    meter = providers.Factory(
        Meter,
        app_name=config.application.name,
        app_version=config.application.version,
    )

    tracer = providers.Factory(
        Trace,
        app_name=config.application.name,
        app_version=config.application.version,
    )

    database_config = providers.Factory(
        DatabaseConfig,
        url=config.database.url,
        username=config.database.username,
        password=config.database.password,
        namespace=config.database.namespace,
        database=config.database.database,
    )

    database = providers.Singleton(
        SurrealDb,
        config=database_config,
    )

    user_repository = providers.Factory(
        UserProductRepository,
        database=database,
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
        user_product_repository=user_repository,
        logger=logger,
    )

