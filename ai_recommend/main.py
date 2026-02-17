from uuid import UUID

from dependency_injector.wiring import Provide, inject
import os
from dotenv import load_dotenv

from ai_recommend.container import ApplicationContainer
from ai_recommend.infrastructure.repository.graph_repository import (
    GraphRepository,
    NodeFilter,
    EdgeFilter,
)
import networkx as nx
import iplotx as ipx


@inject
def main(
    graph_repository: GraphRepository = Provide[ApplicationContainer.repository.graph_repository],
) -> None:
    """Main application function.

    Demonstrates semantic search capabilities on the knowledge graph.

    Args:
        graph_repository: GraphRepository instance
            injected from the container.
    """
    node = graph_repository.get_node_by_id(node_id=UUID("019c6c2c-6496-7eb1-85cd-24cd2fe8e9db"))
    print(f"Node: {node}")

    nodes_by_properties = graph_repository.get_nodes_by_property(
        label="User", property_key="age.value", property_value="23"
    )
    print(f"Nodes: {nodes_by_properties}")

    count_nodes = graph_repository.count_nodes(filter_obj=NodeFilter(label="Product"))
    print(f"Count Nodes: {count_nodes}")

    edge = graph_repository.get_edge_by_id(edge_id=UUID("019c6c2c-67df-7467-9b96-d5cc93b8c0db"))
    print(f"Edge: {edge}")

    edges = graph_repository.get_edges_by_property(
        label="Viewed",
        property_key="session_id",
        property_value="019c6c2c-67dc-72bf-93ab-8a7bc9ee19e0",
    )
    print(f"Edges: {edges}")

    count_edges = graph_repository.count_edges(filter_obj=EdgeFilter(label="Viewed"))
    print(f"Count Edges: {count_edges}")

    results = graph_repository.get_node_statistics(
        node_id=UUID("019c6c2c-6496-7eb1-85cd-24cd2fe8e9db")
    )
    print(f"Result: {results}")

    results = graph_repository.get_user_interactions(
        user_id=UUID("019c6c2c-6496-7eb1-85cd-24cd2fe8e9db")
    )
    print(f"Result: {results}")

    graph = graph_repository.graph_traverse(
        start_node_id=UUID("019c6c2c-6496-7eb1-85cd-24cd2fe8e9db")
    )
    print(graph)

    G = nx.Graph()
    G.add_edge(1, 2)
    G.add_edge(2, 3, weight=0.9)
    layout = nx.layout.circular_layout(G)
    ipx.plot(G, layout)

    # dummy_embedding = [0.1] * 1536  # Replace with actual embedding
    #
    # results = graph_repository.semantic_search(
    #     query_embedding=dummy_embedding,
    #     match_threshold=0.7,
    #     match_count=5,
    #     filter_label="Product",
    # )
    # print(f"Found {len(results)} similar products")


if __name__ == "__main__":
    # Load environment variables from .env file in the same directory
    load_dotenv()

    # Initialize application container
    container = ApplicationContainer()

    # Configure database settings from environment using from_dict()

    container.config.from_dict(
        {
            "database": {
                "graph": {
                    "host": os.getenv("GRAPH_DB_HOST"),
                    "port": os.getenv("GRAPH_DB_PORT", "5432"),
                    "username": os.getenv("GRAPH_DB_USER"),
                    "password": os.getenv("GRAPH_DB_PASSWORD"),
                    "database": os.getenv("GRAPH_DB_DATABASE_NAME"),
                }
            },
            "ai": {
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "ai_provider": os.getenv("AI_PROVIDER"),
                "ai_model": os.getenv("AI_MODEL"),
            }
        }
    )

    # Initialize resources after configuration is set
    container.init_resources()

    # Wire the application for dependency injection
    container.wire(modules=[__name__])

    # Run the main application
    main()
