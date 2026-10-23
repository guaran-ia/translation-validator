#!/usr/bin/env python3
"""
Script para agregar la columna translated a la tabla annotations usando psycopg2.
"""
import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).resolve().parents[1] / "api" / ".env"
load_dotenv(env_path)

# Obtener DATABASE_URL
db_url = os.getenv("DATABASE_URL", "").strip()

if not db_url:
    print("❌ Error: DATABASE_URL no está configurada en .env")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2 import sql
    
    # psycopg2 handles escaped credentials, ports and query parameters.
    database_url = re.sub(r"^postgresql\+[^:]+://", "postgresql://", db_url)
    print("🔄 Conectando a PostgreSQL...")
    conn = psycopg2.connect(database_url)

    cursor = conn.cursor()
    
    # Verificar si la columna ya existe
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'annotations' AND column_name = 'translated'
    """)
    
    if cursor.fetchone():
        print("✓ La columna 'translated' ya existe")
    else:
        print("➕ Agregando columna 'translated' a la tabla 'annotations'...")
        cursor.execute("""
            ALTER TABLE annotations 
            ADD COLUMN translated BOOLEAN NOT NULL DEFAULT FALSE
        """)
        conn.commit()
        print("✓ Columna 'translated' agregada exitosamente")
    
    cursor.close()
    conn.close()
    print("✓ Conexión cerrada")
    print("✅ Base de datos actualizada correctamente")
    
except ImportError:
    print("❌ Error: psycopg2 no está instalado")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
