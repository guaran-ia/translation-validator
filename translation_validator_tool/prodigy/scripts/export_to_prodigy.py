"""
Export translations from PostgreSQL database to Prodigy JSONL format.

This script exports translation data from the validator database to a format
compatible with Prodigy annotation tool.

Usage:
    python export_to_prodigy.py --limit 100 --output data/export/translations.jsonl
    python export_to_prodigy.py --direction gn-sp --category guarani_puro
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to path to import from api
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.translation import Translation
from app.models.validation import Validation
from app.config import settings


def create_db_session():
    """Create database session."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def export_translations_to_jsonl(
    output_file: str,
    limit: Optional[int] = None,
    direction: Optional[str] = None,
    category: Optional[str] = None,
    min_validations: int = 0,
    max_validations: Optional[int] = None,
    only_original: bool = False
) -> int:
    """
    Export translations to JSONL format for Prodigy.
    
    Args:
        output_file: Path to output JSONL file
        limit: Maximum number of translations to export
        direction: Filter by direction (gn-sp or sp-gn)
        category: Filter by category (guarani_puro, jopara, jehea)
        min_validations: Minimum number of validations
        max_validations: Maximum number of validations
        only_original: Only export translations where is_original = True
        
    Returns:
        Number of translations exported
    """
    db = create_db_session()
    
    try:
        # Build query
        query = db.query(Translation)
        
        if only_original:
            query = query.filter(Translation.is_original == True)
        
        if direction:
            query = query.filter(Translation.direction == direction)
        
        if category:
            # This would require joining with validations table
            # For now, we'll export all and filter during annotation
            pass
        
        if limit:
            query = query.limit(limit)
        
        translations = query.all()
        
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export to JSONL
        count = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            for trans in translations:
                # Get validation count for this translation
                validation_count = db.query(Validation).filter(
                    Validation.translation_id == trans.id
                ).count()
                
                # Apply validation filters
                if validation_count < min_validations:
                    continue
                if max_validations and validation_count > max_validations:
                    continue
                
                # Create Prodigy-compatible entry
                entry = {
                    "text": trans.guarani_text,
                    "meta": {
                        "translation_id": trans.id,
                        "spanish_text": trans.spanish_text or "",
                        "direction": trans.direction,
                        "source": trans.source,
                        "is_original": trans.is_original,
                        "pair_id": trans.pair_id,
                        "validation_count": validation_count,
                        "created_at": trans.created_at.isoformat() if trans.created_at else None
                    }
                }
                
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                count += 1
        
        print(f"[OK] Exported {count} translations to {output_file}")
        return count
        
    finally:
        db.close()


def export_validation_history(
    output_file: str,
    translation_ids: Optional[List[int]] = None,
    user_id: Optional[int] = None
) -> int:
    """
    Export validation history for analysis.
    
    Args:
        output_file: Path to output JSONL file
        translation_ids: Filter by specific translation IDs
        user_id: Filter by specific user
        
    Returns:
        Number of validations exported
    """
    db = create_db_session()
    
    try:
        query = db.query(Validation).join(Translation)
        
        if translation_ids:
            query = query.filter(Validation.translation_id.in_(translation_ids))
        
        if user_id:
            query = query.filter(Validation.user_id == user_id)
        
        validations = query.all()
        
        # Create output directory
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        count = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            for val in validations:
                entry = {
                    "validation_id": val.id,
                    "translation_id": val.translation_id,
                    "user_id": val.user_id,
                    "correctness": val.correctness,
                    "fluency_score": val.fluency_score,
                    "accuracy_score": val.accuracy_score,
                    "notes": val.notes or "",
                    "category": val.category or "",
                    "direction": val.direction,
                    "suggestion_id": val.suggestion_id,
                    "created_at": val.created_at.isoformat() if val.created_at else None,
                    "guarani_text": val.translation.guarani_text,
                    "spanish_text": val.translation.spanish_text or ""
                }
                
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                count += 1
        
        print(f"[OK] Exported {count} validations to {output_file}")
        return count
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Export translations from PostgreSQL to Prodigy JSONL format"
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/export/translations.jsonl',
        help='Output JSONL file path'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Maximum number of translations to export'
    )
    
    parser.add_argument(
        '--direction', '-d',
        type=str,
        choices=['gn-sp', 'sp-gn'],
        help='Filter by translation direction'
    )
    
    parser.add_argument(
        '--category', '-c',
        type=str,
        choices=['guarani_puro', 'jopara', 'jehea'],
        help='Filter by category (note: may not be set for all translations)'
    )
    
    parser.add_argument(
        '--min-validations',
        type=int,
        default=0,
        help='Minimum number of validations (default: 0)'
    )
    
    parser.add_argument(
        '--max-validations',
        type=int,
        help='Maximum number of validations'
    )
    
    parser.add_argument(
        '--only-original',
        action='store_true',
        help='Only export translations where is_original = True'
    )
    
    parser.add_argument(
        '--export-validations',
        action='store_true',
        help='Also export validation history'
    )
    
    args = parser.parse_args()
    
    # Export translations
    count = export_translations_to_jsonl(
        output_file=args.output,
        limit=args.limit,
        direction=args.direction,
        category=args.category,
        min_validations=args.min_validations,
        max_validations=args.max_validations,
        only_original=args.only_original
    )
    
    # Optionally export validations
    if args.export_validations:
        validation_file = args.output.replace('.jsonl', '_validations.jsonl')
        export_validation_history(validation_file)
    
    print(f"\n[OK] Export complete! {count} translations exported.")
    print(f"[FILE] {args.output}")
    print(f"\n[NEXT STEPS]:")
    print(f"   1. Review the exported data: cat {args.output}")
    print(f"   2. Load into Prodigy: prodigy db-in guarani_dataset {args.output}")
    print(f"   3. Start annotation: prodigy textcat.manual guarani_dataset {args.output} --label CORRECT,INCORRECT")


if __name__ == "__main__":
    main()
