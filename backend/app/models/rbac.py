"""RBAC 权限模型"""

from sqlalchemy import Column, String, Integer, DateTime, Table, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class Role(Base):
    __tablename__ = "role"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    name = Column(VARCHAR(50), nullable=False)
    code = Column(VARCHAR(50), unique=True, nullable=False)
    description = Column(VARCHAR(255))
    status = Column(VARCHAR(20), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Permission(Base):
    __tablename__ = "permission"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    name = Column(VARCHAR(50), nullable=False)
    code = Column(VARCHAR(100), unique=True, nullable=False)
    resource = Column(VARCHAR(50))
    action = Column(VARCHAR(50))
    description = Column(VARCHAR(255))


role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", VARCHAR(36), ForeignKey("role.id"), primary_key=True),
    Column("permission_id", VARCHAR(36), ForeignKey("permission.id"), primary_key=True),
)


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    user_id = Column(VARCHAR(36), nullable=False)
    role_id = Column(VARCHAR(36), nullable=False)


class Menu(Base):
    __tablename__ = "menu"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    parent_id = Column(VARCHAR(36))
    name = Column(VARCHAR(50), nullable=False)
    path = Column(VARCHAR(100))
    component = Column(VARCHAR(100))
    icon = Column(VARCHAR(50))
    sort_order = Column(Integer, default=0)
    visible = Column(Integer, default=1)  # 1=visible, 0=hidden
    type = Column(Integer, default=1)  # 1=menu, 2=button
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
