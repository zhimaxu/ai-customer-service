"""会话与消息模型"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.mysql import VARCHAR
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class Session(Base):
    __tablename__ = "session"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    user_id = Column(VARCHAR(36), nullable=False)
    channel = Column(VARCHAR(20), default="web")  # web, miniapp, app
    status = Column(VARCHAR(20), default="active")  # active, human, closed
    current_agent_type = Column(VARCHAR(20), default="ai")  # ai, agent
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Message(Base):
    __tablename__ = "message"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    session_id = Column(VARCHAR(36), ForeignKey("session.id"), nullable=False)
    sender_type = Column(VARCHAR(20), nullable=False)  # user, assistant, agent
    content = Column(Text, nullable=False)
    content_type = Column(VARCHAR(20), default="text")  # text, image, video, audio
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Satisfaction(Base):
    __tablename__ = "satisfaction"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    session_id = Column(VARCHAR(36), ForeignKey("session.id"), nullable=False)
    score = Column(Integer, default=5)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
