#!/usr/bin/env python3
"""
Script para aplicar la migración de anotaciones múltiples
Uso: python run_migration.py
"""
import os
import sys
import subprocess
from pathlib import Path

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.absolute()
ALEMBIC_DIR = SCRIPT_DIR / "alembic"
API_DIR = SCRIPT_DIR.parent / "api"

def main():
    """Run the migration"""
    print("=" * 80)
    print("APPLYING ALEMBIC MIGRATION: Multi-user Annotation Support")
    print("=" * 80)
    
    # Change to the db_schema directory
    os.chdir(SCRIPT_DIR)
    
    # Add API directory to path so alembic can import app modules
    sys.path.insert(0, str(API_DIR))
    
    # Run alembic upgrade
    try:
        print("\n[1/2] Running Alembic upgrade head...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=str(SCRIPT_DIR),
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✅ Migration applied successfully!")
            print("\n[2/2] Verifying migration...")
            
            # List applied migrations
            subprocess.run(
                ["alembic", "current"],
                cwd=str(SCRIPT_DIR)
            )
            
            print("\n" + "=" * 80)
            print("MIGRATION COMPLETE")
            print("=" * 80)
            print("\n📝 Changes applied:")
            print("   ✅ Created annotation_assignments table (many-to-many)")
            print("   ✅ Created annotation_translations table (one-to-many)")
            print("   ✅ Migrated existing data to new tables")
            print("   ✅ Dropped old columns: assigned_to_user_id, question_gn, answer_gn")
            print("   ✅ Updated 'translated' flag based on translation count")
            print("\n🔄 Next steps:")
            print("   1. Update API endpoints to use new schema")
            print("   2. Update frontend components (TranslatorAnnotationsPage, AdminAnnotations)")
            print("   3. Test the new multi-user annotation workflow")
            return 0
        else:
            print("\n❌ Migration failed!")
            return 1
            
    except FileNotFoundError:
        print("\n❌ Error: 'alembic' command not found")
        print("   Make sure you have alembic installed: pip install alembic")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
