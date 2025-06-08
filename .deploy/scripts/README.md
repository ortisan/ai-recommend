# PostgreSQL Initialization Scripts

This directory contains SQL scripts that are automatically executed when the PostgreSQL container is first initialized.

## Overview

The database is configured as a **Knowledge Graph with RAG (Retrieval-Augmented Generation)** capabilities, featuring:
- Vector embeddings for semantic search (pgvector)
- Full-text search with PostgreSQL
- Graph traversal functions
- Hybrid search (semantic + keyword)
- Weighted relationships for ranking

See [Knowledge Graph RAG Documentation](../../docs/KNOWLEDGE_GRAPH_RAG.md) for detailed usage guide.

## Execution Order

Scripts are executed in alphabetical order by the PostgreSQL Docker image. The following scripts are present:

1. **0001_schema.sql** - Creates the Knowledge Graph schema
   - Enables extensions: uuid-ossp, pgcrypto, vector (pgvector)
   - UUID v7 generation function
   - `node` table with RAG fields (embedding, text_content, summary, metadata)
   - `edge` table with weighted relationships (weight, context, metadata)
   - Advanced indexes (GIN, IVFFlat for vectors, full-text search)
   - RAG utility functions (semantic search, graph traversal, hybrid search)
   - Materialized views for graph analytics
   - Automatic timestamp triggers

2. **0002_data.sql** - Populates the database with realistic mock data (~10MB)
   - 2,000 User nodes with demographics and behavior
   - 5,000 Product nodes with descriptions and metadata
   - 8,000 Session nodes with engagement metrics
   - ~30,000 Viewed edges with interaction data
   - ~12,000 Bought edges with transaction details
   - All nodes include text_content and summary for RAG
   - All edges include weight and context for ranking

## How It Works

The Docker Compose configuration mounts this directory to `/docker-entrypoint-initdb.d` in the PostgreSQL container:

```yaml
volumes:
  - ./.deploy/scripts:/docker-entrypoint-initdb.d
```

**Important Notes:**
- Scripts only run on **first initialization** when the database is created
- If you want to re-run the scripts, you must delete the `postgres-data` volume
- Scripts with `.sql` extension are executed automatically
- Execution order is alphabetical, hence the numeric prefixes (01_, 02_, etc.)

## Resetting the Database

To reset the database and re-run the initialization scripts:

```bash
# Stop and remove containers
docker-compose down

# Remove the postgres volume
docker volume rm ai-recommend_postgres-data

# Start fresh
docker-compose up -d postgres
```

## Data Structure

### Node Types
- **User**: E-commerce users with properties like user_id, email, age, premium status
- **Product**: Products with properties like product_id, name, price, stock, rating
- **Session**: User sessions with properties like session_id, duration, page_views

### Edge Types
- **Viewed**: User → Product (viewing behavior)
- **Bought**: User → Product (purchase transactions)

All properties use the Field object structure with `name`, `data_type`, and `value` attributes.

