from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models.user import User
from app.models.translation import Translation
from app.models.validation import Validation
from app.models.suggestion import TranslationSuggestion
from app.schemas.translation import TranslationResponse, TranslationWithStats, TranslationAdminCreate
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
        Validation.direction == pair.direction,
        Validation.suggestion_id == None
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
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None
    ).scalar()
    
    # Count unique translations with at least one validation
    validated_translations = db.query(func.count(func.distinct(Validation.translation_id))).filter(Validation.suggestion_id == None).scalar()
    
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
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None
    ).subquery()

    # translations the user already suggested (exclude these as well)
    suggested_subquery = db.query(TranslationSuggestion.translation_id).filter(
        TranslationSuggestion.user_id == current_user.id
    ).subquery()

    # Exclude translations that already have 3 or more validations FOR THE SAME DIRECTION
    # Only count validations that are NOT suggestion validations (suggestion_id is NULL)
    validated_three = db.query(Validation.translation_id).filter(
        Validation.suggestion_id == None
    ).group_by(Validation.translation_id).having(
        func.count(Validation.id) >= 3
    ).subquery()

    # Exclude translations that already have 3 or more suggestions
    suggestions_three = db.query(TranslationSuggestion.translation_id).group_by(TranslationSuggestion.translation_id).having(
        func.count(TranslationSuggestion.id) >= 3
    ).subquery()

    # Exclude originals whose pair the user already validated
    validated_pairs_subquery = db.query(Translation.pair_id).join(
        Validation, Translation.id == Validation.translation_id
    ).filter(
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None,
        Translation.pair_id.isnot(None)
    ).subquery()

    # Ensure deterministic ordering by id so 'next' returns the smallest available original id
    translation = db.query(Translation).filter(
        ~Translation.id.in_(subquery),
        ~Translation.id.in_(suggested_subquery),
        ~Translation.id.in_(validated_three),
        ~Translation.id.in_(suggestions_three),
        ~Translation.id.in_(validated_pairs_subquery),
        Translation.is_original == True
    ).order_by(Translation.id).first()

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No more translations to validate"
        )
    
    # Get validation count for this translation
    # Validation count for this translation and direction
    validation_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == translation.id,
        Validation.direction == translation.direction,
        Validation.suggestion_id == None
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


@router.get("/next/suitable", response_model=TranslationWithStats)
async def get_next_suitable_translation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next translation suitable for the current validator.
    Applies the same filters as the client expects: skip translations the user
    already suggested/validated and skip translations whose direction already
    has >= 3 validations. Returns translation metadata including counts so the
    frontend can decide whether to show/hide validation UI.
    """
    # translations the user already validated
    subquery = db.query(Validation.translation_id).filter(
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None
    ).subquery()

    # translations the user already suggested (exclude these as well)
    suggested_subquery = db.query(TranslationSuggestion.translation_id).filter(
        TranslationSuggestion.user_id == current_user.id
    ).subquery()

    # Exclude translations that already have 3 or more validations for the same direction
    # Only count validations that are NOT suggestion validations (suggestion_id is NULL)
    validated_three = db.query(Validation.translation_id).filter(
        Validation.suggestion_id == None
    ).group_by(Validation.translation_id).having(
        func.count(Validation.id) >= 3
    ).subquery()

    # Exclude translations that already have 3 or more suggestions
    suggestions_three = db.query(TranslationSuggestion.translation_id).group_by(TranslationSuggestion.translation_id).having(
        func.count(TranslationSuggestion.id) >= 3
    ).subquery()

    # Exclude originals whose pair the user already validated
    validated_pairs_subquery = db.query(Translation.pair_id).join(
        Validation, Translation.id == Validation.translation_id
    ).filter(
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None,
        Translation.pair_id.isnot(None)
    ).subquery()

    # Select a random original translation not excluded by the above rules
    # Using ORDER BY RANDOM() to distribute load and avoid concurrency on first translations
    translation = db.query(Translation).filter(
        ~Translation.id.in_(subquery),
        ~Translation.id.in_(suggested_subquery),
        ~Translation.id.in_(validated_three),
        ~Translation.id.in_(suggestions_three),
        ~Translation.id.in_(validated_pairs_subquery),
        Translation.is_original == True
    ).order_by(func.random()).first()

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No more translations to validate"
        )

    # Counts and flags
    validation_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == translation.id,
        Validation.direction == translation.direction,
        Validation.suggestion_id == None
    ).scalar()

    user_has_validated = db.query(Validation).filter(
        Validation.translation_id == translation.id,
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None
    ).first() is not None

    suggestion_count = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.translation_id == translation.id
    ).scalar()
    user_has_suggested = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.translation_id == translation.id,
        TranslationSuggestion.user_id == current_user.id
    ).first() is not None

    pair_count, pair_complete = _get_pair_stats(db, translation)

    return TranslationWithStats(
        **translation.__dict__,
        validation_count=validation_count or 0,
        user_has_validated=bool(user_has_validated),
        suggestion_count=suggestion_count or 0,
        user_has_suggested=bool(user_has_suggested),
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
        Validation.direction == translation.direction,
        Validation.suggestion_id == None
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
        Validation.direction == translation.direction,
        Validation.suggestion_id == None
    ).scalar()

    # Whether current user has validated this translation
    user_has_validated = db.query(Validation).filter(
        Validation.translation_id == translation.id,
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None
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
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None
    ).subquery()

    # translations the user already suggested (exclude these as well)
    suggested_subquery = db.query(TranslationSuggestion.translation_id).filter(
        TranslationSuggestion.user_id == current_user.id
    ).subquery()

    # Exclude translations that already have 3 or more validations for the same direction
    # Only count validations that are NOT suggestion validations (suggestion_id is NULL)
    validated_three = db.query(Validation.translation_id).filter(
        Validation.suggestion_id == None
    ).group_by(Validation.translation_id).having(
        func.count(Validation.id) >= 3
    ).subquery()

    # Exclude translations that already have 3 or more suggestions
    suggestions_three = db.query(TranslationSuggestion.translation_id).group_by(TranslationSuggestion.translation_id).having(
        func.count(TranslationSuggestion.id) >= 3
    ).subquery()

    # Exclude originals whose pair the user already validated
    validated_pairs_subquery = db.query(Translation.pair_id).join(
        Validation, Translation.id == Validation.translation_id
    ).filter(
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None,
        Translation.pair_id.isnot(None)
    ).subquery()

    translation = db.query(Translation).filter(
        and_(
            Translation.id > current_id,
            ~Translation.id.in_(subquery),
            ~Translation.id.in_(suggested_subquery),
            ~Translation.id.in_(validated_three),
            ~Translation.id.in_(suggestions_three),
            ~Translation.id.in_(validated_pairs_subquery),
            Translation.is_original == True
        )
    ).order_by(Translation.id).first()
    
    if not translation:
        # If no next translation found, get the first available original translation
        translation = db.query(Translation).filter(
            ~Translation.id.in_(subquery),
            ~Translation.id.in_(suggested_subquery),
            ~Translation.id.in_(validated_three),
            ~Translation.id.in_(suggestions_three),
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
        Validation.direction == translation.direction,
        Validation.suggestion_id == None
    ).scalar()
    user_has_validated = db.query(Validation).filter(
        and_(
            Validation.translation_id == translation.id,
            Validation.user_id == current_user.id,
            Validation.suggestion_id == None
        )
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
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None
    ).subquery()

    # translations the user already suggested (exclude these as well)
    suggested_subquery = db.query(TranslationSuggestion.translation_id).filter(
        TranslationSuggestion.user_id == current_user.id
    ).subquery()

    # Exclude translations that already have 3 or more validations for the same direction
    # Only count validations that are NOT suggestion validations (suggestion_id is NULL)
    validated_three = db.query(Validation.translation_id).filter(
        Validation.suggestion_id == None
    ).group_by(Validation.translation_id).having(
        func.count(Validation.id) >= 3
    ).subquery()

    # Exclude translations that already have 3 or more suggestions
    suggestions_three = db.query(TranslationSuggestion.translation_id).group_by(TranslationSuggestion.translation_id).having(
        func.count(TranslationSuggestion.id) >= 3
    ).subquery()

    # Exclude originals whose pair the user already validated
    validated_pairs_subquery = db.query(Translation.pair_id).join(
        Validation, Translation.id == Validation.translation_id
    ).filter(
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None,
        Translation.pair_id.isnot(None)
    ).subquery()

    translation = db.query(Translation).filter(
        Translation.id < current_id,
        ~Translation.id.in_(subquery),
        ~Translation.id.in_(suggested_subquery),
        ~Translation.id.in_(validated_three),
        ~Translation.id.in_(suggestions_three),
        ~Translation.id.in_(validated_pairs_subquery),
        Translation.is_original == True
    ).order_by(Translation.id.desc()).first()
    
    if not translation:
        # If no previous translation found, get the last original translation
        translation = db.query(Translation).filter(
            ~Translation.id.in_(subquery),
            ~Translation.id.in_(suggested_subquery),
            ~Translation.id.in_(validated_three),
            ~Translation.id.in_(suggestions_three),
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
        , Validation.suggestion_id == None
    ).scalar()
    
    user_has_validated = db.query(Validation).filter(
        and_(
            Validation.translation_id == translation.id,
            Validation.user_id == current_user.id,
            Validation.suggestion_id == None
        )
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
                , Validation.suggestion_id == None
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
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None
    ).subquery()

    # translations the user already suggested (exclude these as well)
    suggested_subquery = db.query(TranslationSuggestion.translation_id).filter(
        TranslationSuggestion.user_id == current_user.id
    ).subquery()

    # Exclude translations that already have 3 or more validations (non-suggestion validations only)
    validated_three = db.query(Validation.translation_id).filter(Validation.suggestion_id == None).group_by(Validation.translation_id).having(func.count(Validation.id) >= 3).subquery()

    # Exclude translations that already have 3 or more suggestions
    suggestions_three = db.query(TranslationSuggestion.translation_id).group_by(TranslationSuggestion.translation_id).having(func.count(TranslationSuggestion.id) >= 3).subquery()

    translations = db.query(Translation).filter(
        ~Translation.id.in_(subquery), ~Translation.id.in_(validated_three), ~Translation.id.in_(suggestions_three), ~Translation.id.in_(suggested_subquery)
    ).order_by(Translation.id).offset(skip).limit(limit).all()
    
    result = []
    for translation in translations:
        validation_count = db.query(func.count(Validation.id)).filter(
            Validation.translation_id == translation.id
            , Validation.suggestion_id == None
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



@router.get('/admin/list')
async def get_admin_translations(
    skip: int = 0,
    limit: int = 20,
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Admin endpoint: paginated list of all translations with stats.
    Supports optional search query `q` (matches id or text fields).
    Only accessible to superusers.
    """
    is_super = getattr(current_user, 'is_superuser', False)
    if not is_super:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query = db.query(Translation)
    if q:
        # if q looks like an integer, allow id search
        try:
            qid = int(q)
        except Exception:
            qid = None

        like = f"%{q}%"
        if qid is not None:
            query = query.filter(
                (Translation.id == qid) |
                (Translation.guarani_text.ilike(like)) |
                (Translation.spanish_text.ilike(like))
            )
        else:
            query = query.filter(
                (Translation.guarani_text.ilike(like)) |
                (Translation.spanish_text.ilike(like))
            )

    total = query.count()
    translations = query.order_by(Translation.id).offset(skip).limit(limit).all()

    items = []
    for translation in translations:
        validation_count = db.query(func.count(Validation.id)).filter(
            Validation.translation_id == translation.id,
            Validation.direction == translation.direction,
            Validation.suggestion_id == None
        ).scalar() or 0

        suggestion_count = db.query(func.count(TranslationSuggestion.id)).filter(
            TranslationSuggestion.translation_id == translation.id
        ).scalar() or 0

        pair_count, pair_complete = _get_pair_stats(db, translation)

        items.append(TranslationWithStats(
            **translation.__dict__,
            validation_count=validation_count,
            user_has_validated=False,
            suggestion_count=suggestion_count,
            user_has_suggested=False,
            pair_same_direction_count=pair_count,
            pair_is_complete=bool(pair_complete)
        ))

    return {
        'items': items,
        'total': total or 0,
        'skip': skip,
        'limit': limit,
        'has_next': (skip + limit) < (total or 0)
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



@router.get("/pair/{translation_id}", response_model=TranslationWithStats)
async def get_paired_translation(
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Return the paired translation for a given translation id, including basic stats for the paired record.
    If the translation has pair_id, return that row. Otherwise try to find a row whose pair_id == translation_id.
    This endpoint returns validation counts and simple flags so the UI can display whether the paired
    translation is already completed (>=3 validations) and prevent validating it.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found")

    # Prefer the explicit pair_id
    paired = None
    if translation.pair_id:
        paired = db.query(Translation).filter(Translation.id == translation.pair_id).first()
    else:
        paired = db.query(Translation).filter(Translation.pair_id == translation.id).first()

    if not paired:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paired translation not found")

    # Validation count for paired translation in its own direction (excluding suggestion validations)
    validation_count = db.query(func.count(Validation.id)).filter(
        Validation.translation_id == paired.id,
        Validation.direction == paired.direction,
        Validation.suggestion_id == None
    ).scalar()

    user_has_validated = db.query(Validation).filter(
        Validation.translation_id == paired.id,
        Validation.user_id == current_user.id,
        Validation.suggestion_id == None
    ).first() is not None

    # Suggestion info for paired translation
    suggestion_count = db.query(func.count(TranslationSuggestion.id)).filter(
        TranslationSuggestion.translation_id == paired.id
    ).scalar()
    user_has_suggested = db.query(TranslationSuggestion).filter(
        TranslationSuggestion.translation_id == paired.id,
        TranslationSuggestion.user_id == current_user.id
    ).first() is not None

    pair_count, pair_complete = _get_pair_stats(db, paired)

    return TranslationWithStats(
        **paired.__dict__,
        validation_count=validation_count or 0,
        user_has_validated=user_has_validated,
        suggestion_count=suggestion_count or 0,
        user_has_suggested=user_has_suggested,
        pair_same_direction_count=pair_count or 0,
        pair_is_complete=bool(pair_complete)
    )


@router.get("/context/{translation_id}")
async def get_translation_context(
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get context for a translation: previous and next original sentences.
    
    Returns the previous and next translations that are marked as is_original=True,
    which helps show the surrounding context without duplicates from paired entries.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found")
    
    # Get previous original translation (lower ID, is_original=True)
    prev_translation = db.query(Translation).filter(
        Translation.id < translation_id,
        Translation.is_original == True
    ).order_by(Translation.id.desc()).first()
    
    # Get next original translation (higher ID, is_original=True)
    next_translation = db.query(Translation).filter(
        Translation.id > translation_id,
        Translation.is_original == True
    ).order_by(Translation.id.asc()).first()
    
    return {
        "previous": {
            "id": prev_translation.id,
            "guarani_text": prev_translation.guarani_text,
            "spanish_text": prev_translation.spanish_text,
            "source": prev_translation.source,
            "direction": prev_translation.direction
        } if prev_translation else None,
        "current": {
            "id": translation.id,
            "guarani_text": translation.guarani_text,
            "spanish_text": translation.spanish_text,
            "source": translation.source,
            "direction": translation.direction,
            "is_original": translation.is_original
        },
        "next": {
            "id": next_translation.id,
            "guarani_text": next_translation.guarani_text,
            "spanish_text": next_translation.spanish_text,
            "source": next_translation.source,
            "direction": next_translation.direction
        } if next_translation else None
    }


@router.post("/admin/create", response_model=TranslationResponse)
async def admin_create_translation(
    translation_data: TranslationAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Admin endpoint to create new translations.
    - If both guarani_text and spanish_text are provided: creates 2 paired entries (sp-gn and gn-sp)
    - If only guarani_text is provided: creates single entry (gn-sp), pair will be created later when spanish_text is added
    Only accessible to superusers.
    """
    # Check if user is superuser
    is_super = getattr(current_user, 'is_superuser', False)
    if not is_super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only admins can create translations"
        )
    
    try:
        # Case 1: Both texts provided - create paired entries
        if translation_data.guarani_text and translation_data.spanish_text:
            # Create original translation (direction from form)
            original_translation = Translation(
                guarani_text=translation_data.guarani_text,
                spanish_text=translation_data.spanish_text,
                source=translation_data.source,
                direction=translation_data.direction,  # sp-gn or gn-sp as selected
                is_original=True
            )
            
            db.add(original_translation)
            db.flush()  # Get the ID without committing
            
            # Create inverse translation
            inverse_direction = "gn-sp" if translation_data.direction == "sp-gn" else "sp-gn"
            inverse_translation = Translation(
                guarani_text=translation_data.guarani_text,
                spanish_text=translation_data.spanish_text,
                source=translation_data.source,
                direction=inverse_direction,
                is_original=False,
                pair_id=original_translation.id
            )
            
            db.add(inverse_translation)
            db.flush()
            
            # Set pair_id for original
            original_translation.pair_id = inverse_translation.id
            
            db.commit()
            db.refresh(original_translation)
            
            return TranslationResponse.model_validate(original_translation)
            
        # Case 2: Only guarani_text provided - create single entry (gn-sp)
        else:
            db_translation = Translation(
                guarani_text=translation_data.guarani_text,
                spanish_text=None,
                source=translation_data.source,
                direction="gn-sp",  # Force gn-sp for Guaraní-only entries
                is_original=True
            )
            
            db.add(db_translation)
            db.commit()
            db.refresh(db_translation)
            
            return TranslationResponse.model_validate(db_translation)
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create translation: {str(e)}"
        )