from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ImageGenerateRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None


class ImageResponse(BaseModel):
    id: str
    project_id: str
    conversation_id: Optional[str]
    prompt: Optional[str]
    image_url: str
    storage_type: str
    analysis_result: Optional[str]
    analyzed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ImageAnalyzeRequest(BaseModel):
    question: Optional[str] = None
