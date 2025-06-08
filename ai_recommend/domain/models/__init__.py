import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Index, ForeignKey, Float, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
import uuid


class DataType(enum.Enum):
    STRING = "string"
    INT = "int"
    DOUBLE = "double"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    ARRAY = "array"


class Field:
    name: str
    data_type: DataType
    value: str

    def original_value(self):
        if self.data_type == DataType.STRING:
            return self.value
        elif self.data_type == DataType.INT:
            return int(self.value)
        elif self.data_type == DataType.DOUBLE:
            return float(self.value)
        elif self.data_type == DataType.BOOLEAN:
            return self.value.lower() in ("true", "1", "yes")
        elif self.data_type == DataType.DATETIME:
            from datetime import datetime

            return datetime.fromisoformat(self.value)
        elif self.data_type == DataType.DATE:
            from datetime import date

            return date.fromisoformat(self.value)
        elif self.data_type == DataType.ARRAY:
            return self.value.split(",")
        else:
            raise ValueError(f"Unsupported data type: {self.data_type}")


class Base(DeclarativeBase):
    pass


class Node(Base):
    """Knowledge Graph Node with RAG capabilities"""

    __tablename__ = "node"

    # Core fields
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    label: Mapped[str] = mapped_column(String(50), index=True)
    properties: Mapped[dict | None] = mapped_column(JSONB)
    tags: Mapped[dict | None] = mapped_column(JSONB)

    # RAG-specific fields
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))
    text_content: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column(JSONB)  # Renamed from metadata to avoid conflict

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_node_tags_gin", "tags", postgresql_using="gin"),
        Index("ix_node_metadata_gin", "meta", postgresql_using="gin"),
        Index(
            "ix_node_text_content_fts",
            func.to_tsvector("english", text_content),
            postgresql_using="gin",
        ),
        Index(
            "ix_node_embedding_cosine",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("ix_node_label_created", "label", "created_at"),
    )

    def __repr__(self) -> str:
        return f"Node(id={self.id!r}, label={self.label!r}, summary={self.summary[:50] if self.summary else None})"


class Edge(Base):
    """Knowledge Graph Edge with weighted relationships"""

    __tablename__ = "edge"

    # Core fields
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("node.id", ondelete="CASCADE"), index=True
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("node.id", ondelete="CASCADE"), index=True
    )
    label: Mapped[str] = mapped_column(String(50), index=True)
    properties: Mapped[dict | None] = mapped_column(JSONB)
    tags: Mapped[dict | None] = mapped_column(JSONB)

    # RAG-specific fields
    weight: Mapped[float] = mapped_column(Float, default=1.0, index=True)
    context: Mapped[Optional[str]] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column(JSONB)  # Renamed from metadata to avoid conflict

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_edge_tags_gin", "tags", postgresql_using="gin"),
        Index("ix_edge_metadata_gin", "meta", postgresql_using="gin"),
        Index("ix_edge_source_label", "source_id", "label"),
        Index("ix_edge_target_label", "target_id", "label"),
    )

    def __repr__(self) -> str:
        return f"Edge(id={self.id!r}, source_id={self.source_id!r}, target_id={self.target_id!r}, label={self.label!r}, weight={self.weight})"
