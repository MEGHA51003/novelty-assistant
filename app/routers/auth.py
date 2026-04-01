from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_supabase
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.utils.helpers import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, supabase: Client = Depends(get_supabase)):
    existing = supabase.table("users").select("id").eq("email", user_data.email).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user_data.password)

    user = {
        "email": user_data.email,
        "name": user_data.name,
        "hashed_password": hashed_password
    }

    result = supabase.table("users").insert(user).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    return result.data[0]


@router.post("/login")
async def login(login_data: UserLogin, supabase: Client = Depends(get_supabase)):
    result = supabase.table("users").select("*").eq("email", login_data.email).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user = result.data[0]

    if not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(data={"sub": user["id"]})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
