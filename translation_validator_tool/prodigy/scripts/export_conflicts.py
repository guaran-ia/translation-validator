"""
Script para exportar oraciones con conflictos (desacuerdos entre anotadores).

Identifica:
- Oraciones donde 2+ anotadores difieren en sus anotaciones
- Grado de desacuerdo (total, parcial)
- Exporta a JSONL para review

Uso:
    python scripts/export_conflicts.py pos_v2 --output data/export/conflicts.jsonl --threshold 0.5
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def export_dataset(dataset_name: str) -> List[Dict]:
    """Exporta dataset de Prodigy usando db-out."""
    print(f"[INFO] Exportando dataset '{dataset_name}' desde Prodigy...")
    
    try:
        result = subprocess.run(
            ["python", "-m", "prodigy", "db-out", dataset_name],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        
        examples = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                examples.append(json.loads(line))
        
        print(f"[OK] Exportadas {len(examples)} anotaciones")
        return examples
    
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudo exportar dataset: {e.stderr}")
        sys.exit(1)


def group_by_task(examples: List[Dict]) -> Dict[int, List[Dict]]:
    """Agrupa anotaciones por task_hash."""
    grouped = defaultdict(list)
    
    for ex in examples:
        if ex.get("answer") != "accept":
            continue
        
        task_hash = ex.get("_task_hash")
        if task_hash:
            grouped[task_hash].append(ex)
    
    return grouped


def extract_spans(example: Dict) -> Set[Tuple[int, int, str]]:
    """Extrae spans como tuplas (start, end, label)."""
    return {(s["start"], s["end"], s["label"]) for s in example.get("spans", [])}


def calculate_disagreement(annotations: List[Dict]) -> float:
    """
    Calcula grado de desacuerdo entre múltiples anotaciones.
    Returns: 1.0 (desacuerdo total) a 0.0 (acuerdo perfecto)
    """
    if len(annotations) < 2:
        return 0.0
    
    # Extraer spans de cada anotador
    all_spans = [extract_spans(ann) for ann in annotations]
    
    # Calcular intersección (spans en común) y unión (todos los spans únicos)
    intersection = set.intersection(*all_spans) if all_spans else set()
    union = set.union(*all_spans) if all_spans else set()
    
    if not union:
        return 0.0  # Todos vacíos = acuerdo perfecto
    
    # Desacuerdo = 1 - (común / total)
    agreement = len(intersection) / len(union)
    return 1.0 - agreement


def find_conflicts(grouped: Dict[int, List[Dict]], threshold: float = 0.3) -> List[Dict]:
    """
    Encuentra tareas con desacuerdo >= threshold.
    
    Returns:
        Lista de conflictos con metadatos
    """
    conflicts = []
    
    for task_hash, annotations in grouped.items():
        if len(annotations) < 2:
            continue  # Necesitamos al menos 2 anotaciones
        
        disagreement = calculate_disagreement(annotations)
        
        if disagreement >= threshold:
            # Extraer info de la primera anotación (texto, meta)
            first = annotations[0]
            
            conflict = {
                "_task_hash": task_hash,
                "text": first.get("text", ""),
                "meta": first.get("meta", {}),
                "tokens": first.get("tokens", []),
                "disagreement_score": round(disagreement, 3),
                "n_annotators": len(annotations),
                "annotations": []
            }
            
            # Añadir cada anotación
            for ann in annotations:
                conflict["annotations"].append({
                    "session_id": ann.get("_session_id", "unknown"),
                    "spans": ann.get("spans", [])
                })
            
            conflicts.append(conflict)
    
    return conflicts


def export_conflicts_jsonl(conflicts: List[Dict], output_path: Path):
    """Exporta conflictos a JSONL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open('w', encoding='utf-8') as f:
        for conflict in conflicts:
            f.write(json.dumps(conflict, ensure_ascii=False) + '\n')
    
    print(f"[OK] {len(conflicts)} conflictos exportados a: {output_path}")


def print_summary(conflicts: List[Dict]):
    """Imprime resumen de conflictos."""
    if not conflicts:
        print("\n✅ No se encontraron conflictos significativos")
        return
    
    print(f"\n📋 Resumen de Conflictos:\n")
    print(f"Total de oraciones con desacuerdo: {len(conflicts)}")
    
    # Distribución por nivel de desacuerdo
    high = len([c for c in conflicts if c["disagreement_score"] >= 0.7])
    medium = len([c for c in conflicts if 0.4 <= c["disagreement_score"] < 0.7])
    low = len([c for c in conflicts if c["disagreement_score"] < 0.4])
    
    print(f"  - Alto (≥0.7): {high}")
    print(f"  - Medio (0.4-0.7): {medium}")
    print(f"  - Bajo (<0.4): {low}")
    
    # Top 5 conflictos
    top_5 = sorted(conflicts, key=lambda x: x["disagreement_score"], reverse=True)[:5]
    
    print(f"\n🔥 Top 5 Conflictos Mayores:\n")
    for i, c in enumerate(top_5, 1):
        text_preview = c["text"][:60] + "..." if len(c["text"]) > 60 else c["text"]
        print(f"{i}. [{c['disagreement_score']:.2f}] {text_preview}")
        print(f"   Anotadores: {', '.join(a['session_id'] for a in c['annotations'])}\n")


def main():
    parser = argparse.ArgumentParser(description="Exportar conflictos entre anotadores")
    parser.add_argument("dataset", help="Nombre del dataset de Prodigy")
    parser.add_argument("--output", "-o", default="data/export/conflicts.jsonl", help="Archivo de salida (JSONL)")
    parser.add_argument("--threshold", "-t", type=float, default=0.3, help="Umbral de desacuerdo (0.0-1.0)")
    
    args = parser.parse_args()
    
    # Validar threshold
    if not 0.0 <= args.threshold <= 1.0:
        print("[ERROR] Threshold debe estar entre 0.0 y 1.0")
        sys.exit(1)
    
    # Exportar anotaciones
    examples = export_dataset(args.dataset)
    
    if not examples:
        print("[ERROR] No se encontraron anotaciones en el dataset")
        sys.exit(1)
    
    # Agrupar por tarea
    print("[INFO] Agrupando anotaciones...")
    grouped = group_by_task(examples)
    
    # Filtrar tareas multi-anotadas
    multi_annotated = {k: v for k, v in grouped.items() if len(v) >= 2}
    print(f"[INFO] Tareas con múltiples anotaciones: {len(multi_annotated)}")
    
    if not multi_annotated:
        print("[WARN] No hay tareas anotadas por múltiples personas")
        sys.exit(0)
    
    # Buscar conflictos
    print(f"[INFO] Buscando conflictos (threshold={args.threshold})...")
    conflicts = find_conflicts(multi_annotated, args.threshold)
    
    # Exportar
    output_path = Path(args.output)
    export_conflicts_jsonl(conflicts, output_path)
    
    # Mostrar resumen
    print_summary(conflicts)
    
    # Sugerencia de uso
    if conflicts:
        print(f"\n💡 Siguiente paso:")
        print(f"   Revisar conflictos con:")
        print(f"   prodigy guarani-pos-review conflicts_review {output_path} -F recipes/guarani_pos_v2.py")
    
    print("\n✅ Exportación completada")


if __name__ == "__main__":
    main()
