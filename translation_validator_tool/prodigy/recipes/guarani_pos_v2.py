"""
Recipe V2 para anotación POS en Guaraní con:
- Task routing (annotations_per_task=2 para inter-annotator agreement)
- Validación en tiempo real (validate_answer)
- Soporte multi-anotador con sesiones nombradas
"""

import prodigy
from prodigy.components.loaders import JSONL
from prodigy.components.preprocess import add_tokens
from prodigy.util import set_hashes
from prodigy.core import Controller
from typing import List, Dict
import spacy

# Cargar modelo de spaCy para tokenización
nlp = spacy.blank("es")


def task_router_iaa(ctrl: Controller, session_id: str, item: Dict) -> List[str]:
    """
    Task router para inter-annotator agreement.
    Cada ejemplo lo ven exactamente N anotadores (definido por annotations_per_task).
    Usa hashing determinista para asignar consistentemente.
    """
    # Obtener pool de anotadores disponibles
    pool = list(ctrl.session_ids)
    if not pool:
        return []
    
    # Obtener hash del task (único por oración)
    task_hash = item.get("_task_hash")
    if task_hash is None:
        return []
    
    # Definir cuántos anotadores deben ver cada ejemplo
    N_ANNOTATORS = 2  # puedes cambiar a 3 si quieres más overlap
    
    # Comprobar cuántas veces ya fue anotado este task
    # Contamos cuántas anotaciones existen para este _task_hash
    try:
        examples = ctrl.db.get_dataset(ctrl.dataset)
        hash_count = sum(1 for ex in examples if ex.get("_task_hash") == task_hash)
    except:
        # Si falla, asumimos 0
        hash_count = 0
    
    # Si ya alcanzó el número deseado, no lo re-rutees
    if hash_count >= N_ANNOTATORS:
        return []
    
    # Usar hash modulo para seleccionar N anotadores consistentemente
    selected = []
    pool_copy = pool.copy()
    
    for i in range(N_ANNOTATORS):
        if not pool_copy:
            break
        idx = (task_hash + i) % len(pool_copy)
        selected.append(pool_copy.pop(idx))
    
    return selected


def validate_answer(example: Dict) -> None:
    """
    Valida que las anotaciones aceptadas tengan al menos:
    - 1 SUJETO
    - 1 VERBO
    
    Si no cumple, lanza error que el anotador ve en la UI.
    """
    # Solo validar si el usuario aceptó (no validar reject/ignore)
    if example.get("answer") != "accept":
        return
    
    spans = example.get("spans", [])
    labels = [span["label"] for span in spans]
    
    errors = []
    
    # Verificar que tenga al menos 1 SUJETO
    if "SUJETO" not in labels:
        errors.append("⚠️ Falta marcar al menos 1 SUJETO")
    
    # Verificar que tenga al menos 1 VERBO
    if "VERBO" not in labels:
        errors.append("⚠️ Falta marcar al menos 1 VERBO")
    
    # Si hay errores, lanzar excepción (Prodigy mostrará mensaje)
    if errors:
        raise ValueError("\n".join(errors))


@prodigy.recipe(
    "guarani-pos-v2",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
)
def guarani_pos_tagging_v2(dataset, source):
    """
    Recipe mejorado para anotación POS con quality control.
    
    Mejoras vs v1:
    - Task routing: cada oración la ven 2 anotadores (inter-annotator agreement)
    - Validación: requiere al menos 1 SUJETO y 1 VERBO antes de aceptar
    - Sesiones nombradas: usa ?session=nombre en la URL
    
    Uso con múltiples anotadores:
        # Definir anotadores permitidos
        $env:PRODIGY_ALLOWED_SESSIONS="alice,bob,carlos"
        
        # Iniciar servidor
        prodigy guarani-pos-v2 pos_v2 data/export/original_translations.jsonl -F recipes/guarani_pos_v2.py --port 8081
        
        # Cada anotador accede con su sesión:
        # Alice: http://localhost:8081/?session=alice
        # Bob:   http://localhost:8081/?session=bob
        # Carlos: http://localhost:8081/?session=carlos
    
    Exportar anotaciones:
        prodigy db-out pos_v2 > data/annotations/pos_v2_export.jsonl
    """
    
    stream = JSONL(source)
    
    def prepare_for_pos(stream):
        for example in stream:
            # Usar el texto en Guaraní
            guarani_text = example.get('text', '')
            spanish_text = example.get('meta', {}).get('spanish_text', '')
            
            # Tokenizar el texto
            doc = nlp(guarani_text)
            tokens = [
                {
                    "text": token.text,
                    "start": token.idx,
                    "end": token.idx + len(token.text),
                    "id": i
                }
                for i, token in enumerate(doc)
            ]
            
            example["text"] = guarani_text
            example["tokens"] = tokens
            example = set_hashes(example)
            
            example["html"] = f"""
            <div style="max-width: 900px; margin: 0 auto; padding: 10px; font-family: 'Segoe UI', Arial, sans-serif;">
                
                <!-- Header compacto -->
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">
                    <h4 style="margin: 0; font-size: 15px;">🏷️ Anotación Gramatical v2 (Multi-anotador)</h4>
                </div>
                
                <!-- Referencia en Español -->
                <div style="background: #fef3c7; padding: 10px 12px; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #f59e0b;">
                    <strong style="color: #92400e; font-size: 12px;">🇪🇸 Referencia:</strong>
                    <span style="color: #78350f; font-size: 13px; margin-left: 8px;">{spanish_text}</span>
                </div>
                
                <!-- Validación requerida -->
                <div style="background: #fef2f2; padding: 8px 12px; border-radius: 6px; font-size: 11px; color: #991b1b; margin-bottom: 10px; border-left: 3px solid #dc2626;">
                    <strong>✅ Obligatorio:</strong> Marca al menos 1 SUJETO y 1 VERBO para aceptar
                </div>
                
                <!-- Tip de uso -->
                <div style="background: #f0f9ff; padding: 8px 12px; border-radius: 6px; font-size: 11px; color: #0c4a6e; margin-bottom: 10px;">
                    <strong>💡 Guía rápida:</strong> SUJETO (¿quién?) · VERBO (acción) · OBJETO (¿qué/quién?) · Otros según necesites
                </div>
                
            </div>
            """
            yield example
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": prepare_for_pos(stream),
        "validate_answer": validate_answer,  # ← Validación en tiempo real
        "task_router": task_router_iaa,       # ← Task routing para IAA
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "ner_manual"}
            ],
            "labels": [
                "SUJETO",
                "VERBO",
                "OBJETO",
                "SUSTANTIVO",
                "ADJETIVO",
                "ADVERBIO",
                "PRONOMBRE",
                "PREPOSICIÓN",
                "ARTÍCULO",
                "CONJUNCIÓN"
            ],
            # Configuración para multi-anotador
            "feed_overlap": False,  # El task_router maneja el overlap
            "instant_submit": False  # Requiere click en Accept (para validación)
        }
    }
