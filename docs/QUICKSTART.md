# Quick Start Guide: Knowledge Graph RAG

This guide will help you quickly set up and start using the Knowledge Graph RAG system.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.14+ (already set up in your project)
- uv package manager (already installed)

## Step 1: Start PostgreSQL with Knowledge Graph

```bash
# Navigate to project root
cd /Users/marcelo/Documents/Projects/ai-recommend

# Start PostgreSQL container (will auto-initialize with schema and data)
docker compose up -d postgres

# Wait for initialization (check logs)
docker compose logs -f postgres

# Test connection
./.deploy/scripts/pg-manage.sh test
```

## Step 2: Verify Data Load

```bash
# Check database statistics
./.deploy/scripts/pg-manage.sh stats

# Expected output:
# - 2,000 User nodes
# - 5,000 Product nodes
# - 8,000 Session nodes
# - ~30,000 Viewed edges
# - ~12,000 Bought edges
```

## Step 3: Connect via psql (Optional)

```bash
# Open PostgreSQL shell
./.deploy/scripts/pg-manage.sh shell

# Run sample queries
\dt  -- List tables

-- View nodes by type
SELECT label, COUNT(*) FROM node GROUP BY label;

-- View edges by type
SELECT label, COUNT(*) FROM edge GROUP BY label;

-- Sample node with RAG fields
SELECT id, label, summary, text_content FROM node WHERE label = 'Product' LIMIT 1;

-- Exit
\q
```

## Step 4: Use Python Interface

Create a Python script to interact with the Knowledge Graph:

```python
from ai_recommend.infrastructure.repository import KnowledgeGraphRAG

# Initialize connection
kg = KnowledgeGraphRAG(
    "postgresql://postgres:postgres@localhost:5432/ai_recommend"
)

# Example 1: Full-text search (without embeddings)
results = kg.hybrid_search(
    query_text="electronics",
    semantic_weight=0.0,  # Pure full-text search
    match_count=5
)

for result in results:
    print(f"Product: {result['summary']}")
    print(f"Score: {result['score']}")
    print("---")

# Example 2: Get user interactions
# First, get a user ID from the database
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres@localhost:5432/ai_recommend")

with engine.connect() as conn:
    user_result = conn.execute(text("SELECT id FROM node WHERE label = 'User' LIMIT 1"))
    user_id = str(user_result.fetchone()[0])

# Get interactions for that user
interactions = kg.get_user_interactions(
    user_id=user_id,
    interaction_types=["Viewed", "Bought"]
)

print(f"\nUser {user_id} interactions:")
for interaction in interactions[:5]:
    print(f"- {interaction['interaction_type']}: {interaction['product_summary']}")

# Example 3: Get recommendations
recommendations = kg.get_product_recommendations(
    user_id=user_id,
    limit=5
)

print(f"\nRecommendations for user {user_id}:")
for rec in recommendations:
    print(f"- {rec['product_summary']} (score: {rec['recommendation_score']})")
```

## Step 5: Add Vector Embeddings (Optional)

To use semantic search, you need to add embeddings to nodes. Here's how to integrate with OpenAI:

```python
import openai
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Set up OpenAI
openai.api_key = "your-api-key-here"

engine = create_engine("postgresql://postgres:postgres@localhost:5432/ai_recommend")

# Function to generate embedding
def generate_embedding(text: str) -> list:
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

# Update products with embeddings
with Session(engine) as session:
    # Get products without embeddings
    products = session.execute(text("""
        SELECT id, text_content 
        FROM node 
        WHERE label = 'Product' 
            AND embedding IS NULL 
        LIMIT 10
    """)).fetchall()
    
    for product_id, text_content in products:
        if text_content:
            # Generate embedding
            embedding = generate_embedding(text_content)
            
            # Update node
            session.execute(text("""
                UPDATE node 
                SET embedding = :embedding::vector(1536)
                WHERE id = :id
            """), {"embedding": embedding, "id": product_id})
    
    session.commit()
    print(f"Updated {len(products)} products with embeddings")

# Now you can use semantic search
kg = KnowledgeGraphRAG("postgresql://postgres:postgres@localhost:5432/ai_recommend")

query_text = "wireless mouse for gaming"
query_embedding = generate_embedding(query_text)

results = kg.semantic_search(
    query_embedding=query_embedding,
    match_threshold=0.7,
    match_count=5,
    filter_label="Product"
)

print("\nSemantic search results:")
for result in results:
    print(f"- {result['summary']} (similarity: {result['similarity']:.2f})")
```

## Step 6: Implement RAG Pipeline

Here's a complete RAG example:

```python
import openai
from ai_recommend.infrastructure.repository import KnowledgeGraphRAG

# Initialize
openai.api_key = "your-api-key-here"
kg = KnowledgeGraphRAG("postgresql://postgres:postgres@localhost:5432/ai_recommend")


def rag_query(user_query: str, user_id: str = None):
    """RAG pipeline for product recommendations"""

    # 1. Generate query embedding
    query_embedding = openai.embeddings.create(
        input=user_query,
        model="text-embedding-ada-002"
    ).data[0].embedding

    # 2. Retrieve relevant products (hybrid search)
    products = kg.hybrid_search(
        query_text=user_query,
        query_embedding=query_embedding,
        semantic_weight=0.7,
        match_count=5
    )

    # 3. Get user context if provided
    user_context = ""
    if user_id:
        interactions = kg.get_user_interactions(
            user_id=user_id,
            interaction_types=["Viewed", "Bought"]
        )

        if interactions:
            user_context = "\n\nUser's recent activity:\n"
            for i in interactions[:3]:
                user_context += f"- {i['interaction_type']}: {i['product_summary']}\n"

    # 4. Build context for LLM
    context = "Available products:\n"
    for p in products:
        context += f"\n{p['summary']}\n{p['text_content'][:200]}...\n"

    # 5. Generate response with GPT
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful e-commerce shopping assistant. Use the provided product context to answer questions and make recommendations."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n{user_context}\n\nUser question: {user_query}"
            }
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content


# Example usage
result = rag_query("I need a good wireless mouse for gaming")
print(result)

# With user context
# result = rag_query("What else would you recommend?", user_id="some-uuid")
# print(result)
```

## Common Operations

### Reset Database
```bash
# WARNING: This deletes all data!
./.deploy/scripts/pg-manage.sh reset
```

### View Logs
```bash
./.deploy/scripts/pg-manage.sh logs
```

### Stop Database
```bash
docker compose stop postgres
```

### Restart Database
```bash
./.deploy/scripts/pg-manage.sh restart
```

## Troubleshooting

### Port 5432 already in use
```bash
# Check what's using the port
lsof -i :5432

# Stop local PostgreSQL if running
brew services stop postgresql
# or
sudo systemctl stop postgresql
```

### Connection refused
```bash
# Check if container is running
docker compose ps

# Check logs for errors
docker compose logs postgres

# Verify health
./.deploy/scripts/pg-manage.sh test
```

### pgvector extension not found
The schema script should automatically install it. If not:
```sql
-- Connect to database
./.deploy/scripts/pg-manage.sh shell

-- Install extension manually
CREATE EXTENSION IF NOT EXISTS vector;
```

### Data not loading
```bash
# Check if scripts directory is mounted
docker compose exec postgres ls -la /docker-entrypoint-initdb.d

# View initialization logs
docker compose logs postgres | grep -i "database system is ready"

# If needed, reset completely
./.deploy/scripts/pg-manage.sh reset
```

## Next Steps

1. **Add Embeddings**: Generate embeddings for your nodes using OpenAI or another provider
2. **Create API**: Build REST/GraphQL endpoints for your RAG queries
3. **Optimize Performance**: Tune the IVFFlat index parameters based on your data size
4. **Monitor**: Set up monitoring for query performance and index health
5. **Scale**: Consider read replicas for high-traffic scenarios

## Useful Queries

### Check embedding coverage
```sql
SELECT 
    label,
    COUNT(*) as total,
    COUNT(embedding) as with_embedding,
    ROUND(100.0 * COUNT(embedding) / COUNT(*), 2) as coverage_percent
FROM node
GROUP BY label;
```

### Find most connected nodes
```sql
SELECT * FROM node_connectivity 
ORDER BY (outgoing_edges + incoming_edges) DESC 
LIMIT 10;
```

### Analyze edge weights
```sql
SELECT 
    label,
    COUNT(*) as count,
    AVG(weight) as avg_weight,
    MIN(weight) as min_weight,
    MAX(weight) as max_weight
FROM edge
GROUP BY label;
```

## Resources

- [Full Documentation](../docs/KNOWLEDGE_GRAPH_RAG.md)
- [Transformation Summary](../docs/RAG_TRANSFORMATION_SUMMARY.md)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

## Support

For issues or questions:
1. Check the logs: `./.deploy/scripts/pg-manage.sh logs`
2. Review the schema: `.deploy/scripts/0001_schema.sql`
3. Inspect the data generation: `.deploy/scripts/0002_data.sql`
4. Consult the full documentation in `docs/KNOWLEDGE_GRAPH_RAG.md`

