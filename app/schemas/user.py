from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
