from typing import Optional
from supabase import create_client, Client
from app.config import settings

supabase: Optional[Client] = None


def get_supabase() -> Client:
    global supabase
    if supabase is None:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
        )
    return supabase


def init_supabase():
    return get_supabase()
