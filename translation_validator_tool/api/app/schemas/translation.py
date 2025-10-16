from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TranslationBase(BaseModel):
    guarani_text: str
    spanish_text: str
    source: str = "jojajovai"


class TranslationCreate(TranslationBase):
    pass


class TranslationResponse(TranslationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TranslationWithStats(TranslationResponse):
    validation_count: int = 0
    user_has_validated: bool = False
    # Suggestion-related info
    suggestion_count: int = 0
    user_has_suggested: bool = False