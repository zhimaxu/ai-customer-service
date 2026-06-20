"""工单系统模型"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    session_id = Column(String(36), ForeignKey("session.id"))
    creator_type = Column(String(20), default="user")  # user, agent
    type = Column(String(50), default="consultation")  # consultation, complaint, refund, tech_support, other
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    status = Column(String(20), default="pending")  # pending, processing, pending_confirm, resolved, closed
    assigned_to = Column(String(36))  # agent_id
    sla_deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class TicketComment(Base):
    __tablename__ = "ticket_comment"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("ticket.id"), nullable=False)
    sender_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
