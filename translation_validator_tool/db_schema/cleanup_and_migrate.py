#!/usr/bin/env python3
"""
Script para limpiar y ejecutar la migración de anotaciones múltiples
Uso: python cleanup_and_migrate.py
"""
import os
import sys
import subprocess
from pathlib import Path
from sqlalchemy import create_engine, text

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.absolute()
API_DIR = SCRIPT_DIR.parent / "api"

def cleanup_migration_state():
    """Limpiar estado de migración fallida de la BD"""
    print("\n[Step 0] Cleaning up failed migration state...")
    
    try:
        # Cargar configuración
        sys.path.insert(0, str(API_DIR))
        from app.config import settings
        
        # Conectar a la BD
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Verificar qué versión está registrada
            result = conn.execute(text("SELECT version_num FROM alembic_version;"))
            current_version = result.fetchone()
            
            if current_version:
                current_version = current_version[0]
                print(f"   Current version: {current_version}")
                
                # Si es la versión fallida, limpiar
                if current_version and ('20250101' in str(current_version) or len(str(current_version)) > 32):
                    print(f"   ⚠️  Found failed migration version: {current_version}")
                    print("   Cleaning up...")
                    
                    # Limpiar y establecer a la versión anterior
                    conn.execute(text("DELETE FROM alembic_version;"))
                    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('20260324100000');"))
                    conn.commit()
                    
                    print("   ✅ Migration state cleaned")
                    return True
                else:
                    print(f"   ℹ️  Version is OK: {current_version}")
                    return False
            else:
                print("   ⚠️  No version record found")
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('20260324100000');"))
                conn.commit()
                return True
        
    except ModuleNotFoundError as e:
        print(f"   ⚠️  Cannot import app config: {e}")
        print("   Skipping cleanup - will try migration anyway")
        return False
    except Exception as e:
        print(f"   ⚠️  Error during cleanup: {e}")
        print("   Skipping cleanup - will try migration anyway")
        return False


def run_migration():
    """Ejecutar la migración Alembic"""
    print("\n[Step 1] Running Alembic migration...")
    
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=str(SCRIPT_DIR),
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✅ Migration applied successfully!")
            
            # Verificar
            print("\n[Step 2] Verifying migration...")
            subprocess.run(
                ["alembic", "current"],
                cwd=str(SCRIPT_DIR)
            )
            
            return True
        else:
            print("\n❌ Migration failed!")
            return False
            
    except FileNotFoundError:
        print("\n❌ Error: 'alembic' command not found")
        print("   Make sure you have alembic installed: pip install alembic")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Main execution"""
    print("=" * 80)
    print("MIGRATION: Multi-user Annotation Support (with cleanup)")
    print("=" * 80)
    
    # Change to the db_schema directory
    os.chdir(SCRIPT_DIR)
    
    # Step 0: Cleanup
    cleanup_migration_state()
    
    # Step 1: Run migration
    success = run_migration()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETE")
        print("=" * 80)
        print("\n📝 Changes applied:")
        print("   ✅ Created annotation_assignments table (many-to-many)")
        print("   ✅ Created annotation_translations table (one-to-many)")
        print("   ✅ Migrated existing data to new tables")
        print("   ✅ Dropped old columns: assigned_to_user_id, question_gn, answer_gn")
        print("   ✅ Updated 'translated' flag based on translation count")
        print("\n🔄 Next steps:")
        print("   1. Update API endpoints to use new schema")
        print("   2. Update frontend components")
        print("   3. Test the new multi-user annotation workflow")
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ MIGRATION FAILED")
        print("=" * 80)
        print("\nTroubleshooting:")
        print("   1. Check database connection")
        print("   2. Verify Alembic is installed: pip install alembic")
        print("   3. Check migration file syntax")
        print("   4. Review database logs for errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
