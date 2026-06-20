"""统计与分析模型"""

from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class AgentEfficiencyLog(Base):
    __tablename__ = "agent_efficiency_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    agent_type = Column(String(20), default="ai")  # ai, agent
    agent_id = Column(String(36))
    first_response_time = Column(Float)  # seconds
    avg_response_time = Column(Float)  # seconds
    session_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class RatingRecord(Base):
    __tablename__ = "rating_record"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    agent_type = Column(String(20), default="ai")
    agent_id = Column(String(36))
    score = Column(Integer, nullable=False)  # 1-5
    session_id = Column(String(36), ForeignKey("session.id"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class EventLog(Base):
    __tablename__ = "event_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    user_id = Column(String(36))
    event_type = Column(String(50), nullable=False)
    event_data = Column(String(2000))
    ip = Column(String(45))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
