import json
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    PROJECT_NAME: str = "Translation Validator"
    VERSION: str = "1.0.0"
    #CORS_ORIGINS: str = '["http://localhost:5173","http://192.168.20.242:5173"]'
    CORS_ORIGINS: str = '["http://localhost:5173", "https://dylan-drill-organised-missed.trycloudflare.com"]'
    # Prodigy configuration
    PRODIGY_HOST: str = "localhost"
    PRODIGY_PORT: int = 8082
    # Optional SMTP settings for admin notifications on new registrations
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    SMTP_USE_TLS: bool = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)
    
    class Config:
        # Ensure .env is loaded from the api folder even if cwd is different (e.g. when running Alembic)
        env_file = str(Path(__file__).resolve().parent.parent.joinpath('.env'))


settings = Settings()