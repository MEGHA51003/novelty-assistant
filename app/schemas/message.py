from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    role: str = "user"


class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    role: str
    metadata: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    image_url: Optional[str] = None


class ChatResponse(BaseModel):
    message: MessageResponse
    assistant_message: MessageResponse
