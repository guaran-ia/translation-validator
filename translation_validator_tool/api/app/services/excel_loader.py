"""
Service for loading annotations from Excel files.
"""
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import io

try:
    import openpyxl
except ImportError:
    openpyxl = None

from sqlalchemy.orm import Session
from app.models.annotation import Annotation


def get_excel_sheets(file_bytes: bytes) -> List[str]:
    """
    Get list of sheet names from an Excel file.
    
    Args:
        file_bytes: Excel file as bytes
        
    Returns:
        List of sheet names
        
    Raises:
        ValueError: If file is not a valid Excel file
    """
    if not openpyxl:
        raise ImportError("openpyxl is required for Excel support")
    
    try:
        workbook = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        return workbook.sheetnames
    except Exception as e:
        raise ValueError(f"Invalid Excel file: {str(e)}")


def load_annotations_from_excel_bytes(
    file_bytes: bytes,
    sheet_name: str,
    db: Session,
    skip_duplicates: bool = True
) -> Dict[str, any]:
    """
    Load annotations from Excel file bytes.
    
    Expected Excel format:
    - Column B (2): question_es
    - Column D (4): answer_es
    - Column F (6): answer_number
    - Column G (7): equation_solution
    - Data starts from row 2
    
    Args:
        file_bytes: Excel file as bytes
        sheet_name: Name of the sheet to process
        db: Database session
        skip_duplicates: Whether to skip duplicate entries
        
    Returns:
        Dictionary with:
        - added_count: Number of annotations successfully added
        - skipped_count: Number of rows skipped
        - errors: List of error messages
        - details: List of added annotation details
    """
    if not openpyxl:
        raise ImportError("openpyxl is required for Excel support")
    
    result = {
        "added_count": 0,
        "skipped_count": 0,
        "errors": [],
        "details": []
    }
    
    try:
        # Load workbook
        try:
            workbook = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        except Exception as e:
            result["errors"].append(f"Error loading Excel file: {str(e)}")
            return result
        
        # Check sheet exists
        if sheet_name not in workbook.sheetnames:
            result["errors"].append(
                f"Sheet '{sheet_name}' not found. Available sheets: {', '.join(workbook.sheetnames)}"
            )
            return result
        
        sheet = workbook[sheet_name]
        
        # Extract data from columns B, D, F, G starting from row 2
        row_num = 2
        
        while True:
            # Try to read row
            question_es = sheet.cell(row=row_num, column=2).value  # Column B
            answer_es = sheet.cell(row=row_num, column=4).value     # Column D
            answer_number = sheet.cell(row=row_num, column=6).value # Column F
            equation_solution = sheet.cell(row=row_num, column=7).value  # Column G
            
            # Check if row is empty
            if not question_es and not answer_es:
                break
            
            # Skip rows without at least one field (question_es OR answer_es)
            if not question_es and not answer_es:
                result["skipped_count"] += 1
                row_num += 1
                continue
            
            # Clean up values
            question_es = str(question_es).strip() if question_es else None
            answer_es = str(answer_es).strip() if answer_es else None
            
            # Convert answer_number to int if present
            try:
                if answer_number:
                    answer_number = int(answer_number)
                else:
                    answer_number = None
            except (ValueError, TypeError):
                result["errors"].append(
                    f"Row {row_num}: answer_number '{answer_number}' is not a valid integer"
                )
                answer_number = None
            
            equation_solution = str(equation_solution).strip() if equation_solution else None
            
            # Check for duplicates if skip_duplicates is True
            if skip_duplicates:
                query = db.query(Annotation)
                
                if question_es and answer_es:
                    exists = query.filter(
                        Annotation.question_es == question_es,
                        Annotation.answer_es == answer_es
                    ).first()
                elif question_es:
                    exists = query.filter(Annotation.question_es == question_es).first()
                else:
                    exists = query.filter(Annotation.answer_es == answer_es).first()
                
                if exists:
                    result["skipped_count"] += 1
                    row_num += 1
                    continue
            
            # Create annotation record
            try:
                annotation = Annotation(
                    question_es=question_es,
                    answer_es=answer_es,
                    answer_number=answer_number,
                    equation_solution=equation_solution,
                    source="GuaranIA"
                )
                db.add(annotation)
                db.commit()
                db.refresh(annotation)
                
                result["added_count"] += 1
                result["details"].append({
                    "id": annotation.id,
                    "question_es": question_es[:60] + "..." if question_es and len(question_es) > 60 else question_es,
                    "answer_es": answer_es[:60] + "..." if answer_es and len(answer_es) > 60 else answer_es,
                    "equation_solution": equation_solution
                })
                
            except Exception as e:
                result["errors"].append(f"Row {row_num}: {str(e)}")
                result["skipped_count"] += 1
                db.rollback()
            
            row_num += 1
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Error processing file: {str(e)}")
        db.rollback()
        return result
