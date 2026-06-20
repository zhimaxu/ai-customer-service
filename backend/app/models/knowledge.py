"""知识库模型"""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.mysql import VARCHAR
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entry"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    title = Column(VARCHAR(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(VARCHAR(50), default="default")
    tags = Column(VARCHAR(500))  # comma-separated
    vector_id = Column(VARCHAR(100))  # Qdrant point ID
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class FileConversion(Base):
    __tablename__ = "file_conversion"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    original_file = Column(VARCHAR(500))  # file path or URL
    converted_md = Column(Text)
    status = Column(VARCHAR(20), default="pending")  # pending, processing, completed, failed
    created_by = Column(VARCHAR(36))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
