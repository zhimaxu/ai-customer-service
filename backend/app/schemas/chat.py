"""聊天相关 Schema"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    tenant_id: Optional[str] = "default"
    user_id: Optional[str] = "anonymous"
    message: str
    channel: Optional[str] = "web"


class ChatResponse(BaseModel):
    session_id: str
    reply: str


class MessageCreate(BaseModel):
    session_id: str
    content: str
    sender_type: str = "user"


class SessionCreate(BaseModel):
    tenant_id: str
    user_id: str
    channel: Optional[str] = "web"
