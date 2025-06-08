"""
Graph Repository for searching nodes and edges by properties.

This module provides a comprehensive repository for querying nodes and edges
in the knowledge graph using various filter criteria.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import text
from dataclasses import dataclass
from enum import Enum

from ai_recommend.domain.models import Edge, Node
from ai_recommend.infrastructure.db.postgres_db import PostgresDb


class SortOrder(str, Enum):
    """Sort order enumeration"""

    ASC = "ASC"
    DESC = "DESC"


@dataclass
class NodeFilter:
    """Filter criteria for node search"""

    label: Optional[str] = None
    id: Optional[UUID] = None
    tags: Optional[Dict[str, Any]] = None
    limit: int = 100
    offset: int = 0
    sort_by: Optional[str] = None
    sort_order: SortOrder = SortOrder.DESC


@dataclass
class EdgeFilter:
    """Filter criteria for edge search"""

    label: Optional[str] = None
    id: Optional[UUID] = None
    source_id: Optional[UUID] = None
    target_id: Optional[UUID] = None
    tags: Optional[Dict[str, Any]] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    limit: int = 100
    offset: int = 0
    sort_by: Optional[str] = None
    sort_order: SortOrder = SortOrder.DESC


class GraphRepository:
    """Repository for graph operations (nodes and edges)

    Provides methods for searching, filtering, and querying nodes and edges
    with various criteria using PostgreSQL database.
    """

    def __init__(self, postgres_db: PostgresDb):
        """Initialize the Graph Repository

        Args:
            postgres_db: PostgresDb instance for database access
        """
        self.postgres_db = postgres_db

    # ==================== NODE OPERATIONS ====================

    def get_node_by_id(self, node_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a single node by ID

        Args:
            node_id: Node UUID

        Returns:
            Node data or None if not found
        """
        try:
            with self.postgres_db.get_session() as session:
                query = text("""
                    SELECT 
                        id, label, properties, tags, embedding, 
                        text_content, summary, metadata, created_at, updated_at
                    FROM node
                    WHERE id = :node_id
                """)

                result = session.execute(query, {"node_id": str(node_id)}).first()
                return self._format_node_result(result) if result else None
        except Exception as e:
            raise Exception(f"Error getting node by ID: {str(e)}")

    def search_nodes_by_label(
        self, label: str, filter_obj: Optional[NodeFilter] = None
    ) -> List[Dict[str, Any]]:
        """Search nodes by label

        Args:
            label: Node label to search for
            filter_obj: Optional NodeFilter for additional filtering

        Returns:
            List of matching nodes
        """
        if filter_obj is None:
            filter_obj = NodeFilter(label=label)
        else:
            filter_obj.label = label

        return self.search_nodes(filter_obj)

    def search_nodes_by_tags(
        self, tags: Dict[str, Any], filter_obj: Optional[NodeFilter] = None
    ) -> List[Dict[str, Any]]:
        """Search nodes by tags using JSONB query

        Args:
            tags: Tags dictionary to match
            filter_obj: Optional NodeFilter for additional filtering

        Returns:
            List of matching nodes
        """
        if filter_obj is None:
            filter_obj = NodeFilter(tags=tags)
        else:
            filter_obj.tags = tags

        return self.search_nodes(filter_obj)

    def search_nodes(self, filter_obj: NodeFilter) -> List[Dict[str, Any]]:
        """Search nodes with comprehensive filtering

        Args:
            filter_obj: NodeFilter with search criteria

        Returns:
            List of matching nodes
        """
        try:
            with self.postgres_db.get_session() as session:
                # Build the base query
                query = "SELECT id, label, properties, tags, embedding, text_content, summary, metadata, created_at, updated_at FROM node WHERE 1=1"
                params = {}

                # Add filters
                if filter_obj.id:
                    query += " AND id = :id"
                    params["id"] = str(filter_obj.id)

                if filter_obj.label:
                    query += " AND label = :label"
                    params["label"] = filter_obj.label

                if filter_obj.tags:
                    # JSONB contains query
                    query += " AND tags @> :tags::jsonb"
                    params["tags"] = str(filter_obj.tags).replace("'", '"')

                # Add sorting
                if filter_obj.sort_by:
                    query += f" ORDER BY {filter_obj.sort_by} {filter_obj.sort_order.value}"
                else:
                    query += f" ORDER BY created_at {filter_obj.sort_order.value}"

                # Add pagination
                query += " LIMIT :limit OFFSET :offset"
                params["limit"] = filter_obj.limit
                params["offset"] = filter_obj.offset

                result = session.execute(text(query), params).fetchall()
                return [self._format_node_result(row) for row in result if row]
        except Exception as e:
            raise Exception(f"Error searching nodes: {str(e)}")

    def search_nodes_by_text(self, text_query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Full-text search nodes by text content

        Args:
            text_query: Text to search for
            limit: Maximum number of results

        Returns:
            List of matching nodes sorted by relevance
        """
        try:
            with self.postgres_db.get_session() as session:
                query = text("""
                    SELECT 
                        id, label, properties, tags, embedding,
                        text_content, summary, metadata, created_at, updated_at,
                        ts_rank(to_tsvector('english', text_content), 
                                plainto_tsquery('english', :query)) as relevance
                    FROM node
                    WHERE to_tsvector('english', text_content) @@ plainto_tsquery('english', :query)
                    ORDER BY relevance DESC
                    LIMIT :limit
                """)

                result = session.execute(query, {"query": text_query, "limit": limit}).fetchall()
                return [self._format_node_result(row) for row in result if row]
        except Exception as e:
            raise Exception(f"Error searching nodes by text: {str(e)}")

    def get_nodes_by_property(
        self, label: str, property_key: str, property_value: Any, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get nodes by a specific label and property value

        Args:
            label: Node label to search
            property_key: Property key to search (supports dot notation for nested)
            property_value: Property value to match
            limit: Maximum number of results

        Returns:
            List of matching nodes
        """
        try:
            with self.postgres_db.get_session() as session:
                # Support nested property search (e.g., "user.age")
                if "." in property_key:
                    # Convert dot notation to JSONB path: 'user.age' -> properties->'user'->>'age'
                    parts = property_key.split(".")
                    property_path = "properties"
                    for part in parts[:-1]:
                        property_path += f"->'{part}'"
                    property_path += f"->>'{parts[-1]}'"
                else:
                    property_path = f"properties->>'{property_key}'"

                query = text(f"""
                    SELECT 
                        id, label, properties, tags, embedding,
                        text_content, summary, metadata, created_at, updated_at
                    FROM node
                    WHERE label = :label 
                    AND {property_path} = :value
                    LIMIT :limit
                """)

                result = session.execute(
                    query, {"label": label, "value": str(property_value), "limit": limit}
                ).fetchall()
                return [self._format_node_result(row) for row in result if row]
        except Exception as e:
            raise Exception(f"Error getting nodes by property: {str(e)}")

    def count_nodes(self, filter_obj: Optional[NodeFilter] = None) -> int:
        """Count nodes matching criteria

        Args:
            filter_obj: Optional NodeFilter for filtering

        Returns:
            Count of matching nodes
        """
        try:
            with self.postgres_db.get_session() as session:
                query = "SELECT COUNT(*) as count FROM node WHERE 1=1"
                params = {}

                if filter_obj:
                    if filter_obj.label:
                        query += " AND label = :label"
                        params["label"] = filter_obj.label

                    if filter_obj.tags:
                        query += " AND tags @> :tags::jsonb"
                        params["tags"] = str(filter_obj.tags).replace("'", '"')

                result = session.execute(text(query), params).first()
                return result.count if result else 0
        except Exception as e:
            raise Exception(f"Error counting nodes: {str(e)}")

    # ==================== EDGE OPERATIONS ====================

    def get_edge_by_id(self, edge_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a single edge by ID

        Args:
            edge_id: Edge UUID

        Returns:
            Edge data or None if not found
        """
        try:
            with self.postgres_db.get_session() as session:
                query = text("""
                    SELECT 
                        id, source_id, target_id, label, properties, tags,
                        weight, context, metadata, created_at, updated_at
                    FROM edge
                    WHERE id = :edge_id
                """)

                result = session.execute(query, {"edge_id": str(edge_id)}).first()
                return self._format_edge_result(result) if result else None
        except Exception as e:
            raise Exception(f"Error getting edge by ID: {str(e)}")

    def search_edges_by_label(
        self, label: str, filter_obj: Optional[EdgeFilter] = None
    ) -> List[Dict[str, Any]]:
        """Search edges by label

        Args:
            label: Edge label to search for
            filter_obj: Optional EdgeFilter for additional filtering

        Returns:
            List of matching edges
        """
        if filter_obj is None:
            filter_obj = EdgeFilter(label=label)
        else:
            filter_obj.label = label

        return self.search_edges(filter_obj)

    def search_edges_by_tags(
        self, tags: Dict[str, Any], filter_obj: Optional[EdgeFilter] = None
    ) -> List[Dict[str, Any]]:
        """Search edges by tags using JSONB query

        Args:
            tags: Tags dictionary to match
            filter_obj: Optional EdgeFilter for additional filtering

        Returns:
            List of matching edges
        """
        if filter_obj is None:
            filter_obj = EdgeFilter(tags=tags)
        else:
            filter_obj.tags = tags

        return self.search_edges(filter_obj)

    def search_edges(self, filter_obj: EdgeFilter) -> List[Dict[str, Any]]:
        """Search edges with comprehensive filtering

        Args:
            filter_obj: EdgeFilter with search criteria

        Returns:
            List of matching edges
        """
        try:
            with self.postgres_db.get_session() as session:
                # Build the base query
                query = """SELECT id, source_id, target_id, label, properties, tags, 
                           weight, context, metadata, created_at, updated_at 
                           FROM edge WHERE 1=1"""
                params = {}

                # Add filters
                if filter_obj.id:
                    query += " AND id = :id"
                    params["id"] = str(filter_obj.id)

                if filter_obj.label:
                    query += " AND label = :label"
                    params["label"] = filter_obj.label

                if filter_obj.source_id:
                    query += " AND source_id = :source_id"
                    params["source_id"] = str(filter_obj.source_id)

                if filter_obj.target_id:
                    query += " AND target_id = :target_id"
                    params["target_id"] = str(filter_obj.target_id)

                if filter_obj.tags:
                    query += " AND tags @> :tags::jsonb"
                    params["tags"] = str(filter_obj.tags).replace("'", '"')

                if filter_obj.min_weight is not None:
                    query += " AND weight >= :min_weight"
                    params["min_weight"] = filter_obj.min_weight

                if filter_obj.max_weight is not None:
                    query += " AND weight <= :max_weight"
                    params["max_weight"] = filter_obj.max_weight

                # Add sorting
                if filter_obj.sort_by:
                    query += f" ORDER BY {filter_obj.sort_by} {filter_obj.sort_order.value}"
                else:
                    query += f" ORDER BY created_at {filter_obj.sort_order.value}"

                # Add pagination
                query += " LIMIT :limit OFFSET :offset"
                params["limit"] = filter_obj.limit
                params["offset"] = filter_obj.offset

                result = session.execute(text(query), params).fetchall()
                return [self._format_edge_result(row) for row in result if row]
        except Exception as e:
            raise Exception(f"Error searching edges: {str(e)}")

    def get_edges_by_nodes(
        self,
        source_id: UUID,
        target_id: Optional[UUID] = None,
        label: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get edges between two nodes or from a source node

        Args:
            source_id: Source node UUID
            target_id: Optional target node UUID (if None, gets all outgoing edges)
            label: Optional edge label filter
            limit: Maximum number of results

        Returns:
            List of matching edges
        """
        try:
            with self.postgres_db.get_session() as session:
                query = "SELECT id, source_id, target_id, label, properties, tags, weight, context, metadata, created_at, updated_at FROM edge WHERE source_id = :source_id"
                params = {"source_id": str(source_id), "limit": limit}

                if target_id:
                    query += " AND target_id = :target_id"
                    params["target_id"] = str(target_id)

                if label:
                    query += " AND label = :label"
                    params["label"] = label

                query += " LIMIT :limit"

                result = session.execute(text(query), params).fetchall()
                return [self._format_edge_result(row) for row in result if row]
        except Exception as e:
            raise Exception(f"Error getting edges by nodes: {str(e)}")

    def get_incoming_edges(
        self, target_id: UUID, label: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get incoming edges to a node

        Args:
            target_id: Target node UUID
            label: Optional edge label filter
            limit: Maximum number of results

        Returns:
            List of matching edges
        """
        try:
            with self.postgres_db.get_session() as session:
                query = "SELECT id, source_id, target_id, label, properties, tags, weight, context, metadata, created_at, updated_at FROM edge WHERE target_id = :target_id"
                params = {"target_id": str(target_id), "limit": limit}

                if label:
                    query += " AND label = :label"
                    params["label"] = label

                query += " LIMIT :limit"

                result = session.execute(text(query), params).fetchall()
                return [self._format_edge_result(row) for row in result if row]
        except Exception as e:
            raise Exception(f"Error getting incoming edges: {str(e)}")

    def get_edges_by_property(
        self, label: str, property_key: str, property_value: Any, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get edges by a specific property value

        Args:
            label: Edge label to search for
            property_key: Property key to search
            property_value: Property value to match
            limit: Maximum number of results

        Returns:
            List of matching edges
        """
        with self.postgres_db.get_session() as session:
            try:
                # Support nested property search (e.g., "user.age")
                if "." in property_key:
                    # Convert dot notation to JSONB path: 'user.age' -> properties->'user'->>'age'
                    parts = property_key.split(".")
                    property_path = "properties"
                    for part in parts[:-1]:
                        property_path += f"->'{part}'"
                    property_path += f"->>'{parts[-1]}'"
                else:
                    property_path = f"properties->>'{property_key}'"

                query = text(f"""
                    SELECT 
                        id, source_id, target_id, label, properties, tags,
                        weight, context, metadata, created_at, updated_at
                    FROM edge
                    WHERE {property_path} = :value
                    LIMIT :limit
                """)

                result = session.execute(
                    query, {"label": label, "value": str(property_value), "limit": limit}
                ).fetchall()
                session.close()

                return [self._format_edge_result(row) for row in result if row]
            except Exception as e:
                raise Exception(f"Error getting edges by property: {str(e)}")

    def count_edges(self, filter_obj: Optional[EdgeFilter] = None) -> int:
        """Count edges matching criteria

        Args:
            filter_obj: Optional EdgeFilter for filtering

        Returns:
            Count of matching edges
        """
        with self.postgres_db.get_session() as session:
            try:
                query = "SELECT COUNT(*) as count FROM edge WHERE 1=1"
                params = {}

                if filter_obj:
                    if filter_obj.label:
                        query += " AND label = :label"
                        params["label"] = filter_obj.label

                    if filter_obj.source_id:
                        query += " AND source_id = :source_id"
                        params["source_id"] = str(filter_obj.source_id)

                    if filter_obj.target_id:
                        query += " AND target_id = :target_id"
                        params["target_id"] = str(filter_obj.target_id)

                    if filter_obj.tags:
                        query += " AND tags @> :tags::jsonb"
                        params["tags"] = str(filter_obj.tags).replace("'", '"')

                result = session.execute(text(query), params).first()
                return result.count if result else 0
            except Exception as e:
                raise Exception(f"Error counting edges: {str(e)}")

    # ==================== RELATIONSHIP OPERATIONS ====================

    def get_connected_nodes(
        self,
        node_id: UUID,
        edge_label: Optional[str] = None,
        direction: str = "both",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get nodes connected to a given node

        Args:
            node_id: Source node UUID
            edge_label: Optional edge label filter
            direction: 'outgoing', 'incoming', or 'both'
            limit: Maximum number of results

        Returns:
            List of connected nodes with edge information
        """
        with self.postgres_db.get_session() as session:
            try:
                if direction == "outgoing":
                    query = """
                        SELECT 
                            n.id, n.label, n.properties, n.tags, n.embedding,
                            n.text_content, n.summary, n.metadata, n.created_at, n.updated_at,
                            e.label as edge_label, e.weight
                        FROM edge e
                        JOIN node n ON e.target_id = n.id
                        WHERE e.source_id = :node_id
                    """
                elif direction == "incoming":
                    query = """
                        SELECT 
                            n.id, n.label, n.properties, n.tags, n.embedding,
                            n.text_content, n.summary, n.metadata, n.created_at, n.updated_at,
                            e.label as edge_label, e.weight
                        FROM edge e
                        JOIN node n ON e.source_id = n.id
                        WHERE e.target_id = :node_id
                    """
                else:  # both
                    query = """
                        SELECT 
                            n.id, n.label, n.properties, n.tags, n.embedding,
                            n.text_content, n.summary, n.metadata, n.created_at, n.updated_at,
                            e.label as edge_label, e.weight
                        FROM edge e
                        JOIN node n ON (e.target_id = n.id AND e.source_id = :node_id)
                            OR (e.source_id = n.id AND e.target_id = :node_id)
                        WHERE :node_id IN (e.source_id, e.target_id)
                    """

                params = {"node_id": str(node_id), "limit": limit}

                if edge_label:
                    query += " AND e.label = :edge_label"
                    params["edge_label"] = edge_label

                query += " LIMIT :limit"

                result = session.execute(text(query), params).fetchall()

                nodes = []
                for row in result:
                    node_data = self._format_node_result(row)
                    node_data["edge_label"] = row.edge_label
                    node_data["edge_weight"] = row.weight
                    nodes.append(node_data)

                return nodes
            except Exception as e:
                raise Exception(f"Error getting connected nodes: {str(e)}")

    def get_node_statistics(self, node_id: UUID) -> Dict[str, Any]:
        """Get statistics about a node (connections, relationships)

        Args:
            node_id: Node UUID

        Returns:
            Dictionary with node statistics
        """
        with self.postgres_db.get_session() as session:
            try:
                # Get the node first
                node = self.get_node_by_id(node_id)
                if not node:
                    return {"error": "Node not found"}

                query = text("""
                    SELECT 
                        COUNT(DISTINCT e1.id) as outgoing_edges,
                        COUNT(DISTINCT e2.id) as incoming_edges,
                        COUNT(DISTINCT CASE WHEN e1.label = :viewed THEN e1.target_id END) as viewed_count,
                        COUNT(DISTINCT CASE WHEN e1.label = :bought THEN e1.target_id END) as bought_count,
                        AVG(CASE WHEN e1.id IS NOT NULL THEN e1.weight ELSE NULL END) as avg_outgoing_weight,
                        AVG(CASE WHEN e2.id IS NOT NULL THEN e2.weight ELSE NULL END) as avg_incoming_weight
                    FROM node n
                    LEFT JOIN edge e1 ON n.id = e1.source_id
                    LEFT JOIN edge e2 ON n.id = e2.target_id
                    WHERE n.id = :node_id
                """)

                result = session.execute(
                    query, {"node_id": str(node_id), "viewed": "Viewed", "bought": "Bought"}
                ).first()

                return {
                    "node": node,
                    "outgoing_edges": result.outgoing_edges or 0,
                    "incoming_edges": result.incoming_edges or 0,
                    "viewed_count": result.viewed_count or 0,
                    "bought_count": result.bought_count or 0,
                    "avg_outgoing_weight": float(result.avg_outgoing_weight)
                    if result.avg_outgoing_weight
                    else 0,
                    "avg_incoming_weight": float(result.avg_incoming_weight)
                    if result.avg_incoming_weight
                    else 0,
                }
            except Exception as e:
                raise Exception(f"Error getting node statistics: {str(e)}")

    def semantic_search(
        self,
        query_embedding: List[float],
        match_threshold: float = 0.7,
        match_count: int = 10,
        filter_label: Optional[str] = None,
    ) -> List[dict]:
        """Perform semantic search using vector embeddings

        Args:
            query_embedding: Query embedding vector (1536 dimensions)
            match_threshold: Minimum similarity threshold (0-1)
            match_count: Maximum number of results
            filter_label: Optional filter by node label

        Returns:
            List of matching nodes with similarity scores
        """
        with self.postgres_db.get_session() as session:
            query = text("""
                         SELECT * FROM search_nodes_by_embedding(
                                 :embedding::vector(1536),
                                 :threshold,
                                 :count,
                                 :label
                                       )
                         """)

            results = session.execute(
                query,
                {
                    "embedding": query_embedding,
                    "threshold": match_threshold,
                    "count": match_count,
                    "label": filter_label,
                },
            )

            return [
                {
                    "id": row.id,
                    "label": row.label,
                    "text_content": row.text_content,
                    "summary": row.summary,
                    "similarity": row.similarity,
                }
                for row in results
            ]

    def graph_traverse(
        self,
        start_node_id: UUID,
        edge_labels: Optional[List[str]] = None,
        max_depth: int = 3,
        direction: str = "both",
    ) -> List[dict]:
        """Traverse the graph from a starting node

        Args:
            start_node_id: Starting node UUID
            edge_labels: Optional list of edge labels to follow
            max_depth: Maximum traversal depth
            direction: 'outgoing', 'incoming', or 'both'

        Returns:
            List of nodes in traversal order with depth and path
        """
        with self.postgres_db.get_session() as session:
            query = text("""
                         SELECT * FROM traverse_graph(
                                 :start_id,
                                 :labels,
                                 :depth,
                                 :direction
                                       )
                         """)

            results = session.execute(
                query,
                {
                    "start_id": start_node_id,
                    "labels": edge_labels,
                    "depth": max_depth,
                    "direction": direction,
                },
            )

            rows = [
                {
                    "node_id": str(row.node_id),
                    "node_label": row.node_label,
                    "depth": row.depth,
                    "path": [str(p) for p in row.path],
                    "edge_labels_path": [str(l) for l in row.edge_labels_path],
                    "edge_weights_path": [float(w) for w in row.edge_weights_path],
                }
                for row in results
            ]

            return rows

    def hybrid_search(
        self,
        query_text: str,
        query_embedding: Optional[List[float]] = None,
        semantic_weight: float = 0.5,
        match_count: int = 10,
    ) -> List[dict]:
        """Perform hybrid search combining semantic and full-text search

        Args:
            query_text: Text query for full-text search
            query_embedding: Optional embedding for semantic search
            semantic_weight: Weight for semantic vs full-text (0-1)
            match_count: Maximum number of results

        Returns:
            List of matching nodes with combined scores
        """
        with self.postgres_db.get_session() as session:
            query = text("""
                         SELECT * FROM hybrid_search(
                                 :text,
                                 :embedding::vector(1536),
                                 :weight,
                                 :count
                                       )
                         """)

            results = session.execute(
                query,
                {
                    "text": query_text,
                    "embedding": query_embedding,
                    "weight": semantic_weight,
                    "count": match_count,
                },
            )

            return [
                {
                    "id": row.id,
                    "label": row.label,
                    "text_content": row.text_content,
                    "summary": row.summary,
                    "score": row.score,
                }
                for row in results
            ]

    def get_user_interactions(
        self, user_id: UUID, interaction_types: Optional[List[str]] = None
    ) -> List[dict]:
        """Get all interactions for a user

        Args:
            user_id: User node UUID
            interaction_types: Optional filter by edge labels (e.g., ['Viewed', 'Bought'])

        Returns:
            List of interactions with product details
        """
        with self.postgres_db.get_session() as session:
            interaction_filter = ""
            if interaction_types:
                placeholders = ",".join([f"'{t}'" for t in interaction_types])
                interaction_filter = f"AND e.label IN ({placeholders})"

            query = text(f"""
                    SELECT 
                        n.id as product_id,
                        n.label as product_label,
                        n.summary as product_summary,
                        n.text_content as product_description,
                        e.label as interaction_type,
                        e.weight as interaction_weight,
                        e.context as interaction_context,
                        e.created_at as interaction_time
                    FROM node n
                    JOIN edge e ON e.target_id = n.id
                    WHERE e.source_id = :user_id
                        {interaction_filter}
                    ORDER BY e.weight DESC, e.created_at DESC
                """)

            results = session.execute(query, {"user_id": user_id})

            return [
                {
                    "product_id": str(row.product_id),
                    "product_label": row.product_label,
                    "product_summary": row.product_summary,
                    "product_description": row.product_description,
                    "interaction_type": row.interaction_type,
                    "interaction_weight": row.interaction_weight,
                    "interaction_context": row.interaction_context,
                    "interaction_time": row.interaction_time,
                }
                for row in results
            ]

    def get_product_recommendations(self, user_id: UUID, limit: int = 10) -> List[dict]:
        """Get product recommendations based on collaborative filtering

        Args:
            user_id: User node UUID
            limit: Maximum number of recommendations

        Returns:
            List of recommended products with scores
        """
        with self.postgres_db.get_session() as session:
            query = text("""
                         WITH similar_users AS (
                             -- Find users who bought similar products
                             SELECT DISTINCT e2.source_id as similar_user_id
                             FROM edge e1
                                      JOIN edge e2 ON e1.target_id = e2.target_id
                             WHERE e1.source_id = :user_id
                             AND e1.label = 'Bought'
                             AND e2.label = 'Bought'
                             AND e2.source_id != :user_id
                             LIMIT 100
                             )
                         SELECT
                             n.id as product_id,
                             n.label as product_label,
                             n.summary as product_summary,
                             n.text_content as product_description,
                             COUNT(*) as recommendation_score,
                             AVG(e.weight) as avg_weight
                         FROM similar_users su
                                  JOIN edge e ON e.source_id = su.similar_user_id
                                  JOIN node n ON n.id = e.target_id
                         WHERE e.label = 'Bought'
                           AND n.label = 'Product'
                           AND NOT EXISTS (
                             SELECT 1 FROM edge e2
                             WHERE e2.source_id = :user_id
                                 AND e2.target_id = n.id
                                 AND e2.label = 'Bought'
                         )
                         GROUP BY n.id, n.label, n.summary, n.text_content
                         ORDER BY recommendation_score DESC, avg_weight DESC
                             LIMIT :limit
                         """)

            results = session.execute(query, {"user_id": user_id, "limit": limit})

            return [
                {
                    "product_id": str(row.product_id),
                    "product_label": row.product_label,
                    "product_summary": row.product_summary,
                    "product_description": row.product_description,
                    "recommendation_score": row.recommendation_score,
                    "avg_weight": float(row.avg_weight),
                }
                for row in results
            ]

    def create_node_with_embedding(
        self,
        label: str,
        text_content: str,
        summary: str,
        embedding: List[float],
        properties: Optional[dict] = None,
        tags: Optional[dict] = None,
        meta: Optional[dict] = None,
    ) -> str:
        """Create a new node with embedding

        Args:
            label: Node type
            text_content: Full text content
            summary: Short summary
            embedding: Embedding vector (1536 dimensions)
            properties: Optional structured properties
            tags: Optional tags
            meta: Optional metadata

        Returns:
            Created node ID
        """
        with self.postgres_db.get_session() as session:
            node = Node(
                label=label,
                text_content=text_content,
                summary=summary,
                embedding=embedding,
                properties=properties or {},
                tags=tags or {},
                meta=meta or {},
            )
            session.add(node)
            session.commit()
            session.refresh(node)
            return str(node.id)

    def create_weighted_edge(
        self,
        source_id: UUID,
        target_id: UUID,
        label: str,
        weight: float,
        context: str,
        properties: Optional[dict] = None,
        tags: Optional[dict] = None,
        meta: Optional[dict] = None,
    ) -> str:
        """Create a new weighted edge

        Args:
            source_id: Source node UUID
            target_id: Target node UUID
            label: Edge type
            weight: Edge importance/strength
            context: Contextual description
            properties: Optional structured properties
            tags: Optional tags
            meta: Optional metadata

        Returns:
            Created edge ID
        """
        with self.postgres_db.get_session() as session:
            edge = Edge(
                source_id=source_id,
                target_id=target_id,
                label=label,
                weight=weight,
                context=context,
                properties=properties or {},
                tags=tags or {},
                meta=meta or {},
            )
            session.add(edge)
            session.commit()
            session.refresh(edge)
            return str(edge.id)

    # ==================== HELPER METHODS ====================

    @staticmethod
    def _format_node_result(row) -> Optional[Dict[str, Any]]:
        """Format database row to node dictionary"""
        if row is None:
            return None

        return {
            "id": str(row.id),
            "label": row.label,
            "properties": dict(row.properties) if row.properties else {},
            "tags": dict(row.tags) if row.tags else {},
            "text_content": row.text_content,
            "summary": row.summary,
            "metadata": dict(row.metadata) if row.metadata else {},
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def _format_edge_result(row) -> Optional[Dict[str, Any]]:
        """Format database row to edge dictionary"""
        if row is None:
            return None

        return {
            "id": str(row.id),
            "source_id": str(row.source_id),
            "target_id": str(row.target_id),
            "label": row.label,
            "properties": dict(row.properties) if row.properties else {},
            "tags": dict(row.tags) if row.tags else {},
            "weight": float(row.weight) if row.weight else 1.0,
            "context": row.context,
            "metadata": dict(row.metadata) if row.metadata else {},
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    def search_edges_by_embedding(
        self,
        query_embedding: List[float],
        match_threshold: float = 0.7,
        match_count: int = 10,
        filter_label: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Perform semantic search over edges using vector embeddings

        Args:
            query_embedding: Query embedding vector (1536 dimensions)
            match_threshold: Minimum similarity threshold (0-1)
            match_count: Maximum number of results
            filter_label: Optional filter by edge label

        Returns:
            List of matching edges with similarity scores
        """
        try:
            with self.postgres_db.get_session() as session:
                query = text("""
                    SELECT * FROM search_edges_by_embedding(
                        :embedding::vector(1536),
                        :threshold,
                        :count,
                        :label
                    )
                """)

                results = session.execute(
                    query,
                    {
                        "embedding": query_embedding,
                        "threshold": match_threshold,
                        "count": match_count,
                        "label": filter_label,
                    },
                )

                return [
                    {
                        "id": str(row.id),
                        "source_id": str(row.source_id),
                        "target_id": str(row.target_id),
                        "label": row.label,
                        "context": row.context,
                        "weight": float(row.weight) if row.weight else 1.0,
                        "similarity": row.similarity,
                    }
                    for row in results
                ]
        except Exception as e:
            raise Exception(f"Error searching edges by embedding: {str(e)}")
