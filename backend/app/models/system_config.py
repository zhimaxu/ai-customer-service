"""系统与配置模型"""

from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(255))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class Translation(Base):
    __tablename__ = "translation"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    language = Column(String(20), nullable=False)
    key = Column(String(200), nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
