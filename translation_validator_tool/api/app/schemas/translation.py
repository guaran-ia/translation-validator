from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TranslationBase(BaseModel):
    guarani_text: str
    spanish_text: Optional[str] = None  # Allow null for sentences without translation
    source: str = "jojajovai"


class TranslationCreate(TranslationBase):
    direction: str = "sp-gn"
    is_original: bool = True


class TranslationAdminCreate(BaseModel):
    """Schema for admin to create translations (allows sentences without spanish translation)"""
    guarani_text: str
    spanish_text: Optional[str] = None  # Optional for sentences without translation
    source: str = "admin"
    direction: str = "gn-sp"  # Default for guarani sentences
    is_original: bool = True


class TranslationResponse(TranslationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    direction: str = "sp-gn"
    pair_id: Optional[int] = None
    is_original: bool = True
    model_config = ConfigDict(from_attributes=True)


class TranslationWithStats(TranslationResponse):
    validation_count: int = 0
    user_has_validated: bool = False
    # Suggestion-related info
    suggestion_count: int = 0
    user_has_suggested: bool = False
    # Pair info: how many validations the paired translation has in its own direction
    pair_same_direction_count: int = 0
    pair_is_complete: bool = False