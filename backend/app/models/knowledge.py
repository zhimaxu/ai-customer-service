"""知识库模型"""

from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entry"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), default="default")
    tags = Column(String(500))  # comma-separated
    vector_id = Column(String(100))  # Qdrant point ID
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class FileConversion(Base):
    __tablename__ = "file_conversion"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    original_file = Column(String(500))  # file path or URL
    converted_md = Column(Text)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_by = Column(String(36))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
