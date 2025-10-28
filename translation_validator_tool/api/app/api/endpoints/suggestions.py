from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.translation import Translation
from app.models.suggestion import TranslationSuggestion
from app.schemas.suggestion import SuggestionCreate, SuggestionResponse
from app.api.deps import get_current_active_user

router = APIRouter()


@router.post("", response_model=SuggestionResponse)
async def create_suggestion(
    suggestion_data: SuggestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new translation suggestion."""
    # Check if translation exists
    translation = db.query(Translation).filter(Translation.id == suggestion_data.translation_id).first()
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    # Validate that at least one suggestion is provided
    if not suggestion_data.suggested_guarani and not suggestion_data.suggested_spanish:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one suggested translation (Guarani or Spanish) must be provided"
        )
    # Do not allow creating suggestions on translations that are not original
    # (suggestions must reference an original translation)
    if getattr(translation, 'is_original', True) is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create a suggestion for a non-original translation"
        )
    
    # Check if user already has a suggestion for this translation
    existing_suggestion = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.translation_id == suggestion_data.translation_id,
        TranslationSuggestion.user_id == current_user.id
    ).first()
    
    if existing_suggestion:
        # Update existing suggestion instead of creating duplicate
        existing_suggestion.suggested_guarani = suggestion_data.suggested_guarani
        existing_suggestion.suggested_spanish = suggestion_data.suggested_spanish
        existing_suggestion.reason = suggestion_data.reason
        existing_suggestion.created_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_suggestion)
        
        return SuggestionResponse.model_validate(existing_suggestion)
    
    # Create new suggestion
    db_suggestion = TranslationSuggestion(
        translation_id=suggestion_data.translation_id,
        user_id=current_user.id,
        suggested_guarani=suggestion_data.suggested_guarani,
        suggested_spanish=suggestion_data.suggested_spanish,
        reason=suggestion_data.reason,
        direction=translation.direction
    )
    
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    
    return SuggestionResponse.model_validate(db_suggestion)


@router.get("", response_model=List[SuggestionResponse])
async def get_suggestions(
    translation_id: int = Query(..., description="Translation ID to get suggestions for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all suggestions for a specific translation."""
    # Check if translation exists
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    suggestions = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.translation_id == translation_id
    ).order_by(TranslationSuggestion.created_at.desc()).all()
    
    return [SuggestionResponse.model_validate(s) for s in suggestions]


@router.get("/my-suggestions", response_model=List[SuggestionResponse])
async def get_user_suggestions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get suggestions created by current user."""
    suggestions = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.user_id == current_user.id
    ).order_by(TranslationSuggestion.created_at.desc()).offset(skip).limit(limit).all()
    
    return [SuggestionResponse.model_validate(s) for s in suggestions]


@router.get("/stats")
async def get_suggestion_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get statistics about suggestions."""
    from sqlalchemy import func
    
    # Total suggestions by current user
    user_suggestions = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.user_id == current_user.id
    ).scalar()
    
    # Total suggestions in system
    total_suggestions = db.query(func.count(TranslationSuggestion.id)).scalar()
    
    # Translations with suggestions
    translations_with_suggestions = db.query(func.count(func.distinct(TranslationSuggestion.translation_id))).scalar()
    
    return {
        "user_suggestions": user_suggestions or 0,
        "total_suggestions": total_suggestions or 0,
        "translations_with_suggestions": translations_with_suggestions or 0
    }


@router.delete("/{suggestion_id}")
async def delete_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a suggestion (only the author can delete)."""
    suggestion = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.id == suggestion_id,
        TranslationSuggestion.user_id == current_user.id
    ).first()
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found or not authorized"
        )
    
    db.delete(suggestion)
    db.commit()
    
    return {"message": "Suggestion deleted successfully"}