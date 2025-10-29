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
    # Number of validations this suggestion has received (separate from translation validations)
    validation_count: int = 0
    # Whether the current user has validated this suggestion (when returned in a user context)
    user_has_validated: Optional[bool] = False
    direction: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)