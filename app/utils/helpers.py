from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
from app.config import settings
from app.database import get_supabase
from supabase import Client
security = HTTPBearer()
def get_demo_user() -> dict:
    supabase = get_supabase()
    
    result = supabase.table("users").select("*").eq("email", "demo@example.com").execute()
    
    if result.data:
        return result.data[0]
    
    new_user = {
        "email": "demo@example.com",
        "name": "Demo User",
        "hashed_password": "demo"
    }
    
    insert_result = supabase.table("users").insert(new_user).execute()
    
    if insert_result.data:
        return insert_result.data[0]
    
    return {
        "id": "fallback-id",
        "email": "demo@example.com",
        "name": "Demo User"
    }
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> dict:
    if credentials is None:
        return get_demo_user()
    
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        return get_demo_user()
    supabase: Client = get_supabase()
    user_id = payload.get("sub")
    if not user_id:
        return get_demo_user()
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not response.data:
        return get_demo_user()
    return response.data[0]
async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None