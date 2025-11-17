"""
Sincronizar anotaciones de Prodigy de vuelta a PostgreSQL
Este script importa las anotaciones realizadas en Prodigy y las guarda en la base de datos
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.translation import Translation
from app.models.validation import Validation
from app.models.user import User
from app.config import settings


def create_db_session():
    """Create database session."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def sync_translation_validations(
    dataset_name: str,
    user_id: int,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Sincronizar validaciones de traducciones desde Prodigy a PostgreSQL
    
    Args:
        dataset_name: Nombre del dataset en Prodigy (ej: 'guarani_validation')
        user_id: ID del usuario que realizó las anotaciones
        dry_run: Si es True, solo muestra lo que haría sin guardar
        
    Returns:
        Dict con estadísticas de sincronización
    """
    import subprocess
    
    # Exportar anotaciones de Prodigy
    print(f"📤 Exportando anotaciones de Prodigy dataset '{dataset_name}'...")
    result = subprocess.run(
        ["python", "-m", "prodigy", "db-out", dataset_name],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Error exportando: {result.stderr}")
        return {"error": result.stderr}
    
    annotations = []
    for line in result.stdout.strip().split('\n'):
        if line:
            annotations.append(json.loads(line))
    
    print(f"✅ Encontradas {len(annotations)} anotaciones")
    
    # Conectar a PostgreSQL
    db = create_db_session()
    stats = {
        "total": len(annotations),
        "created": 0,
        "skipped": 0,
        "errors": 0
    }
    
    try:
        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ Usuario con ID {user_id} no encontrado")
            return {"error": f"User {user_id} not found"}
        
        for ann in annotations:
            try:
                # Extraer datos de la anotación
                translation_id = ann.get('meta', {}).get('translation_id')
                answer = ann.get('answer')  # 'accept', 'reject', 'ignore'
                
                if not translation_id or answer == 'ignore':
                    stats['skipped'] += 1
                    continue
                
                # Verificar que la traducción existe
                translation = db.query(Translation).filter(
                    Translation.id == translation_id
                ).first()
                
                if not translation:
                    print(f"⚠️  Translation ID {translation_id} no encontrada, skip")
                    stats['skipped'] += 1
                    continue
                
                # Verificar si ya existe una validación de este usuario para esta traducción
                existing = db.query(Validation).filter(
                    Validation.translation_id == translation_id,
                    Validation.user_id == user_id
                ).first()
                
                if existing:
                    print(f"⏭️  Ya existe validación para translation {translation_id}, skip")
                    stats['skipped'] += 1
                    continue
                
                # Mapear respuesta de Prodigy a validación
                is_correct = (answer == 'accept')
                
                # Extraer evaluación de calidad si existe
                choice = ann.get('accept', [])
                quality = 'unknown'
                if choice:
                    quality = choice[0] if isinstance(choice, list) else str(choice)
                
                if dry_run:
                    print(f"🔍 [DRY RUN] Crearía validación:")
                    print(f"   Translation: {translation_id}")
                    print(f"   User: {user_id}")
                    print(f"   Correct: {is_correct}")
                    print(f"   Quality: {quality}")
                    stats['created'] += 1
                else:
                    # Crear nueva validación
                    validation = Validation(
                        translation_id=translation_id,
                        user_id=user_id,
                        is_correct=is_correct,
                        fluency_score=5 if is_correct else 3,  # Default values
                        accuracy_score=5 if is_correct else 3,
                        notes=f"Importado de Prodigy dataset '{dataset_name}' - Quality: {quality}",
                        created_at=datetime.utcnow()
                    )
                    
                    db.add(validation)
                    stats['created'] += 1
                    print(f"✅ Creada validación para translation {translation_id}")
                
            except Exception as e:
                print(f"❌ Error procesando anotación: {e}")
                stats['errors'] += 1
                continue
        
        if not dry_run:
            db.commit()
            print("\n💾 Cambios guardados en la base de datos")
        else:
            print("\n🔍 [DRY RUN] No se guardaron cambios")
        
    finally:
        db.close()
    
    return stats


def sync_pos_annotations(
    dataset_name: str,
    output_file: Optional[str] = None
) -> int:
    """
    Exportar anotaciones POS (Part-of-Speech) de Prodigy a archivo
    
    Args:
        dataset_name: Nombre del dataset en Prodigy (ej: 'pos_guarani')
        output_file: Archivo de salida (opcional)
        
    Returns:
        Número de anotaciones exportadas
    """
    import subprocess
    
    print(f"📤 Exportando anotaciones POS de '{dataset_name}'...")
    
    if output_file:
        # Exportar a archivo
        result = subprocess.run(
            ["python", "-m", "prodigy", "db-out", dataset_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return 0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        
        count = len(result.stdout.strip().split('\n'))
        print(f"✅ {count} anotaciones guardadas en {output_file}")
        return count
    else:
        # Solo mostrar
        result = subprocess.run(
            ["python", "-m", "prodigy", "db-out", dataset_name, "--format", "csv"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return 0
        
        print(result.stdout)
        return len(result.stdout.strip().split('\n')) - 1  # -1 por el header


def main():
    parser = argparse.ArgumentParser(
        description='Sincronizar anotaciones de Prodigy a PostgreSQL'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando: sync-validations
    sync_val = subparsers.add_parser(
        'sync-validations',
        help='Sincronizar validaciones de traducciones'
    )
    sync_val.add_argument(
        'dataset',
        type=str,
        help='Nombre del dataset en Prodigy (ej: guarani_validation)'
    )
    sync_val.add_argument(
        '--user-id',
        type=int,
        required=True,
        help='ID del usuario que realizó las anotaciones'
    )
    sync_val.add_argument(
        '--dry-run',
        action='store_true',
        help='Simular sin guardar cambios'
    )
    
    # Comando: export-pos
    export_pos = subparsers.add_parser(
        'export-pos',
        help='Exportar anotaciones POS a archivo'
    )
    export_pos.add_argument(
        'dataset',
        type=str,
        help='Nombre del dataset en Prodigy (ej: pos_guarani)'
    )
    export_pos.add_argument(
        '--output',
        type=str,
        help='Archivo de salida (opcional)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'sync-validations':
        stats = sync_translation_validations(
            dataset_name=args.dataset,
            user_id=args.user_id,
            dry_run=args.dry_run
        )
        
        print("\n" + "="*50)
        print("📊 RESUMEN DE SINCRONIZACIÓN")
        print("="*50)
        print(f"Total anotaciones: {stats.get('total', 0)}")
        print(f"✅ Creadas: {stats.get('created', 0)}")
        print(f"⏭️  Saltadas: {stats.get('skipped', 0)}")
        print(f"❌ Errores: {stats.get('errors', 0)}")
        print("="*50)
        
    elif args.command == 'export-pos':
        count = sync_pos_annotations(
            dataset_name=args.dataset,
            output_file=args.output
        )
        print(f"\n✅ Total: {count} anotaciones")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
