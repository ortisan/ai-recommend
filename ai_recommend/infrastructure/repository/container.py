from dependency_injector import providers, containers

from ai_recommend.infrastructure.repository.graph_repository import GraphRepository


class RepositoryContainer(containers.DeclarativeContainer):
    """Repository container for dependency injection.

    Manages repository instances and their dependencies.
    """

    # Reference to the database container
    database = providers.DependenciesContainer()

    graph_repository = providers.Singleton(
        GraphRepository,
        postgres_db=database.postgres_db,
    )
