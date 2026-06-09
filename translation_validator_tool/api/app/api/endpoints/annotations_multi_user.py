"""
NEW ENDPOINTS for multi-user annotation support
Endpoints for managing AnnotationAssignment and AnnotationTranslation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, text

from app.database import get_db
from app.models.user import User
from app.models.annotation import Annotation
from app.models.annotation_assignment import AnnotationAssignment
from app.models.annotation_translation import AnnotationTranslation
from app.schemas.annotation_schemas import (
    AnnotationAssignmentResponse,
    AnnotationAssignmentCreate,
    AnnotationTranslationResponse,
    AnnotationTranslationCreate,
    AnnotationTranslationUpdate,
    BulkAssignRequest,
    BulkAssignResponse,
    TranslationBulkCreateRequest,
    TranslationBulkCreateResponse,
    AnnotationTranslationBase,
)
from app.api.deps import get_current_active_user

router = APIRouter()


# ==================== ANNOTATION ASSIGNMENT ENDPOINTS ====================

@router.get("/{annotation_id}/assignments", response_model=list[AnnotationAssignmentResponse])
async def get_annotation_assignments(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all assignments for an annotation"""
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    assignments = db.query(AnnotationAssignment).filter(
        AnnotationAssignment.annotation_id == annotation_id
    ).all()
    
    return assignments


@router.post("/{annotation_id}/assign", response_model=AnnotationAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_annotation(
    annotation_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Assign an annotation to a translator
    Admins can assign to anyone. Translators can assign themselves.
    """
    # Allow self-assignment for translators; assigning others requires admin
    if current_user.id != user_id:
        if current_user.role != "admin" and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can assign annotations to other users",
            )

    # Check annotation exists
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    # Check user exists and is a translator
    translator = db.query(User).filter(User.id == user_id).first()
    if not translator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if translator.role != "traductor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a translator",
        )

    # Check if already assigned
    existing = db.query(AnnotationAssignment).filter(
        and_(
            AnnotationAssignment.annotation_id == annotation_id,
            AnnotationAssignment.user_id == user_id,
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Annotation {annotation_id} is already assigned to user {user_id}",
        )
    
    # Create assignment
    assignment = AnnotationAssignment(
        annotation_id=annotation_id,
        user_id=user_id,
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment


@router.delete("/{annotation_id}/assign/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_annotation(
    annotation_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove an assignment"""
    # Allow admins or the user themself to unassign
    if not (current_user.role == "admin" or current_user.is_superuser or current_user.id == user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or the assigned user can remove assignments",
        )
    
    assignment = db.query(AnnotationAssignment).filter(
        and_(
            AnnotationAssignment.annotation_id == annotation_id,
            AnnotationAssignment.user_id == user_id,
        )
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )
    
    db.delete(assignment)
    db.commit()


@router.post("/assign/bulk", response_model=BulkAssignResponse)
async def bulk_assign(
    request: BulkAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Bulk assign annotations to multiple users"""
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform bulk assignments",
        )
    
    created_count = 0
    skipped_count = 0
    
    for annotation_id in request.annotation_ids:
        for user_id in request.user_ids:
            existing = db.query(AnnotationAssignment).filter(
                and_(
                    AnnotationAssignment.annotation_id == annotation_id,
                    AnnotationAssignment.user_id == user_id,
                )
            ).first()
            
            if not existing:
                assignment = AnnotationAssignment(
                    annotation_id=annotation_id,
                    user_id=user_id,
                )
                db.add(assignment)
                created_count += 1
            else:
                skipped_count += 1
    
    db.commit()
    
    return BulkAssignResponse(
        created_count=created_count,
        skipped_count=skipped_count,
        message=f"Created {created_count} assignments, skipped {skipped_count} duplicates",
    )


# ==================== ANNOTATION TRANSLATION ENDPOINTS ====================

@router.get("/{annotation_id}/translations", response_model=list[AnnotationTranslationResponse])
async def get_annotation_translations(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all translations for an annotation"""
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    translations = db.query(AnnotationTranslation).filter(
        AnnotationTranslation.annotation_id == annotation_id
    ).order_by(desc(AnnotationTranslation.created_at)).all()
    
    return translations


@router.get("/{annotation_id}/translations/{user_id}", response_model=AnnotationTranslationResponse)
async def get_user_translation(
    annotation_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific user's translation for an annotation"""
    translation = db.query(AnnotationTranslation).filter(
        and_(
            AnnotationTranslation.annotation_id == annotation_id,
            AnnotationTranslation.user_id == user_id,
        )
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found",
        )
    
    return translation


@router.post("/{annotation_id}/translations", response_model=AnnotationTranslationResponse, status_code=status.HTTP_201_CREATED)
async def create_translation(
    annotation_id: int,
    translation_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create or update a translation for an annotation.
    A translator can only have ONE translation per annotation.
    If they already have one, this will fail - use PUT to update.
    """
    # Check annotation exists
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    # Check if user already has a translation
    existing = db.query(AnnotationTranslation).filter(
        and_(
            AnnotationTranslation.annotation_id == annotation_id,
            AnnotationTranslation.user_id == current_user.id,
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a translation for this annotation. Use PUT to update.",
        )
    
    # At least one of question_gn or answer_gn must be provided
    question_gn = translation_data.get('question_gn')
    answer_gn = translation_data.get('answer_gn')
    if not question_gn and not answer_gn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of 'question_gn' or 'answer_gn' must be provided",
        )
    
    # Create translation
    translation = AnnotationTranslation(
        annotation_id=annotation_id,
        user_id=current_user.id,
        question_gn=question_gn,
        answer_gn=answer_gn,
    )
    
    db.add(translation)
    db.commit()
    
    # Update annotation's 'translated' flag based on translation count
    translation_count = db.query(func.count(AnnotationTranslation.id)).filter(
        AnnotationTranslation.annotation_id == annotation_id
    ).scalar() or 0
    
    annotation.translated = (translation_count >= 3)
    db.commit()
    db.refresh(translation)
    
    return translation


@router.put("/{annotation_id}/translations/{translation_id}", response_model=AnnotationTranslationResponse)
async def update_translation(
    annotation_id: int,
    translation_id: int,
    update_data: AnnotationTranslationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a translation (only the owner can update)"""
    translation = db.query(AnnotationTranslation).filter(
        AnnotationTranslation.id == translation_id
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found",
        )
    
    # Check ownership
    if translation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own translations",
        )
    
    # Update fields
    if update_data.question_gn is not None:
        translation.question_gn = update_data.question_gn
    if update_data.answer_gn is not None:
        translation.answer_gn = update_data.answer_gn
    
    db.commit()
    db.refresh(translation)
    
    return translation


@router.delete("/{annotation_id}/translations/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_translation(
    annotation_id: int,
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a translation (only owner or admin can delete)"""
    translation = db.query(AnnotationTranslation).filter(
        AnnotationTranslation.id == translation_id
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found",
        )
    
    # Check permission
    is_owner = translation.user_id == current_user.id
    is_admin = current_user.role == "admin" or current_user.is_superuser
    
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this translation",
        )
    
    db.delete(translation)
    db.commit()
    
    # Update annotation's 'translated' flag
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if annotation:
        translation_count = db.query(func.count(AnnotationTranslation.id)).filter(
            AnnotationTranslation.annotation_id == annotation_id
        ).scalar() or 0
        
        annotation.translated = (translation_count >= 3)
        db.commit()


@router.post("/translations/bulk", response_model=TranslationBulkCreateResponse)
async def bulk_create_translations(
    request: TranslationBulkCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Bulk create translations (admin only)
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform bulk translation operations",
        )
    
    created_count = 0
    skipped_count = 0
    
    for trans_data in request.translations:
        # Check if already exists
        existing = db.query(AnnotationTranslation).filter(
            and_(
                AnnotationTranslation.annotation_id == trans_data.annotation_id,
                AnnotationTranslation.user_id == trans_data.user_id,
            )
        ).first()
        
        if not existing:
            translation = AnnotationTranslation(
                annotation_id=trans_data.annotation_id,
                user_id=trans_data.user_id,
                question_gn=trans_data.question_gn,
                answer_gn=trans_data.answer_gn,
            )
            db.add(translation)
            created_count += 1
        else:
            skipped_count += 1
    
    db.commit()
    
    # Update all affected annotations' 'translated' flags
    annotation_ids = set(t.annotation_id for t in request.translations)
    for ann_id in annotation_ids:
        annotation = db.query(Annotation).filter(Annotation.id == ann_id).first()
        if annotation:
            translation_count = db.query(func.count(AnnotationTranslation.id)).filter(
                AnnotationTranslation.annotation_id == ann_id
            ).scalar() or 0
            annotation.translated = (translation_count >= 3)
    
    db.commit()
    
    return TranslationBulkCreateResponse(
        created_count=created_count,
        skipped_count=skipped_count,
        message=f"Created {created_count} translations, skipped {skipped_count} duplicates",
    )


# ==================== ANNOTATION LISTING ENDPOINTS ====================

@router.get("/my-assignments", response_model=dict)
async def get_my_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get annotations assigned to the current user (NOT translated yet)
    """
    # Get annotation IDs assigned to this user
    assignment_ids = db.query(AnnotationAssignment.annotation_id).filter(
        AnnotationAssignment.user_id == current_user.id
    ).all()
    print(f"assignment_ids raw: {assignment_ids}")
    annotation_ids = [a[0] for a in assignment_ids]
    print(f"User {current_user.id} assigned annotation IDs: {annotation_ids}")

    # Additional debug: fetch full assignment rows for this user
    full_assignments = db.query(AnnotationAssignment).filter(
        AnnotationAssignment.user_id == current_user.id
    ).all()
    print(f"Full assignment rows for user {current_user.id}: {full_assignments}")

    # For each annotation id, print current counts and assignment details
    for aid in annotation_ids:
        ann = db.query(Annotation).filter(Annotation.id == aid).first()
        if not ann:
            print(f"Annotation id {aid} not found in DB")
            continue
        trans_count = db.query(func.count(AnnotationTranslation.id)).filter(
            AnnotationTranslation.annotation_id == aid
        ).scalar() or 0
        assign_count = db.query(func.count(AnnotationAssignment.id)).filter(
            AnnotationAssignment.annotation_id == aid
        ).scalar() or 0
        print(f"Annotation {aid}: translations={trans_count}, assignments={assign_count}, translated_flag={ann.translated}")
        # list assigned user ids
        assigned_users = [ar.user_id for ar in db.query(AnnotationAssignment).filter(AnnotationAssignment.annotation_id == aid).all()]
        print(f"  assigned_users for {aid}: {assigned_users}")

    if not annotation_ids:
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "has_next": False,
        }

    # Exclude annotations that this user already translated (we want only pending)
    translated_ids = db.query(AnnotationTranslation.annotation_id).filter(
        and_(
            AnnotationTranslation.user_id == current_user.id,
            AnnotationTranslation.annotation_id.in_(annotation_ids),
        )
    ).all()
    translated_ids = [t[0] for t in translated_ids]
    pending_ids = [aid for aid in annotation_ids if aid not in translated_ids]

    if not pending_ids:
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "has_next": False,
        }

    # Get annotations that are assigned to this user and not yet translated by them
    query = db.query(Annotation).filter(
        Annotation.id.in_(pending_ids)
    ).order_by(Annotation.id.asc())
    print(f"Query for assigned annotations: {query}")
    
    total = query.count()
    annotation_rows = query.offset(skip).limit(limit).all()
    print(f"Query returned total={total}, rows={len(annotation_rows)}")
    
    # Convert to dict for proper JSON serialization
    items = []
    for ann in annotation_rows:
        suggestion_count = len(ann.suggestions) if getattr(ann, 'suggestions', None) is not None else 0
        validation_count = len(ann.validations) if getattr(ann, 'validations', None) is not None else 0
        user_has_suggested = any(s.user_id == current_user.id for s in (ann.suggestions or []))
        user_has_validated = any(v.user_id == current_user.id for v in (ann.validations or []))
        assigned_user_ids = [a.user_id for a in (ann.assignments or [])]
        assigned_to_user_id = current_user.id if current_user.id in assigned_user_ids else (assigned_user_ids[0] if assigned_user_ids else None)

        items.append({
            "id": ann.id,
            "question_es": ann.question_es,
            "answer_es": ann.answer_es,
            "answer_number": ann.answer_number,
            "equation_solution": ann.equation_solution,
            "source": ann.source,
            "suggestion_count": suggestion_count,
            "validation_count": validation_count,
            "user_has_suggested": user_has_suggested,
            "user_has_validated": user_has_validated,
            "assigned_to_user_id": assigned_to_user_id,
            "created_at": ann.created_at.isoformat() if ann.created_at else None,
            "updated_at": ann.updated_at.isoformat() if ann.updated_at else None,
        })
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": (skip + limit) < total,
    }


@router.get("/my-translations", response_model=dict)
async def get_my_translations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get annotations that the current user has translated
    """
    query = db.query(Annotation).filter(
        db.query(AnnotationTranslation).filter(
            and_(
                AnnotationTranslation.annotation_id == Annotation.id,
                AnnotationTranslation.user_id == current_user.id,
            )
        ).exists()
    )
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": (skip + limit) < total,
    }

@router.get("/weekly-user-activity", response_model=dict)
async def get_weekly_user_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Obtiene asignaciones y traducciones por usuario de la semana actual.
    Semana: lunes 00:00 hasta domingo 23:59:59.
    Ajusta la hora del servidor restando 3 horas.
    """
    query = text("""
        WITH week_range AS (
            SELECT
                date_trunc('week', NOW() - INTERVAL '3 hours') AS week_start,
                date_trunc('week', NOW() - INTERVAL '3 hours') + INTERVAL '7 days' AS week_end
        ),
        assignment_stats AS (
            SELECT
                aa.user_id,
                COUNT(*) AS asignaciones_semana
            FROM annotation_assignments aa
            CROSS JOIN week_range wr
            WHERE (aa.assigned_at - INTERVAL '3 hours') >= wr.week_start
              AND (aa.assigned_at - INTERVAL '3 hours') < wr.week_end
            GROUP BY aa.user_id
        ),
        translation_stats AS (
            SELECT
                at.user_id,
                COUNT(*) AS traducciones_semana
            FROM annotation_translations at
            CROSS JOIN week_range wr
            WHERE (at.created_at - INTERVAL '3 hours') >= wr.week_start
              AND (at.created_at - INTERVAL '3 hours') < wr.week_end
            GROUP BY at.user_id
        )
        SELECT
            u.id AS user_id,
            u.nombre_completo,
            u.email,
            COALESCE(a.asignaciones_semana, 0) AS asignaciones_semana,
            COALESCE(t.traducciones_semana, 0) AS traducciones_semana,
            wr.week_start::date AS week_start,
            (wr.week_end::date - 1) AS week_end
        FROM users u
        CROSS JOIN week_range wr
        LEFT JOIN assignment_stats a ON a.user_id = u.id
        LEFT JOIN translation_stats t ON t.user_id = u.id
        WHERE COALESCE(a.asignaciones_semana, 0) > 0
           OR COALESCE(t.traducciones_semana, 0) > 0
        ORDER BY
            COALESCE(t.traducciones_semana, 0) DESC,
            COALESCE(a.asignaciones_semana, 0) DESC,
            u.nombre_completo ASC;
    """)

    rows = db.execute(query).fetchall()

    if not rows:
        return {
            "week_start": None,
            "week_end": None,
            "items": [],
            "total": 0,
        }

    return {
        "week_start": rows[0].week_start.isoformat(),
        "week_end": rows[0].week_end.isoformat(),
        "items": [
            {
                "user_id": row.user_id,
                "nombre_completo": row.nombre_completo,
                "email": row.email,
                "asignaciones_semana": row.asignaciones_semana,
                "traducciones_semana": row.traducciones_semana,
                "actividad_total": row.asignaciones_semana + row.traducciones_semana,
            }
            for row in rows
        ],
        "total": len(rows),
    }