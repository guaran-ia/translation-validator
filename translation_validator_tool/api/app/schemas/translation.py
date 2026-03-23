from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TranslationBase(BaseModel):
    guarani_text: Optional[str] = None  # Allow null for sentences without guarani translation
    spanish_text: Optional[str] = None  # Allow null for sentences without translation
    source: str = "jojajovai"


class TranslationCreate(TranslationBase):
    direction: str = "sp-gn"
    is_original: bool = True


class TranslationAdminCreate(BaseModel):
    """Schema for admin to create translations (spanish is primary, guarani is optional)"""
    spanish_text: str  # Spanish text is now required/primary
    guarani_text: Optional[str] = None  # Optional guarani translation
    source: str = "GuaranIA"
    direction: str = "sp-gn"  # Default: Spanish to Guarani (spanish is original)
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