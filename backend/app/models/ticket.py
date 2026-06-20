"""工单系统模型"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.mysql import VARCHAR
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    session_id = Column(VARCHAR(36), ForeignKey("session.id"))
    creator_type = Column(VARCHAR(20), default="user")  # user, agent
    type = Column(VARCHAR(50), default="consultation")  # consultation, complaint, refund, tech_support, other
    priority = Column(VARCHAR(20), default="normal")  # low, normal, high, urgent
    status = Column(VARCHAR(20), default="pending")  # pending, processing, pending_confirm, resolved, closed
    assigned_to = Column(VARCHAR(36))  # agent_id
    sla_deadline = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class TicketComment(Base):
    __tablename__ = "ticket_comment"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    ticket_id = Column(VARCHAR(36), ForeignKey("ticket.id"), nullable=False)
    sender_type = Column(VARCHAR(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
