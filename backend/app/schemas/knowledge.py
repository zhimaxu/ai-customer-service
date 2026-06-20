"""知识库相关 Schema"""

from pydantic import BaseModel
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

    class Config:
        from_attributes = True
