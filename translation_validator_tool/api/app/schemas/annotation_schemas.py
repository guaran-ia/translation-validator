"""
Pydantic schemas for annotations with multi-user support
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== AnnotationTranslation Schemas ====================

class AnnotationTranslationBase(BaseModel):
    """Base schema for annotation translations"""
    question_gn: Optional[str] = Field(None, description="Guarani translation of question")
    answer_gn: Optional[str] = Field(None, description="Guarani translation of answer")


class AnnotationTranslationCreate(AnnotationTranslationBase):
    """Schema for creating an annotation translation"""
    annotation_id: int
    user_id: int


class AnnotationTranslationUpdate(AnnotationTranslationBase):
    """Schema for updating an annotation translation"""
    pass


class AnnotationTranslationResponse(AnnotationTranslationBase):
    """Schema for annotation translation response"""
    id: int
    annotation_id: int
    user_id: int
    validated: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== AnnotationAssignment Schemas ====================

class AnnotationAssignmentBase(BaseModel):
    """Base schema for annotation assignments"""
    annotation_id: int
    user_id: int


class AnnotationAssignmentCreate(AnnotationAssignmentBase):
    """Schema for creating an annotation assignment"""
    pass


class AnnotationAssignmentResponse(AnnotationAssignmentBase):
    """Schema for annotation assignment response"""
    id: int
    assigned_at: datetime

    class Config:
        from_attributes = True


# ==================== Annotation Schemas (Updated) ====================

class AnnotationCreate(BaseModel):
    """Schema for creating an annotation (without translations)"""
    question_es: Optional[str] = Field(None, description="Spanish question text")
    answer_es: Optional[str] = Field(None, description="Spanish answer text")
    answer_number: Optional[int] = None
    equation_solution: Optional[str] = None
    source: str = Field(..., description="Source of the annotation")


class AnnotationUpdate(BaseModel):
    """Schema for updating an annotation (without translations)"""
    question_es: Optional[str] = None
    answer_es: Optional[str] = None
    answer_number: Optional[int] = None
    equation_solution: Optional[str] = None
    source: Optional[str] = None
    translated: Optional[bool] = None
    validated: Optional[bool] = None


class AnnotationResponse(BaseModel):
    """Schema for annotation response WITH relationships"""
    id: int
    question_es: Optional[str]
    answer_es: Optional[str]
    answer_number: Optional[int]
    equation_solution: Optional[str]
    source: str
    translated: bool
    validated: bool
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    assignments: Optional[List[AnnotationAssignmentResponse]] = None
    translations: Optional[List[AnnotationTranslationResponse]] = None

    class Config:
        from_attributes = True


class AnnotationSimpleResponse(BaseModel):
    """Schema for annotation response WITHOUT relationships (lightweight)"""
    id: int
    question_es: Optional[str]
    answer_es: Optional[str]
    answer_number: Optional[int]
    equation_solution: Optional[str]
    source: str
    translated: bool
    validated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Combined Response Schemas ====================

class AnnotationWithTranslationsResponse(AnnotationResponse):
    """Annotation with all translations for a user"""
    pass


class AnnotationWithAssignmentsResponse(AnnotationResponse):
    """Annotation with all assignments"""
    pass


# ==================== Batch Operation Schemas ====================

class BulkAssignRequest(BaseModel):
    """Schema for bulk assigning annotations to users"""
    annotation_ids: List[int]
    user_ids: List[int]


class BulkAssignResponse(BaseModel):
    """Response for bulk assignment"""
    created_count: int
    skipped_count: int
    message: str


class TranslationBulkCreateRequest(BaseModel):
    """Schema for bulk creating translations"""
    translations: List[AnnotationTranslationCreate]


class TranslationBulkCreateResponse(BaseModel):
    """Response for bulk translation creation"""
    created_count: int
    skipped_count: int
    message: str
