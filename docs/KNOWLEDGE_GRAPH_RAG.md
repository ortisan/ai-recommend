# Knowledge Graph RAG Implementation Guide

This document explains the Knowledge Graph setup optimized for Retrieval-Augmented Generation (RAG) in the AI Recommend system.

## Overview

The system uses a graph database structure (nodes and edges) enhanced with RAG-specific capabilities including:
- Vector embeddings for semantic search
- Full-text search capabilities
- Graph traversal functions
- Hybrid search (semantic + keyword)
- Weighted relationships

## Database Schema

### Node Table
Stores entities in the knowledge graph with RAG capabilities.

**Core Fields:**
- `id` (UUID v7): Primary key, time-ordered
- `label` (VARCHAR): Entity type (e.g., User, Product, Session)
- `properties` (JSONB): Structured properties using Field objects
- `tags` (JSONB): Flexible tags for categorization

**RAG-Specific Fields:**
- `embedding` (VECTOR(1536)): Vector embeddings for semantic search (OpenAI ada-002 compatible)
- `text_content` (TEXT): Full text content for retrieval and full-text search
- `summary` (TEXT): Concise summary for quick context in prompts
- `metadata` (JSONB): Flexible metadata (source, version, confidence, etc.)
- `created_at` / `updated_at`: Automatic timestamps

**Indexes:**
- GIN indexes on JSONB fields (tags, metadata)
- Full-text search index on text_content
- IVFFlat index on embeddings for fast vector search
- Composite indexes for common query patterns

### Edge Table
Stores relationships between nodes with contextual information.

**Core Fields:**
- `id` (UUID v7): Primary key
- `source_id` / `target_id` (UUID): Foreign keys to nodes
- `label` (VARCHAR): Relationship type (e.g., Viewed, Bought)
- `properties` (JSONB): Relationship properties
- `tags` (JSONB): Categorization tags

**RAG-Specific Fields:**
- `weight` (FLOAT): Edge importance/strength for weighted traversal
- `context` (TEXT): Contextual description of the relationship
- `metadata` (JSONB): Additional metadata
- `created_at` / `updated_at`: Automatic timestamps

## RAG Functions

### 1. Semantic Search
```sql
SELECT * FROM search_nodes_by_embedding(
    query_embedding := '[0.1, 0.2, ...]'::vector(1536),
    match_threshold := 0.7,
    match_count := 10,
    filter_label := 'Product'
);
```

Finds nodes similar to a query embedding using cosine similarity.

### 2. Graph Traversal
```sql
SELECT * FROM traverse_graph(
    start_node_id := '018d1234-5678-7000-8000-000000000001'::uuid,
    edge_labels := ARRAY['Viewed', 'Bought'],
    max_depth := 3,
    direction := 'both'  -- 'outgoing', 'incoming', or 'both'
);
```

Traverses the graph from a starting node following specified edge types.

### 3. Hybrid Search
```sql
SELECT * FROM hybrid_search(
    query_text := 'wireless mouse',
    query_embedding := '[0.1, 0.2, ...]'::vector(1536),
    semantic_weight := 0.5,
    match_count := 10
);
```

Combines semantic (vector) and keyword (full-text) search with configurable weighting.

## Usage Patterns

### 1. Product Recommendations
```python
from sqlalchemy import text

# Find similar products based on embeddings
query = text("""
    SELECT id, label, summary, 
           1 - (embedding <=> :query_embedding) as similarity
    FROM node
    WHERE label = 'Product'
        AND embedding IS NOT NULL
    ORDER BY embedding <=> :query_embedding
    LIMIT 10
""")

results = session.execute(query, {"query_embedding": embedding_vector})
```

### 2. User Behavior Analysis
```python
# Get products a user viewed and bought
query = text("""
    SELECT 
        n.id,
        n.summary,
        e.label as interaction_type,
        e.weight,
        e.context
    FROM node n
    JOIN edge e ON e.target_id = n.id
    WHERE e.source_id = :user_id
        AND e.label IN ('Viewed', 'Bought')
    ORDER BY e.weight DESC, e.created_at DESC
""")

results = session.execute(query, {"user_id": user_id})
```

### 3. Context Retrieval for RAG
```python
# Get relevant context for a user query
query = text("""
    SELECT 
        n.text_content,
        n.summary,
        n.label,
        e.context as relationship_context
    FROM node n
    LEFT JOIN edge e ON e.source_id = n.id
    WHERE to_tsvector('english', n.text_content) @@ plainto_tsquery('english', :query)
        OR (n.embedding IS NOT NULL AND 1 - (n.embedding <=> :query_embedding) > 0.7)
    ORDER BY 
        CASE WHEN n.embedding IS NOT NULL THEN
            1 - (n.embedding <=> :query_embedding)
        ELSE 0 END DESC
    LIMIT 5
""")

context_results = session.execute(query, {
    "query": "electronics recommendations",
    "query_embedding": query_vector
})
```

### 4. Graph-Based Recommendations
```python
# Find products based on collaborative filtering
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
        n.id,
        n.summary,
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
    GROUP BY n.id, n.summary
    ORDER BY recommendation_score DESC, avg_weight DESC
    LIMIT 10
""")

recommendations = session.execute(query, {"user_id": user_id})
```

## SQLAlchemy Models

### Node Model
```python
from ai_recommend.domain.models import Node

# Create a new node
node = Node(
    label="Product",
    properties={
        "product_id": {"name": "product_id", "data_type": "string", "value": "P001"},
        "name": {"name": "name", "data_type": "string", "value": "Wireless Mouse"}
    },
    tags={"category": "electronics", "featured": True},
    text_content="High quality wireless mouse with ergonomic design...",
    summary="Wireless Mouse - Premium electronics",
    meta={"source": "product_catalog", "version": "1.0"},
    embedding=[0.1, 0.2, ...]  # 1536-dimensional vector
)
session.add(node)
session.commit()
```

### Edge Model
```python
from ai_recommend.domain.models import Edge

# Create a relationship
edge = Edge(
    source_id=user_id,
    target_id=product_id,
    label="Viewed",
    properties={
        "duration_seconds": {"name": "duration_seconds", "data_type": "int", "value": "45"}
    },
    tags={"device": "mobile", "source": "search"},
    weight=0.8,
    context="User viewed product for 45 seconds via mobile search",
    meta={"interaction_type": "product_view", "timestamp": "2026-02-16T10:00:00Z"}
)
session.add(edge)
session.commit()
```

## Data Generation

The system includes mock data generation with:
- **2,000 Users** with demographic and behavioral data
- **5,000 Products** with detailed descriptions and metadata
- **8,000 Sessions** tracking user activity
- **~30,000 Viewed** interactions with engagement metrics
- **~12,000 Bought** transactions with purchase details

All data includes RAG-specific fields populated with realistic content.

## pgvector Extension

The system uses pgvector for efficient vector similarity search:
- Supports up to 16,000 dimensions
- Cosine distance operator: `<=>`
- IVFFlat index for approximate nearest neighbor search
- Compatible with OpenAI, Cohere, and other embedding models

## Best Practices

### 1. Embedding Generation
- Use consistent embedding models (e.g., OpenAI ada-002, 1536 dimensions)
- Store both embedding and text_content for flexibility
- Update embeddings when text_content changes

### 2. Graph Traversal
- Use `weight` field to prioritize important relationships
- Implement cycle detection for recursive queries
- Limit traversal depth to prevent performance issues

### 3. Context Window Management
- Store concise summaries for quick context
- Use full text_content only when needed
- Leverage metadata for filtering and ranking

### 4. Index Maintenance
```sql
-- Refresh materialized view periodically
REFRESH MATERIALIZED VIEW node_connectivity;

-- Rebuild vector index if needed
REINDEX INDEX ix_node_embedding_cosine;
```

## Performance Optimization

1. **Vector Search**: Use appropriate `lists` parameter in IVFFlat index based on data size
2. **Full-Text Search**: Create custom dictionaries for domain-specific terms
3. **Graph Queries**: Use CTEs and proper indexing for complex traversals
4. **Caching**: Cache frequently accessed nodes and embeddings

## Docker Setup

The PostgreSQL container automatically:
1. Enables required extensions (uuid-ossp, pgcrypto, vector)
2. Creates UUID v7 generation function
3. Initializes schema with RAG capabilities
4. Loads mock data for testing

To reset and reinitialize:
```bash
./deploy/scripts/pg-manage.sh reset
```

## Integration with LLMs

### Example RAG Pipeline
```python
# 1. Generate embedding from user query
query_embedding = openai.embeddings.create(
    input="I need wireless electronics",
    model="text-embedding-ada-002"
).data[0].embedding

# 2. Retrieve relevant context
context_nodes = session.execute(
    text("SELECT * FROM search_nodes_by_embedding(:embedding, 0.7, 5)"),
    {"embedding": query_embedding}
).fetchall()

# 3. Build context for LLM
context = "\n".join([node.text_content for node in context_nodes])

# 4. Generate response with LLM
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful shopping assistant."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuery: {user_query}"}
    ]
)
```

## Monitoring

Key metrics to monitor:
- Vector search latency
- Graph traversal depth and execution time
- Index size and fragmentation
- Node/edge counts by label
- Embedding coverage (nodes with vs without embeddings)

Query the materialized view:
```sql
SELECT * FROM node_connectivity ORDER BY outgoing_edges DESC LIMIT 10;
```

## Future Enhancements

- [ ] Add support for multiple embedding dimensions
- [ ] Implement graph algorithms (PageRank, community detection)
- [ ] Add temporal queries for time-series analysis
- [ ] Implement batch embedding updates
- [ ] Add graph visualization endpoints
- [ ] Support for multi-modal embeddings (text + image)

