"""
Endpoints del flujo de validación.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.database import get_db
from app.models.annotation import Annotation
from app.models.annotation_translation import AnnotationTranslation
from app.models.annotation_validation import AnnotationValidation
from app.models.user import User
from app.schemas.validator import ValidatorPendingTranslationsResponse


router = APIRouter()


@router.get("/random-translations", response_model=ValidatorPendingTranslationsResponse)
async def get_random_translations_for_validation(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Obtiene traducciones ya realizadas para precargar el flujo de validación.
    """
    rows = (
        db.query(AnnotationTranslation, Annotation, User)
        .join(Annotation, Annotation.id == AnnotationTranslation.annotation_id)
        .join(User, User.id == AnnotationTranslation.user_id)
        .order_by(func.random())
        .limit(limit)
        .all()
    )

    items = []

    for translation, annotation, translator in rows:
        validation_count = db.query(func.count(AnnotationValidation.id)).filter(
            AnnotationValidation.annotation_id == annotation.id,
            AnnotationValidation.suggestion_id == None,
        ).scalar() or 0

        user_has_validated = db.query(AnnotationValidation.id).filter(
            and_(
                AnnotationValidation.annotation_id == annotation.id,
                AnnotationValidation.user_id == current_user.id,
                AnnotationValidation.suggestion_id == None,
            )
        ).first() is not None

        items.append({
            "translation": {
                "id": translation.id,
                "annotation_id": translation.annotation_id,
                "user_id": translation.user_id,
                "question_gn": translation.question_gn,
                "answer_gn": translation.answer_gn,
                "created_at": translation.created_at,
            },
            "annotation": {
                "id": annotation.id,
                "question_es": annotation.question_es,
                "answer_es": annotation.answer_es,
                "answer_number": annotation.answer_number,
                "equation_solution": annotation.equation_solution,
                "source": annotation.source,
                "md5": annotation.md5,
                "translated": annotation.translated,
                "created_at": annotation.created_at,
                "updated_at": annotation.updated_at,
            },
            "translator": {
                "user_id": translator.id,
                "username": translator.username,
                "nombre_completo": translator.nombre_completo,
                "email": translator.email,
            },
            "validation_count": validation_count,
            "user_has_validated": user_has_validated,
        })

    return {
        "items": items,
        "total": len(items),
    }
