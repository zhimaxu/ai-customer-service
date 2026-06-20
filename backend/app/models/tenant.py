"""租户与用户模型"""

from sqlalchemy import Column, String, Integer, DateTime, Enum as SAEnum
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class Tenant(Base):
    __tablename__ = "tenant"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    industry = Column(String(50))
    contact_email = Column(String(100))
    phone = Column(String(20))
    status = Column(String(20), default="active")  # active, suspended
    plan = Column(String(20), default="free")  # free, standard, professional, enterprise
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class User(Base):
    __tablename__ = "user"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(255))
    gender = Column(Integer)  # 0=unknown, 1=male, 2=female
    birthday = Column(DateTime)
    region = Column(String(50))
    membership_level = Column(String(20), default="regular")  # regular, silver, gold, diamond
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class AdminUser(Base):
    __tablename__ = "admin_user"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100))
    avatar = Column(String(255))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
