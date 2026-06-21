"""知识库相关 Schema"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class KnowledgeEntryCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = "default"
    tags: Optional[list[str]] = []


class KnowledgeEntryResponse(BaseModel):
    id: str
    title: str
    category: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeDetailResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    category: str
    tags: Optional[str]
    vector_id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class KnowledgeUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
