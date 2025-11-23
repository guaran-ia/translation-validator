"""
Script para calcular Inter-Annotator Agreement (IAA) en anotaciones POS.

Calcula:
- Cohen's Kappa por par de anotadores
- Acuerdo por etiqueta (label-level agreement)
- Detecta outliers (anotadores con baja consistencia)
- Genera reporte markdown

Uso:
    python scripts/calculate_iaa.py pos_v2 --output reports/iaa_report.md
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set
from itertools import combinations
import subprocess

# Añadir el directorio raíz al path para importar módulos del proyecto
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
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error parseando JSON: {e}")
        sys.exit(1)


def group_by_task_and_session(examples: List[Dict]) -> Dict[int, Dict[str, Dict]]:
    """
    Agrupa anotaciones por task_hash y session_id.
    
    Returns:
        {task_hash: {session_id: example, ...}, ...}
    """
    grouped = defaultdict(dict)
    
    for ex in examples:
        if ex.get("answer") != "accept":
            continue  # Solo considerar anotaciones aceptadas
        
        task_hash = ex.get("_task_hash")
        session_id = ex.get("_session_id")
        
        if task_hash and session_id:
            grouped[task_hash][session_id] = ex
    
    return grouped


def extract_span_tuples(example: Dict) -> Set[Tuple[int, int, str]]:
    """
    Extrae spans como tuplas (start, end, label) para comparación.
    """
    spans = example.get("spans", [])
    return {(span["start"], span["end"], span["label"]) for span in spans}


def calculate_agreement(spans_a: Set[Tuple], spans_b: Set[Tuple]) -> float:
    """
    Calcula acuerdo simple entre dos conjuntos de spans.
    Agreement = (spans en común) / (total de spans únicos)
    """
    if not spans_a and not spans_b:
        return 1.0  # Ambos vacíos = acuerdo perfecto
    
    if not spans_a or not spans_b:
        return 0.0  # Uno vacío, otro no = desacuerdo total
    
    intersection = spans_a & spans_b
    union = spans_a | spans_b
    
    return len(intersection) / len(union) if union else 0.0


def cohen_kappa_spans(spans_a: Set[Tuple], spans_b: Set[Tuple], text_length: int) -> float:
    """
    Calcula Cohen's Kappa para spans.
    
    Kappa = (P_o - P_e) / (1 - P_e)
    donde:
    - P_o = acuerdo observado
    - P_e = acuerdo esperado por azar
    
    Para simplificar, usamos aproximación basada en tokens.
    """
    # Extraer posiciones marcadas por cada anotador
    positions_a = set()
    positions_b = set()
    
    for start, end, label in spans_a:
        positions_a.update(range(start, end))
    
    for start, end, label in spans_b:
        positions_b.update(range(start, end))
    
    # Total de posiciones posibles (caracteres en el texto)
    total_positions = text_length
    
    if total_positions == 0:
        return 1.0
    
    # Calcular acuerdos
    both_marked = len(positions_a & positions_b)
    both_unmarked = total_positions - len(positions_a | positions_b)
    
    # Acuerdo observado
    p_o = (both_marked + both_unmarked) / total_positions
    
    # Acuerdo esperado por azar
    p_a_marked = len(positions_a) / total_positions
    p_b_marked = len(positions_b) / total_positions
    p_e = p_a_marked * p_b_marked + (1 - p_a_marked) * (1 - p_b_marked)
    
    # Cohen's Kappa
    if p_e == 1.0:
        return 1.0
    
    kappa = (p_o - p_e) / (1 - p_e)
    return max(0.0, min(1.0, kappa))  # Clamp entre 0 y 1


def calculate_pairwise_iaa(grouped: Dict[int, Dict[str, Dict]]) -> Dict[Tuple[str, str], Dict]:
    """
    Calcula IAA para cada par de anotadores.
    
    Returns:
        {(session_a, session_b): {
            "agreement": float,
            "kappa": float,
            "n_compared": int,
            "label_agreements": {label: float, ...}
        }}
    """
    # Obtener todos los anotadores únicos
    all_sessions = set()
    for task_annotations in grouped.values():
        all_sessions.update(task_annotations.keys())
    
    all_sessions = sorted(all_sessions)
    
    print(f"[INFO] Anotadores encontrados: {', '.join(all_sessions)}")
    
    results = {}
    
    # Para cada par de anotadores
    for session_a, session_b in combinations(all_sessions, 2):
        agreements = []
        kappas = []
        label_agreements = defaultdict(list)
        n_compared = 0
        
        # Para cada tarea anotada por ambos
        for task_hash, task_annotations in grouped.items():
            if session_a in task_annotations and session_b in task_annotations:
                ex_a = task_annotations[session_a]
                ex_b = task_annotations[session_b]
                
                spans_a = extract_span_tuples(ex_a)
                spans_b = extract_span_tuples(ex_b)
                
                # Acuerdo simple
                agreement = calculate_agreement(spans_a, spans_b)
                agreements.append(agreement)
                
                # Cohen's Kappa
                text_length = len(ex_a.get("text", ""))
                kappa = cohen_kappa_spans(spans_a, spans_b, text_length)
                kappas.append(kappa)
                
                # Acuerdo por etiqueta
                labels_a = {span[2] for span in spans_a}
                labels_b = {span[2] for span in spans_b}
                all_labels = labels_a | labels_b
                
                for label in all_labels:
                    spans_a_label = {s for s in spans_a if s[2] == label}
                    spans_b_label = {s for s in spans_b if s[2] == label}
                    label_agr = calculate_agreement(spans_a_label, spans_b_label)
                    label_agreements[label].append(label_agr)
                
                n_compared += 1
        
        # Promediar resultados
        avg_agreement = sum(agreements) / len(agreements) if agreements else 0.0
        avg_kappa = sum(kappas) / len(kappas) if kappas else 0.0
        
        avg_label_agreements = {
            label: sum(scores) / len(scores)
            for label, scores in label_agreements.items()
        }
        
        results[(session_a, session_b)] = {
            "agreement": avg_agreement,
            "kappa": avg_kappa,
            "n_compared": n_compared,
            "label_agreements": avg_label_agreements
        }
    
    return results


def generate_report(dataset_name: str, iaa_results: Dict, output_path: Path):
    """Genera reporte markdown con resultados de IAA."""
    
    report = f"""# 📊 Reporte de Inter-Annotator Agreement (IAA)

**Dataset:** `{dataset_name}`  
**Fecha:** {Path(__file__).parent.parent.parent}

---

## 🎯 Resumen General

"""
    
    # Calcular promedios globales
    all_agreements = [r["agreement"] for r in iaa_results.values()]
    all_kappas = [r["kappa"] for r in iaa_results.values()]
    
    avg_agreement = sum(all_agreements) / len(all_agreements) if all_agreements else 0.0
    avg_kappa = sum(all_kappas) / len(all_kappas) if all_kappas else 0.0
    
    report += f"""
- **Acuerdo promedio (simple):** {avg_agreement:.2%}
- **Cohen's Kappa promedio:** {avg_kappa:.3f}
- **Total de pares evaluados:** {len(iaa_results)}

### Interpretación de Kappa:
- `< 0.20`: Acuerdo pobre
- `0.21 - 0.40`: Acuerdo bajo
- `0.41 - 0.60`: Acuerdo moderado
- `0.61 - 0.80`: Acuerdo sustancial
- `0.81 - 1.00`: Acuerdo casi perfecto

---

## 👥 Acuerdo por Par de Anotadores

"""
    
    # Ordenar por kappa descendente
    sorted_pairs = sorted(iaa_results.items(), key=lambda x: x[1]["kappa"], reverse=True)
    
    for (session_a, session_b), metrics in sorted_pairs:
        report += f"""
### `{session_a}` ↔ `{session_b}`

- **Acuerdo simple:** {metrics["agreement"]:.2%}
- **Cohen's Kappa:** {metrics["kappa"]:.3f}
- **Oraciones comparadas:** {metrics["n_compared"]}

"""
        
        if metrics["label_agreements"]:
            report += "**Acuerdo por etiqueta:**\n\n"
            report += "| Etiqueta | Acuerdo |\n"
            report += "|----------|--------|\n"
            
            for label, agr in sorted(metrics["label_agreements"].items(), key=lambda x: x[1], reverse=True):
                report += f"| {label} | {agr:.2%} |\n"
            
            report += "\n"
    
    # Detectar outliers (anotadores con bajo acuerdo consistente)
    report += """---

## ⚠️ Outliers Detectados

"""
    
    # Calcular score promedio por anotador
    annotator_scores = defaultdict(list)
    for (session_a, session_b), metrics in iaa_results.items():
        annotator_scores[session_a].append(metrics["kappa"])
        annotator_scores[session_b].append(metrics["kappa"])
    
    avg_scores = {
        session: sum(scores) / len(scores)
        for session, scores in annotator_scores.items()
    }
    
    threshold = 0.50  # Umbral para considerar "bajo acuerdo"
    outliers = [s for s, score in avg_scores.items() if score < threshold]
    
    if outliers:
        report += "Los siguientes anotadores tienen acuerdo promedio < 0.50 (considerado bajo):\n\n"
        for session in outliers:
            report += f"- **{session}**: Kappa promedio = {avg_scores[session]:.3f}\n"
        report += "\n**Recomendación:** Revisar guidelines con estos anotadores o proveer más ejemplos.\n"
    else:
        report += "✅ No se detectaron anotadores con acuerdo consistentemente bajo.\n"
    
    report += """
---

## 📈 Recomendaciones

1. **Kappa < 0.60:** Revisar guidelines y hacer sesión de calibración con anotadores.
2. **Desacuerdo en etiquetas específicas:** Añadir ejemplos claros en POS_ANNOTATION_GUIDE.md.
3. **Outliers detectados:** Sesión 1-on-1 para entender dudas.
4. **Alto acuerdo (>0.80):** Puede reducirse overlap (usar annotations_per_task=1.5).

---

*Generado por `calculate_iaa.py`*
"""
    
    # Guardar reporte
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding='utf-8')
    print(f"\n[OK] Reporte guardado en: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Calcular Inter-Annotator Agreement (IAA)")
    parser.add_argument("dataset", help="Nombre del dataset de Prodigy")
    parser.add_argument("--output", "-o", default="reports/iaa_report.md", help="Archivo de salida (markdown)")
    
    args = parser.parse_args()
    
    # Exportar anotaciones
    examples = export_dataset(args.dataset)
    
    if not examples:
        print("[ERROR] No se encontraron anotaciones en el dataset")
        sys.exit(1)
    
    # Agrupar por task y session
    print("[INFO] Agrupando anotaciones por tarea y anotador...")
    grouped = group_by_task_and_session(examples)
    
    # Filtrar tareas con múltiples anotadores
    multi_annotated = {k: v for k, v in grouped.items() if len(v) >= 2}
    
    print(f"[INFO] Tareas anotadas por múltiples personas: {len(multi_annotated)}")
    
    if not multi_annotated:
        print("[WARN] No hay suficientes anotaciones multi-anotador para calcular IAA")
        print("[HINT] Asegúrate de usar task_router con annotations_per_task >= 2")
        sys.exit(0)
    
    # Calcular IAA
    print("[INFO] Calculando acuerdos por pares...")
    iaa_results = calculate_pairwise_iaa(multi_annotated)
    
    # Generar reporte
    output_path = Path(args.output)
    generate_report(args.dataset, iaa_results, output_path)
    
    print("\n✅ Análisis completado")


if __name__ == "__main__":
    main()
