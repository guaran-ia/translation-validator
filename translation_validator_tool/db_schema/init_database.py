#!/usr/bin/env python3
"""
Script independiente para inicializar la base de datos.
Uso: 
  python init_database.py          # Inicializar BD completa
  python init_database.py reset    # Resetear BD completa  
  python init_database.py drop     # Eliminar todas las tablas
  python init_database.py test     # Probar conexión
"""
import sys
import os
from pathlib import Path

# Add API directory to Python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

try:
    from init_db import initialize_database, reset_database, drop_all_tables, test_database_connection
except ImportError:
    print("❌ Error importing database functions")
    sys.exit(1)

import logging

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("🗄️  TRANSLATION VALIDATOR - DATABASE INITIALIZATION")
    print("=" * 60)
    
    command = sys.argv[1] if len(sys.argv) > 1 else "init"
    
    try:
        if command == "init":
            print("🚀 Initializing database...")
            initialize_database()
            print("\n📋 Next steps:")
            print("1. Start API: cd ../api && uvicorn app.main:app --reload")
            print("2. Login with: username=admin, password=4dm!n$Pass")
            print("3. Change admin password immediately!")
            
        elif command == "reset":
            print("🔄 Resetting database...")
            reset_database()
            print("✅ Database reset completed!")
            
        elif command == "drop":
            print("⚠️  Dropping all tables...")
            drop_all_tables()
            print("✅ All tables dropped!")
            
        elif command == "test":
            print("🔍 Testing database connection...")
            if test_database_connection():
                print("✅ Connection successful!")
            else:
                print("❌ Connection failed!")
                sys.exit(1)
                
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: init, reset, drop, test")
            sys.exit(1)
            
        print("=" * 60)
        print("🎉 Operation completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print("=" * 60)
        print("💥 Operation failed!")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()