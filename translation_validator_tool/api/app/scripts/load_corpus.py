"""
Script para cargar datos del corpus jojajovai a la base de datos.
Uso: python -m app.scripts.load_corpus --file path/to/corpus.csv
"""
import sys
import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import tuple_
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

        # Allow common alias column names and normalize to expected names
        # e.g. 'gn' -> 'guarani', 'es' -> 'spanish'
        col_map = {}
        if 'gn' in df.columns and 'guarani' not in df.columns:
            col_map['gn'] = 'guarani'
        if 'es' in df.columns and 'spanish' not in df.columns:
            col_map['es'] = 'spanish'
        if 'gn_text' in df.columns and 'guarani' not in df.columns:
            col_map['gn_text'] = 'guarani'
        if 'es_text' in df.columns and 'spanish' not in df.columns:
            col_map['es_text'] = 'spanish'

        if col_map:
            df = df.rename(columns=col_map)
            print(f"Note: normalized columns: {col_map}")
        
        # Validate required columns
        required_columns = ['guarani', 'spanish']
        if not all(col in df.columns for col in required_columns):
            print(f"❌ CSV must have columns: {required_columns}")
            print(f"   Found columns: {list(df.columns)}")
            return
        
        # Add source column if not present
        if 'source' not in df.columns:
            df['source'] = 'jojajovai'
        
        # Normalize values and drop empty rows
        df = df.dropna(subset=['guarani', 'spanish'])
        df['guarani'] = df['guarani'].astype(str).str.strip()
        df['spanish'] = df['spanish'].astype(str).str.strip()
        if 'source' not in df.columns:
            df['source'] = 'jojajovai'
        else:
            df['source'] = df['source'].fillna('jojajovai').astype(str).str.strip()

        # Deduplicate CSV by (guarani, spanish)
        dedupe_df = df[['guarani', 'spanish', 'source']].drop_duplicates(subset=['guarani', 'spanish'])
        pairs = list(zip(dedupe_df['guarani'], dedupe_df['spanish']))

        total_pairs = len(pairs)
        if total_pairs == 0:
            print("No valid rows to load after normalization.")
            return

        # Find existing translations in DB in chunks to avoid huge IN lists
        existing = set()
        CHUNK = 1000
        for i in range(0, total_pairs, CHUNK):
            chunk_pairs = pairs[i:i+CHUNK]
            q = db.query(Translation.guarani_text, Translation.spanish_text).filter(
                tuple_(Translation.guarani_text, Translation.spanish_text).in_(chunk_pairs)
            ).all()
            for row_pair in q:
                existing.add((row_pair[0], row_pair[1]))

        # Prepare new translations (those not in existing)
        to_add = []
        for g, s, src in zip(dedupe_df['guarani'], dedupe_df['spanish'], dedupe_df['source']):
            if (g, s) not in existing:
                to_add.append(Translation(guarani_text=g, spanish_text=s, source=src))

        # Bulk insert in chunks
        added = 0
        BATCH = 500
        for i in range(0, len(to_add), BATCH):
            batch = to_add[i:i+BATCH]
            db.add_all(batch)
            try:
                db.commit()
            except Exception as e:
                print(f"❌ Error committing batch: {e}")
                db.rollback()
                raise
            added += len(batch)

        skipped = total_pairs - len(to_add)
        print(f"✅ Successfully loaded {added} new translations")
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