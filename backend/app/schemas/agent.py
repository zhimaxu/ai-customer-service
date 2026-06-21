"""客服工作台相关 Schema"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SessionListItem(BaseModel):
    id: str
    user_id: str
    status: str
    current_agent_type: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionDetailItem(BaseModel):
    id: str
    user_id: str
    channel: str
    status: str
    current_agent_type: str
    last_message_at: Optional[datetime]
    message_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReplyRequest(BaseModel):
    message: str


class QuickReplyRequest(BaseModel):
    message: str
    agent_id: Optional[str] = None


class TakeoverRequest(BaseModel):
    agent_id: Optional[str] = None
