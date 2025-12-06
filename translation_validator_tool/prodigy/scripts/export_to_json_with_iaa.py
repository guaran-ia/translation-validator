"""
Exporta anotaciones desde Prodigy a formato JSON con reportes de acuerdo entre anotadores.

Características:
- Exporta a JSON estructurado (no JSONL)
- Calcula métricas IAA por ejemplo
- Identifica conflictos entre anotadores
- Genera reporte de calidad
- Mapeo automático a Universal Dependencies

Uso:
    python scripts/export_to_json_with_iaa.py pos_openai --output data/export/pos_openai_report.json
    python scripts/export_to_json_with_iaa.py pos_v2 --output data/export/pos_v2_report.json --min-agreement 0.7
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
from datetime import datetime

import prodigy
from prodigy.components.db import connect

# Importar mapper centralizado (NUEVA VERSIÓN)
try:
    from ud_guarani_mapper import (
        FRIENDLY_TO_UD, 
        UD_TO_FRIENDLY, 
        map_label, 
        VALID_UPOS,
        VALID_FEATURES
    )
except ImportError:
    # Si no se puede importar, agregar el directorio al path
    sys.path.insert(0, str(Path(__file__).parent))
    from ud_guarani_mapper import (
        FRIENDLY_TO_UD,
        UD_TO_FRIENDLY,
        map_label,
        VALID_UPOS,
        VALID_FEATURES
    )


def calculate_span_agreement(spans_list: List[List[Dict]]) -> Tuple[float, List[Dict]]:
    """
    Calcula el acuerdo entre múltiples anotadores para spans.
    
    Returns:
        (agreement_score, conflicts)
        - agreement_score: 0.0 (sin acuerdo) a 1.0 (acuerdo perfecto)
        - conflicts: Lista de spans donde hubo desacuerdo
    """
    if len(spans_list) <= 1:
        return 1.0, []
    
    # Convertir spans a tuplas (start, end, label) para comparar
    span_sets = []
    for spans in spans_list:
        span_set = {(s["start"], s["end"], s["label"]) for s in spans}
        span_sets.append(span_set)
    
    # Encontrar intersección (spans en los que todos coinciden)
    if not span_sets:
        return 1.0, []
    
    common_spans = set.intersection(*span_sets)
    all_spans = set.union(*span_sets)
    
    # Calcular acuerdo como Jaccard similarity
    if not all_spans:
        agreement = 1.0
    else:
        agreement = len(common_spans) / len(all_spans)
    
    # Identificar conflictos (spans que no están en común)
    conflicts = []
    for span in all_spans - common_spans:
        # Ver en cuántas anotaciones aparece este span
        appearances = sum(1 for span_set in span_sets if span in span_set)
        
        conflicts.append({
            "start": span[0],
            "end": span[1],
            "label": span[2],
            "agreement_ratio": appearances / len(span_sets),
            "annotators_agree": appearances,
            "total_annotators": len(span_sets)
        })
    
    return agreement, conflicts


def export_with_iaa(
    dataset: str,
    output_path: str,
    min_agreement: float = 0.0,
    verbose: bool = False
):
    """
    Exporta dataset con cálculo de IAA por ejemplo.
    
    Args:
        dataset: Nombre del dataset en Prodigy
        output_path: Path donde guardar el JSON
        min_agreement: Mínimo acuerdo para incluir ejemplo (0.0-1.0)
        verbose: Imprimir detalles
    """
    
    # Conectar a DB
    db = connect()
    
    # Verificar que existe el dataset
    if dataset not in db.datasets:
        available = ", ".join(db.datasets)
        raise ValueError(
            f"❌ Dataset '{dataset}' no existe.\n"
            f"   Datasets disponibles: {available}"
        )
    
    # Cargar anotaciones (usando método moderno para evitar DeprecationWarning)
    try:
        examples = list(db.get_dataset_examples(dataset))
    except AttributeError:
        # Fallback para versiones antiguas de Prodigy
        examples = list(db.get_dataset(dataset))
    
    if not examples:
        raise ValueError(f"❌ Dataset '{dataset}' está vacío")
    
    if verbose:
        print(f"📚 Cargadas {len(examples)} anotaciones de '{dataset}'")
    
    # Agrupar por _task_hash (mismo texto)
    grouped = defaultdict(list)
    for ex in examples:
        task_hash = ex.get("_task_hash")
        if task_hash:
            grouped[task_hash].append(ex)
    
    if verbose:
        print(f"📊 {len(grouped)} textos únicos encontrados")
    
    # Procesar cada grupo
    results = []
    total_conflicts = 0
    total_agreement = 0.0
    
    for task_hash, annotations in grouped.items():
        # Extraer información común
        text = annotations[0].get("text", "")
        meta = annotations[0].get("meta", {})
        
        # Extraer spans de cada anotador
        annotators = []
        spans_list = []
        
        for ann in annotations:
            session_id = ann.get("_session_id", "unknown")
            spans = ann.get("spans", [])
            answer = ann.get("answer", "unknown")
            timestamp = ann.get("_timestamp", 0)
            
            # Solo incluir anotaciones aceptadas
            if answer == "accept":
                annotators.append({
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "num_spans": len(spans)
                })
                spans_list.append(spans)
        
        if not spans_list:
            continue
        
        # Calcular acuerdo entre anotadores
        agreement, conflicts = calculate_span_agreement(spans_list)
        
        # Filtrar por acuerdo mínimo
        if agreement < min_agreement:
            continue
        
        total_agreement += agreement
        total_conflicts += len(conflicts)
        
        # Encontrar spans con consenso (aparecen en todas las anotaciones)
        consensus_spans = []
        if len(spans_list) > 1:
            span_counter = Counter()
            for spans in spans_list:
                for span in spans:
                    key = (span["start"], span["end"], span["label"])
                    span_counter[key] += 1
            
            # Consenso = aparece en todas las anotaciones
            for (start, end, label), count in span_counter.items():
                if count == len(spans_list):
                    # Usar el mapper centralizado para convertir a UD
                    ud_label = map_label(label, "to_ud")
                    
                    consensus_spans.append({
                        "start": start,
                        "end": end,
                        "label": label,           # Etiqueta original (amigable)
                        "ud_label": ud_label,     # Etiqueta Universal Dependencies
                        "text": text[start:end],
                        "confidence": 1.0
                    })
        else:
            # Solo 1 anotador: usar sus spans directamente
            for span in spans_list[0]:
                label = span.get("label", "")
                
                # Usar el mapper centralizado para convertir a UD
                ud_label = map_label(label, "to_ud")
                
                consensus_spans.append({
                    **span,
                    "text": text[span["start"]:span["end"]],
                    "ud_label": ud_label,     # Etiqueta Universal Dependencies
                    "confidence": 1.0
                })
        
        # Construir resultado
        result = {
            "text": text,
            "meta": meta,
            "spans": consensus_spans,
            "iaa_metrics": {
                "agreement_score": round(agreement, 3),
                "num_annotators": len(annotators),
                "num_conflicts": len(conflicts),
                "conflicts": conflicts
            },
            "annotators": annotators,
            "_task_hash": task_hash
        }
        
        results.append(result)
    
    # Calcular estadísticas globales
    avg_agreement = total_agreement / len(results) if results else 0.0
    
    metadata = {
        "dataset_name": dataset,
        "export_date": datetime.now().isoformat(),
        "total_examples": len(results),
        "total_annotations": sum(r["iaa_metrics"]["num_annotators"] for r in results),
        "average_agreement": round(avg_agreement, 3),
        "total_conflicts": total_conflicts,
        "min_agreement_filter": min_agreement,
        "examples_filtered": len(grouped) - len(results)
    }
    
    # Guardar JSON
    output = {
        "metadata": metadata,
        "examples": results
    }
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    if verbose:
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   Total ejemplos: {metadata['total_examples']}")
        print(f"   Total anotaciones: {metadata['total_annotations']}")
        print(f"   Acuerdo promedio: {metadata['average_agreement']:.1%}")
        print(f"   Conflictos totales: {metadata['total_conflicts']}")
        print(f"   Ejemplos filtrados: {metadata['examples_filtered']}")
        print(f"\n✅ Exportado a: {output_path}")
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Exporta anotaciones Prodigy a JSON con cálculo de IAA"
    )
    
    parser.add_argument(
        "dataset",
        help="Nombre del dataset en Prodigy"
    )
    
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Path donde guardar el JSON"
    )
    
    parser.add_argument(
        "--min-agreement", "-m",
        type=float,
        default=0.0,
        help="Mínimo acuerdo para incluir ejemplo (0.0-1.0, default: 0.0)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Imprimir detalles"
    )
    
    args = parser.parse_args()
    
    try:
        export_with_iaa(
            dataset=args.dataset,
            output_path=args.output,
            min_agreement=args.min_agreement,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
