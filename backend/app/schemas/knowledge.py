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
