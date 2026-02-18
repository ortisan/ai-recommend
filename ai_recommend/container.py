from dependency_injector import providers, containers

from ai_recommend.ai.container import AIContainer
from ai_recommend.infrastructure.db.container import DatabaseContainer
from ai_recommend.infrastructure.repository.container import RepositoryContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container for dependency injection.

    Manages all application-level dependencies including database
    and repository containers.
    """

    config = providers.Configuration()

    database = providers.Container(
        DatabaseContainer,
        config=config.database,
    )

    repository = providers.Container(RepositoryContainer, database=database)

    ai = providers.Container(AIContainer, config=config.ai)
