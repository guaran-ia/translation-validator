from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models.user import User
from app.models.translation import Translation
from app.models.validation import Validation
from app.models.suggestion import TranslationSuggestion
from app.schemas.translation import TranslationResponse, TranslationWithStats
from app.api.deps import get_current_active_user

router = APIRouter()


def _get_pair_stats(db: Session, translation: Translation):
    """Return (pair_same_direction_count, pair_is_complete) for a translation's paired record, if any."""
    if not translation:
        return 0, False
    # Find paired record
    pair = None
    if getattr(translation, 'pair_id', None):
        pair = db.query(Translation).filter(Translation.id == translation.pair_id).first()
    else:
        pair = db.query(Translation).filter(Translation.pair_id == translation.id).first()

    if not pair:
        return 0, False

    pair_same_direction_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == pair.id,
        Validation.direction == pair.direction
    ).scalar() or 0

    return pair_same_direction_count, (pair_same_direction_count >= 3)


@router.get("/stats/public")
async def get_public_stats(
    db: Session = Depends(get_db)
):
    """Get public translation statistics (no authentication required)."""
    total_translations = db.query(func.count(Translation.id)).scalar()
    validated_translations = db.query(func.count(func.distinct(Validation.translation_id))).scalar()
    
    return {
        "total": total_translations or 0,
        "validated": validated_translations or 0,
        "pending": (total_translations or 0) - (validated_translations or 0)
    }


@router.get("/stats")
async def get_translation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get translation statistics."""
    total_translations = db.query(func.count(Translation.id)).scalar()
    
    # Count validated translations by current user
    user_validated = db.query(func.count(Validation.id)).filter(
        Validation.user_id == current_user.id
    ).scalar()
    
    # Count unique translations with at least one validation
    validated_translations = db.query(func.count(func.distinct(Validation.translation_id))).scalar()
    
    return {
        "total": total_translations or 0,
        "validated": validated_translations or 0,
        "pending": (total_translations or 0) - (validated_translations or 0),
        "user_progress": user_validated or 0
    }


@router.get("/next", response_model=TranslationWithStats)
async def get_next_translation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next translation that hasn't been validated by the current user.
    Skip originals when the user already validated the inverse pair.
    """
    # Find translations not validated by current user
    subquery = db.query(Validation.translation_id).filter(
        Validation.user_id == current_user.id
    ).subquery()

    # Exclude translations that already have 3 or more validations FOR THE SAME DIRECTION
    validated_three = db.query(Validation.translation_id).group_by(Validation.translation_id).having(
        func.count(func.nullif(Validation.direction != Translation.direction, True)) >= 3
    ).subquery()

    # Exclude originals whose pair the user already validated
    validated_pairs_subquery = db.query(Translation.pair_id).join(
        Validation, Translation.id == Validation.translation_id
    ).filter(
        Validation.user_id == current_user.id,
        Translation.pair_id.isnot(None)
    ).subquery()

    translation = db.query(Translation).filter(
        ~Translation.id.in_(subquery),
        ~Translation.id.in_(validated_three),
        ~Translation.id.in_(validated_pairs_subquery),
        Translation.is_original == True
    ).first()

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No more translations to validate"
        )
    
    # Get validation count for this translation
    # Validation count for this translation and direction
    validation_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == translation.id,
        Validation.direction == translation.direction
    ).scalar()
    # Get suggestion count and whether current user suggested
    suggestion_count = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.translation_id == translation.id
    ).scalar()
    user_has_suggested = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.translation_id == translation.id,
        TranslationSuggestion.user_id == current_user.id
    ).first() is not None
    
    pair_count, pair_complete = _get_pair_stats(db, translation)

    # Hide sensitive stats for non-superusers (validators)
    is_super = getattr(current_user, 'is_superuser', False)
    if not is_super:
        # do not expose validation/suggestion/pair stats or user-specific flags
        return TranslationWithStats(
            **translation.__dict__,
            validation_count=0,
            user_has_validated=False,
            suggestion_count=0,
            user_has_suggested=False,
            pair_same_direction_count=0,
            pair_is_complete=False
        )

    return TranslationWithStats(
        **translation.__dict__,
        validation_count=validation_count or 0,
        user_has_validated=False,
        suggestion_count=suggestion_count or 0,
        user_has_suggested=user_has_suggested,
        pair_same_direction_count=pair_count or 0,
        pair_is_complete=bool(pair_complete)
    )


@router.get("/random", response_model=TranslationWithStats)
async def get_random_translation(
    db: Session = Depends(get_db)
):
    """Get a random translation (no authentication required)."""
    # Exclude translations that already have 3 or more validations for the same direction
    validated_three = db.query(Validation.translation_id).group_by(Validation.translation_id).having(
        func.count(func.nullif(Validation.direction != Translation.direction, True)) >= 3
    ).subquery()

    # Get a random translation that isn't completed
    translation = db.query(Translation).filter(~Translation.id.in_(validated_three)).order_by(func.random()).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No translations available"
        )
    
    # Get validation count for this translation
    validation_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == translation.id,
        Validation.direction == translation.direction
    ).scalar()
    # Suggestion info (no user context -> only count)
    suggestion_count = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.translation_id == translation.id
    ).scalar()
    pair_count, pair_complete = _get_pair_stats(db, translation)

    return TranslationWithStats(
        **translation.__dict__,
        validation_count=validation_count or 0,
        user_has_validated=False,
        suggestion_count=suggestion_count or 0,
        user_has_suggested=False,
        pair_same_direction_count=pair_count or 0,
        pair_is_complete=bool(pair_complete)
    )


@router.get("/{translation_id}", response_model=TranslationWithStats)
async def get_translation(
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific translation by ID, including validation/suggestion stats and paired translation info."""
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    # Validation count for this translation in its own direction
    validation_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == translation.id,
        Validation.direction == translation.direction
    ).scalar()

    # Whether current user has validated this translation
    user_has_validated = db.query(Validation).filter(
        Validation.translation_id == translation.id,
        Validation.user_id == current_user.id
    ).first() is not None

    # Suggestion info
    suggestion_count = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.translation_id == translation.id
    ).scalar()
    user_has_suggested = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.translation_id == translation.id,
        TranslationSuggestion.user_id == current_user.id
    ).first() is not None

    pair_count, pair_complete = _get_pair_stats(db, translation)

    is_super = getattr(current_user, 'is_superuser', False)
    if not is_super:
        return TranslationWithStats(
            **translation.__dict__,
            validation_count=0,
            user_has_validated=False,
            suggestion_count=0,
            user_has_suggested=False,
            pair_same_direction_count=0,
            pair_is_complete=False
        )

    return TranslationWithStats(
        **translation.__dict__,
        validation_count=validation_count or 0,
        user_has_validated=user_has_validated,
        suggestion_count=suggestion_count or 0,
        user_has_suggested=user_has_suggested,
        pair_same_direction_count=pair_count or 0,
        pair_is_complete=bool(pair_complete)
    )


@router.get("/navigation/next/{current_id}", response_model=TranslationWithStats)
async def get_next_translation_from_id(
    current_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next translation after the current ID that hasn't been validated by the user.
    Skip originals when the user already validated the inverse pair.
    """
    # Find translations not validated by current user with ID greater than current_id
    subquery = db.query(Validation.translation_id).filter(
        Validation.user_id == current_user.id
    ).subquery()

    # Exclude translations that already have 3 or more validations for the same direction
    validated_three = db.query(Validation.translation_id).group_by(Validation.translation_id).having(
        func.count(func.nullif(Validation.direction != Translation.direction, True)) >= 3
    ).subquery()

    # Exclude originals whose pair the user already validated
    validated_pairs_subquery = db.query(Translation.pair_id).join(
        Validation, Translation.id == Validation.translation_id
    ).filter(
        Validation.user_id == current_user.id,
        Translation.pair_id.isnot(None)
    ).subquery()

    translation = db.query(Translation).filter(
        and_(
            Translation.id > current_id,
            ~Translation.id.in_(subquery),
            ~Translation.id.in_(validated_three),
            ~Translation.id.in_(validated_pairs_subquery),
            Translation.is_original == True
        )
    ).order_by(Translation.id).first()
    
    if not translation:
        # If no next translation found, get the first available original translation
        translation = db.query(Translation).filter(
            ~Translation.id.in_(subquery),
            ~Translation.id.in_(validated_three),
            ~Translation.id.in_(validated_pairs_subquery),
            Translation.is_original == True
        ).order_by(Translation.id).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No more translations to validate"
        )
    
    # Get validation count and user validation status
    validation_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == translation.id,
        Validation.direction == translation.direction
    ).scalar()
    
    user_has_validated = db.query(Validation).filter(
        and_(Validation.translation_id == translation.id, Validation.user_id == current_user.id)
    ).first() is not None
    # Suggestion info
    suggestion_count = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.translation_id == translation.id
    ).scalar()
    user_has_suggested = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.translation_id == translation.id,
        TranslationSuggestion.user_id == current_user.id
    ).first() is not None
    
    pair_count, pair_complete = _get_pair_stats(db, translation)

    is_super = getattr(current_user, 'is_superuser', False)
    if not is_super:
        return TranslationWithStats(
            **translation.__dict__,
            validation_count=0,
            user_has_validated=False,
            suggestion_count=0,
            user_has_suggested=False,
            pair_same_direction_count=0,
            pair_is_complete=False
        )

    return TranslationWithStats(
        **translation.__dict__,
        validation_count=validation_count or 0,
        user_has_validated=user_has_validated,
        suggestion_count=suggestion_count or 0,
        user_has_suggested=user_has_suggested,
        pair_same_direction_count=pair_count or 0,
        pair_is_complete=bool(pair_complete)
    )


@router.get("/navigation/previous/{current_id}", response_model=TranslationWithStats)
async def get_previous_translation_from_id(
    current_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the previous translation before the current ID.
    Skip originals when the user already validated the inverse pair.
    """
    # Find translations not validated by current user
    subquery = db.query(Validation.translation_id).filter(
        Validation.user_id == current_user.id
    ).subquery()

    # Exclude translations that already have 3 or more validations for the same direction
    validated_three = db.query(Validation.translation_id).group_by(Validation.translation_id).having(
        func.count(func.nullif(Validation.direction != Translation.direction, True)) >= 3
    ).subquery()

    # Exclude originals whose pair the user already validated
    validated_pairs_subquery = db.query(Translation.pair_id).join(
        Validation, Translation.id == Validation.translation_id
    ).filter(
        Validation.user_id == current_user.id,
        Translation.pair_id.isnot(None)
    ).subquery()

    translation = db.query(Translation).filter(
        Translation.id < current_id,
        ~Translation.id.in_(subquery),
        ~Translation.id.in_(validated_three),
        ~Translation.id.in_(validated_pairs_subquery),
        Translation.is_original == True
    ).order_by(Translation.id.desc()).first()
    
    if not translation:
        # If no previous translation found, get the last original translation
        translation = db.query(Translation).filter(
            ~Translation.id.in_(subquery),
            ~Translation.id.in_(validated_pairs_subquery),
            Translation.is_original == True
        ).order_by(Translation.id.desc()).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No translations available"
        )
    
    # Get validation count and user validation status
    validation_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == translation.id
    ).scalar()
    
    user_has_validated = db.query(Validation).filter(
        and_(Validation.translation_id == translation.id, Validation.user_id == current_user.id)
    ).first() is not None
    # Suggestion info
    suggestion_count = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.translation_id == translation.id
    ).scalar()
    user_has_suggested = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.translation_id == translation.id,
        TranslationSuggestion.user_id == current_user.id
    ).first() is not None
    
    pair_count, pair_complete = _get_pair_stats(db, translation)

    is_super = getattr(current_user, 'is_superuser', False)
    if not is_super:
        return TranslationWithStats(
            **translation.__dict__,
            validation_count=0,
            user_has_validated=False,
            suggestion_count=0,
            user_has_suggested=False,
            pair_same_direction_count=0,
            pair_is_complete=False
        )

    return TranslationWithStats(
        **translation.__dict__,
        validation_count=validation_count or 0,
        user_has_validated=user_has_validated,
        suggestion_count=suggestion_count or 0,
        user_has_suggested=user_has_suggested,
        pair_same_direction_count=pair_count or 0,
        pair_is_complete=bool(pair_complete)
    )


@router.get("/validated/my-history")
async def get_my_validated_translations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated list of translations validated by the current user."""
    # Get validations with translation data
    validations = db.query(Validation).filter(
        Validation.user_id == current_user.id
    ).order_by(Validation.created_at.desc()).offset(skip).limit(limit).all()
    
    # Get translation details for each validation
    result = []
    for validation in validations:
        translation = db.query(Translation).filter(Translation.id == validation.translation_id).first()
        if translation:
            validation_count = db.query(func.count(Validation.id)).filter(
                Validation.translation_id == translation.id
            ).scalar()
            pair_count, pair_complete = _get_pair_stats(db, translation)

            result.append({
                "translation": TranslationWithStats(
                    **translation.__dict__,
                    validation_count=validation_count or 0,
                    user_has_validated=True,
                    pair_same_direction_count=pair_count or 0,
                    pair_is_complete=bool(pair_complete)
                ),
                "validation": {
                    "id": validation.id,
                    "correctness": validation.correctness,
                    "fluency_score": validation.fluency_score,
                    "accuracy_score": validation.accuracy_score,
                    "notes": validation.notes,
                    "created_at": validation.created_at
                }
            })
    
    # Get total count for pagination
    total = db.query(func.count(Validation.id)).filter(
        Validation.user_id == current_user.id
    ).scalar()
    
    return {
        "items": result,
        "total": total or 0,
        "skip": skip,
        "limit": limit,
        "has_next": (skip + limit) < (total or 0)
    }


@router.get("/pending/for-me")
async def get_my_pending_translations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated list of translations pending validation by the current user."""
    # Find translations not validated by current user
    subquery = db.query(Validation.translation_id).filter(
        Validation.user_id == current_user.id
    ).subquery()

    # Exclude translations that already have 3 or more validations
    validated_three = db.query(Validation.translation_id).group_by(Validation.translation_id).having(func.count(Validation.id) >= 3).subquery()

    translations = db.query(Translation).filter(
        ~Translation.id.in_(subquery), ~Translation.id.in_(validated_three)
    ).order_by(Translation.id).offset(skip).limit(limit).all()
    
    result = []
    for translation in translations:
        validation_count = db.query(func.count(Validation.id)).filter(
            Validation.translation_id == translation.id
        ).scalar()
        # Suggestion info (user context)
        suggestion_count = db.query(func.count(TranslationSuggestion.id)).filter(
            TranslationSuggestion.translation_id == translation.id
        ).scalar()
        user_has_suggested = db.query(TranslationSuggestion).filter(
            TranslationSuggestion.translation_id == translation.id,
            TranslationSuggestion.user_id == current_user.id
        ).first() is not None

        pair_count, pair_complete = _get_pair_stats(db, translation)

        result.append(TranslationWithStats(
            **translation.__dict__,
            validation_count=validation_count or 0,
            user_has_validated=False,
            suggestion_count=suggestion_count or 0,
            user_has_suggested=user_has_suggested,
            pair_same_direction_count=pair_count or 0,
            pair_is_complete=bool(pair_complete)
        ))
    
    # Get total count of pending translations (excluding completed ones)
    total = db.query(func.count(Translation.id)).filter(
        ~Translation.id.in_(subquery), ~Translation.id.in_(validated_three)
    ).scalar()
    
    return {
        "items": result,
        "total": total or 0,
        "skip": skip,
        "limit": limit,
        "has_next": (skip + limit) < (total or 0)
    }



@router.patch("/{translation_id}/direction", response_model=TranslationResponse)
async def update_translation_direction(
    translation_id: int,
    direction: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update the direction flag for a translation (sp-gn or gn-sp)."""
    if direction not in ("sp-gn", "gn-sp"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid direction")

    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found")

    # Simple permission: only superusers can change direction (optional change)
    try:
        is_super = getattr(current_user, 'is_superuser', False)
    except Exception:
        is_super = False

    if not is_super:
        # For now allow any authenticated user; change to is_super check if restricted
        pass

    translation.direction = direction
    db.add(translation)
    db.commit()
    db.refresh(translation)

    return TranslationResponse.model_validate(translation)



@router.get("/pair/{translation_id}", response_model=TranslationResponse)
async def get_paired_translation(
    translation_id: int,
    db: Session = Depends(get_db),
):
    """Return the paired translation for a given translation id.
    If the translation has pair_id, return that row. Otherwise try to find a row whose pair_id == translation_id.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found")

    # Prefer the explicit pair_id
    if translation.pair_id:
        paired = db.query(Translation).filter(Translation.id == translation.pair_id).first()
        if paired:
            return TranslationResponse.model_validate(paired)

    # Otherwise try to find the record that references this one as pair
    paired = db.query(Translation).filter(Translation.pair_id == translation.id).first()
    if paired:
        return TranslationResponse.model_validate(paired)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paired translation not found")