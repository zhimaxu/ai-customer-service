"""会话与消息模型"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class Session(Base):
    __tablename__ = "session"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)
    channel = Column(String(20), default="web")  # web, miniapp, app
    status = Column(String(20), default="active")  # active, human, closed
    current_agent_type = Column(String(20), default="ai")  # ai, agent
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class Message(Base):
    __tablename__ = "message"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("session.id"), nullable=False)
    sender_type = Column(String(20), nullable=False)  # user, assistant, agent
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text")  # text, image, video, audio
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class Satisfaction(Base):
    __tablename__ = "satisfaction"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("session.id"), nullable=False)
    score = Column(Integer, default=5)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
