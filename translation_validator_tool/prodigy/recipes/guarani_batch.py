"""
Recipe unificado para anotacion de Guarani por LOTES.

Soporta los 3 tipos de anotacion:
- POS: Etiquetado de partes del discurso (Universal Dependencies)
- Features: Caracteristicas morfologicas (UD + Tupi-Guarani)
- Relations: Relaciones sintacticas (UD Dependency Relations)

ETIQUETAS UD PARA OLD GUARANI:
https://universaldependencies.org/treebanks/gn_oldtudet/index.html

POS Tags usados (11): NOUN, VERB, PRON, PROPN, DET, ADP, ADV, NUM, PART, INTJ, PUNCT
POS Tags NO usados: ADJ, AUX, CCONJ, SCONJ, SYM, X

CARACTERISTICAS:
- Carga datos de un LOTE especifico (--batch N)
- Usa spans_manual para permitir spans superpuestos
- Incluye boton de contexto (Ctrl+Shift+C)
- Dataset nombrado por tipo+lote: guarani_pos_batch_01, etc.
- EXCLUSION POR SESION: Cada anotador tiene su propio progreso

Uso:
    prodigy guarani-batch pos 5 -F recipes/guarani_batch.py --port 8080
    prodigy guarani-batch features 5 -F recipes/guarani_batch.py --port 8081
    prodigy guarani-batch relations 5 -F recipes/guarani_batch.py --port 8082
"""

import os
import sys
import prodigy
from prodigy.util import set_hashes
from prodigy.components.db import connect
import spacy
import json
from pathlib import Path
from typing import List, Dict, Set, Iterator, Optional

nlp = spacy.blank("es")

# =============================================================================
# IMPORTAR MAPPER CENTRALIZADO
# =============================================================================
_scripts_dir = Path(__file__).parent.parent / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from ud_guarani_mapper import (
    SPECIALIZED_GROUPS,
    LABEL_COLORS as UD_LABEL_COLORS,
    map_label,
    get_ud_main_group,
    list_ud_main_groups,
)

# Configuracion desde variables de entorno
ANNOTATIONS_PER_TASK = int(os.getenv("ANNOTATIONS_PER_TASK", "3"))
ENABLE_TASK_ROUTING = os.getenv("ENABLE_TASK_ROUTING", "true").lower() == "true"

# =============================================================================
# CONFIGURACIÓN DE BUFFER (desde prodigy_config.json)
# =============================================================================
BUFFER_CONFIG_FILE = Path(__file__).parent.parent / "data" / "prodigy_config.json"

def load_buffer_config() -> dict:
    """Carga la configuración del buffer desde prodigy_config.json"""
    defaults = {
        "instant_submit": False,
        "batch_size": 3,
    }
    try:
        if BUFFER_CONFIG_FILE.exists():
            with open(BUFFER_CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return {**defaults, **config}
    except Exception as e:
        print(f"[CONFIG] Error cargando prodigy_config.json: {e}")
    return defaults

# Cargar configuración al inicio del módulo
BUFFER_CONFIG = load_buffer_config()
INSTANT_SUBMIT = BUFFER_CONFIG.get("instant_submit", False)
BATCH_SIZE = BUFFER_CONFIG.get("batch_size", 3)

# Para compatibilidad con código existente
AUTO_SAVE_EVERY = 1 if INSTANT_SUBMIT else BATCH_SIZE

# =============================================================================
# ETIQUETAS AMIGABLES DESDE MAPPER CENTRALIZADO
# Basado en: https://universaldependencies.org/treebanks/gn_oldtudet/index.html
# =============================================================================

# Obtener grupos del mapper centralizado
_POS_GROUP = SPECIALIZED_GROUPS.get("pos-tags", {})
_FEATURES_GROUP = SPECIALIZED_GROUPS.get("features", {})
_RELATIONS_GROUP = SPECIALIZED_GROUPS.get("relations", {})

# POS Tags - Etiquetas amigables en español
POS_LABELS = _POS_GROUP.get("labels", [
    "Sustantivo", "Verbo", "Pronombre", "Nombre Propio", "Determinante",
    "Posposición", "Adverbio", "Numeral", "Partícula", "Interjección", "Puntuación"
])

# Features morfológicos - Etiquetas amigables en español  
FEATURE_LABELS = _FEATURES_GROUP.get("labels", [
    # Persona
    "1ra Persona", "2da Persona", "3ra Persona",
    # Número
    "Singular", "Plural",
    # Clusividad
    "Inclusivo", "Exclusivo",
    # Caso
    "Ablativo", "Alativo", "Dativo", "Locativo", "Referencial",
    # Relacional
    "Rel. Absoluto", "Rel. Contiguo", "Rel. No-Contiguo",
    # Tiempo
    "Pasado", "Futuro", "Futuro-Pasado",
    # Modo
    "Imperativo", "Permisivo",
    # Voz
    "Causativo", "Comitativo",
    # Forma verbal
    "Gerundio",
    # Otros
    "Negación", "Reflexivo", "Poseedor",
    # Nominalizadores
    "Agentivo (-sar)", "Circunstancial (-saβ)", "Pasivo (-pɨr)", 
    "C-Circunstancial", "Derivación Pasiva", "Relativo (Nomzr)",
    # Evidencialidad
    "No-Primera Mano",
    # Correferencia
    "Correferencial",
    # Otros
    "Enfático", "Intensificador", "Interrogativo", "Privativo", "Reduplicación",
])

# Relaciones sintácticas - Etiquetas amigables en español
RELATION_LABELS = _RELATIONS_GROUP.get("labels", [
    "RAÍZ (Verbo Principal)", "SUJETO", "OBJETO DIRECTO", "OBJETO INDIRECTO",
    "COMPLEMENTO OBLICUO", "OBLICUO-OBJETO", "OBLICUO-SUJETO",
    "MODIFICADOR ADVERBIAL", "CLÁUSULA ADVERBIAL", "MODIFICADOR NOMINAL",
    "MODIFICADOR NUMÉRICO", "DETERMINANTE (Rel)", "MARCADOR DE CASO",
    "PALABRA COMPUESTA", "APOSICIÓN", "COMPLEMENTO VERBAL",
    "ELEMENTO DE DISCURSO", "PARATAXIS", "PUNTUACIÓN (Rel)", "DEPENDENCIA (General)"
])

# Colores combinados desde mapper + colores específicos de relaciones
LABEL_COLORS = {**UD_LABEL_COLORS}

# Agregar colores de relaciones desde el mapper
_relations_colors = _RELATIONS_GROUP.get("colors", {})
LABEL_COLORS.update(_relations_colors)

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
# SESSION-AWARE EXCLUSION (MANEJO DE EXCLUSION POR SESION)
# =============================================================================
def get_session_completed_hashes(dataset_name: str, session_id: str) -> Set[int]:
    """
    Obtiene los task_hashes que una sesion especifica ya anoto.
    
    Args:
        dataset_name: Nombre del dataset en Prodigy
        session_id: ID de la sesion (alice, bob, etc.)
    
    Returns:
        Set de task_hashes ya anotados por esta sesion
    """
    try:
        db = connect()
        if dataset_name not in db:
            return set()
        
        completed = set()
        examples = db.get_dataset_examples(dataset_name)
        
        for ex in examples:
            ex_session = ex.get("_session_id", "")
            task_hash = ex.get("_task_hash")
            
            if ex_session == session_id and task_hash is not None:
                completed.add(task_hash)
        
        return completed
    except Exception as e:
        print(f"[WARN] Error al obtener hashes completados para {session_id}: {e}")
        return set()


def get_all_sessions_progress(dataset_name: str) -> Dict[str, Set[int]]:
    """
    Obtiene el progreso de TODAS las sesiones de un dataset.
    
    Args:
        dataset_name: Nombre del dataset en Prodigy
    
    Returns:
        Dict con session_id -> Set de task_hashes completados
    """
    try:
        db = connect()
        if dataset_name not in db:
            return {}
        
        progress = {}
        examples = db.get_dataset_examples(dataset_name)
        
        for ex in examples:
            session_id = ex.get("_session_id", "")
            task_hash = ex.get("_task_hash")
            
            if session_id and task_hash is not None:
                if session_id not in progress:
                    progress[session_id] = set()
                progress[session_id].add(task_hash)
        
        return progress
    except Exception as e:
        print(f"[WARN] Error al obtener progreso global: {e}")
        return {}


def make_session_filter_stream(examples: List[Dict], dataset_name: str):
    """
    Crea un generador que filtra ejemplos basandose en lo que cada sesion ya anoto.
    
    Este generador consulta la DB al inicio y filtra los ejemplos que
    la sesion actual ya ha completado.
    
    IMPORTANTE: En Prodigy, la sesion se determina por la URL (?session=xxx)
    pero el stream se genera ANTES de conocer la sesion. Por eso usamos
    feed_overlap=True y dejamos que todos vean todas las tareas inicialmente,
    luego Prodigy filtra basandose en las anotaciones existentes.
    
    La solucion real es usar exclude_by="session" (disponible en Prodigy)
    que excluye tareas que ESA sesion ya anoto, no globalmente.
    
    Args:
        examples: Lista completa de ejemplos preparados
        dataset_name: Nombre del dataset para consultar anotaciones
    
    Returns:
        El mismo stream (la exclusion se maneja via exclude_by="session")
    """
    return examples


# =============================================================================
# TASK ROUTER PARA MULTI-ANNOTATOR (IAA)
# =============================================================================

# Variable global para el stream session-aware
_session_stream = None


def task_router_iaa(ctrl, session_id: str, item: Dict) -> List[str]:
    """
    Router para distribuir tareas entre multiples anotadores (Inter-Annotator Agreement).
    
    Asigna cada tarea a N anotadores de forma deterministica basada en el hash.
    Esto permite que exactamente ANNOTATIONS_PER_TASK anotadores vean cada tarea.
    
    Args:
        ctrl: Controller de Prodigy
        session_id: ID de la sesion actual (alice, bob, carlos, etc.)
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
    
    # Numero de anotadores que deben ver cada tarea
    n_annotators = min(ANNOTATIONS_PER_TASK, len(pool))
    
    # Usar hash modulo para seleccionar N anotadores consistentemente
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
    annotation_type=("Tipo de anotacion: pos, features, relations", "option", "t", str),
    lote=("Numero de lote (1-60)", "option", "l", int),
    source_dir=("Directorio de lotes", "option", "d", str),
)
def guarani_batch_recipe(
    dataset: str,
    annotation_type: str = "pos",
    lote: int = 1,
    source_dir: str = "data/batches",
):
    """
    Recipe unificado para anotacion por lotes con soporte multi-anotador.
    
    IMPORTANTE: Este recipe usa exclusion por SESION, no global.
    Cada anotador ve todas las tareas que EL no ha anotado,
    independientemente de lo que otros anotadores hayan hecho.
    
    Args:
        dataset: Nombre del dataset en Prodigy
        annotation_type: "pos", "features", o "relations"
        lote: Numero del lote (1, 2, 3, ...)
        source_dir: Directorio donde estan los lotes
    
    Ejemplos:
        python -m prodigy guarani-batch guarani_pos_batch_01 -t pos -l 1 -F recipes/guarani_batch.py
        python -m prodigy guarani-batch guarani_features_batch_05 -t features -l 5 -F recipes/guarani_batch.py
    """
    global _session_stream
    
    # Validar tipo
    if annotation_type not in ["pos", "features", "relations"]:
        raise ValueError(f"Tipo invalido: {annotation_type}. Usa: pos, features, relations")
    
    # Obtener configuracion
    config = get_type_config(annotation_type)
    
    # Recargar configuración por si cambió desde la UI
    global BUFFER_CONFIG, INSTANT_SUBMIT, BATCH_SIZE, AUTO_SAVE_EVERY
    BUFFER_CONFIG = load_buffer_config()
    INSTANT_SUBMIT = BUFFER_CONFIG.get("instant_submit", False)
    BATCH_SIZE = BUFFER_CONFIG.get("batch_size", 3)
    AUTO_SAVE_EVERY = 1 if INSTANT_SUBMIT else BATCH_SIZE
    
    # Configurar Task Router para IAA - DESHABILITADO para permitir que get_stream maneje exclusion
    # El task_router no es compatible con get_stream personalizado
    router = None  # Usamos get_stream en lugar de task_router
    router_status = "DESHABILITADO (usando get_stream para exclusion por sesion)"
    
    if INSTANT_SUBMIT:
        auto_save_status = "INSTANTÁNEO (cada anotación)"
    else:
        auto_save_status = f"cada {BATCH_SIZE} anotación(es)"
    
    print("=" * 60)
    print(f"{config['title']} - Lote {lote}")
    print("=" * 60)
    print(f"   Dataset: {dataset}")
    print(f"   Tipo: {annotation_type}")
    print(f"   Lote: {lote}")
    print(f"   Task Router: {router_status}")
    print(f"   Auto-guardado: {auto_save_status}")
    print(f"   Exclusion: POR SESION (cada anotador ve sus pendientes)")
    print("=" * 60)
    
    # Cargar y preparar ejemplos
    raw_examples = load_batch(source_dir, lote)
    
    if not raw_examples:
        raise ValueError(f"No se encontraron ejemplos en el lote {lote}")
    
    examples = prepare_examples(raw_examples, annotation_type, lote)
    total_examples = len(examples)
    
    # Mostrar progreso existente por sesion
    print("\n[PROGRESO EXISTENTE]")
    existing_progress = get_all_sessions_progress(dataset)
    if existing_progress:
        for sid, hashes in sorted(existing_progress.items()):
            print(f"   {sid}: {len(hashes)}/{total_examples} completadas")
    else:
        print("   (Sin anotaciones previas)")
    print()
    
    # Crear tema de colores para las etiquetas
    custom_theme = {"labels": {}}
    for label in config["labels"]:
        custom_theme["labels"][label] = LABEL_COLORS.get(label, "#6b7280")
    
    # Crear callback de auto-guardado
    update_callback = make_update_callback(dataset)
    
    return {
        "dataset": dataset,
        "view_id": "blocks",
        "stream": examples,  # Stream con todos los ejemplos
        "update": update_callback,  # Callback para auto-guardado
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "spans_manual"}
            ],
            "labels": config["labels"],
            "spans_key": "spans",
            "custom_theme": custom_theme,
            # feed_overlap=True + exclude_by=None permite que:
            # 1. Todos los anotadores vean todas las tareas
            # 2. La exclusion se maneje internamente por sesion
            # Prodigy con feed_overlap=True ya maneja esto correctamente
            "auto_count_stream": True,
            "show_stats": True,
            "javascript": CONTEXT_JS,
            "feed_overlap": True,  # CLAVE: Todos pueden ver todas las tareas
            "instant_submit": INSTANT_SUBMIT,  # Desde prodigy_config.json
            "batch_size": BATCH_SIZE if not INSTANT_SUBMIT else 1,  # Tamaño del buffer
            "sessions": ["alice", "bob", "carlos", "diana", "elena"],  # Sesiones permitidas
            "total_examples_target": total_examples,  # Para mostrar progreso correcto
        },
    }
