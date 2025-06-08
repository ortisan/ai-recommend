from dependency_injector import providers, containers

from ai_recommend.infrastructure.db.config import DatabaseConfig
from ai_recommend.infrastructure.db.postgres_db import PostgresDb


class DatabaseContainer(containers.DeclarativeContainer):
    """Database container for dependency injection.

    Manages database configuration and connection pooling.
    """

    # This config is passed from the parent container
    config = providers.Configuration()

    database_config = providers.Singleton(
        DatabaseConfig,
        host=config.graph.host,
        port=config.graph.port,
        username=config.graph.username,
        password=config.graph.password,
        database=config.graph.database,
    )

    postgres_db = providers.Singleton(PostgresDb, config=database_config)
