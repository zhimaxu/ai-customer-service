"""客服工作台相关 Schema"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionListItem(BaseModel):
    id: str
    user_id: str
    status: str
    current_agent_type: str
    updated_at: datetime

    class Config:
        from_attributes = True


class ReplyRequest(BaseModel):
    message: str
