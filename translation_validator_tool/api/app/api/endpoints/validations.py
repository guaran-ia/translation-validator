from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.validation import Validation
from app.models.translation import Translation
from app.schemas.validation import ValidationCreate, ValidationUpdate, ValidationResponse
from app.api.deps import get_current_active_user
from app.models.suggestion import TranslationSuggestion

router = APIRouter()


@router.post("", response_model=ValidationResponse)
async def create_validation(
    validation_data: ValidationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new validation."""
    # Check if translation exists
    translation = db.query(Translation).filter(Translation.id == validation_data.translation_id).first()
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    # Validate category requirement for gn-sp direction
    if translation.direction == "gn-sp" and translation.is_original:
        if not validation_data.category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is required for Guarani original sentences (gn-sp direction)"
            )
        if validation_data.category not in ["guarani_puro", "jopara", "jehea"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category. Must be: guarani_puro, jopara, or jehea"
            )
    
    # Check if user already validated this translation
    existing_validation = db.query(Validation).filter(
        Validation.translation_id == validation_data.translation_id,
        Validation.user_id == current_user.id
    ).first()
    
    if existing_validation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has validado esta traducción"
        )

    # Prevent users from validating a translation they have suggested for
    # If validating a suggestion (suggestion_id provided), ensure the suggestion exists
    suggestion_id = getattr(validation_data, 'suggestion_id', None)
    suggestion_obj = None
    if suggestion_id:
        suggestion_obj = db.query(TranslationSuggestion).filter(TranslationSuggestion.id == suggestion_id).first()
        if not suggestion_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
        # Ensure the suggestion belongs to the same translation
        if suggestion_obj.translation_id != translation.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Suggestion does not belong to the specified translation")
        # Prevent suggestion author from validating their own suggestion
        if suggestion_obj.user_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot validate your own suggestion")
        # Prevent adding more than 3 validations to a single suggestion
        suggestion_validation_count = db.query(func.count(Validation.id)).filter(
            Validation.suggestion_id == suggestion_id
        ).scalar() or 0

        if suggestion_validation_count >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta sugerencia ya tiene 3 validaciones; no se pueden añadir más validaciones a esta sugerencia."
            )
    # Removed restriction: Users can now both suggest AND validate the same translation
    # This allows for more flexible workflow where validators can provide alternatives
    
    # Prevent creating a validation if this translation already has >= 3 validations
    # in its own direction (the pair may have reached the threshold).
    # When counting validations that close a translation, only consider validations that are NOT for suggestions
    same_dir_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == translation.id,
        Validation.direction == translation.direction,
        Validation.suggestion_id == None
    ).scalar() or 0

    if same_dir_count >= 3:
        # Provide a clear message; if this is the inverse (is_original False) mention it
        if getattr(translation, 'is_original', None) is False:
            detail_msg = "La traducción inversa ya tiene 3 o más validaciones; no se pueden añadir más validaciones sobre la inversa."
        else:
            detail_msg = "Esta traducción ya tiene 3 o más validaciones en su dirección; no se pueden añadir más."

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_msg
        )
    
    # Create validation
    db_validation = Validation(
        translation_id=validation_data.translation_id,
        user_id=current_user.id,
        correctness=validation_data.correctness,
        fluency_score=validation_data.fluency_score,
        accuracy_score=validation_data.accuracy_score,
        notes=validation_data.notes,
        direction=translation.direction,
        suggestion_id=suggestion_id,
        category=validation_data.category  # Include category from validation data
    )
    
    try:
        db.add(db_validation)
        db.commit()
        db.refresh(db_validation)
        return ValidationResponse.model_validate(db_validation)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation could not be created"
        )


@router.put("/{validation_id}", response_model=ValidationResponse)
async def update_validation(
    validation_id: int,
    validation_data: ValidationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing validation."""
    # Get validation
    validation = db.query(Validation).filter(
        Validation.id == validation_id,
        Validation.user_id == current_user.id
    ).first()
    
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found or you don't have permission to update it"
        )
    
    # Update fields
    update_data = validation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(validation, field, value)
    
    db.commit()
    db.refresh(validation)
    
    return ValidationResponse.model_validate(validation)


@router.get("/my-history", response_model=List[ValidationResponse])
async def get_user_validations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get validation history for current user."""
    validations = db.query(Validation).filter(
        Validation.user_id == current_user.id
    ).order_by(Validation.created_at.desc()).offset(skip).limit(limit).all()
    
    return [ValidationResponse.model_validate(v) for v in validations]


@router.get("/by-translation/{translation_id}", response_model=ValidationResponse)
async def get_validation_by_translation(
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's validation for a specific translation."""
    validation = db.query(Validation).filter(
        Validation.translation_id == translation_id,
        Validation.user_id == current_user.id
    ).first()
    
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    
    return ValidationResponse.model_validate(validation)