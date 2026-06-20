"""系统与配置模型"""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.mysql import VARCHAR
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    key = Column(VARCHAR(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(VARCHAR(255))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Translation(Base):
    __tablename__ = "translation"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    language = Column(VARCHAR(20), nullable=False)
    key = Column(VARCHAR(200), nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
