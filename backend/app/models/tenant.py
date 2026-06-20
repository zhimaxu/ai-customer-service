"""租户与用户模型"""

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.mysql import VARCHAR
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class Tenant(Base):
    __tablename__ = "tenant"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    name = Column(VARCHAR(100), nullable=False)
    industry = Column(VARCHAR(50))
    contact_email = Column(VARCHAR(100))
    phone = Column(VARCHAR(20))
    status = Column(VARCHAR(20), default="active")  # active, suspended
    plan = Column(VARCHAR(20), default="free")  # free, standard, professional, enterprise
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class User(Base):
    __tablename__ = "user"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    nickname = Column(VARCHAR(50))
    avatar = Column(VARCHAR(255))
    gender = Column(Integer)  # 0=unknown, 1=male, 2=female
    birthday = Column(DateTime)
    region = Column(VARCHAR(50))
    membership_level = Column(VARCHAR(20), default="regular")  # regular, silver, gold, diamond
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class AdminUser(Base):
    __tablename__ = "admin_user"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    username = Column(VARCHAR(50), unique=True, nullable=False)
    password_hash = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(100))
    avatar = Column(VARCHAR(255))
    status = Column(VARCHAR(20), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
