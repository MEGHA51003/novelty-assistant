from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class BriefBase(BaseModel):
    title: str
    description: Optional[str] = None
    goals: Optional[str] = None
    reference_links: List[str] = []
    tags: List[str] = []


class ProjectCreate(BriefBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    goals: Optional[str] = None
    reference_links: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class BriefUpdate(BaseModel):
    title: Optional[str] = None
    brief_description: Optional[str] = None
    brief_goals: Optional[str] = None
    brief_reference_links: Optional[List[str]] = None
    brief_tags: Optional[List[str]] = None


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    goals: Optional[str] = None
    reference_links: List[str] = []
    tags: List[str] = []
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectBriefResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    goals: Optional[str] = None
    reference_links: List[str] = []
    tags: List[str] = []

    class Config:
        from_attributes = True
