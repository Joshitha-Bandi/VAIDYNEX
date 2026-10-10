import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# .env is at backend/.env — resolve relative to this file
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "MediKiosk Clinical Intelligence Gateway"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SUPABASE_URL: str = "https://smydwqouangckxqzskwm.supabase.co"
    SUPABASE_KEY: str = ""
    SARVAM_API_KEY: Optional[str] = ""

    RED_FLAG_TIMEOUT_MS: int = 150
    DEFAULT_HOSPITAL_NAME: str = "All India Institute of Ayurveda (AIIA)"
    DEFAULT_HOSPITAL_ID: str = "IN0110000142"

    class Config:
        env_file = str(_ENV_FILE)
        extra = "ignore"

settings = Settings()
