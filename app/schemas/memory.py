from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class MemoryType(BaseModel):
    type: Literal["context", "decisions", "todos", "facts", "concepts"]


class MemoryCreate(BaseModel):
    memory_type: Literal["context", "decisions", "todos", "facts", "concepts"]
    title: str
    content: Dict[str, Any]


class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    memory_type: Optional[Literal["context", "decisions", "todos", "facts", "concepts"]] = None


class MemoryResponse(BaseModel):
    id: str
    project_id: str
    memory_type: str
    title: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
