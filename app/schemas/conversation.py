from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    project_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    messages: list = []
