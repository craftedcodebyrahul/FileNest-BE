from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="config.env")

 

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 1
    DATABASE_URL = os.getenv("DATABASE_URL")

@lru_cache()
def get_settings():
    return Settings()