"""
Endpoints for managing annotations (question-answer pairs with translations).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import logging

from app.database import get_db
from app.models.user import User
from app.models.annotation import Annotation
from app.services.excel_loader import get_excel_sheets, load_annotations_from_excel_bytes
from app.models.annotation_validation import AnnotationValidation
from app.schemas.annotation import (
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse,
    AnnotationWithStats,
    AnnotationValidationCreate,
    AnnotationAssignCreate,
)
from app.api.deps import get_current_active_user

router = APIRouter()
# Use the uvicorn error logger so logs are visible in the server output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@router.get("/", response_model=dict)
async def list_annotations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    q: str = Query("", description="Search by question or answer text"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List annotations.
    - Admins see all annotations (or filtered by search)
    - Translators see only annotations that are NOT marked as translated, NOT translated by them, and NOT assigned to them
    Returns paginated results with total count.
    """
    query = db.query(Annotation)
    
    # Translators see ONLY non-translated annotations EXCEPT those they already translated or that are assigned to them
    if current_user.role == "traductor":
        from app.models.annotation_assignment import AnnotationAssignment
        from app.models.annotation_translation import AnnotationTranslation

        # Collect annotation IDs the user has translated
        translated_rows = db.query(AnnotationTranslation.annotation_id).filter(
            AnnotationTranslation.user_id == current_user.id
        ).all()
        translated_ids = {r[0] for r in translated_rows}

        # Collect annotation IDs the user is assigned to
        assigned_rows = db.query(AnnotationAssignment.annotation_id).filter(
            AnnotationAssignment.user_id == current_user.id
        ).all()
        assigned_ids = {r[0] for r in assigned_rows}

        exclude_ids = translated_ids.union(assigned_ids)

        # Base: only not-yet-marked-as-translated annotations
        query = query.filter(Annotation.translated == False)

        # Exclude those the user already interacted with (translated by him OR assigned to him)
        if exclude_ids:
            query = query.filter(~Annotation.id.in_(list(exclude_ids)))
    
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Annotation.question_es.ilike(search_term),
                Annotation.question_gn.ilike(search_term),
                Annotation.answer_es.ilike(search_term),
                Annotation.answer_gn.ilike(search_term),
            )
        )

    # Order by id ascending for consistency
    query = query.order_by(Annotation.id.asc())
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                **AnnotationResponse.model_validate(a).model_dump(),
                "validation_count": len(a.validations),
            }
            for a in items
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": (skip + limit) < total,
    }


@router.get("/stats", response_model=dict)
async def get_annotation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get annotation statistics."""
    total_annotations = db.query(Annotation).count()
    annotated_with_guarani = db.query(Annotation).filter(
        Annotation.question_gn.isnot(None),
        Annotation.answer_gn.isnot(None)
    ).count()
    
    return {
        "total_annotations": total_annotations,
        "annotated_with_guarani": annotated_with_guarani,
        "pending_translation": total_annotations - annotated_with_guarani,
    }


@router.get("/my-assignments", response_model=dict)
async def get_my_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get annotations assigned to the current user.
    Only for translators.
    
    Returns the actual Annotation objects (with all details) that are assigned to the current user.
    No filtering applied - just show what's assigned.
    """
    if current_user.role != "traductor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only translators can view their assignments",
        )

    from app.models.annotation_assignment import AnnotationAssignment

    # Get UNIQUE annotation IDs assigned to the user (use distinct, efficient query)
    assigned_annotation_rows = db.query(AnnotationAssignment.annotation_id).filter(
        AnnotationAssignment.user_id == current_user.id
    ).distinct().all()
    
    logger.debug(f"DEBUG: User ID: {current_user.id}")
    # Fallback: print to stdout so uvicorn always shows the debug info
    print(f"DEBUG: User ID: {current_user.id}")
    logger.debug(f"DEBUG: Raw assignment rows (annotation_id tuples): {assigned_annotation_rows}")
    print(f"DEBUG: Raw assignment rows (annotation_id tuples): {assigned_annotation_rows}")
    logger.debug(f"DEBUG: Number of assignment rows: {len(assigned_annotation_rows)}")
    print(f"DEBUG: Number of assignment rows: {len(assigned_annotation_rows)}")
    # assigned_annotation_rows is a list of 1-tuples (annotation_id,), extract values
    annotation_ids = [row[0] for row in assigned_annotation_rows]
    logger.debug(f"DEBUG: Extracted annotation_ids: {annotation_ids}")
    print(f"DEBUG: Extracted annotation_ids: {annotation_ids}")

    if not annotation_ids:
        logger.warning("DEBUG: No annotation IDs found, returning empty list")
        print("DEBUG: No annotation IDs found, returning empty list")
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "has_next": False,
        }

    # Get the actual annotations
    query = db.query(Annotation).filter(Annotation.id.in_(annotation_ids))
    
    logger.info(f"DEBUG: Query SQL: {query}")
    print(f"DEBUG: Query SQL: {query}")
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    logger.info(f"DEBUG: Total annotations found: {total}")
    print(f"DEBUG: Total annotations found: {total}")
    logger.info(f"DEBUG: Items returned: {len(items)}")
    print(f"DEBUG: Items returned: {len(items)}")
    for item in items:
        logger.info(f"  - Annotation ID {item.id}: {item.question_es[:50] if item.question_es else 'No question'}")
        print(f"  - Annotation ID {item.id}: {item.question_es[:50] if item.question_es else 'No question'}")
    return {
        "items": [
            {
                **AnnotationResponse.model_validate(a).model_dump(),
                "validation_count": len(a.validations),
            }
            for a in items
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": (skip + limit) < total,
    }


@router.get("/my-translations", response_model=dict)
async def get_my_translations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get translations submitted by the current user.
    Only for translators.
    """
    if current_user.role != "traductor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only translators can view their translations",
        )
    
    from app.models.annotation_translation import AnnotationTranslation
    
    translations = db.query(AnnotationTranslation).filter(
        AnnotationTranslation.user_id == current_user.id
    ).all()
    
    return {
        "items": [
            {
                "id": t.id,
                "annotation_id": t.annotation_id,
                "user_id": t.user_id,
                "question_gn": t.question_gn,
                "answer_gn": t.answer_gn,
                "created_at": t.created_at
            }
            for t in translations
        ],
        "total": len(translations)
    }


@router.get("/available-for-translation", response_model=dict)
async def get_available_for_translation(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    random: bool = Query(False, description="If true, return items in random order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    TEMP MODE: Return annotations ordered by smallest ID first (for debugging/QA).
    Previous complex filters are commented out temporarily.
    """
    if current_user.role != "traductor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only translators can view available annotations",
        )

    # --- Reintroduce filters: hide completed, hide annotations assigned to the user, and those the user already translated ---
    from app.models.annotation_assignment import AnnotationAssignment
    from app.models.annotation_translation import AnnotationTranslation

    # IDs the user already translated
    translated_rows = db.query(AnnotationTranslation.annotation_id).filter(
        AnnotationTranslation.user_id == current_user.id
    ).all()
    translated_ids = {r[0] for r in translated_rows}

    # IDs the user is assigned to
    assigned_rows = db.query(AnnotationAssignment.annotation_id).filter(
        AnnotationAssignment.user_id == current_user.id
    ).all()
    assigned_ids = {r[0] for r in assigned_rows}

    exclude_ids = translated_ids.union(assigned_ids)

    # Build query over Annotation with translation counts and filters
    q = db.query(Annotation, func.count(AnnotationTranslation.id).label('translation_count'))
    q = q.outerjoin(AnnotationTranslation, AnnotationTranslation.annotation_id == Annotation.id)
    # Exclude annotations already marked as translated/completed
    q = q.filter(Annotation.translated == False)

    if exclude_ids:
        q = q.filter(~Annotation.id.in_(list(exclude_ids)))

    q = q.group_by(Annotation.id)
    # Only include items with fewer than 3 translations
    q = q.having(func.count(AnnotationTranslation.id) < 3)

    # Ordering: deterministic by id or random if requested
    if random:
        # Use DB random ordering
        try:
            q = q.order_by(func.random())
        except Exception:
            # Fallback to SQL-level random function name for some DBs
            q = q.order_by(func.rand())
    else:
        q = q.order_by(Annotation.id.asc())

    # Derive total using a subquery of matched ids
    ids_subq = q.with_entities(Annotation.id).subquery()
    total = db.query(func.count()).select_from(ids_subq).scalar() or 0

    rows = q.offset(skip).limit(limit).all()

    items = []
    for ann, trans_count in rows:
        item = AnnotationResponse.model_validate(ann).model_dump()
        item.update({
            'translation_count': int(trans_count or 0),
        })
        items.append(item)

    return {
        'items': items,
        'total': total,
        'skip': skip,
        'limit': limit,
        'has_next': (skip + limit) < total,
    }


@router.get("/{annotation_id}", response_model=AnnotationWithStats)
async def get_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific annotation by ID."""
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    user_validated = db.query(AnnotationValidation).filter(
        AnnotationValidation.annotation_id == annotation_id,
        AnnotationValidation.user_id == current_user.id,
    ).first() is not None
    
    result = AnnotationResponse.model_validate(annotation).model_dump()
    result.update({
        "validation_count": len(annotation.validations),
        "user_has_validated": user_validated,
    })
    
    return result


@router.post("/", response_model=AnnotationResponse, status_code=status.HTTP_201_CREATED)
async def create_annotation(
    annotation_data: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new annotation.
    Only admins can create annotations.
    At least one of question_es or answer_es must be provided.
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create annotations",
        )
    
    # Validate that at least one of question_es or answer_es is provided
    if not annotation_data.question_es and not annotation_data.answer_es:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of 'question_es' or 'answer_es' must be provided",
        )
    
    # Create new annotation
    annotation = Annotation(
        question_es=annotation_data.question_es,
        question_gn=annotation_data.question_gn,
        answer_es=annotation_data.answer_es,
        answer_gn=annotation_data.answer_gn,
        answer_number=annotation_data.answer_number,
        equation_solution=annotation_data.equation_solution,
        source=annotation_data.source,
    )
    
    db.add(annotation)
    db.commit()
    db.refresh(annotation)
    
    return AnnotationResponse.model_validate(annotation)


@router.put("/{annotation_id}", response_model=AnnotationResponse)
async def update_annotation(
    annotation_id: int,
    annotation_data: AnnotationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an annotation's translations.
    - Admins can update any annotation
    - Translators can update only annotations assigned to them
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    # Check permissions
    is_admin = current_user.role == "admin" or current_user.is_superuser
    is_assigned_translator = (
        current_user.role == "traductor" and 
        annotation.assigned_to_user_id == current_user.id
    )
    
    if not (is_admin or is_assigned_translator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or the assigned translator can update annotations",
        )
    
    # Update allowed fields
    if annotation_data.question_gn is not None:
        annotation.question_gn = annotation_data.question_gn
    if annotation_data.answer_gn is not None:
        annotation.answer_gn = annotation_data.answer_gn
    
    # Mark as translated if at least one translation is provided (question_gn OR answer_gn)
    annotation.translated = bool(annotation.question_gn or annotation.answer_gn)
    
    db.commit()
    db.refresh(annotation)
    
    return AnnotationResponse.model_validate(annotation)


@router.delete("/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete an annotation.
    Only admins can delete annotations.
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete annotations",
        )
    
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    db.delete(annotation)
    db.commit()


@router.post("/{annotation_id}/validate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_validation(
    annotation_id: int,
    validation_data: AnnotationValidationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Submit validation feedback for an annotation translation.
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    # Create validation record
    validation = AnnotationValidation(
        annotation_id=annotation_id,
        user_id=current_user.id,
        part_type=validation_data.part_type,
        correctness=validation_data.correctness,
        fluency_score=validation_data.fluency_score,
        accuracy_score=validation_data.accuracy_score,
        notes=validation_data.notes,
        category=validation_data.category,
    )
    
    db.add(validation)
    db.commit()
    db.refresh(validation)
    
    return {
        "id": validation.id,
        "annotation_id": annotation_id,
        "user_id": current_user.id,
        "part_type": validation.part_type,
        "correctness": validation.correctness,
        "fluency_score": validation.fluency_score,
        "accuracy_score": validation.accuracy_score,
        "created_at": validation.created_at,
    }


@router.post("/{annotation_id}/assign", response_model=dict)
async def assign_to_me(
    annotation_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Translator self-assigns to an annotation.
    Creates an assignment if not already assigned.
    """
    if current_user.role != "traductor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only translators can self-assign",
        )
    
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only assign to yourself",
        )
    
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    from app.models.annotation_assignment import AnnotationAssignment
    
    # Check if already assigned
    existing = db.query(AnnotationAssignment).filter(
        and_(
            AnnotationAssignment.annotation_id == annotation_id,
            AnnotationAssignment.user_id == current_user.id
        )
    ).first()
    
    if existing:
        return {
            "success": False,
            "message": "Already assigned to this annotation"
        }
    
    # Create new assignment
    assignment = AnnotationAssignment(
        annotation_id=annotation_id,
        user_id=current_user.id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return {
        "success": True,
        "message": "Assigned successfully",
        "assignment": {
            "id": assignment.id,
            "annotation_id": assignment.annotation_id,
            "user_id": assignment.user_id,
            "assigned_at": assignment.assigned_at
        }
    }


@router.post("/upload/sheets")
async def list_excel_sheets(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get list of sheet names from an Excel file.
    Only admins can use this endpoint.
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can upload annotations",
        )
    
    try:
        file_bytes = await file.read()
        sheets = get_excel_sheets(file_bytes)
        return {"sheets": sheets, "filename": file.filename}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading Excel file: {str(e)}",
        )


@router.post("/upload/bulk")
async def bulk_upload_annotations(
    file: UploadFile = File(...),
    sheet: str = Form(..., description="Sheet name to process"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Bulk upload annotations from Excel file.
    Expected columns:
    - Column B: question_es
    - Column D: answer_es
    - Column F: answer_number
    - Column G: equation_solution
    
    Only admins can use this endpoint.
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can upload annotations",
        )
    
    try:
        file_bytes = await file.read()
        result = load_annotations_from_excel_bytes(
            file_bytes=file_bytes,
            sheet_name=sheet,
            db=db,
            skip_duplicates=True
        )
        
        return {
            "success": result["added_count"] > 0 or len(result["errors"]) == 0,
            "filename": file.filename,
            "sheet": sheet,
            "added_count": result["added_count"],
            "skipped_count": result["skipped_count"],
            "errors": result["errors"],
            "details": result["details"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing Excel file: {str(e)}",
        )


@router.get("/{annotation_id}/translations/{user_id}", response_model=dict)
async def get_translation_by_user(
    annotation_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a translation for an annotation by a specific user.
    """
    from app.models.annotation_translation import AnnotationTranslation
    
    translation = db.query(AnnotationTranslation).filter(
        AnnotationTranslation.annotation_id == annotation_id,
        AnnotationTranslation.user_id == user_id
    ).first()
    
    if not translation:
        return {
            "id": None,
            "annotation_id": annotation_id,
            "user_id": user_id,
            "question_gn": None,
            "answer_gn": None,
            "created_at": None
        }
    
    return {
        "id": translation.id,
        "annotation_id": translation.annotation_id,
        "user_id": translation.user_id,
        "question_gn": translation.question_gn,
        "answer_gn": translation.answer_gn,
        "created_at": translation.created_at
    }


