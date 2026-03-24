"""
Endpoints for managing annotations (question-answer pairs with translations).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.database import get_db
from app.models.user import User
from app.models.annotation import Annotation
from app.services.excel_loader import get_excel_sheets, load_annotations_from_excel_bytes
from app.models.annotation_validation import AnnotationValidation
from app.models.annotation_suggestion import AnnotationSuggestion
from app.schemas.annotation import (
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse,
    AnnotationWithStats,
    AnnotationValidationCreate,
    AnnotationSuggestionCreate,
    AnnotationAssignCreate,
)
from app.api.deps import get_current_active_user

router = APIRouter()


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
    - Translators see only annotations assigned to them that haven't been translated yet
    Returns paginated results with total count.
    """
    query = db.query(Annotation)
    
    # Translators only see annotations assigned to them AND not yet translated
    if current_user.role == "traductor":
        query = query.filter(
            and_(
                Annotation.assigned_to_user_id == current_user.id,
                Annotation.translated == False
            )
        )
    
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
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                **AnnotationResponse.model_validate(a).model_dump(),
                "validation_count": len(a.validations),
                "suggestion_count": len(a.suggestions),
            }
            for a in items
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": (skip + limit) < total,
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
    
    user_suggested = db.query(AnnotationSuggestion).filter(
        AnnotationSuggestion.annotation_id == annotation_id,
        AnnotationSuggestion.user_id == current_user.id,
    ).first() is not None
    
    result = AnnotationResponse.model_validate(annotation).model_dump()
    result.update({
        "validation_count": len(annotation.validations),
        "suggestion_count": len(annotation.suggestions),
        "user_has_validated": user_validated,
        "user_has_suggested": user_suggested,
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


@router.post("/{annotation_id}/suggest", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_suggestion(
    annotation_id: int,
    suggestion_data: AnnotationSuggestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Submit a translation suggestion for an annotation.
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    # Create suggestion record
    suggestion = AnnotationSuggestion(
        annotation_id=annotation_id,
        user_id=current_user.id,
        part_type=suggestion_data.part_type,
        suggested_question_gn=suggestion_data.suggested_question_gn,
        suggested_answer_gn=suggestion_data.suggested_answer_gn,
        reason=suggestion_data.reason,
    )
    
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    
    return {
        "id": suggestion.id,
        "annotation_id": annotation_id,
        "user_id": current_user.id,
        "part_type": suggestion.part_type,
        "suggested_question_gn": suggestion.suggested_question_gn,
        "suggested_answer_gn": suggestion.suggested_answer_gn,
        "reason": suggestion.reason,
        "created_at": suggestion.created_at,
    }


@router.get("/stats", response_model=dict)
async def get_annotation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get statistics about annotations."""
    total_annotations = db.query(func.count(Annotation.id)).scalar() or 0
    total_validations = db.query(func.count(AnnotationValidation.id)).scalar() or 0
    total_suggestions = db.query(func.count(AnnotationSuggestion.id)).scalar() or 0
    
    annotated_with_guarani = db.query(func.count(Annotation.id)).filter(
        Annotation.answer_gn.isnot(None),
        Annotation.question_gn.isnot(None)
    ).scalar() or 0
    
    return {
        "total_annotations": total_annotations,
        "total_validations": total_validations,
        "total_suggestions": total_suggestions,
        "annotated_with_guarani": annotated_with_guarani,
        "pending_translation": total_annotations - annotated_with_guarani,
    }


@router.put("/{annotation_id}/assign", response_model=AnnotationResponse)
async def assign_annotation(
    annotation_id: int,
    assign_data: AnnotationAssignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Assign an annotation to a translator.
    Only admins can assign annotations.
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign annotations",
        )
    
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    
    # If assigned_to_user_id is provided, verify the user exists and is a translator
    if assign_data.assigned_to_user_id is not None:
        user = db.query(User).filter(User.id == assign_data.assigned_to_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if user.role != "traductor":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be a translator (role='traductor')",
            )
    
    annotation.assigned_to_user_id = assign_data.assigned_to_user_id
    db.commit()
    db.refresh(annotation)
    
    return AnnotationResponse.model_validate(annotation)


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

