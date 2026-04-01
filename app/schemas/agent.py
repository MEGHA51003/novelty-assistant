from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class AgentExecutionCreate(BaseModel):
    agent_type: str
    input_data: Dict[str, Any] = {}


class AgentExecutionResponse(BaseModel):
    id: str
    project_id: str
    agent_type: str
    status: Literal["pending", "running", "completed", "failed"]
    input_data: Dict[str, Any] = {}
    output_data: Dict[str, Any] = {}
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
