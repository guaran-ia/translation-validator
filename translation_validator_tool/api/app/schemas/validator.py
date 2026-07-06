"""
Schemas para endpoints del flujo de validación.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ValidatorAnnotationInfo(BaseModel):
    id: int
    question_es: Optional[str] = None
    answer_es: Optional[str] = None
    answer_number: Optional[int] = None
    equation_solution: Optional[str] = None
    source: Optional[str] = None
    md5: Optional[str] = None
    translated: bool
    validated: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ValidatorTranslatorInfo(BaseModel):
    user_id: int
    username: str
    nombre_completo: str
    email: str


class ValidatorTranslationInfo(BaseModel):
    id: int
    annotation_id: int
    user_id: int
    question_gn: Optional[str] = None
    answer_gn: Optional[str] = None
    validated: bool = False
    created_at: Optional[datetime] = None


class ValidatorPendingTranslation(BaseModel):
    validation_id: int
    translation: ValidatorTranslationInfo
    annotation: ValidatorAnnotationInfo
    translator: ValidatorTranslatorInfo
    validation_count: int
    user_has_validated: bool


class ValidatorPendingTranslationsResponse(BaseModel):
    items: list[ValidatorPendingTranslation]
    total: int
    message: Optional[str] = None
    replaced_due_to_limit: bool = False


class ValidatorValidationSubmit(BaseModel):
    correctness: str
    fluency_score: int
    accuracy_score: int
    notes: Optional[str] = None
    category: Optional[str] = None
    suggestion_id: Optional[int] = None
