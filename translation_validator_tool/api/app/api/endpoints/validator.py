"""
Endpoints del flujo de validación.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.database import get_db
from app.models.annotation import Annotation
from app.models.annotation_suggestion import AnnotationSuggestion
from app.models.annotation_translation import AnnotationTranslation
from app.models.annotation_validation import AnnotationValidation
from app.models.user import User
from app.schemas.validator import ValidatorPendingTranslationsResponse, ValidatorValidationSubmit


router = APIRouter()

VALIDATOR_PART_TYPE = "both"
VALIDATIONS_REQUIRED = 3


def _translation_validation_count(db: Session, translation_id: int) -> int:
    return db.query(func.count(AnnotationValidation.id)).filter(
        AnnotationValidation.translation_id == translation_id,
        AnnotationValidation.status == "completed",
    ).scalar() or 0


def _close_translation_if_complete(db: Session, translation: AnnotationTranslation) -> int:
    validation_count = _translation_validation_count(db, translation.id)

    if validation_count >= VALIDATIONS_REQUIRED:
        translation.validated = True
        db.query(AnnotationValidation).filter(
            AnnotationValidation.translation_id == translation.id,
            AnnotationValidation.part_type == VALIDATOR_PART_TYPE,
            AnnotationValidation.status == "pending",
        ).delete(synchronize_session=False)

    return validation_count


def _mark_translations_with_required_validations(db: Session) -> None:
    rows = db.query(AnnotationValidation.translation_id).filter(
        AnnotationValidation.part_type == VALIDATOR_PART_TYPE,
        AnnotationValidation.status == "completed",
    ).group_by(AnnotationValidation.translation_id).having(
        func.count(AnnotationValidation.id) >= VALIDATIONS_REQUIRED
    ).all()

    translation_ids = [row[0] for row in rows]
    if not translation_ids:
        return

    db.query(AnnotationTranslation).filter(
        AnnotationTranslation.id.in_(translation_ids),
        AnnotationTranslation.validated == False,
    ).update({AnnotationTranslation.validated: True}, synchronize_session=False)
    db.query(AnnotationValidation).filter(
        AnnotationValidation.translation_id.in_(translation_ids),
        AnnotationValidation.part_type == VALIDATOR_PART_TYPE,
        AnnotationValidation.status == "pending",
    ).delete(synchronize_session=False)


def _remove_pending_if_translation_closed(db: Session, validation: AnnotationValidation) -> bool:
    translation = validation.translation
    if not translation:
        db.delete(validation)
        return True

    validation_count = _translation_validation_count(db, translation.id)
    if translation.validated or validation_count >= VALIDATIONS_REQUIRED:
        if validation_count >= VALIDATIONS_REQUIRED:
            translation.validated = True
        db.delete(validation)
        return True

    return False


def _build_validator_item(db: Session, validation: AnnotationValidation) -> dict:
    translation = validation.translation
    annotation = validation.annotation
    translator = translation.user

    validation_count = _translation_validation_count(db, translation.id)

    return {
        "validation_id": validation.id,
        "translation": {
            "id": translation.id,
            "annotation_id": translation.annotation_id,
            "user_id": translation.user_id,
            "question_gn": translation.question_gn,
            "answer_gn": translation.answer_gn,
            "validated": translation.validated,
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
            "validated": annotation.validated,
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
        "user_has_validated": validation.status == "completed",
    }


def _get_current_pending_validation(db: Session, user_id: int) -> AnnotationValidation | None:
    return db.query(AnnotationValidation).filter(
        AnnotationValidation.user_id == user_id,
        AnnotationValidation.part_type == VALIDATOR_PART_TYPE,
        AnnotationValidation.status == "pending",
    ).order_by(AnnotationValidation.created_at.asc()).first()


def _assign_random_translation(db: Session, user_id: int) -> AnnotationValidation | None:
    _mark_translations_with_required_validations(db)

    completed_translation_ids = db.query(AnnotationValidation.translation_id).filter(
        AnnotationValidation.user_id == user_id,
        AnnotationValidation.part_type == VALIDATOR_PART_TYPE,
        AnnotationValidation.status == "completed",
    )

    user_pending_translation_ids = db.query(AnnotationValidation.translation_id).filter(
        AnnotationValidation.user_id == user_id,
        AnnotationValidation.part_type == VALIDATOR_PART_TYPE,
        AnnotationValidation.status == "pending",
    )

    completed_three_translation_ids = db.query(AnnotationValidation.translation_id).filter(
        AnnotationValidation.part_type == VALIDATOR_PART_TYPE,
        AnnotationValidation.status == "completed",
    ).group_by(AnnotationValidation.translation_id).having(
        func.count(AnnotationValidation.id) >= VALIDATIONS_REQUIRED
    )

    row = (
        db.query(AnnotationTranslation, Annotation, User)
        .join(Annotation, Annotation.id == AnnotationTranslation.annotation_id)
        .join(User, User.id == AnnotationTranslation.user_id)
        .filter(AnnotationTranslation.validated == False)
        .filter(~AnnotationTranslation.id.in_(completed_translation_ids))
        .filter(~AnnotationTranslation.id.in_(user_pending_translation_ids))
        .filter(~AnnotationTranslation.id.in_(completed_three_translation_ids))
        .order_by(func.random())
        .first()
    )

    if not row:
        db.commit()
        return None

    translation, annotation, _translator = row
    validation = AnnotationValidation(
        annotation_id=annotation.id,
        translation_id=translation.id,
        user_id=user_id,
        part_type=VALIDATOR_PART_TYPE,
        status="pending",
    )
    db.add(validation)
    db.commit()
    db.refresh(validation)
    return validation


def _get_or_assign_translation(db: Session, user_id: int) -> AnnotationValidation | None:
    pending_validation = _get_current_pending_validation(db, user_id)
    if pending_validation:
        removed = _remove_pending_if_translation_closed(db, pending_validation)
        if not removed:
            return pending_validation
        db.commit()

    return _assign_random_translation(db, user_id)


def _response_from_validation(
    db: Session,
    validation: AnnotationValidation | None,
    message: str | None = None,
    replaced_due_to_limit: bool = False,
) -> dict:
    if not validation:
        return {"items": [], "total": 0, "message": message, "replaced_due_to_limit": replaced_due_to_limit}

    return {
        "items": [_build_validator_item(db, validation)],
        "total": 1,
        "message": message,
        "replaced_due_to_limit": replaced_due_to_limit,
    }


@router.get("/random-translations", response_model=ValidatorPendingTranslationsResponse)
async def get_random_translations_for_validation(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Obtiene o crea la asignación pendiente del usuario para el flujo de validación.
    """
    validation = _get_or_assign_translation(db, current_user.id)
    return _response_from_validation(db, validation)


@router.post("/skip-current", response_model=ValidatorPendingTranslationsResponse)
async def skip_current_validation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Elimina la asignación pendiente actual y asigna otra traducción aleatoria.
    """
    pending_validations = db.query(AnnotationValidation).filter(
        AnnotationValidation.user_id == current_user.id,
        AnnotationValidation.part_type == VALIDATOR_PART_TYPE,
        AnnotationValidation.status == "pending",
    ).all()

    for validation in pending_validations:
        db.delete(validation)

    db.commit()
    validation = _assign_random_translation(db, current_user.id)
    return _response_from_validation(db, validation)


@router.post("/complete-current", response_model=ValidatorPendingTranslationsResponse)
async def complete_current_validation(
    validation_data: ValidatorValidationSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Completa la asignación pendiente actual y devuelve una nueva si existe.
    """
    if validation_data.fluency_score < 1 or validation_data.fluency_score > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fluency score must be between 1 and 5")
    if validation_data.accuracy_score < 1 or validation_data.accuracy_score > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accuracy score must be between 1 and 5")

    validation = _get_current_pending_validation(db, current_user.id)
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending validation assignment found",
        )

    translation = db.query(AnnotationTranslation).filter(
        AnnotationTranslation.id == validation.translation_id,
    ).with_for_update().first()

    if not translation:
        db.delete(validation)
        db.commit()
        next_validation = _assign_random_translation(db, current_user.id)
        return _response_from_validation(db, next_validation)

    validation_count = _translation_validation_count(db, translation.id)
    if translation.validated or validation_count >= VALIDATIONS_REQUIRED:
        if validation_count >= VALIDATIONS_REQUIRED:
            translation.validated = True
        db.delete(validation)
        db.commit()
        next_validation = _assign_random_translation(db, current_user.id)
        return _response_from_validation(
            db,
            next_validation,
            message="Lo sentimos, la traducción ya fue validada 3 veces. Te asignaremos una nueva.",
            replaced_due_to_limit=True,
        )

    suggestion_id = validation_data.suggestion_id
    if not suggestion_id:
        latest_suggestion = db.query(AnnotationSuggestion).filter(
            AnnotationSuggestion.annotation_id == validation.annotation_id,
            AnnotationSuggestion.translation_id == validation.translation_id,
            AnnotationSuggestion.user_id == current_user.id,
        ).order_by(AnnotationSuggestion.created_at.desc()).first()
        if latest_suggestion:
            suggestion_id = latest_suggestion.id

    if suggestion_id:
        suggestion = db.query(AnnotationSuggestion).filter(
            AnnotationSuggestion.id == suggestion_id,
            AnnotationSuggestion.annotation_id == validation.annotation_id,
            AnnotationSuggestion.translation_id == validation.translation_id,
            AnnotationSuggestion.user_id == current_user.id,
        ).first()
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Suggestion does not belong to the current validation assignment",
            )

    validation.correctness = validation_data.correctness
    validation.fluency_score = validation_data.fluency_score
    validation.accuracy_score = validation_data.accuracy_score
    validation.regular_reason = validation_data.regular_reason
    validation.notes = validation_data.notes
    validation.category = validation_data.category
    validation.suggestion_id = suggestion_id
    validation.status = "completed"

    db.flush()
    _close_translation_if_complete(db, translation)
    db.commit()
    next_validation = _assign_random_translation(db, current_user.id)
    return _response_from_validation(db, next_validation)
