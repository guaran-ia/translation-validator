#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
match_annotations.py
====================
Script para combinar anotaciones de POS, Features y Relations del mismo lote.

Este script:
1. Lee las anotaciones de cada dataset de Prodigy por lote
2. Combina las anotaciones del mismo sentence usando input_hash
3. Genera un archivo unificado con todas las capas de anotación

Uso:
    python scripts/match_annotations.py --batch 1 --output data/export/batch_01_combined.json
    python scripts/match_annotations.py --all --output data/export/all_combined.json
"""

import json
import argparse
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional


def run_prodigy_command(cmd: List[str]) -> str:
    """Ejecuta un comando de Prodigy y retorna la salida."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout
    except Exception as e:
        print(f"Error ejecutando comando: {e}", file=sys.stderr)
        return ""


def get_prodigy_datasets() -> List[str]:
    """Obtiene la lista de datasets disponibles en Prodigy."""
    result = run_prodigy_command(["prodigy", "stats", "-l"])
    if not result:
        return []
    
    datasets = []
    for line in result.strip().split('\n'):
        line = line.strip()
        if line and not line.startswith('='):
            # Prodigy stats -l muestra datasets, uno por línea
            datasets.append(line)
    
    return datasets


def export_dataset(dataset_name: str) -> List[Dict[str, Any]]:
    """Exporta un dataset de Prodigy a memoria."""
    try:
        result = subprocess.run(
            ["prodigy", "db-out", dataset_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"Error exportando {dataset_name}: {result.stderr}", file=sys.stderr)
            return []
        
        # db-out retorna JSONL
        annotations = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    annotations.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return annotations
    except Exception as e:
        print(f"Error exportando {dataset_name}: {e}", file=sys.stderr)
        return []


def get_batch_datasets(batch_num: int) -> Dict[str, str]:
    """
    Obtiene los nombres de datasets para un lote específico.
    
    Returns:
        Dict con keys 'pos', 'features', 'relations' y valores los nombres de dataset
    """
    batch_str = f"{batch_num:02d}"
    return {
        'pos': f"guarani_pos_batch_{batch_str}",
        'features': f"guarani_features_batch_{batch_str}",
        'relations': f"guarani_relations_batch_{batch_str}"
    }


def combine_annotations(
    pos_annotations: List[Dict],
    features_annotations: List[Dict],
    relations_annotations: List[Dict]
) -> List[Dict[str, Any]]:
    """
    Combina anotaciones de las tres capas usando _input_hash o text como clave.
    
    Returns:
        Lista de documentos combinados con todas las capas de anotación
    """
    # Indexar por input_hash o text
    combined = defaultdict(lambda: {
        'text': '',
        'guarani_text': '',
        'translation_id': None,
        'tokens': [],
        'pos_spans': [],
        'feature_spans': [],
        'relations': [],
        'pos_answer': None,
        'features_answer': None,
        'relations_answer': None,
        '_input_hash': None
    })
    
    # Procesar anotaciones POS
    for ann in pos_annotations:
        key = ann.get('_input_hash') or ann.get('text', '')
        if not key:
            continue
        
        combined[key]['text'] = ann.get('text', '')
        combined[key]['guarani_text'] = ann.get('guarani_text', '')
        combined[key]['translation_id'] = ann.get('translation_id')
        combined[key]['tokens'] = ann.get('tokens', [])
        combined[key]['_input_hash'] = ann.get('_input_hash')
        combined[key]['pos_spans'] = ann.get('spans', [])
        combined[key]['pos_answer'] = ann.get('answer')
    
    # Procesar anotaciones Features
    for ann in features_annotations:
        key = ann.get('_input_hash') or ann.get('text', '')
        if not key:
            continue
        
        if not combined[key]['text']:
            combined[key]['text'] = ann.get('text', '')
            combined[key]['guarani_text'] = ann.get('guarani_text', '')
            combined[key]['translation_id'] = ann.get('translation_id')
            combined[key]['_input_hash'] = ann.get('_input_hash')
        
        if not combined[key]['tokens']:
            combined[key]['tokens'] = ann.get('tokens', [])
        
        combined[key]['feature_spans'] = ann.get('spans', [])
        combined[key]['features_answer'] = ann.get('answer')
    
    # Procesar anotaciones Relations
    for ann in relations_annotations:
        key = ann.get('_input_hash') or ann.get('text', '')
        if not key:
            continue
        
        if not combined[key]['text']:
            combined[key]['text'] = ann.get('text', '')
            combined[key]['guarani_text'] = ann.get('guarani_text', '')
            combined[key]['translation_id'] = ann.get('translation_id')
            combined[key]['_input_hash'] = ann.get('_input_hash')
        
        if not combined[key]['tokens']:
            combined[key]['tokens'] = ann.get('tokens', [])
        
        combined[key]['relations'] = ann.get('relations', [])
        combined[key]['relations_answer'] = ann.get('answer')
    
    # Convertir a lista y filtrar vacíos
    result = []
    for key, doc in combined.items():
        if doc['text']:
            result.append(doc)
    
    # Ordenar por translation_id si está disponible
    result.sort(key=lambda x: x.get('translation_id') or 0)
    
    return result


def calculate_batch_stats(combined: List[Dict]) -> Dict[str, Any]:
    """Calcula estadísticas del lote combinado."""
    stats = {
        'total_sentences': len(combined),
        'with_pos': 0,
        'with_features': 0,
        'with_relations': 0,
        'complete': 0,  # Tiene las 3 capas
        'accepted': {
            'pos': 0,
            'features': 0,
            'relations': 0
        },
        'rejected': {
            'pos': 0,
            'features': 0,
            'relations': 0
        }
    }
    
    for doc in combined:
        has_pos = bool(doc.get('pos_spans'))
        has_features = bool(doc.get('feature_spans'))
        has_relations = bool(doc.get('relations'))
        
        if has_pos:
            stats['with_pos'] += 1
        if has_features:
            stats['with_features'] += 1
        if has_relations:
            stats['with_relations'] += 1
        if has_pos and has_features and has_relations:
            stats['complete'] += 1
        
        # Contar respuestas
        if doc.get('pos_answer') == 'accept':
            stats['accepted']['pos'] += 1
        elif doc.get('pos_answer') == 'reject':
            stats['rejected']['pos'] += 1
        
        if doc.get('features_answer') == 'accept':
            stats['accepted']['features'] += 1
        elif doc.get('features_answer') == 'reject':
            stats['rejected']['features'] += 1
        
        if doc.get('relations_answer') == 'accept':
            stats['accepted']['relations'] += 1
        elif doc.get('relations_answer') == 'reject':
            stats['rejected']['relations'] += 1
    
    return stats


def process_batch(batch_num: int, output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Procesa un lote completo y combina las anotaciones.
    
    Args:
        batch_num: Número de lote (1-60)
        output_path: Path donde guardar el resultado (opcional)
    
    Returns:
        Dict con 'combined' (datos) y 'stats' (estadísticas)
    """
    print(f"\n📦 Procesando lote {batch_num:02d}...")
    
    datasets = get_batch_datasets(batch_num)
    
    # Exportar cada dataset
    pos_data = export_dataset(datasets['pos'])
    features_data = export_dataset(datasets['features'])
    relations_data = export_dataset(datasets['relations'])
    
    print(f"   - POS: {len(pos_data)} anotaciones")
    print(f"   - Features: {len(features_data)} anotaciones")
    print(f"   - Relations: {len(relations_data)} anotaciones")
    
    # Combinar
    combined = combine_annotations(pos_data, features_data, relations_data)
    stats = calculate_batch_stats(combined)
    
    print(f"   - Combinados: {len(combined)} oraciones")
    print(f"   - Completos (3 capas): {stats['complete']}")
    
    result = {
        'batch': batch_num,
        'stats': stats,
        'data': combined
    }
    
    # Guardar si se especifica output
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Guardado en: {output_path}")
    
    return result


def process_all_batches(output_dir: Path, max_batch: int = 60) -> Dict[str, Any]:
    """
    Procesa todos los lotes disponibles.
    
    Args:
        output_dir: Directorio donde guardar los resultados
        max_batch: Número máximo de lotes a procesar
    
    Returns:
        Dict con resumen global
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_combined = []
    global_stats = {
        'total_batches': 0,
        'total_sentences': 0,
        'total_complete': 0,
        'batches': []
    }
    
    for batch_num in range(1, max_batch + 1):
        try:
            result = process_batch(batch_num, output_dir / f"batch_{batch_num:02d}_combined.json")
            
            if result['data']:
                global_stats['total_batches'] += 1
                global_stats['total_sentences'] += result['stats']['total_sentences']
                global_stats['total_complete'] += result['stats']['complete']
                global_stats['batches'].append({
                    'batch': batch_num,
                    'sentences': result['stats']['total_sentences'],
                    'complete': result['stats']['complete']
                })
                all_combined.extend(result['data'])
        except Exception as e:
            print(f"   ⚠️ Error en lote {batch_num}: {e}")
    
    # Guardar combinado global
    global_result = {
        'stats': global_stats,
        'data': all_combined
    }
    
    global_path = output_dir / "all_batches_combined.json"
    with open(global_path, 'w', encoding='utf-8') as f:
        json.dump(global_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Resumen Global:")
    print(f"   - Lotes procesados: {global_stats['total_batches']}")
    print(f"   - Total oraciones: {global_stats['total_sentences']}")
    print(f"   - Total completos: {global_stats['total_complete']}")
    print(f"   ✅ Guardado en: {global_path}")
    
    return global_result


def main():
    parser = argparse.ArgumentParser(
        description='Combina anotaciones de POS, Features y Relations por lote'
    )
    parser.add_argument(
        '--batch', '-b',
        type=int,
        help='Número de lote a procesar (1-60)'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Procesar todos los lotes'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/export',
        help='Archivo o directorio de salida'
    )
    parser.add_argument(
        '--max-batch',
        type=int,
        default=60,
        help='Número máximo de lotes (default: 60)'
    )
    
    args = parser.parse_args()
    
    if not args.batch and not args.all:
        parser.error('Debe especificar --batch N o --all')
    
    output_path = Path(args.output)
    
    if args.all:
        process_all_batches(output_path, args.max_batch)
    else:
        if args.batch < 1 or args.batch > args.max_batch:
            parser.error(f'El lote debe estar entre 1 y {args.max_batch}')
        
        # Si output es directorio, crear nombre de archivo
        if output_path.is_dir() or not output_path.suffix:
            output_path = output_path / f"batch_{args.batch:02d}_combined.json"
        
        process_batch(args.batch, output_path)


if __name__ == "__main__":
    main()
