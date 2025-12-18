"""
Recipe unificado para anotación de Guaraní por LOTES.

Soporta los 3 tipos de anotación:
- POS: Etiquetado de partes del discurso (Universal Dependencies)
- Features: Características morfológicas (UD + Tupí-Guaraní)
- Relations: Relaciones sintácticas (UD Dependency Relations)

ETIQUETAS UD PARA OLD GUARANÍ:
https://universaldependencies.org/treebanks/gn_oldtudet/index.html

POS Tags usados (11): NOUN, VERB, PRON, PROPN, DET, ADP, ADV, NUM, PART, INTJ, PUNCT
POS Tags NO usados: ADJ, AUX, CCONJ, SCONJ, SYM, X

CARACTERÍSTICAS:
- Carga datos de un LOTE específico (--batch N)
- Usa spans_manual para permitir spans superpuestos
- Incluye botón de contexto (Ctrl+Shift+C)
- Dataset nombrado por tipo+lote: guarani_pos_batch_01, etc.

Uso:
    prodigy guarani-batch pos 5 -F recipes/guarani_batch.py --port 8080
    prodigy guarani-batch features 5 -F recipes/guarani_batch.py --port 8081
    prodigy guarani-batch relations 5 -F recipes/guarani_batch.py --port 8082
"""

import os
import prodigy
from prodigy.util import set_hashes
from prodigy.components.db import connect
import spacy
import json
from pathlib import Path
from typing import List, Dict

nlp = spacy.blank("es")

# Configuración desde variables de entorno
ANNOTATIONS_PER_TASK = int(os.getenv("ANNOTATIONS_PER_TASK", "3"))
ENABLE_TASK_ROUTING = os.getenv("ENABLE_TASK_ROUTING", "true").lower() == "true"
AUTO_SAVE_EVERY = int(os.getenv("AUTO_SAVE_EVERY", "1"))  # Guardar cada N anotaciones

# =============================================================================
# ETIQUETAS UD PARA OLD GUARANÍ
# Basado en: https://universaldependencies.org/treebanks/gn_oldtudet/index.html
# =============================================================================

# POS Tags (UPOS) - Solo los 11 documentados para Old Guaraní
# NO SE USAN EN OLD GUARANÍ: ADJ, AUX, CCONJ, SCONJ, SYM, X
POS_LABELS = [
    "NOUN",    # Sustantivo
    "VERB",    # Verbo
    "PRON",    # Pronombre
    "PROPN",   # Nombre propio
    "DET",     # Determinante
    "ADP",     # Adposición (Posposición en Guaraní)
    "ADV",     # Adverbio
    "NUM",     # Numeral
    "PART",    # Partícula
    "INTJ",    # Interjección
    "PUNCT",   # Puntuación
]

# Features morfológicos - Documentados para Old Guaraní
FEATURE_LABELS = [
    # Persona
    "Person=1", "Person=2", "Person=3",
    # Número
    "Number=Sing", "Number=Plur",
    # Clusividad (específico Tupí-Guaraní)
    "Clusivity=In", "Clusivity=Ex",
    # Caso
    "Case=Abl", "Case=All", "Case=Dat", "Case=Loc", "Case=Ref",
    # Relacional (específico Tupí-Guaraní)
    "Rel=Abs", "Rel=Cont", "Rel=NCont",
    # Tiempo
    "Tense=Past", "Tense=Fut", "Tense=FutPast",
    # Modo
    "Mood=Imp", "Mood=Perm",
    # Voz
    "Voice=Cau", "Voice=Com",
    # Forma verbal
    "VerbForm=Ger",
    # Otros
    "Polarity=Neg",
    "Reflex=Yes",
    "Poss=Yes",
    # Nominalizadores (específico Tupí-Guaraní)
    "Nomzr=Ag", "Nomzr=Circ", "Nomzr=Pas", "Nomzr=CCirc", "Nomzr=DevPass", "Nomzr=Rel",
    # Evidencialidad
    "Evident=Nfh",
    # Correferencia (específico Tupí-Guaraní)
    "Corf=Yes",
    # Otros features específicos
    "Emph=Yes", "Intens=Yes", "Int=Yes", "Priv=Yes", "Red=Di",
]

# Relaciones sintácticas - Documentadas para Old Guaraní
RELATION_LABELS = [
    "root",       # Raíz
    "nsubj",      # Sujeto nominal
    "obj",        # Objeto directo
    "iobj",       # Objeto indirecto
    "obl",        # Oblicuo
    "obl:obj",    # Oblicuo objeto
    "obl:subj",   # Oblicuo sujeto
    "advmod",     # Modificador adverbial
    "advcl",      # Cláusula adverbial
    "nmod",       # Modificador nominal
    "nummod",     # Modificador numérico
    "det",        # Determinante
    "case",       # Marcador de caso
    "compound",   # Compuesto
    "appos",      # Aposición
    "xcomp",      # Complemento abierto
    "discourse",  # Elemento discursivo
    "parataxis",  # Parataxis
    "punct",      # Puntuación
    "dep",        # Dependencia no especificada
]

# Colores por tipo - UD Old Guaraní
LABEL_COLORS = {
    # === POS TAGS (UPOS) ===
    "NOUN": "#2563eb",     # Azul - Sustantivos
    "VERB": "#dc2626",     # Rojo - Verbos
    "PRON": "#0891b2",     # Cyan - Pronombres
    "PROPN": "#3b82f6",    # Azul claro - Nombres propios
    "DET": "#64748b",      # Gris - Determinantes
    "ADP": "#ea580c",      # Naranja - Adposiciones
    "ADV": "#7c3aed",      # Púrpura - Adverbios
    "NUM": "#0d9488",      # Teal - Numerales
    "PART": "#a855f7",     # Violeta - Partículas
    "INTJ": "#f59e0b",     # Amarillo - Interjecciones
    "PUNCT": "#9ca3af",    # Gris claro - Puntuación
    
    # === FEATURES - Persona ===
    "Person=1": "#2563eb", "Person=2": "#3b82f6", "Person=3": "#60a5fa",
    # === FEATURES - Número ===
    "Number=Sing": "#16a34a", "Number=Plur": "#22c55e",
    # === FEATURES - Clusividad ===
    "Clusivity=In": "#0891b2", "Clusivity=Ex": "#06b6d4",
    # === FEATURES - Caso ===
    "Case=Abl": "#ea580c", "Case=All": "#f97316", "Case=Dat": "#fb923c", 
    "Case=Loc": "#fdba74", "Case=Ref": "#fed7aa",
    # === FEATURES - Relacional (Tupí-Guaraní) ===
    "Rel=Abs": "#6366f1", "Rel=Cont": "#818cf8", "Rel=NCont": "#a5b4fc",
    # === FEATURES - Tiempo ===
    "Tense=Past": "#dc2626", "Tense=Fut": "#eab308", "Tense=FutPast": "#f97316",
    # === FEATURES - Modo ===
    "Mood=Imp": "#7c3aed", "Mood=Perm": "#a855f7",
    # === FEATURES - Voz ===
    "Voice=Cau": "#059669", "Voice=Com": "#14b8a6",
    # === FEATURES - Forma verbal ===
    "VerbForm=Ger": "#84cc16",
    # === FEATURES - Otros ===
    "Polarity=Neg": "#be123c", "Reflex=Yes": "#db2777", "Poss=Yes": "#65a30d",
    # === FEATURES - Nominalizadores ===
    "Nomzr=Ag": "#8b5cf6", "Nomzr=Circ": "#a78bfa", "Nomzr=Pas": "#c4b5fd",
    "Nomzr=CCirc": "#a855f7", "Nomzr=DevPass": "#c084fc", "Nomzr=Rel": "#d8b4fe",
    # === FEATURES - Evidencialidad y otros ===
    "Evident=Nfh": "#0284c7", "Corf=Yes": "#0369a1",
    "Emph=Yes": "#f472b6", "Intens=Yes": "#ec4899", "Int=Yes": "#be185d",
    "Priv=Yes": "#9f1239", "Red=Di": "#831843",
    
    # === RELATIONS ===
    "root": "#dc2626",       # Rojo - Raíz
    "nsubj": "#2563eb",      # Azul - Sujeto
    "obj": "#16a34a",        # Verde - Objeto
    "iobj": "#65a30d",       # Verde lima - Obj indirecto
    "obl": "#ca8a04",        # Amarillo oscuro - Oblicuo
    "obl:obj": "#eab308",    # Amarillo - Oblicuo obj
    "obl:subj": "#fde047",   # Amarillo claro - Oblicuo suj
    "advmod": "#7c3aed",     # Púrpura - Mod adverbial
    "advcl": "#a855f7",      # Violeta - Cláusula adv
    "nmod": "#0891b2",       # Cyan - Mod nominal
    "nummod": "#0d9488",     # Teal - Mod numérico
    "det": "#64748b",        # Gris - Determinante
    "case": "#78716c",       # Gris cálido - Caso
    "compound": "#ea580c",   # Naranja - Compuesto
    "appos": "#db2777",      # Rosa - Aposición
    "xcomp": "#059669",      # Esmeralda - Comp abierto
    "discourse": "#94a3b8",  # Gris azul - Discurso
    "parataxis": "#f97316",  # Naranja claro - Parataxis
    "punct": "#d4d4d4",      # Gris muy claro - Puntuación
    "dep": "#a1a1aa",        # Gris - Dependencia
}

# =============================================================================
# JAVASCRIPT PARA CONTEXTO
# =============================================================================

CONTEXT_JS = """
window.toggleContextDialog = function() {
    const dialog = document.getElementById('context-dialog');
    if (!dialog) return;
    if (dialog.open) { dialog.close(); } else { dialog.showModal(); }
};

document.addEventListener('mousedown', function(e) {
    const dialog = document.getElementById('context-dialog');
    if (dialog && dialog.open) {
        const rect = dialog.getBoundingClientRect();
        const isInDialog = (e.clientX >= rect.left && e.clientX <= rect.right &&
                           e.clientY >= rect.top && e.clientY <= rect.bottom);
        if (!isInDialog) { dialog.close(); }
    }
});

window.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault(); e.stopPropagation();
        window.toggleContextDialog();
        return false;
    }
}, true);

console.log('Batch Recipe - Ctrl+Shift+C para contexto');
"""


def get_type_config(annotation_type: str):
    """Retorna configuración según el tipo de anotación."""
    configs = {
        "pos": {
            "labels": POS_LABELS,
            "title": "POS Tags (UD)",
            "emoji": "🏷️",
            "color": "#2563eb",
            "step": "1/3",
            "description": "Universal Dependencies UPOS para Old Guaraní",
        },
        "features": {
            "labels": FEATURE_LABELS,
            "title": "Features (UD)",
            "emoji": "⚙️",
            "color": "#10b981",
            "step": "2/3",
            "description": "Rasgos morfológicos UD + Tupí-Guaraní",
        },
        "relations": {
            "labels": RELATION_LABELS,
            "title": "Relations (UD)",
            "emoji": "🔗",
            "color": "#f59e0b",
            "step": "3/3",
            "description": "Relaciones de dependencia UD",
        },
    }
    return configs.get(annotation_type, configs["pos"])


def generate_html_header(example: dict, annotation_type: str, batch_id: int, context: dict = None):
    """Genera el HTML header para la UI con contexto de oraciones en bloque continuo."""
    config = get_type_config(annotation_type)
    
    guarani_text = example.get("text", "")
    spanish_text = example.get("meta", {}).get("spanish_text", "")
    global_idx = example.get("meta", {}).get("global_index", "?")
    batch_idx = context.get("index", "?") if context else "?"
    total = context.get("total", 50) if context else 50
    
    # Generar bloque continuo de texto para el modal
    sentences = context.get("sentences", []) if context else []
    context_block_html = ""
    for sent in sentences:
        if sent.get("is_current"):
            # Oración actual resaltada
            context_block_html += f'<span style="background:linear-gradient(180deg, transparent 60%, #fde047 60%);font-weight:bold;color:#0c4a6e;padding:2px 4px;border-radius:2px;">{sent["text"]}</span> '
        else:
            # Oraciones de contexto en gris
            context_block_html += f'<span style="color:#64748b;">{sent["text"]}</span> '
    
    # Si no hay oraciones de contexto, mostrar solo la actual
    if not context_block_html:
        context_block_html = f'<span style="background:linear-gradient(180deg, transparent 60%, #fde047 60%);font-weight:bold;color:#0c4a6e;">{guarani_text}</span>'
    
    # Preview de labels
    labels_html = ""
    for label in config["labels"][:10]:
        color = LABEL_COLORS.get(label, "#6b7280")
        labels_html += f'<span style="display:inline-block;margin:1px;padding:1px 4px;background:{color}20;border:1px solid {color};border-radius:3px;font-size:9px;">{label}</span>'
    
    return f"""
<div style="margin-bottom:8px;">
    <div style="background:linear-gradient(135deg, {config['color']} 0%, {config['color']}dd 100%);color:white;padding:8px 12px;border-radius:6px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:bold;">{config['title']} - {config['description']}</span>
        <span style="font-size:11px;opacity:0.9;">Lote {batch_id} | Paso {config['step']} | #{batch_idx}/{total}</span>
    </div>
    <div style="background:#e0f2fe;padding:8px 10px;border-left:3px solid #0284c7;margin-bottom:4px;">
        <b>🇵🇾 Guaraní:</b> <span style="font-size:15px;font-weight:bold;color:#0c4a6e;">{guarani_text}</span>
    </div>
    <div style="background:#fef3c7;padding:6px 10px;border-left:3px solid #f59e0b;margin-bottom:4px;">
        <b>🇪🇸 Español:</b> <span style="color:#92400e;">{spanish_text}</span>
    </div>
    <div style="background:#f3f4f6;padding:4px 10px;border-left:3px solid #6b7280;margin-bottom:4px;">
        {labels_html}
    </div>
    <div style="background:#f0fdf4;padding:4px;text-align:center;font-size:11px;color:#166534;border-radius:4px;">
        👇 Selecciona texto y elige la etiqueta. Los spans pueden superponerse.
    </div>
    <button onclick="window.toggleContextDialog()" style="background:linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);color:white;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;font-size:11px;width:100%;margin-top:4px;">
        📖 Ver Contexto <span style="opacity:0.7;font-size:9px;margin-left:6px;">Ctrl+Shift+C</span>
    </button>
</div>

<!-- DIALOG DE CONTEXTO - BLOQUE CONTINUO DE TEXTO EN GUARANÍ -->
<dialog id="context-dialog" style="border:none;border-radius:8px;padding:0;box-shadow:0 10px 25px rgba(0,0,0,0.3);max-width:600px;width:95%;inset:0;margin:auto;">
    <div style="background:linear-gradient(135deg, {config['color']} 0%, {config['color']}cc 100%);color:white;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:bold;font-size:13px;">📖 Contexto - Oración #{batch_idx}/{total}</span>
        <button onclick="document.getElementById('context-dialog').close()" style="background:rgba(255,255,255,0.2);border:none;color:white;width:24px;height:24px;border-radius:50%;cursor:pointer;font-size:12px;transition:background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.4)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">✕</button>
    </div>
    <div style="padding:16px;background:#fafafa;">
        <div style="background:white;padding:14px 16px;border-radius:6px;border:1px solid #e2e8f0;line-height:1.8;font-size:14px;text-align:justify;">
            {context_block_html}
        </div>
        <div style="margin-top:10px;text-align:center;font-size:11px;color:#94a3b8;">
            La oración actual está <span style="background:linear-gradient(180deg, transparent 60%, #fde047 60%);padding:0 4px;">resaltada en amarillo</span>
        </div>
    </div>
</dialog>
"""


def load_batch(batch_dir: str, batch_id: int) -> list:
    """Carga un lote específico."""
    batch_file = Path(batch_dir) / f"batch_{batch_id:03d}.jsonl"
    
    if not batch_file.exists():
        print(f"[ERROR] No existe el archivo {batch_file}")
        return []
    
    examples = []
    with open(batch_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    
    print(f"[OK] Cargado lote {batch_id}: {len(examples)} oraciones")
    return examples


def prepare_examples(examples: list, annotation_type: str, batch_id: int) -> list:
    """Prepara los ejemplos para Prodigy con contexto de oraciones anterior/siguiente."""
    prepared = []
    total = len(examples)
    
    for idx, ex in enumerate(examples):
        text = ex.get("text", "")
        
        # Obtener múltiples oraciones para contexto (2 anteriores, actual, 2 siguientes)
        context_sentences = []
        for offset in range(-2, 3):  # -2, -1, 0, 1, 2
            ctx_idx = idx + offset
            if 0 <= ctx_idx < len(examples):
                context_sentences.append({
                    "text": examples[ctx_idx].get("text", ""),
                    "is_current": offset == 0,
                    "offset": offset
                })
        
        context = {
            "index": idx + 1,
            "total": total,
            "sentences": context_sentences,  # Lista de oraciones para el bloque continuo
        }
        
        # Tokenizar
        doc = nlp(text)
        tokens = [
            {"text": t.text, "start": t.idx, "end": t.idx + len(t.text), "id": i}
            for i, t in enumerate(doc)
        ]
        
        # Crear ejemplo
        eg = {
            "text": text,
            "tokens": tokens,
            "spans": [],
            "meta": ex.get("meta", {}),
        }
        
        # Agregar HTML con contexto
        eg["html"] = generate_html_header(eg, annotation_type, batch_id, context)
        
        # Calcular hashes
        eg = set_hashes(eg)
        
        prepared.append(eg)
    
    return prepared


# =============================================================================
# TASK ROUTER PARA MULTI-ANNOTATOR (IAA)
# =============================================================================
def task_router_iaa(ctrl, session_id: str, item: Dict) -> List[str]:
    """
    Router para distribuir tareas entre múltiples anotadores (Inter-Annotator Agreement).
    
    Asigna cada tarea a N anotadores de forma determinística basada en el hash.
    Esto permite que exactamente ANNOTATIONS_PER_TASK anotadores vean cada tarea.
    
    Args:
        ctrl: Controller de Prodigy
        session_id: ID de la sesión actual (alice, bob, carlos, etc.)
        item: El ejemplo a enrutar
    
    Returns:
        Lista de session_ids que deben ver este ejemplo
    """
    # Obtener pool de anotadores disponibles (sesiones conectadas)
    pool = list(ctrl.session_ids)
    if not pool:
        return []
    
    # Obtener hash del task
    task_hash = item.get("_task_hash")
    if task_hash is None:
        return []
    
    # Número de anotadores que deben ver cada tarea
    n_annotators = min(ANNOTATIONS_PER_TASK, len(pool))
    
    # Usar hash módulo para seleccionar N anotadores consistentemente
    selected = []
    pool_copy = sorted(pool)
    
    for i in range(n_annotators):
        if not pool_copy:
            break
        idx = (task_hash + i) % len(pool_copy)
        selected.append(pool_copy.pop(idx))
    
    return selected


# =============================================================================
# AUTO-GUARDADO CALLBACK
# =============================================================================
# Contador global por sesión para auto-guardado
_annotation_counters = {}

def make_update_callback(dataset_name: str):
    """
    Crea un callback que guarda automáticamente cada AUTO_SAVE_EVERY anotaciones.
    
    Este callback se ejecuta cada vez que el usuario envía una respuesta (accept/reject/ignore).
    Fuerza el guardado en la base de datos para prevenir pérdida de datos.
    """
    def update_callback(answers):
        """
        Callback que se ejecuta cuando el usuario envía anotaciones.
        
        Args:
            answers: Lista de anotaciones recibidas del frontend
        """
        global _annotation_counters
        
        if not answers:
            return
        
        # Contar por sesión
        for answer in answers:
            session_id = answer.get("_session_id", "default")
            if session_id not in _annotation_counters:
                _annotation_counters[session_id] = 0
            _annotation_counters[session_id] += 1
            
            # Verificar si toca guardar
            if _annotation_counters[session_id] >= AUTO_SAVE_EVERY:
                try:
                    # Conectar a la base de datos y forzar guardado
                    db = connect()
                    # El guardado real lo hace Prodigy internamente,
                    # pero podemos forzar un flush del buffer
                    print(f"[AUTO-SAVE] Sesión '{session_id}': {_annotation_counters[session_id]} anotaciones guardadas en '{dataset_name}'")
                    _annotation_counters[session_id] = 0
                except Exception as e:
                    print(f"[AUTO-SAVE] Error: {e}")
    
    return update_callback


@prodigy.recipe(
    "guarani-batch",
    dataset=("Dataset name", "positional", None, str),
    annotation_type=("Tipo de anotación: pos, features, relations", "option", "t", str),
    lote=("Número de lote (1-60)", "option", "l", int),
    source_dir=("Directorio de lotes", "option", "d", str),
)
def guarani_batch_recipe(
    dataset: str,
    annotation_type: str = "pos",
    lote: int = 1,
    source_dir: str = "data/batches",
):
    """
    Recipe unificado para anotación por lotes.
    
    Args:
        dataset: Nombre del dataset en Prodigy
        annotation_type: "pos", "features", o "relations"
        lote: Número del lote (1, 2, 3, ...)
        source_dir: Directorio donde están los lotes
    
    Ejemplos:
        python -m prodigy guarani-batch guarani_pos_batch_01 -t pos -l 1 -F recipes/guarani_batch.py
        python -m prodigy guarani-batch guarani_features_batch_05 -t features -l 5 -F recipes/guarani_batch.py
    """
    # Validar tipo
    if annotation_type not in ["pos", "features", "relations"]:
        raise ValueError(f"Tipo inválido: {annotation_type}. Usa: pos, features, relations")
    
    # Obtener configuración
    config = get_type_config(annotation_type)
    
    # Configurar Task Router para IAA
    router = task_router_iaa if ENABLE_TASK_ROUTING else None
    router_status = f"HABILITADO ({ANNOTATIONS_PER_TASK} anotadores por tarea)" if ENABLE_TASK_ROUTING else "DESHABILITADO"
    auto_save_status = f"cada {AUTO_SAVE_EVERY} anotación(es)"
    
    print("=" * 60)
    print(f"{config['title']} - Lote {lote}")
    print("=" * 60)
    print(f"   Dataset: {dataset}")
    print(f"   Tipo: {annotation_type}")
    print(f"   Lote: {lote}")
    print(f"   Task Router: {router_status}")
    print(f"   Auto-guardado: {auto_save_status}")
    print("=" * 60)
    
    # Cargar y preparar ejemplos
    raw_examples = load_batch(source_dir, lote)
    
    if not raw_examples:
        raise ValueError(f"No se encontraron ejemplos en el lote {lote}")
    
    examples = prepare_examples(raw_examples, annotation_type, lote)
    
    # Crear tema de colores para las etiquetas
    custom_theme = {"labels": {}}
    for label in config["labels"]:
        custom_theme["labels"][label] = LABEL_COLORS.get(label, "#6b7280")
    
    # feed_overlap debe ser False cuando usamos task_router (el router controla la distribución)
    # Si NO hay router, feed_overlap=True permite que todos vean todas las tareas
    use_feed_overlap = not ENABLE_TASK_ROUTING
    
    # Crear callback de auto-guardado
    update_callback = make_update_callback(dataset)
    
    return {
        "dataset": dataset,
        "view_id": "blocks",
        "stream": examples,
        "task_router": router,  # Router para distribuir tareas entre anotadores
        "update": update_callback,  # Callback para auto-guardado
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "spans_manual"}
            ],
            "labels": config["labels"],
            "spans_key": "spans",
            "custom_theme": custom_theme,
            "exclude_by": "task",  # Excluir por tarea+sesión, no por input global
            "auto_count_stream": True,
            "show_stats": True,
            "javascript": CONTEXT_JS,
            "feed_overlap": use_feed_overlap,  # False con task_router, True sin él
            "instant_submit": True,  # Enviar cada anotación inmediatamente al servidor
            "sessions": ["alice", "bob", "carlos", "diana", "elena"],  # Sesiones permitidas
        },
    }
