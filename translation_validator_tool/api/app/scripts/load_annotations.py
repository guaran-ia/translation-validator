"""
Script para cargar anotaciones (question-answer pairs) desde un archivo Excel.
Uso: python -m app.scripts.load_annotations
     python -m app.scripts.load_annotations --file /path/to/custom/file.xlsx

Por defecto busca en: ../../data/train_mgsm_es_to_gn.xlsx
"""
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional

try:
    import openpyxl
except ImportError:
    print("❌ openpyxl no está instalado. Instálalo con: pip install openpyxl")
    sys.exit(1)

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.annotation import Annotation
from app.models import user, validation, suggestion, annotation_validation, annotation_suggestion  # Import to ensure tables are created
from app.database import Base


def load_annotations_from_excel(file_path: str):
    """
    Load annotations from Excel file.
    Expected Excel format:
    - Sheet name: 'train_mgsm_es_to_gn'
    - Column A: ID (optional, not used)
    - Column B: question_es
    - Column D: answer_es
    - Column F: answer_number
    - Column G: equation_solution
    - Data starts from row 2
    """
    db = SessionLocal()
    
    try:
        print(f"Loading annotations from {file_path}...")
        
        # Verify file exists
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return
        
        # Load workbook
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
        except Exception as e:
            print(f"❌ Error loading Excel file: {e}")
            return
        
        # Get the specific sheet
        sheet_name = 'train_mgsm_es_to_gn'
        if sheet_name not in workbook.sheetnames:
            print(f"❌ Sheet '{sheet_name}' not found in Excel file")
            print(f"   Available sheets: {workbook.sheetnames}")
            return
        
        sheet = workbook[sheet_name]
        print(f"✅ Found sheet '{sheet_name}'")
        
        # Extract data from columns B, D, F, G starting from row 2
        # Column mapping: A=1, B=2, D=4, F=6, G=7
        annotations_data: List[Dict] = []
        
        row_num = 2
        added_count = 0
        skipped_count = 0
        
        # Iterate through rows until we find an empty row in the first column with data
        while True:
            # Try to read row
            question_es = sheet.cell(row=row_num, column=2).value  # Column B
            answer_es = sheet.cell(row=row_num, column=4).value     # Column D
            answer_number = sheet.cell(row=row_num, column=6).value # Column F
            equation_solution = sheet.cell(row=row_num, column=7).value  # Column G
            
            # Check if row is empty (no question and no answer)
            if not question_es and not answer_es:
                print(f"✓ Reached end of data at row {row_num}")
                break
            
            # Skip rows without required fields
            if not question_es or not answer_es:
                print(f"⚠️  Skipping row {row_num}: missing question_es or answer_es")
                skipped_count += 1
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
                print(f"⚠️  Row {row_num}: answer_number '{answer_number}' is not a valid integer, setting to None")
                answer_number = None
            
            equation_solution = str(equation_solution).strip() if equation_solution else None
            
            # Check for duplicates
            exists = db.query(Annotation).filter(
                Annotation.question_es == question_es,
                Annotation.answer_es == answer_es
            ).first()
            
            if exists:
                print(f"⚠️  Row {row_num}: annotation already exists (question_es, answer_es), skipping")
                skipped_count += 1
                row_num += 1
                continue
            
            # Create annotation record
            try:
                annotation = Annotation(
                    question_es=question_es,
                    question_gn=None,  # No guaraní translation yet
                    answer_es=answer_es,
                    answer_gn=None,  # No guaraní translation yet
                    answer_number=answer_number,
                    equation_solution=equation_solution,
                    source="GuaranIA"
                )
                db.add(annotation)
                db.commit()
                db.refresh(annotation)
                
                print(f"✓ Row {row_num}: Created annotation ID {annotation.id}")
                print(f"   Q: {question_es[:60]}...")
                print(f"   A: {answer_es[:60]}...")
                if equation_solution:
                    print(f"   Equation: {equation_solution}")
                
                added_count += 1
                
            except Exception as e:
                print(f"❌ Error inserting row {row_num}: {e}")
                db.rollback()
                skipped_count += 1
            
            row_num += 1
        
        print(f"\n" + "="*60)
        print(f"✅ Successfully loaded {added_count} annotations")
        print(f"⚠️  Skipped {skipped_count} rows")
        print(f"="*60)
        
    except Exception as e:
        print(f"❌ Error loading annotations: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Load annotations from Excel file")
    parser.add_argument("--file", type=str, default="../../data/data.xlsx", help="Path to Excel file (.xlsx), default: ../../data/train_mgsm_es_to_gn.xlsx")
    
    args = parser.parse_args()
    
    # Create tables
    print("Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)
    
    # Load annotations
    load_annotations_from_excel(args.file)


if __name__ == "__main__":
    main()
