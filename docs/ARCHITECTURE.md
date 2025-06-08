# Knowledge Graph RAG Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Recommend System                          │
│                  Knowledge Graph RAG Platform                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Application    │      │   Infrastructure │      │    Database      │
│     Layer        │◄────►│      Layer       │◄────►│   PostgreSQL     │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

## Detailed Architecture

### 1. Database Layer (PostgreSQL + pgvector)

```
┌────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                     │
├────────────────────────────────────────────────────────────┤
│  Extensions:                                                │
│  • uuid-ossp   - UUID utilities                            │
│  • pgcrypto    - Cryptographic functions                   │
│  • vector      - Vector similarity search (pgvector)       │
├────────────────────────────────────────────────────────────┤
│  Core Tables:                                               │
│  ┌──────────────────────────┐  ┌──────────────────────┐   │
│  │         node             │  │        edge          │   │
│  ├──────────────────────────┤  ├──────────────────────┤   │
│  │ • id (UUID v7)           │  │ • id (UUID v7)       │   │
│  │ • label (VARCHAR)        │  │ • source_id (FK)     │   │
│  │ • properties (JSONB)     │  │ • target_id (FK)     │   │
│  │ • tags (JSONB)           │  │ • label (VARCHAR)    │   │
│  │ • embedding (VECTOR)     │  │ • properties (JSONB) │   │
│  │ • text_content (TEXT)    │  │ • tags (JSONB)       │   │
│  │ • summary (TEXT)         │  │ • weight (FLOAT)     │   │
│  │ • metadata (JSONB)       │  │ • context (TEXT)     │   │
│  │ • created_at             │  │ • metadata (JSONB)   │   │
│  │ • updated_at             │  │ • created_at         │   │
│  └──────────────────────────┘  │ • updated_at         │   │
│                                  └──────────────────────┘   │
├────────────────────────────────────────────────────────────┤
│  Indexes:                                                   │
│  • GIN indexes on JSONB fields                             │
│  • IVFFlat index on embeddings (vector_cosine_ops)         │
│  • Full-text search (GIN) on text_content                  │
│  • Composite indexes for common patterns                   │
├────────────────────────────────────────────────────────────┤
│  Functions:                                                 │
│  • uuid_generate_v7()        - Generate UUID v7            │
│  • search_nodes_by_embedding() - Semantic search           │
│  • traverse_graph()          - Graph traversal             │
│  • hybrid_search()           - Combined search             │
│  • update_updated_at_column() - Auto timestamps            │
├────────────────────────────────────────────────────────────┤
│  Materialized Views:                                        │
│  • node_connectivity - Graph statistics                    │
└────────────────────────────────────────────────────────────┘
```

### 2. Domain Models (SQLAlchemy ORM)

```
┌────────────────────────────────────────────────────────────┐
│              ai_recommend.domain.models                    │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  class Node(Base):                                          │
│      """Knowledge Graph Node with RAG capabilities"""      │
│      - Maps to 'node' table                                │
│      - Type hints with Mapped[]                            │
│      - Automatic UUID v7 generation                        │
│      - Vector embeddings support                           │
│      - Automatic timestamps                                │
│                                                             │
│  class Edge(Base):                                          │
│      """Knowledge Graph Edge with weighted relationships"""│
│      - Maps to 'edge' table                                │
│      - Foreign keys to Node                                │
│      - Weighted relationships                              │
│      - Contextual information                              │
│                                                             │
│  class Field:                                               │
│      """Structured property field"""                       │
│      - name: str                                           │
│      - data_type: DataType (enum)                          │
│      - value: str                                          │
│      - original_value() method for type conversion         │
│                                                             │
│  enum DataType:                                             │
│      STRING, INT, DOUBLE, BOOLEAN, DATETIME, DATE, ARRAY   │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 3. Infrastructure Layer

```
┌────────────────────────────────────────────────────────────┐
│          ai_recommend.infrastructure.graph                 │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  class KnowledgeGraphRAG:                                   │
│      """High-level interface for RAG operations"""         │
│                                                             │
│      Search Operations:                                     │
│      ┌────────────────────────────────────────┐            │
│      │ • semantic_search()                    │            │
│      │   - Vector similarity search           │            │
│      │   - Cosine distance matching           │            │
│      │   - Configurable threshold             │            │
│      │                                        │            │
│      │ • hybrid_search()                      │            │
│      │   - Semantic + full-text combined     │            │
│      │   - Weighted scoring                   │            │
│      │   - Ranked results                     │            │
│      └────────────────────────────────────────┘            │
│                                                             │
│      Graph Operations:                                      │
│      ┌────────────────────────────────────────┐            │
│      │ • graph_traverse()                     │            │
│      │   - Recursive traversal                │            │
│      │   - Cycle detection                    │            │
│      │   - Path tracking                      │            │
│      │                                        │            │
│      │ • get_user_interactions()              │            │
│      │   - User activity retrieval            │            │
│      │   - Filtered by interaction type       │            │
│      │                                        │            │
│      │ • get_product_recommendations()        │            │
│      │   - Collaborative filtering            │            │
│      │   - Weight-based ranking               │            │
│      └────────────────────────────────────────┘            │
│                                                             │
│      Write Operations:                                      │
│      ┌────────────────────────────────────────┐            │
│      │ • create_node_with_embedding()         │            │
│      │   - Create nodes with vectors          │            │
│      │                                        │            │
│      │ • create_weighted_edge()               │            │
│      │   - Create weighted relationships      │            │
│      └────────────────────────────────────────┘            │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 4. RAG Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      RAG Pipeline                            │
└─────────────────────────────────────────────────────────────┘

1. Query Input
   │
   ├─► User Query: "I need wireless electronics"
   │
   ▼

2. Embedding Generation
   │
   ├─► OpenAI Embeddings API
   │   model: "text-embedding-ada-002"
   │   output: 1536-dimensional vector
   │
   ▼

3. Context Retrieval (Parallel)
   │
   ├─► Semantic Search
   │   • Vector similarity (cosine distance)
   │   • Top-k most similar nodes
   │   • Threshold filtering
   │
   ├─► Full-Text Search
   │   • PostgreSQL tsvector/tsquery
   │   • Ranked by relevance
   │
   ├─► Graph Traversal (Optional)
   │   • Related entities
   │   • User history
   │   • Product associations
   │
   ▼

4. Context Aggregation
   │
   ├─► Combine results
   ├─► Rank by score/weight
   ├─► Build context window
   │   • Summaries for overview
   │   • Full text for details
   │   • Metadata for filtering
   │
   ▼

5. LLM Generation
   │
   ├─► GPT-4 / Claude / etc.
   │   system: "You are a helpful assistant..."
   │   user: "Context: [retrieved data]\n\nQuestion: [query]"
   │
   ▼

6. Response
   │
   └─► Generated answer with citations
```

### 5. Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Flow Diagram                         │
└─────────────────────────────────────────────────────────────┘

Application Layer
      │
      ├─► KnowledgeGraphRAG
      │   │
      │   ├─► semantic_search()
      │   │   │
      │   │   ├─► SQL: search_nodes_by_embedding()
      │   │   │        ↓
      │   │   │   IVFFlat Index Scan
      │   │   │        ↓
      │   │   │   Cosine Distance Calc
      │   │   │        ↓
      │   │   └─► Results (id, summary, similarity)
      │   │
      │   ├─► hybrid_search()
      │   │   │
      │   │   ├─► SQL: hybrid_search()
      │   │   │        ↓
      │   │   │   Parallel: Vector Search + FTS
      │   │   │        ↓
      │   │   │   Weighted Scoring
      │   │   │        ↓
      │   │   └─► Results (ranked by score)
      │   │
      │   ├─► graph_traverse()
      │   │   │
      │   │   ├─► SQL: traverse_graph() [Recursive CTE]
      │   │   │        ↓
      │   │   │   Breadth-First Traversal
      │   │   │        ↓
      │   │   │   Cycle Detection
      │   │   │        ↓
      │   │   └─► Results (nodes + paths)
      │   │
      │   └─► get_product_recommendations()
      │       │
      │       ├─► SQL: Collaborative Filtering
      │       │        ↓
      │       │   Find Similar Users
      │       │        ↓
      │       │   Aggregate Products
      │       │        ↓
      │       │   Weight-Based Ranking
      │       │        ↓
      │       └─► Results (recommendations)
      │
      ▼
PostgreSQL Database
```

### 6. Index Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                   Index Architecture                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Node Table Indexes:                                         │
│  ┌────────────────────────────────────────────────┐         │
│  │ 1. PRIMARY KEY (id) - B-tree                   │         │
│  │    → Fast primary key lookups                  │         │
│  │                                                 │         │
│  │ 2. ix_node_label - B-tree                      │         │
│  │    → Filter by entity type                     │         │
│  │                                                 │         │
│  │ 3. ix_node_tags_gin - GIN                      │         │
│  │    → Fast JSONB key-value queries              │         │
│  │                                                 │         │
│  │ 4. ix_node_metadata_gin - GIN                  │         │
│  │    → Metadata filtering                        │         │
│  │                                                 │         │
│  │ 5. ix_node_text_content_fts - GIN              │         │
│  │    → Full-text search (tsvector)               │         │
│  │                                                 │         │
│  │ 6. ix_node_embedding_cosine - IVFFlat          │         │
│  │    → Approximate nearest neighbor              │         │
│  │    → Cosine distance operator (<=>)            │         │
│  │    → Lists parameter: 100                      │         │
│  │                                                 │         │
│  │ 7. ix_node_label_created - B-tree (composite)  │         │
│  │    → Recent entities by type                   │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  Edge Table Indexes:                                         │
│  ┌────────────────────────────────────────────────┐         │
│  │ 1. PRIMARY KEY (id) - B-tree                   │         │
│  │                                                 │         │
│  │ 2. ix_edge_source_id - B-tree                  │         │
│  │    → Outgoing edges from node                  │         │
│  │                                                 │         │
│  │ 3. ix_edge_target_id - B-tree                  │         │
│  │    → Incoming edges to node                    │         │
│  │                                                 │         │
│  │ 4. ix_edge_label - B-tree                      │         │
│  │    → Filter by relationship type               │         │
│  │                                                 │         │
│  │ 5. ix_edge_weight - B-tree                     │         │
│  │    → Sort by importance                        │         │
│  │                                                 │         │
│  │ 6. ix_edge_source_label - B-tree (composite)   │         │
│  │    → Specific relationships from node          │         │
│  │                                                 │         │
│  │ 7. ix_edge_target_label - B-tree (composite)   │         │
│  │    → Specific relationships to node            │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Docker Compose Setup                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Host Machine (macOS)                                        │
│  └─► Docker Desktop                                          │
│      │                                                       │
│      ├─► Network: ai-recommend-bridge (bridge driver)       │
│      │   └─► 0.0.0.0:5432 → postgres:5432                   │
│      │                                                       │
│      └─► Container: postgres                                │
│          ├─► Image: postgres:16-alpine                      │
│          ├─► Environment:                                   │
│          │   • POSTGRES_USER=postgres                       │
│          │   • POSTGRES_PASSWORD=postgres                   │
│          │   • POSTGRES_DB=ai_recommend                     │
│          ├─► Volumes:                                       │
│          │   • postgres-data → /var/lib/postgresql/data    │
│          │   • .deploy/scripts → /docker-entrypoint-initdb.d │
│          ├─► Health Check:                                  │
│          │   • pg_isready -U postgres                       │
│          │   • Interval: 10s, Timeout: 5s, Retries: 5      │
│          └─► Auto-initialization:                           │
│              • 0001_schema.sql (runs first)                 │
│              • 0002_data.sql (runs second)                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 8. Management Tools

```
┌─────────────────────────────────────────────────────────────┐
│              Management Script (pg-manage.sh)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Commands:                                                   │
│  ┌──────────────────────────────────────────────┐           │
│  │ start    → docker compose up -d postgres     │           │
│  │ stop     → docker compose stop postgres      │           │
│  │ restart  → docker compose restart postgres   │           │
│  │ reset    → Remove volume + reinitialize      │           │
│  │ logs     → docker compose logs -f postgres   │           │
│  │ shell    → psql -U postgres -d ai_recommend  │           │
│  │ stats    → Show node/edge counts by type     │           │
│  │ test     → Check connection + display info   │           │
│  │ help     → Show usage information            │           │
│  └──────────────────────────────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Performance Characteristics

### Query Performance

| Operation              | Avg Time    | Index Used           | Scalability        |
|------------------------|-------------|----------------------|--------------------|
| Semantic Search        | ~10-50ms    | IVFFlat             | O(log n)           |
| Full-Text Search       | ~5-30ms     | GIN (tsvector)      | O(log n)           |
| Hybrid Search          | ~20-80ms    | Both                | O(log n)           |
| Graph Traversal (d=3)  | ~10-100ms   | B-tree on edges     | O(k^d) k=branching |
| Collaborative Filter   | ~50-200ms   | Multiple B-tree     | O(n log n)         |

### Storage Estimates

| Component              | Size (10MB dataset) | Size (1GB dataset) | Size (100GB dataset) |
|------------------------|---------------------|--------------------|-----------------------|
| Node table             | ~8 MB               | ~800 MB            | ~80 GB                |
| Edge table             | ~2 MB               | ~200 MB            | ~20 GB                |
| Vector index (IVFFlat) | ~1 MB               | ~100 MB            | ~10 GB                |
| GIN indexes            | ~500 KB             | ~50 MB             | ~5 GB                 |
| Total                  | ~12 MB              | ~1.2 GB            | ~120 GB               |

## Summary

The Knowledge Graph RAG system provides:

✅ **Complete RAG Infrastructure**
   - Vector embeddings for semantic search
   - Full-text search for keyword matching
   - Graph traversal for relationship discovery
   - Hybrid search for best of both worlds

✅ **Scalable Architecture**
   - Efficient indexing strategies
   - Optimized query functions
   - Materialized views for analytics
   - Automatic maintenance (timestamps, triggers)

✅ **Developer-Friendly**
   - Clean Python interface (KnowledgeGraphRAG)
   - SQLAlchemy ORM models
   - Management scripts
   - Comprehensive documentation

✅ **Production-Ready**
   - Docker containerization
   - Health checks
   - Auto-initialization
   - Data persistence

The system is now ready for AI-powered recommendation engines, semantic search applications, and advanced RAG pipelines.

