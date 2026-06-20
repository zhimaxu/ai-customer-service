"""RBAC 权限模型"""

from sqlalchemy import Column, String, Integer, DateTime, Table, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class Role(Base):
    __tablename__ = "role"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    name = Column(String(50), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class Permission(Base):
    __tablename__ = "permission"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    resource = Column(String(50))
    action = Column(String(50))
    description = Column(String(255))


role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("role.id"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permission.id"), primary_key=True),
)


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    role_id = Column(String(36), nullable=False)


class Menu(Base):
    __tablename__ = "menu"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    parent_id = Column(String(36))
    name = Column(String(50), nullable=False)
    path = Column(String(100))
    component = Column(String(100))
    icon = Column(String(50))
    sort_order = Column(Integer, default=0)
    visible = Column(Integer, default=1)  # 1=visible, 0=hidden
    type = Column(Integer, default=1)  # 1=menu, 2=button
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
