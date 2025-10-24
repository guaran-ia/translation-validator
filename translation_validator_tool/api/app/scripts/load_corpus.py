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

        # direction aliases
        if 'dir' in df.columns and 'direction' not in df.columns:
            col_map['dir'] = 'direction'
        if 'lang_dir' in df.columns and 'direction' not in df.columns:
            col_map['lang_dir'] = 'direction'

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
        # Add default direction if not present
        if 'direction' not in df.columns:
            df['direction'] = 'sp-gn'
        
        # Normalize values and drop empty rows
        df = df.dropna(subset=['guarani', 'spanish'])
        df['guarani'] = df['guarani'].astype(str).str.strip()
        df['spanish'] = df['spanish'].astype(str).str.strip()
        if 'source' not in df.columns:
            df['source'] = 'jojajovai'
        else:
            df['source'] = df['source'].fillna('jojajovai').astype(str).str.strip()

        # Deduplicate CSV by (guarani, spanish)
        dedupe_df = df[['guarani', 'spanish', 'source', 'direction']].drop_duplicates(subset=['guarani', 'spanish'])
        pairs = list(zip(dedupe_df['guarani'], dedupe_df['spanish']))

        total_pairs = len(pairs)
        if total_pairs == 0:
            print("No valid rows to load after normalization.")
            return

        # We'll create paired records: for each (guarani, spanish) create two translations
        # (original: sp-gn) and (inverse: gn-sp) and link them via pair_id.
        added = 0
        for g, s, src, dirv in zip(dedupe_df['guarani'], dedupe_df['spanish'], dedupe_df['source'], dedupe_df['direction']):
            # Determine inverse direction
            inverse_dir = 'gn-sp' if dirv == 'sp-gn' else 'sp-gn'

            # Check if records exist for the same text pair but with specific directions
            exists_main = db.query(Translation).filter(
                Translation.guarani_text == g,
                Translation.spanish_text == s,
                Translation.direction == dirv
            ).first()
            exists_inverse = db.query(Translation).filter(
                Translation.guarani_text == g,
                Translation.spanish_text == s,
                Translation.direction == inverse_dir
            ).first()

            if exists_main and exists_inverse:
                # Both sides exist; ensure pair_id set both ways if missing
                if not exists_main.pair_id and exists_inverse.id:
                    exists_main.pair_id = exists_inverse.id
                if not exists_inverse.pair_id and exists_main.id:
                    exists_inverse.pair_id = exists_main.id
                db.add_all([exists_main, exists_inverse])
                db.commit()
                continue

            if exists_main or exists_inverse:
                # One side exists; create the missing counterpart and link
                try:
                    if exists_main:
                        # First check if an incorrectly-swapped inverse exists (guarani_text==s and spanish_text==g)
                        swapped_inverse = db.query(Translation).filter(
                            Translation.guarani_text == s,
                            Translation.spanish_text == g,
                            Translation.direction == inverse_dir
                        ).first()
                        if swapped_inverse:
                            # Repair swapped fields so both records store the same pair and set pair links
                            swapped_inverse.guarani_text = g
                            swapped_inverse.spanish_text = s
                            swapped_inverse.pair_id = exists_main.id
                            exists_main.pair_id = swapped_inverse.id
                            db.add_all([swapped_inverse, exists_main])
                            db.commit()
                            added += 1
                        else:
                            # create inverse with same texts but inverse direction
                            inv = Translation(
                                guarani_text=g,
                                spanish_text=s,
                                source=src,
                                direction=inverse_dir,
                                is_original=False,
                                pair_id=exists_main.id
                            )
                            db.add(inv)
                            db.flush()
                            exists_main.pair_id = inv.id
                            db.add(exists_main)
                            db.commit()
                            added += 1
                    else:
                        # exists_inverse exists -> create main/original
                        # But first check if an inverse was stored swapped (guarani_text==s and spanish_text==g) with dir==inverse_dir
                        swapped_main = db.query(Translation).filter(
                            Translation.guarani_text == s,
                            Translation.spanish_text == g,
                            Translation.direction == dirv
                        ).first()
                        if swapped_main:
                            # Repair swapped_main to correct fields and link
                            swapped_main.guarani_text = g
                            swapped_main.spanish_text = s
                            swapped_main.pair_id = exists_inverse.id
                            exists_inverse.pair_id = swapped_main.id
                            db.add_all([swapped_main, exists_inverse])
                            db.commit()
                            added += 1
                        else:
                            org = Translation(
                                guarani_text=g,
                                spanish_text=s,
                                source=src,
                                direction=dirv,
                                is_original=True,
                                pair_id=exists_inverse.id
                            )
                            db.add(org)
                            db.flush()
                            exists_inverse.pair_id = org.id
                            db.add(exists_inverse)
                            db.commit()
                            added += 1
                except Exception as e:
                    print(f"❌ Error creating pair for ({g},{s}): {e}")
                    db.rollback()
                continue

            # Neither side exists: create main (original) then inverse and link
            try:
                org = Translation(
                    guarani_text=g,
                    spanish_text=s,
                    source=src,
                    direction=dirv,
                    is_original=True
                )
                db.add(org)
                db.flush()  # get org.id

                inv = Translation(
                    guarani_text=g,
                    spanish_text=s,
                    source=src,
                    direction=inverse_dir,
                    is_original=False,
                    pair_id=org.id
                )
                db.add(inv)
                db.flush()  # get inv.id

                org.pair_id = inv.id
                db.add(org)

                db.commit()
                added += 2
            except Exception as e:
                print(f"❌ Error inserting pair ({g},{s}): {e}")
                db.rollback()
                raise

        print(f"✅ Successfully created/updated {added} translations (pairs handled)")
        
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