import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# .env is at backend/.env — resolve relative to this file
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "VAIDYNEX Clinical Intelligence Gateway"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SUPABASE_URL: str = "https://smydwqouangckxqzskwm.supabase.co"
    SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNteWR3cW91YW5nY2t4cXpza3dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgyNTg3ODksImV4cCI6MjEwMzgzNDc4OX0.4hV98Wk-CCr-bsOPG0bz--HxbDDN3NPVSXHakngPtrw"
    SARVAM_API_KEY: Optional[str] = "sk_6cogtu4i_AUqyZ8eTmEBU4YvKyO6gYtCi"

    RED_FLAG_TIMEOUT_MS: int = 150
    DEFAULT_HOSPITAL_NAME: str = "All India Institute of Ayurveda (AIIA)"
    DEFAULT_HOSPITAL_ID: str = "IN0110000142"

    class Config:
        env_file = str(_ENV_FILE)
        extra = "ignore"

settings = Settings()
