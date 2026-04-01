from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    ANTHROPIC_API_KEY: str = ""
    
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    GEMINI_API_KEY: str = ""
    
    REPLICATE_API_TOKEN: str = ""
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    AI_PROVIDER: str = "ollama"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
