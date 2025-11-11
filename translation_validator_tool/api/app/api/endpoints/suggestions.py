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
from sqlalchemy import func
from app.models.validation import Validation

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
    # Allow creating suggestions for any translation (original or inverse).
    # Previously suggestions were restricted to originals; that restriction
    # has been removed so validators can propose improvements on inverse
    # translations as well.
    
    # Check if user already has a non-promoted suggestion for this translation
    existing_suggestion = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.translation_id == suggestion_data.translation_id,
        TranslationSuggestion.user_id == current_user.id,
        TranslationSuggestion.is_promoted == False  # Solo considerar sugerencias no promovidas
    ).first()
    
    if existing_suggestion:
        # Update existing suggestion instead of creating duplicate
        existing_suggestion.suggested_guarani = suggestion_data.suggested_guarani
        existing_suggestion.suggested_spanish = suggestion_data.suggested_spanish
        existing_suggestion.reason = suggestion_data.reason
        existing_suggestion.created_at = datetime.utcnow()
        
        # If this is the only suggestion and translation still missing spanish_text, 
        # promote the updated suggestion
        if (translation.spanish_text is None and 
            suggestion_data.suggested_spanish and 
            translation.direction == 'gn-sp'):
            
            # Count other non-promoted suggestions for this translation (excluding current one)
            other_count = db.query(func.count(TranslationSuggestion.id)).filter(
                TranslationSuggestion.translation_id == suggestion_data.translation_id,
                TranslationSuggestion.id != existing_suggestion.id,
                TranslationSuggestion.is_promoted == False
            ).scalar() or 0
            
            # If this is the only suggestion, update translation
            if other_count == 0:
                translation.spanish_text = suggestion_data.suggested_spanish
                db.add(translation)
                
                # Create the paired inverse translation (sp-gn) now that we have both texts
                inverse_translation = Translation(
                    guarani_text=translation.guarani_text,
                    spanish_text=suggestion_data.suggested_spanish,
                    source=translation.source,
                    direction="sp-gn",  # Inverse direction
                    is_original=False,
                    pair_id=translation.id
                )
                
                db.add(inverse_translation)
                db.flush()  # Get the ID
                
                # Update original translation with pair_id
                translation.pair_id = inverse_translation.id
                db.add(translation)
                
                # IMPORTANT: Mark the auto-promoted suggestion as promoted (logical deletion)
                # Since it's now the official translation, we don't want users to validate it as a "suggestion"
                existing_suggestion.is_promoted = True
                db.add(existing_suggestion)
                
                # Commit all changes for auto-promotion
                db.commit()
                db.refresh(existing_suggestion)
                
                # Return response indicating the suggestion was auto-promoted and removed
                return SuggestionResponse.model_validate({
                    **existing_suggestion.__dict__,
                    "id": existing_suggestion.id,
                    "validation_count": 0,
                    "user_has_validated": False
                })
        
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
    db.flush()  # Flush to get the ID and persist the suggestion
    
    # Check if this is the first suggestion and translation is missing spanish_text
    # If so, automatically promote the suggestion to become the official translation
    if (translation.spanish_text is None and 
        suggestion_data.suggested_spanish and 
        translation.direction == 'gn-sp'):
        
        # Count existing non-promoted suggestions for this translation (including the current one)
        existing_count = db.query(func.count(TranslationSuggestion.id)).filter(
            TranslationSuggestion.translation_id == suggestion_data.translation_id,
            TranslationSuggestion.is_promoted == False
        ).scalar() or 0
        
        # If this is the first suggestion (count should be 1 with current one), auto-promote it
        if existing_count == 1:
            translation.spanish_text = suggestion_data.suggested_spanish
            db.add(translation)
            
            # Create the paired inverse translation (sp-gn) now that we have both texts
            inverse_translation = Translation(
                guarani_text=translation.guarani_text,
                spanish_text=suggestion_data.suggested_spanish,
                source=translation.source,
                direction="sp-gn",  # Inverse direction
                is_original=False,
                pair_id=translation.id
            )
            
            db.add(inverse_translation)
            db.flush()  # Get the ID
            
            # Update original translation with pair_id
            translation.pair_id = inverse_translation.id
            db.add(translation)
            
            # IMPORTANT: Mark the auto-promoted suggestion as promoted (logical deletion)
            # Since it's now the official translation, we don't want users to validate it as a "suggestion"
            db_suggestion.is_promoted = True
            db.add(db_suggestion)
            
            # Commit all changes for auto-promotion
            db.commit()
            db.refresh(db_suggestion)
            
            # Return response indicating the suggestion was auto-promoted and removed
            return SuggestionResponse.model_validate({
                **db_suggestion.__dict__,
                "id": db_suggestion.id,
                "validation_count": 0,
                "user_has_validated": False
            })
    
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
        TranslationSuggestion.translation_id == translation_id,
        TranslationSuggestion.is_promoted == False  # Solo mostrar sugerencias no promovidas
    ).order_by(TranslationSuggestion.created_at.desc()).all()
    # Augment suggestions with per-suggestion validation counts and whether current user validated them
    result = []
    for s in suggestions:
        vcount = db.query(func.count(Validation.id)).filter(Validation.suggestion_id == s.id).scalar() or 0
        user_has_validated = db.query(Validation).filter(Validation.suggestion_id == s.id, Validation.user_id == current_user.id).first() is not None
        # Build a response-compatible object
        obj = SuggestionResponse.model_validate(s)
        # Attach computed fields
        obj.validation_count = vcount
        obj.user_has_validated = bool(user_has_validated)
        result.append(obj)

    return result


@router.get("/my-suggestions", response_model=List[SuggestionResponse])
async def get_user_suggestions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get suggestions created by current user."""
    suggestions = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.user_id == current_user.id,
        TranslationSuggestion.is_promoted == False  # Solo mostrar sugerencias no promovidas
    ).order_by(TranslationSuggestion.created_at.desc()).offset(skip).limit(limit).all()
    
    return [SuggestionResponse.model_validate(s) for s in suggestions]


@router.get("/stats")
async def get_suggestion_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get statistics about suggestions."""
    from sqlalchemy import func
    
    # Total non-promoted suggestions by current user
    user_suggestions = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.user_id == current_user.id,
        TranslationSuggestion.is_promoted == False
    ).scalar()
    
    # Total non-promoted suggestions in system
    total_suggestions = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.is_promoted == False
    ).scalar()
    
    # Translations with non-promoted suggestions
    translations_with_suggestions = db.query(func.count(func.distinct(TranslationSuggestion.translation_id))).filter(
        TranslationSuggestion.is_promoted == False
    ).scalar()
    
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
        TranslationSuggestion.user_id == current_user.id,
        TranslationSuggestion.is_promoted == False  # Solo permitir eliminar sugerencias no promovidas
    ).first()
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found, not authorized, or already promoted"
        )
    
    # Usar borrado lógico marcando como promovida
    suggestion.is_promoted = True
    db.add(suggestion)
    db.commit()
    
    return {"message": "Suggestion deleted successfully"}