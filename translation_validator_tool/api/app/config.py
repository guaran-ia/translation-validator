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
    CORS_ORIGINS: str = '["http://localhost:5173"]'
    
    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)
    
    class Config:
        # Ensure .env is loaded from the api folder even if cwd is different (e.g. when running Alembic)
        env_file = str(Path(__file__).resolve().parent.parent.joinpath('.env'))


settings = Settings()