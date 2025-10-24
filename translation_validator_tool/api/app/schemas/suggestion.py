from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SuggestionBase(BaseModel):
    suggested_guarani: Optional[str] = None
    suggested_spanish: Optional[str] = None
    reason: Optional[str] = None


class SuggestionCreate(SuggestionBase):
    translation_id: int


class SuggestionResponse(SuggestionBase):
    id: int
    translation_id: int
    user_id: int
    direction: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)