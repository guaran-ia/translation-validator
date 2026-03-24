"""
Schemas for Annotation (question-answer pair translation) data validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AnnotationBase(BaseModel):
    """Base schema for annotation data."""
    question_es: Optional[str] = None
    answer_es: Optional[str] = None
    answer_number: Optional[int] = None
    equation_solution: Optional[str] = None
    source: str = "GuaranIA"


class AnnotationCreate(AnnotationBase):
    """Schema for creating a new annotation."""
    question_gn: Optional[str] = None
    answer_gn: Optional[str] = None


class AnnotationUpdate(BaseModel):
    """Schema for updating annotation translations."""
    question_gn: Optional[str] = None
    answer_gn: Optional[str] = None


class AnnotationResponse(AnnotationBase):
    """Schema for annotation response."""
    id: int
    question_gn: Optional[str] = None
    answer_gn: Optional[str] = None
    assigned_to_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AnnotationWithStats(AnnotationResponse):
    """Schema for annotation with statistics."""
    validation_count: int = 0
    suggestion_count: int = 0
    user_has_validated: bool = False
    user_has_suggested: bool = False


class AnnotationValidationCreate(BaseModel):
    """Schema for creating annotation validation feedback."""
    part_type: str = "both"  # "question", "answer", or "both"
    correctness: str
    fluency_score: int  # 1-5
    accuracy_score: int  # 1-5
    notes: Optional[str] = None
    category: Optional[str] = None


class AnnotationSuggestionCreate(BaseModel):
    """Schema for creating annotation suggestion."""
    part_type: str = "both"  # "question", "answer", or "both"
    suggested_question_gn: Optional[str] = None
    suggested_answer_gn: Optional[str] = None
    reason: Optional[str] = None


class AnnotationAssignCreate(BaseModel):
    """Schema for assigning annotation to a user."""
    assigned_to_user_id: Optional[int] = None
