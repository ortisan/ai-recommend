-- PostgreSQL DDL for Knowledge Graph RAG
-- Schema for graph-based retrieval-augmented generation

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector for embeddings

-- Create UUID v7 generation function
CREATE OR REPLACE FUNCTION uuid_generate_v7() RETURNS uuid AS $$
DECLARE
    unix_ts_ms BIGINT;
    uuid_bytes BYTEA;
BEGIN
    unix_ts_ms := (EXTRACT(EPOCH FROM clock_timestamp()) * 1000)::BIGINT;
    uuid_bytes :=
        substring(int8send(unix_ts_ms) from 3 for 6) ||
        substring(gen_random_bytes(10) from 1 for 2) ||
        substring(gen_random_bytes(10) from 3 for 8);
    uuid_bytes := set_byte(uuid_bytes, 6, (get_byte(uuid_bytes, 6) & 15) | 112);
    uuid_bytes := set_byte(uuid_bytes, 8, (get_byte(uuid_bytes, 8) & 63) | 128);
    RETURN encode(uuid_bytes, 'hex')::uuid;
END;
$$ LANGUAGE plpgsql VOLATILE;

-- Create Node table with RAG capabilities
CREATE TABLE IF NOT EXISTS node (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    label VARCHAR(50) NOT NULL,
    properties JSONB,
    tags JSONB,

    -- RAG-specific fields
    embedding vector(1536),  -- For semantic search (OpenAI ada-002 dimension)
    text_content TEXT,  -- Full text content for retrieval
    summary TEXT,  -- Short summary for quick context
    metadata JSONB,  -- Additional metadata (source, timestamps, version, etc.)

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for Node table
CREATE INDEX IF NOT EXISTS ix_node_label ON node(label);
CREATE INDEX IF NOT EXISTS ix_node_tags_gin ON node USING gin(tags);
CREATE INDEX IF NOT EXISTS ix_node_metadata_gin ON node USING gin(metadata);
CREATE INDEX IF NOT EXISTS ix_node_text_content_fts ON node USING gin(to_tsvector('english', text_content));
CREATE INDEX IF NOT EXISTS ix_node_embedding_cosine ON node USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS ix_node_created_at ON node(created_at DESC);

-- Create Edge table with RAG capabilities
CREATE TABLE IF NOT EXISTS edge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    source_id UUID NOT NULL,
    target_id UUID NOT NULL,
    label VARCHAR(50) NOT NULL,
    properties JSONB,
    tags JSONB,

    -- RAG-specific fields
    weight FLOAT DEFAULT 1.0,  -- Edge importance/strength
    context TEXT,  -- Contextual information about the relationship
    metadata JSONB,  -- Additional metadata
    embedding vector(1536),  -- Optional embedding for edge semantics

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for Edge table
CREATE INDEX IF NOT EXISTS ix_edge_source_id ON edge(source_id);
CREATE INDEX IF NOT EXISTS ix_edge_target_id ON edge(target_id);
CREATE INDEX IF NOT EXISTS ix_edge_label ON edge(label);
CREATE INDEX IF NOT EXISTS ix_edge_tags_gin ON edge USING gin(tags);
CREATE INDEX IF NOT EXISTS ix_edge_metadata_gin ON edge USING gin(metadata);
CREATE INDEX IF NOT EXISTS ix_edge_weight ON edge(weight DESC);
CREATE INDEX IF NOT EXISTS ix_edge_created_at ON edge(created_at DESC);
CREATE INDEX IF NOT EXISTS ix_edge_embedding_cosine ON edge USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS ix_edge_source_label ON edge(source_id, label);
CREATE INDEX IF NOT EXISTS ix_edge_target_label ON edge(target_id, label);
CREATE INDEX IF NOT EXISTS ix_node_label_created ON node(label, created_at DESC);

-- Add foreign key constraints
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_edge_source'
    ) THEN
        ALTER TABLE edge ADD CONSTRAINT fk_edge_source FOREIGN KEY (source_id) REFERENCES node(id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_edge_target'
    ) THEN
        ALTER TABLE edge ADD CONSTRAINT fk_edge_target FOREIGN KEY (target_id) REFERENCES node(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
DROP TRIGGER IF EXISTS update_node_updated_at ON node;
CREATE TRIGGER update_node_updated_at BEFORE UPDATE ON node
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_edge_updated_at ON edge;
CREATE TRIGGER update_edge_updated_at BEFORE UPDATE ON edge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create materialized view for graph traversal optimization
DROP MATERIALIZED VIEW IF EXISTS node_connectivity;
CREATE MATERIALIZED VIEW node_connectivity AS
SELECT
    n.id,
    n.label,
    COUNT(DISTINCT e_out.id) as outgoing_edges,
    COUNT(DISTINCT e_in.id) as incoming_edges,
    COUNT(DISTINCT e_out.target_id) as connected_nodes_out,
    COUNT(DISTINCT e_in.source_id) as connected_nodes_in
FROM node n
LEFT JOIN edge e_out ON n.id = e_out.source_id
LEFT JOIN edge e_in ON n.id = e_in.target_id
GROUP BY n.id, n.label;

CREATE UNIQUE INDEX IF NOT EXISTS ix_node_connectivity_id ON node_connectivity (id);

-- Create function for semantic search
DROP FUNCTION IF EXISTS search_nodes_by_embedding(vector(1536), float, int, varchar);
CREATE FUNCTION search_nodes_by_embedding(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    filter_label varchar DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    label varchar,
    text_content text,
    summary text,
    similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        n.id,
        n.label,
        n.text_content,
        n.summary,
        1 - (n.embedding <=> query_embedding) as similarity
    FROM node n
    WHERE
        (filter_label IS NULL OR n.label = filter_label)
        AND n.embedding IS NOT NULL
        AND 1 - (n.embedding <=> query_embedding) > match_threshold
    ORDER BY n.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Create function for graph traversal
DROP FUNCTION IF EXISTS traverse_graph(uuid, text[], int, text);
CREATE FUNCTION traverse_graph(
    start_node_id uuid,
    edge_labels text[] DEFAULT NULL,
    max_depth int DEFAULT 3,
    direction text DEFAULT 'both'  -- 'outgoing', 'incoming', or 'both'
)
RETURNS TABLE (
    node_id uuid,
    node_label varchar,
    depth int,
    path uuid[],
    edge_labels_path text[],
    edge_weights_path float[]
) AS $$
WITH RECURSIVE graph_traversal AS (
    -- Base case: starting node
    SELECT
        n.id as node_id,
        n.label as node_label,
        0 as depth,
        ARRAY[n.id] as path,
        ARRAY[]::text[] as edge_labels_path,
        ARRAY[]::float[] as edge_weights_path
    FROM node n
    WHERE n.id = start_node_id

    UNION

    -- Recursive case: traverse edges
    SELECT
        CASE
            WHEN direction IN ('outgoing', 'both') THEN e.target_id
            WHEN direction = 'incoming' THEN e.source_id
        END as node_id,
        n.label as node_label,
        gt.depth + 1 as depth,
        gt.path || CASE
            WHEN direction IN ('outgoing', 'both') THEN e.target_id
            WHEN direction = 'incoming' THEN e.source_id
        END as path,
        gt.edge_labels_path || e.label as edge_labels_path,
        gt.edge_weights_path || e.weight as edge_weights_path
    FROM graph_traversal gt
    JOIN edge e ON (
        (direction IN ('outgoing', 'both') AND e.source_id = gt.node_id) OR
        (direction = 'incoming' AND e.target_id = gt.node_id)
    )
    JOIN node n ON n.id = CASE
        WHEN direction IN ('outgoing', 'both') THEN e.target_id
        WHEN direction = 'incoming' THEN e.source_id
    END
    WHERE
        gt.depth < max_depth
        AND (edge_labels IS NULL OR e.label = ANY(edge_labels))
        AND NOT (CASE
            WHEN direction IN ('outgoing', 'both') THEN e.target_id
            WHEN direction = 'incoming' THEN e.source_id
        END = ANY(gt.path))  -- Prevent cycles
)
SELECT * FROM graph_traversal;
$$ LANGUAGE sql;

-- Create function for hybrid search (semantic + full-text)
DROP FUNCTION IF EXISTS hybrid_search(text, vector(1536), float, int);
CREATE FUNCTION hybrid_search(
    query_text text,
    query_embedding vector(1536) DEFAULT NULL,
    semantic_weight float DEFAULT 0.5,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    label varchar,
    text_content text,
    summary text,
    score float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        n.id,
        n.label,
        n.text_content,
        n.summary,
        (
            CASE WHEN query_embedding IS NOT NULL THEN
                semantic_weight * (1 - (n.embedding <=> query_embedding))
            ELSE 0 END
            +
            (1 - semantic_weight) * ts_rank(to_tsvector('english', n.text_content), plainto_tsquery('english', query_text))
        ) as score
    FROM node n
    WHERE
        (query_embedding IS NULL OR n.embedding IS NOT NULL)
        AND (
            to_tsvector('english', n.text_content) @@ plainto_tsquery('english', query_text)
            OR (query_embedding IS NOT NULL AND 1 - (n.embedding <=> query_embedding) > 0.5)
        )
    ORDER BY score DESC
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Create function for edge semantic search
DROP FUNCTION IF EXISTS search_edges_by_embedding(vector(1536), float, int, varchar);
CREATE FUNCTION search_edges_by_embedding(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    filter_label varchar DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    source_id uuid,
    target_id uuid,
    label varchar,
    context text,
    weight float,
    similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.source_id,
        e.target_id,
        e.label,
        e.context,
        e.weight,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM edge e
    WHERE
        (filter_label IS NULL OR e.label = filter_label)
        AND e.embedding IS NOT NULL
        AND 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Add helpful comments
COMMENT ON TABLE node IS 'Knowledge graph nodes with RAG capabilities (embeddings, full-text, metadata)';
COMMENT ON TABLE edge IS 'Knowledge graph edges with weighted relationships and context';
COMMENT ON COLUMN node.embedding IS 'Vector embedding for semantic search (1536 dimensions for OpenAI ada-002)';
COMMENT ON COLUMN node.text_content IS 'Full text content for retrieval and full-text search';
COMMENT ON COLUMN node.summary IS 'Concise summary for quick context in RAG prompts';
COMMENT ON COLUMN node.metadata IS 'Flexible metadata (source, version, confidence, etc.)';
COMMENT ON COLUMN edge.weight IS 'Edge importance/strength for weighted graph traversal';
COMMENT ON COLUMN edge.context IS 'Contextual information about the relationship';
COMMENT ON COLUMN edge.embedding IS 'Vector embedding for edge semantic search (optional)';
COMMENT ON FUNCTION search_nodes_by_embedding IS 'Semantic search using vector embeddings';
COMMENT ON FUNCTION traverse_graph IS 'Graph traversal with configurable depth and direction';
COMMENT ON FUNCTION hybrid_search IS 'Hybrid search combining semantic and full-text search';
COMMENT ON FUNCTION search_edges_by_embedding IS 'Semantic search over edges using vector embeddings';
