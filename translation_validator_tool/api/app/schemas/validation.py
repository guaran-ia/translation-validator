from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class CorrectnessEnum(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    GN_MORE = "gn_more"  # Guarani has more information
    ES_MORE = "es_more"  # Spanish has more information


class ValidationBase(BaseModel):
    correctness: CorrectnessEnum
    fluency_score: int = Field(ge=1, le=5, description="Fluency score from 1 to 5")
    accuracy_score: int = Field(ge=1, le=5, description="Accuracy score from 1 to 5")
    notes: Optional[str] = None


class ValidationCreate(ValidationBase):
    translation_id: int


class ValidationUpdate(BaseModel):
    correctness: Optional[CorrectnessEnum] = None
    fluency_score: Optional[int] = Field(None, ge=1, le=5)
    accuracy_score: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class ValidationResponse(ValidationBase):
    id: int
    translation_id: int
    user_id: int
    direction: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)