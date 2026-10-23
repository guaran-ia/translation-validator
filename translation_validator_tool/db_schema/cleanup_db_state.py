#!/usr/bin/env python3
"""
Script directo para limpiar estado de BD e intentar migración
Sin usar Alembic, usando SQL directo
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.absolute()
API_DIR = SCRIPT_DIR.parent / "api"

def cleanup_and_reset():
    """Limpiar y resetear el estado de migración"""
    print("=" * 80)
    print("DATABASE CLEANUP AND RESET")
    print("=" * 80)
    
    try:
        # Cargar configuración
        sys.path.insert(0, str(API_DIR))
        from app.config import settings
        
        # Conectar a la BD
        print("\n[1] Connecting to database...")
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.begin() as conn:
            # Verificar tabla alembic_version
            print("[2] Checking alembic_version table...")
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'alembic_version'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                current_version = result.fetchone()
                
                if current_version:
                    current_version = current_version[0]
                    print(f"    Current version: {current_version}")
                    print(f"    Version length: {len(current_version)}")
                    
                    # Limpiar
                    print("[3] Cleaning up migration state...")
                    conn.execute(text("DELETE FROM alembic_version"))
                    print("    ✅ Deleted old migration record")
            else:
                print("    ℹ️  Table doesn't exist, will be created")
            
            # Verificar si las tablas nuevas existen (y eliminarlas si es necesario para rollback)
            print("[4] Checking for incomplete migration artifacts...")
            for table in ['annotation_assignments', 'annotation_translations']:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    )
                """))
                if result.scalar():
                    print(f"    ⚠️  Found table {table}, will be replaced by migration")
            
            print("\n✅ Cleanup complete - Database ready for migration")
            return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nManual cleanup needed:")
        print("1. Connect to PostgreSQL")
        print("2. Run: DELETE FROM alembic_version;")
        print("3. Run: INSERT INTO alembic_version (version_num) VALUES ('20260324100000');")
        print("4. Run: alembic upgrade head")
        return False


if __name__ == "__main__":
    success = cleanup_and_reset()
    sys.exit(0 if success else 1)
