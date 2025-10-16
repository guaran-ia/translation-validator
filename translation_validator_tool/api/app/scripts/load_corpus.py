"""
Script para cargar datos del corpus jojajovai a la base de datos.
Uso: python -m app.scripts.load_corpus --file path/to/corpus.csv
"""
import sys
import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.translation import Translation
from app.models import user, validation, suggestion  # Import to ensure tables are created
from app.database import Base


def load_corpus_from_csv(file_path: str):
    """
    Load corpus from CSV file.
    Expected CSV format:
    guarani,spanish,source
    """
    db = SessionLocal()
    
    try:
        print(f"Loading corpus from {file_path}...")
        
        # Read CSV file
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return
        
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_columns = ['guarani', 'spanish']
        if not all(col in df.columns for col in required_columns):
            print(f"❌ CSV must have columns: {required_columns}")
            print(f"   Found columns: {list(df.columns)}")
            return
        
        # Add source column if not present
        if 'source' not in df.columns:
            df['source'] = 'jojajovai'
        
        count = 0
        skipped = 0
        
        for _, row in df.iterrows():
            # Skip rows with empty text
            if pd.isna(row['guarani']) or pd.isna(row['spanish']):
                skipped += 1
                continue
            
            # Check if translation already exists
            exists = db.query(Translation).filter(
                Translation.guarani_text == str(row['guarani']).strip(),
                Translation.spanish_text == str(row['spanish']).strip()
            ).first()
            
            if not exists:
                translation = Translation(
                    guarani_text=str(row['guarani']).strip(),
                    spanish_text=str(row['spanish']).strip(),
                    source=str(row.get('source', 'jojajovai')).strip()
                )
                db.add(translation)
                count += 1
            else:
                skipped += 1
        
        db.commit()
        print(f"✅ Successfully loaded {count} new translations")
        print(f"📋 Skipped {skipped} duplicates or empty entries")
        
    except Exception as e:
        print(f"❌ Error loading corpus: {e}")
        db.rollback()
    finally:
        db.close()


def load_sample_data():
    """Load some sample translation data for testing."""
    db = SessionLocal()
    
    sample_translations = [
        {
            "guarani_text": "Mba'éichapa reiko?",
            "spanish_text": "¿Cómo estás?",
            "source": "sample"
        },
        {
            "guarani_text": "Che aipota che angirũ.",
            "spanish_text": "Quiero a mi amigo.",
            "source": "sample"
        },
        {
            "guarani_text": "Araka'eve ko'ã ára oĩ haku.",
            "spanish_text": "Ahora estos días hace calor.",
            "source": "sample"
        },
        {
            "guarani_text": "Pe tenda porã heta ko'ápe.",
            "spanish_text": "Hay muchos lugares hermosos aquí.",
            "source": "sample"
        },
        {
            "guarani_text": "Che ahayhu che óga.",
            "spanish_text": "Amo mi casa.",
            "source": "sample"
        }
    ]
    
    try:
        count = 0
        for translation_data in sample_translations:
            # Check if already exists
            exists = db.query(Translation).filter(
                Translation.guarani_text == translation_data["guarani_text"],
                Translation.spanish_text == translation_data["spanish_text"]
            ).first()
            
            if not exists:
                translation = Translation(**translation_data)
                db.add(translation)
                count += 1
        
        db.commit()
        print(f"✅ Loaded {count} sample translations")
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Load translation corpus data")
    parser.add_argument("--file", type=str, help="Path to CSV file to load")
    parser.add_argument("--sample", action="store_true", help="Load sample data for testing")
    
    args = parser.parse_args()
    
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    if args.sample:
        load_sample_data()
    elif args.file:
        load_corpus_from_csv(args.file)
    else:
        print("Please provide either --file or --sample option")
        parser.print_help()


if __name__ == "__main__":
    main()