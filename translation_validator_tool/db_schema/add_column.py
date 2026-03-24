#!/usr/bin/env python3
"""
Script para agregar la columna translated a la tabla annotations usando psycopg2.
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Obtener DATABASE_URL
db_url = "postgresql://postgres:1234@localhost:5432/translation_validator"

if not db_url:
    print("❌ Error: DATABASE_URL no está configurada en .env")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2 import sql
    
    # Parsear la URL de conexión
    # postgresql+psycopg://user:password@host:port/dbname
    db_url_clean = db_url.replace('postgresql+psycopg://', '').replace('postgresql://', '')
    
    parts = db_url_clean.split('@')
    credentials = parts[0].split(':')
    host_db = parts[1].split('/')
    
    user = credentials[0]
    password = credentials[1]
    host_port = host_db[0].split(':')
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    dbname = host_db[1]
    
    print(f"🔄 Conectando a PostgreSQL: {host}:{port}/{dbname}...")
    
    # Conectar
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=dbname,
        user=user,
        password=password
    )
    
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
