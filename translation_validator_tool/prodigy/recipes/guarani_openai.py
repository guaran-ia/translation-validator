"""
Recipe para anotación ASISTIDA POR OpenAI de textos Guaraní
=============================================================

Este recipe usa OpenAI GPT para pre-anotar automáticamente los morfemas
y etiquetas gramaticales, permitiendo al usuario corregir manualmente.

Características:
- Pre-anotación automática con GPT-4o/GPT-4o-mini
- Etiquetas amigables en español
- Mapeo automático a Universal Dependencies
- Soporte para overlapping spans
- Cache para evitar llamadas repetidas

Uso:
    prodigy guarani-openai dataset ./data/texts.jsonl -F recipes/guarani_openai.py
    prodigy guarani-openai-fetch ./data/texts.jsonl ./data/annotated.jsonl -F recipes/guarani_openai.py
"""

import os
import sys
import json
import hashlib
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from collections import defaultdict

import prodigy
from prodigy.components.loaders import JSONL
from prodigy.util import set_hashes
from prodigy.core import Controller

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / f"openai_recipe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configurar logging a archivo y consola
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("guarani_openai")
logger.info(f"="*60)
logger.info(f"LOG INICIADO: {log_file}")
logger.info(f"="*60)

print(f"\n🔧 LOGS en: {log_file}\n")

# Cargar variables de entorno
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Importar mapper centralizado
_scripts_dir = Path(__file__).parent.parent / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from ud_guarani_mapper import (
    FRIENDLY_TO_UD,
    UD_TO_FRIENDLY,
    LABEL_FAMILIES,
    LABEL_COLORS,
    FAMILY_KEYS,
    map_label,
    get_all_friendly_labels,
    SPECIALIZED_GROUPS,
    UD_MAIN_GROUPS,
    get_specialized_group,
    get_specialized_labels,
    list_specialized_groups,
    get_ud_main_group,
    get_ud_main_labels,
    list_ud_main_groups,
    get_all_ud_ordered_labels,
    get_ud_label_colors,
)

# =============================================================================
# CONFIGURACIÓN DE OPENAI
# =============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("PRODIGY_OPENAI_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))

# =============================================================================
# CONFIGURACIÓN DE TASK ROUTING (para Inter-Annotator Agreement)
# =============================================================================
# Cuántos anotadores deben ver cada tarea
ANNOTATIONS_PER_TASK = int(os.getenv("ANNOTATIONS_PER_TASK", "2"))
# Si el task routing está habilitado
ENABLE_TASK_ROUTING = os.getenv("ENABLE_TASK_ROUTING", "true").lower() == "true"

# Cache para respuestas de OpenAI
CACHE_DIR = Path(__file__).parent.parent / "data" / "openai_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# JAVASCRIPT PARA DIALOG DE CONTEXTO
# =============================================================================
CONTEXT_POPUP_JS = """
// Función para abrir/cerrar el dialog de contexto
window.toggleContextDialog = function() {
    const dialog = document.getElementById('context-dialog');
    if (!dialog) {
        console.log('Dialog not found!');
        return;
    }
    
    if (dialog.open) {
        dialog.close();
    } else {
        dialog.showModal();
        // Centrar relativo al contenedor principal de Prodigy
        const container = document.querySelector('.prodigy-content') || document.querySelector('.prodigy-container') || document.body;
        const rect = container.getBoundingClientRect();
        dialog.style.left = (rect.left + rect.width / 2) + 'px';
    }
};

// Cerrar con click en el backdrop
document.addEventListener('mousedown', function(e) {
    const dialog = document.getElementById('context-dialog');
    if (dialog && dialog.open) {
        const rect = dialog.getBoundingClientRect();
        const isInDialog = (e.clientX >= rect.left && e.clientX <= rect.right &&
                           e.clientY >= rect.top && e.clientY <= rect.bottom);
        if (!isInDialog) {
            dialog.close();
        }
    }
});

// Atajo de teclado: Ctrl+Shift+C para toggle contexto (evita conflictos con Prodigy)
window.addEventListener('keydown', function(e) {
    // Ctrl+Shift+C
    if (e.ctrlKey && e.shiftKey && (e.key === 'c' || e.key === 'C' || e.code === 'KeyC')) {
        e.preventDefault();
        e.stopPropagation();
        window.toggleContextDialog();
        return false;
    }
}, true);  // useCapture = true para capturar antes que Prodigy

console.log('📖 Context Dialog JS loaded. Press Ctrl+Shift+C to open context.');
"""

# =============================================================================
# TASK ROUTER PARA INTER-ANNOTATOR AGREEMENT
# =============================================================================
def task_router_iaa(ctrl: Controller, session_id: str, item: Dict) -> List[str]:
    """
    Task router para inter-annotator agreement.
    Cada ejemplo lo ven exactamente N anotadores (definido por ANNOTATIONS_PER_TASK).
    Usa hashing determinista para asignar consistentemente.
    
    Args:
        ctrl: Controller de Prodigy
        session_id: ID de la sesión actual (alice, bob, etc.)
        item: El ejemplo a enrutar
    
    Returns:
        Lista de session_ids que deben ver este ejemplo
    """
    # Obtener pool de anotadores disponibles
    pool = list(ctrl.session_ids)
    if not pool:
        logger.debug(f"  [ROUTER] Sin sesiones disponibles, retornando vacío")
        return []
    
    # Obtener hash del task (único por oración)
    task_hash = item.get("_task_hash")
    if task_hash is None:
        logger.debug(f"  [ROUTER] Sin _task_hash, retornando vacío")
        return []
    
    # Usar el valor de .env para cuántos anotadores deben ver cada ejemplo
    n_annotators = min(ANNOTATIONS_PER_TASK, len(pool))
    
    # Comprobar cuántas veces ya fue anotado este task
    try:
        examples = ctrl.db.get_dataset(ctrl.dataset)
        hash_count = sum(1 for ex in examples if ex.get("_task_hash") == task_hash)
    except:
        hash_count = 0
    
    # Si ya alcanzó el número deseado, no lo re-rutees
    if hash_count >= n_annotators:
        logger.debug(f"  [ROUTER] Task {task_hash} ya tiene {hash_count}/{n_annotators} anotaciones")
        return []
    
    # Usar hash modulo para seleccionar N anotadores consistentemente
    selected = []
    pool_copy = sorted(pool)  # Ordenar para consistencia
    
    for i in range(n_annotators):
        if not pool_copy:
            break
        idx = (task_hash + i) % len(pool_copy)
        selected.append(pool_copy.pop(idx))
    
    logger.debug(f"  [ROUTER] Task {task_hash} asignado a: {selected}")
    return selected

# =============================================================================
# ETIQUETAS PARA EL PROMPT
# =============================================================================
# Etiquetas que queremos que OpenAI identifique
ANNOTATION_LABELS = {
    # Morfemas
    "Raíz": "La raíz o lexema principal de la palabra",
    "Prefijo": "Prefijo morfológico (antes de la raíz)",
    "Sufijo": "Sufijo morfológico (después de la raíz)",
    
    # Persona
    "1ra Persona": "Marcador de primera persona (a-, che-)",
    "2da Persona": "Marcador de segunda persona (re-, nde-)",
    "3ra Persona": "Marcador de tercera persona (o-, i-, h-)",
    
    # Número
    "Singular": "Número singular",
    "Plural": "Número plural (kuéra, -ita)",
    
    # Clusividad
    "Inclusivo": "Primera persona plural inclusiva (ñande-)",
    "Exclusivo": "Primera persona plural exclusiva (ore-)",
    
    # Tiempo
    "Pasado": "Marcador de tiempo pasado (-kue, -va'ekue)",
    "Futuro": "Marcador de tiempo futuro (-ta, -ne)",
    
    # Modo
    "Imperativo": "Modo imperativo (e-, pe-)",
    "Permisivo": "Modo permisivo/optativo (t-)",
    
    # Negación
    "Negación": "Marcador de negación (nd-...-i, na-...-i)",
    
    # Relacional
    "Rel. Contiguo": "Prefijo relacional contiguo (r-)",
    "Rel. No-Contiguo": "Prefijo relacional no-contiguo (h-, i-)",
    
    # Caso
    "Locativo": "Caso locativo (-pe, -me)",
    "Ablativo": "Caso ablativo/origen (-gui)",
    
    # Categorías
    "Verbo": "Palabra que expresa acción o estado",
    "Sustantivo": "Palabra que nombra entidades",
    "Pronombre": "Palabra que sustituye al sustantivo",
    "Adverbio": "Palabra que modifica al verbo",
    "Posposición": "Palabra que indica relación espacial/temporal",
    "Partícula": "Palabra funcional sin flexión",
}

# =============================================================================
# PROMPT PARA OPENAI
# =============================================================================
SYSTEM_PROMPT = """Eres un experto lingüista especializado en la lengua Guaraní (avañe'ẽ).
Tu tarea es realizar análisis morfológico de oraciones en Guaraní, identificando:
- Morfemas (raíces, prefijos, sufijos)
- Marcadores de persona, número y tiempo
- Categorías gramaticales
- Rasgos especiales del Guaraní (relacionales, clusividad, etc.)

IMPORTANTE:
- El Guaraní es una lengua aglutinante con prefijos y sufijos que se adhieren a la raíz
- Los prefijos personales son: a- (1s), re- (2s), o- (3s), ja-/ña- (1p.incl), ro- (1p.excl), pe- (2p), o- (3p)
- Los prefijos relacionales son: r- (contiguo), h-/i- (no-contiguo), t- (absoluto)
- Los sufijos temporales incluyen: -ta (futuro), -kue (pasado nominal), -va'ekue (pasado)
- La negación se marca con nd-...-i o na-...-i

Analiza el texto y devuelve anotaciones precisas."""

USER_PROMPT_TEMPLATE = """Analiza morfológicamente la siguiente oración en Guaraní:

ORACIÓN GUARANÍ: "{text}"
{spanish_context}

Identifica y anota los siguientes elementos cuando estén presentes:

ETIQUETAS DISPONIBLES Y SUS DEFINICIONES:
{label_definitions}

FORMATO DE RESPUESTA:
Devuelve un JSON con el siguiente formato (SIN explicaciones adicionales):
{{
    "spans": [
        {{"start": <int>, "end": <int>, "label": "<etiqueta>", "text": "<texto>"}},
        ...
    ],
    "analysis": "<breve explicación del análisis>"
}}

REGLAS:
1. "start" y "end" son posiciones de caracteres (0-indexed) en la oración original
2. "text" debe coincidir exactamente con el substring en las posiciones indicadas
3. Las etiquetas deben ser EXACTAMENTE las de la lista (sensible a mayúsculas/tildes)
4. Los spans pueden superponerse (ej: un prefijo puede ser "1ra Persona" y parte del "Verbo")
5. Identifica la Raíz de cada palabra cuando sea posible
6. Marca los prefijos y sufijos que modifiquen la raíz

EJEMPLO para "ahayhu" (yo amo):
{{
    "spans": [
        {{"start": 0, "end": 1, "label": "Prefijo", "text": "a"}},
        {{"start": 0, "end": 1, "label": "1ra Persona", "text": "a"}},
        {{"start": 1, "end": 6, "label": "Raíz", "text": "hayhu"}},
        {{"start": 0, "end": 6, "label": "Verbo", "text": "ahayhu"}}
    ],
    "analysis": "Verbo transitivo 'amar' con prefijo de 1ra persona singular"
}}

Ahora analiza la oración dada:"""


def get_label_definitions() -> str:
    """Genera las definiciones de etiquetas para el prompt."""
    lines = []
    for label, description in ANNOTATION_LABELS.items():
        ud = map_label(label, "to_ud")
        lines.append(f"- {label} ({ud}): {description}")
    return "\n".join(lines)


def get_group_label_definitions(group_name: str) -> str:
    """Genera definiciones de etiquetas para un grupo específico.
    
    Args:
        group_name: Nombre del grupo (morfemas-basicos, categorias, etc.)
    
    Returns:
        String con las definiciones formateadas para el prompt
    """
    group = get_specialized_group(group_name)
    if not group:
        logger.warning(f"Grupo '{group_name}' no encontrado, usando todas las etiquetas")
        return get_label_definitions()
    
    lines = []
    for label in group["labels"]:
        # Buscar descripción en ANNOTATION_LABELS o crear una genérica
        if label in ANNOTATION_LABELS:
            description = ANNOTATION_LABELS[label]
        else:
            # Intentar obtener la descripción del grupo
            description = f"Etiqueta morfológica: {label}"
        ud = map_label(label, "to_ud")
        lines.append(f"- {label} ({ud}): {description}")
    
    return "\n".join(lines)


def get_group_labels_dict(group_name: str) -> Dict[str, str]:
    """Obtiene diccionario de etiquetas para un grupo específico.
    
    Args:
        group_name: Nombre del grupo
    
    Returns:
        Dict con {label: description}
    """
    group = get_specialized_group(group_name)
    if not group:
        return ANNOTATION_LABELS.copy()
    
    result = {}
    for label in group["labels"]:
        if label in ANNOTATION_LABELS:
            result[label] = ANNOTATION_LABELS[label]
        else:
            result[label] = f"Etiqueta morfológica: {label}"
    return result


# =============================================================================
# CLIENTE OPENAI
# =============================================================================
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI no instalado. Ejecutar: pip install openai")


def get_cache_key(text: str, model: str) -> str:
    """Genera una clave de cache única para el texto."""
    content = f"{text}:{model}:{OPENAI_TEMPERATURE}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cached_response(cache_key: str) -> Optional[Dict]:
    """Obtiene respuesta cacheada si existe."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return None


def save_to_cache(cache_key: str, response: Dict):
    """Guarda respuesta en cache."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
    except:
        pass


def call_openai(text: str, spanish_text: str = "", use_cache: bool = True, group: str = None) -> Dict:
    """
    Llama a OpenAI para obtener anotaciones.
    
    Args:
        text: Texto en Guaraní a anotar
        spanish_text: Traducción al español (opcional)
        use_cache: Si usar cache de respuestas
        group: Nombre del grupo de etiquetas (opcional, si None usa todas)
    
    Returns:
        Dict con "spans" y "analysis"
    """
    logger.info(f"📤 call_openai() - Texto: '{text[:50]}...' ({len(text)} chars)")
    if group:
        logger.info(f"   Grupo: {group}")
    start_time = time.time()
    
    if not OPENAI_AVAILABLE:
        logger.error("❌ OpenAI no disponible (no instalado)")
        return {"spans": [], "analysis": "OpenAI no disponible", "error": True}
    
    if not OPENAI_API_KEY:
        logger.error("❌ API key no configurada")
        return {"spans": [], "analysis": "API key no configurada", "error": True}
    
    # Determinar qué etiquetas usar (grupo específico o todas)
    if group:
        active_labels = get_group_labels_dict(group)
        label_defs = get_group_label_definitions(group)
        logger.info(f"   Usando {len(active_labels)} etiquetas del grupo '{group}'")
    else:
        active_labels = ANNOTATION_LABELS
        label_defs = get_label_definitions()
    
    # Verificar cache (incluir grupo en la key)
    cache_suffix = f":{group}" if group else ""
    cache_key = get_cache_key(text + cache_suffix, OPENAI_MODEL)
    if use_cache:
        cached = get_cached_response(cache_key)
        if cached:
            cached["from_cache"] = True
            logger.info(f"📦 CACHE HIT - {len(cached.get('spans', []))} spans (0.00s)")
            return cached
    
    logger.info(f"🌐 API CALL - Modelo: {OPENAI_MODEL}, Temp: {OPENAI_TEMPERATURE}")
    
    # Preparar prompt
    spanish_context = ""
    if spanish_text:
        spanish_context = f'\nTRADUCCIÓN AL ESPAÑOL (referencia): "{spanish_text}"'
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        text=text,
        spanish_context=spanish_context,
        label_definitions=label_defs
    )
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.debug(f"📡 Enviando request a OpenAI...")
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            response_format={"type": "json_object"}
        )
        
        elapsed = time.time() - start_time
        logger.info(f"✅ OpenAI respondió en {elapsed:.2f}s")
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Validar y limpiar spans
        validated_spans = []
        used_positions = set()  # Para evitar duplicados exactos
        
        for span in result.get("spans", []):
            # Verificar que el span es válido
            start = span.get("start", 0)
            end = span.get("end", 0)
            label = span.get("label", "")
            span_text = span.get("text", "").strip()
            
            # Verificar que la etiqueta es válida
            if label not in active_labels:
                logger.warning(f"  ⚠ Etiqueta no válida: '{label}'")
                continue
            
            # ESTRATEGIA: Si OpenAI da posiciones, verificar. Si no coinciden, buscar el texto.
            actual_text = ""
            final_start = start
            final_end = end
            
            # Verificar si las posiciones de OpenAI son correctas
            if 0 <= start < end <= len(text):
                actual_text = text[start:end]
                if actual_text.lower() == span_text.lower():
                    # Las posiciones son correctas
                    final_start = start
                    final_end = end
                    logger.debug(f"  ✓ Posiciones OpenAI correctas: [{start}:{end}] '{actual_text}'")
                else:
                    # Las posiciones son incorrectas, buscar el texto
                    actual_text = ""
            
            # Si no tenemos texto válido, buscar en la oración
            if not actual_text and span_text:
                # Buscar el texto exacto primero
                idx = text.find(span_text)
                if idx == -1:
                    # Buscar case-insensitive
                    idx = text.lower().find(span_text.lower())
                
                if idx >= 0:
                    final_start = idx
                    final_end = idx + len(span_text)
                    actual_text = text[final_start:final_end]
                    logger.debug(f"  🔍 Texto encontrado: [{final_start}:{final_end}] '{actual_text}' (OpenAI dijo [{start}:{end}])")
                else:
                    logger.warning(f"  ⚠ Texto no encontrado en oración: '{span_text}'")
                    continue
            
            if not actual_text:
                logger.warning(f"  ⚠ Span sin texto válido: start={start}, end={end}, label={label}")
                continue
            
            # Evitar duplicados exactos (misma posición, misma etiqueta)
            pos_key = (final_start, final_end, label)
            if pos_key in used_positions:
                logger.debug(f"  ⏭ Duplicado ignorado: [{final_start}:{final_end}] '{actual_text}' -> {label}")
                continue
            used_positions.add(pos_key)
            
            validated_spans.append({
                "start": final_start,
                "end": final_end,
                "label": label,
                "text": actual_text
            })
            logger.debug(f"  ✓ Span válido: [{final_start}:{final_end}] '{actual_text}' -> {label}")
        
        logger.info(f"📊 {len(validated_spans)} spans validados de {len(result.get('spans', []))} originales")
        
        result["spans"] = validated_spans
        result["from_cache"] = False
        result["model"] = OPENAI_MODEL
        
        # Guardar en cache
        if use_cache:
            save_to_cache(cache_key, result)
            logger.debug(f"💾 Guardado en cache: {cache_key[:16]}...")
        
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Error OpenAI ({elapsed:.2f}s): {str(e)}")
        return {
            "spans": [],
            "analysis": f"Error: {str(e)}",
            "error": True
        }


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def generate_html_info(example: Dict, openai_result: Dict, context: Dict = None) -> str:
    """Genera HTML compacto con info de OpenAI + botón de contexto al final."""
    guarani_text = example.get("text", "N/A")
    spanish_text = example.get("meta", {}).get("spanish_text", "N/A")
    analysis = openai_result.get("analysis", "Sin análisis")
    from_cache = openai_result.get("from_cache", False)
    model = openai_result.get("model", OPENAI_MODEL)
    error = openai_result.get("error", False)
    num_spans = len(openai_result.get("spans", []))
    
    cache_badge = "📦" if from_cache else "🌐"
    status_color = "#ef4444" if error else "#10b981"
    
    ctx = context or {}
    sentence_index = ctx.get("index", "?")
    total_sentences = ctx.get("total", "?")
    prev_gn = ctx.get("prev_guarani", "")
    prev_es = ctx.get("prev_spanish", "")
    next_gn = ctx.get("next_guarani", "")
    next_es = ctx.get("next_spanish", "")
    
    # Spans como badges compactos
    spans_html = ""
    for span in openai_result.get("spans", []):
        label = span.get("label", "?")
        text = span.get("text", "?")
        color = LABEL_COLORS.get(label, "#6b7280")
        spans_html += f'<span style="display:inline-block;margin:1px 2px;padding:1px 4px;background:{color}20;border:1px solid {color};border-radius:3px;font-size:11px;"><b>{text}</b>→{label}</span>'
    
    if not spans_html:
        spans_html = '<span style="color:#9ca3af;font-size:11px;">Sin spans detectados</span>'
    
    return f"""
<div style="margin-bottom:8px;">
    <div style="background:linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);color:white;padding:8px 12px;border-radius:6px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:bold;">🤖 Análisis IA</span>
        <span style="font-size:11px;opacity:0.9;">📊 {sentence_index}/{total_sentences} | {cache_badge} {model}</span>
    </div>
    <div style="background:#e0f2fe;padding:8px 10px;border-left:3px solid #0284c7;margin-bottom:4px;">
        <b>🇵🇾</b> <span style="font-size:16px;font-weight:bold;color:#0c4a6e;">{guarani_text}</span>
        <span style="margin-left:12px;color:#92400e;"><b>🇪🇸</b> {spanish_text}</span>
    </div>
    <div style="background:#f0fdf4;padding:6px 10px;border-left:3px solid {status_color};margin-bottom:4px;font-size:13px;">
        <b>🔬 GPT:</b> {analysis}
    </div>
    <div style="background:#fdf4ff;padding:6px 10px;border-left:3px solid #a855f7;margin-bottom:4px;">
        <b style="font-size:12px;">🏷️ Spans ({num_spans}):</b> {spans_html}
    </div>
    <div style="background:#f5f5f5;padding:6px;text-align:center;font-size:12px;color:#6b7280;border-radius:4px;">
        👇 Selecciona texto abajo para anotar. Click en span + X para eliminar.
    </div>
    <button onclick="window.toggleContextDialog()" style="background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%);color:white;border:none;padding:6px 12px;border-radius:4px;cursor:pointer;font-size:12px;width:100%;margin-top:6px;font-weight:bold;">
        📖 Ver Contexto (Oración Anterior/Siguiente) <span style="opacity:0.7;font-size:10px;margin-left:8px;">Ctrl+Shift+C</span>
    </button>
</div>

<!-- DIALOG DE CONTEXTO (centrado en el área de contenido) -->
<dialog id="context-dialog" style="border:none;border-radius:8px;padding:0;box-shadow:0 10px 25px rgba(0,0,0,0.3);max-width:500px;width:95%;inset:0;margin:auto;">
    <div style="background:#f59e0b;color:white;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:bold;font-size:14px;">📖 Contexto #{sentence_index}/{total_sentences}</span>
        <button onclick="document.getElementById('context-dialog').close()" style="background:rgba(255,255,255,0.2);border:none;color:white;width:24px;height:24px;border-radius:50%;cursor:pointer;font-size:14px;">✕</button>
    </div>
    <div style="padding:10px;display:flex;gap:10px;">
        <div style="flex:1;background:#f0fdf4;border-radius:6px;padding:8px;border-left:3px solid #22c55e;">
            <div style="color:#166534;font-weight:bold;font-size:11px;margin-bottom:4px;">⬅️ ANTERIOR</div>
            <div style="font-size:13px;color:#1e3a5f;">{prev_gn if prev_gn else '<i style="color:#999;">Inicio</i>'}</div>
            <div style="font-size:11px;color:#78350f;margin-top:2px;">{prev_es if prev_es else '—'}</div>
        </div>
        <div style="flex:1;background:#eff6ff;border-radius:6px;padding:8px;border-left:3px solid #3b82f6;">
            <div style="color:#1e40af;font-weight:bold;font-size:11px;margin-bottom:4px;">➡️ SIGUIENTE</div>
            <div style="font-size:13px;color:#1e3a5f;">{next_gn if next_gn else '<i style="color:#999;">Fin</i>'}</div>
            <div style="font-size:11px;color:#78350f;margin-top:2px;">{next_es if next_es else '—'}</div>
        </div>
    </div>
    <div style="background:#f5f5f5;padding:6px;text-align:center;font-size:11px;color:#888;border-radius:0 0 8px 8px;">Click afuera o en ✕ para cerrar</div>
</dialog>
"""


def generate_context_html(context: Dict) -> str:
    """Genera HTML COMPACTO para el panel de contexto (DEBAJO de spans) - YA NO SE USA."""
    return ""  # Ya no se usa, el contexto está en generate_html_info
    ctx = context or {}
    prev_gn = ctx.get("prev_guarani", "")
    prev_es = ctx.get("prev_spanish", "")
    next_gn = ctx.get("next_guarani", "")
    next_es = ctx.get("next_spanish", "")
    
    # Versión inline ultra compacta
    prev_text = f'⬅️ <b>{prev_gn}</b> <span style="color:#666;">({prev_es or "—"})</span>' if prev_gn else '⬅️ <i style="color:#999;">inicio</i>'
    next_text = f'➡️ <b>{next_gn}</b> <span style="color:#666;">({next_es or "—"})</span>' if next_gn else '➡️ <i style="color:#999;">fin</i>'
    
    return f'''<div style="margin-top:6px;">
<button id="context-toggle-btn" onclick="window.toggleContextPanel()" style="background:#f59e0b;color:white;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;font-size:12px;width:100%;">
<span id="context-toggle-icon">▶</span> 📖 Contexto <span style="opacity:0.7;font-size:10px;margin-left:8px;">Alt+C</span>
</button>
<div id="context-panel-content" style="display:none;margin-top:4px;padding:6px 10px;background:#fffbeb;border:1px solid #f59e0b;border-radius:4px;font-size:12px;">
<div style="display:flex;gap:20px;"><div style="flex:1;">{prev_text}</div><div style="flex:1;">{next_text}</div></div>
</div>
</div>'''


# =============================================================================
# RECIPE: ANOTACIÓN ASISTIDA CON CORRECCIÓN
# =============================================================================
@prodigy.recipe(
    "guarani-openai",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
    no_cache=("Disable cache", "flag", "nc", bool),
    group=("Grupo de etiquetas específico", "option", "g", str),
)
def guarani_openai_correct(
    dataset: str,
    source: str,
    model: str = None,
    no_cache: bool = False,
    group: str = None
):
    """
    Anotación morfológica asistida por OpenAI con interfaz de corrección.
    
    OpenAI pre-anota automáticamente y el usuario puede corregir.
    
    Uso:
        prodigy guarani-openai dataset ./data/texts.jsonl -F recipes/guarani_openai.py
        prodigy guarani-openai dataset ./data/texts.jsonl -m gpt-4o -F recipes/guarani_openai.py
        prodigy guarani-openai dataset ./data/texts.jsonl -g morfemas-basicos -F recipes/guarani_openai.py
    
    Grupos disponibles:
        - morfemas-basicos: Raíz, Prefijo, Sufijo
        - categorias: Verbo, Sustantivo, Pronombre, etc.
        - persona-numero: Marcadores de persona y número
        - tam: Tiempo, Aspecto, Modo
        - caso-relacional: Caso locativo, ablativo, relacionales
        - voz-polaridad: Voz y negación
        - nominalizadores: Nominalizadores y gerundios
        - otros-features: Cortesía, derivación, etc.
    """
    global OPENAI_MODEL
    if model:
        OPENAI_MODEL = model
    
    logger.info("="*60)
    logger.info("🚀 INICIANDO RECIPE: guarani-openai")
    logger.info("="*60)
    
    if not OPENAI_API_KEY:
        logger.error("❌ OPENAI_API_KEY no configurada")
        print("❌ Error: OPENAI_API_KEY no configurada")
        print("   Configurar en .env: OPENAI_API_KEY=sk-...")
        sys.exit(1)
    
    # Determinar etiquetas a usar
    if group:
        # Primero intentar buscar en grupos UD principales
        group_info = get_ud_main_group(group)
        if group_info:
            all_labels = group_info["labels"]
            # Colores del grupo UD principal
            group_color = group_info.get("color", "#6b7280")
            label_colors = {lbl: LABEL_COLORS.get(lbl, group_color) for lbl in all_labels}
            print(f"📋 Grupo UD: {group} - {group_info['description']}")
            logger.info(f"📋 Grupo UD: {group} - {len(all_labels)} etiquetas")
        else:
            # Buscar en grupos especializados legacy
            group_info = get_specialized_group(group)
            if not group_info:
                available_ud = ", ".join(list_ud_main_groups())
                available_spec = ", ".join(list_specialized_groups())
                print(f"❌ Error: Grupo '{group}' no encontrado")
                print(f"   Grupos UD: {available_ud}")
                print(f"   Grupos especializados: {available_spec}")
                sys.exit(1)
            all_labels = group_info["labels"]
            label_colors = {lbl: LABEL_COLORS.get(lbl, group_info.get("color", "#6b7280")) for lbl in all_labels}
            print(f"📋 Grupo: {group} - {group_info['description']}")
            logger.info(f"📋 Grupo: {group} - {len(all_labels)} etiquetas")
    else:
        # Sin grupo: usar todas las etiquetas ordenadas por grupos UD
        # Esto agrupa visualmente: POS Tags → Features → Morfemas
        all_labels = get_all_ud_ordered_labels()
        # Aplicar colores según grupo UD (visualmente diferenciados)
        label_colors = get_ud_label_colors()
        print(f"📋 Usando todas las etiquetas ordenadas por grupos UD")
        logger.info(f"📋 Etiquetas ordenadas: {len(all_labels)} etiquetas")
        # Mostrar grupos UD disponibles
        print(f"   Grupos UD disponibles: {', '.join(list_ud_main_groups().keys())}")
    
    logger.info(f"🤖 Modelo: {OPENAI_MODEL}")
    logger.info(f"📦 Cache: {'Desactivado' if no_cache else 'Activado'}")
    logger.info(f"📂 Cache dir: {CACHE_DIR}")
    logger.info(f"📁 Source: {source}")
    logger.info(f"💾 Dataset: {dataset}")
    logger.info(f"🏷️ Labels disponibles: {len(all_labels)}")
    
    print(f"🤖 Modelo: {OPENAI_MODEL}")
    print(f"📦 Cache: {'Desactivado' if no_cache else 'Activado'}")
    print(f"📂 Cache dir: {CACHE_DIR}")
    
    # Ya no necesitamos spaCy - tokenizamos a nivel de caracter
    logger.info(f"📚 Tokenización a nivel de caracter habilitada")
    
    # Pre-cargar todas las oraciones para tener contexto (anterior/siguiente)
    all_examples = list(JSONL(source))
    logger.info(f"📚 Cargadas {len(all_examples)} oraciones para contexto")
    
    # Crear índice de contexto: para cada oración, guardar anterior y siguiente
    context_index = {}
    for idx, ex in enumerate(all_examples):
        text = ex.get("text", "")
        prev_example = all_examples[idx - 1] if idx > 0 else None
        next_example = all_examples[idx + 1] if idx < len(all_examples) - 1 else None
        
        context_index[text] = {
            "index": idx + 1,
            "total": len(all_examples),
            "prev_guarani": prev_example.get("text", "") if prev_example else "",
            "prev_spanish": prev_example.get("meta", {}).get("spanish_text", "") if prev_example else "",
            "next_guarani": next_example.get("text", "") if next_example else "",
            "next_spanish": next_example.get("meta", {}).get("spanish_text", "") if next_example else "",
        }
    
    def prepare_openai_stream(examples_list, label_group=None):
        example_count = 0
        for example in examples_list:
            example_count += 1
            text = example.get("text", "")
            spanish_text = example.get("meta", {}).get("spanish_text", "")
            
            logger.info(f"")
            logger.info(f"{'='*40}")
            logger.info(f"📝 EJEMPLO #{example_count}")
            logger.info(f"   Texto: '{text}'")
            logger.info(f"   Español: '{spanish_text}'")
            
            if not text:
                logger.warning(f"⚠️ Ejemplo sin texto, saltando...")
                continue
            
            # TOKENIZAR A NIVEL DE CARACTER (para selección por caracteres!)
            tokens = []
            for i, char in enumerate(text):
                tokens.append({
                    "text": char,
                    "start": i,
                    "end": i + 1,
                    "id": i,
                    "ws": False  # Sin espacios adicionales entre caracteres
                })
            example["tokens"] = tokens
            logger.info(f"   Tokens (caracteres): {len(tokens)}")
            
            # Llamar a OpenAI (pasando el grupo para filtrar etiquetas)
            logger.info(f"🤖 Llamando a OpenAI...")
            result = call_openai(text, spanish_text, use_cache=not no_cache, group=label_group)
            
            # Preparar spans con token_start y token_end para spans_manual
            # Como cada caracter es un token, token_start = start, token_end = end - 1
            openai_spans = result.get("spans", [])
            prepared_spans = []
            for span in openai_spans:
                prepared_span = {
                    "start": span["start"],
                    "end": span["end"],
                    "token_start": span["start"],  # Cada caracter = 1 token
                    "token_end": span["end"] - 1,  # Último token incluido
                    "label": span["label"]
                }
                prepared_spans.append(prepared_span)
                logger.info(f"   📌 Span preparado: [{span['start']}:{span['end']}] '{span.get('text', '')}' -> {span['label']}")
            
            example["spans"] = prepared_spans
            example["_openai_analysis"] = result.get("analysis", "")
            example["_openai_model"] = result.get("model", OPENAI_MODEL)
            example["_from_cache"] = result.get("from_cache", False)
            example["_label_group"] = label_group
            
            # Obtener contexto de oraciones anterior/siguiente
            ctx = context_index.get(text, {})
            example["_context"] = ctx
            
            # Generar HTML informativo (ARRIBA del área de spans)
            example["html"] = generate_html_info(example, result, ctx)
            
            # Generar HTML de contexto (DEBAJO del área de spans)
            example["html_context"] = generate_context_html(ctx)
            
            logger.info(f"✅ Ejemplo preparado:")
            logger.info(f"   - text: '{example.get('text', 'MISSING!')}'")
            logger.info(f"   - tokens: {len(example.get('tokens', []))}")
            logger.info(f"   - spans: {len(example.get('spans', []))}")
            logger.info(f"   - html: {len(example.get('html', ''))} chars")
            logger.info(f"   - html_context: {len(example.get('html_context', ''))} chars")
            
            example = set_hashes(example)
            logger.info(f"🔄 Yielding ejemplo #{example_count}...")
            yield example
        
        logger.info(f"")
        logger.info(f"✅ Stream completado: {example_count} ejemplos procesados")
    
    # Construir tema con colores
    custom_theme = {"labels": {}}
    for label in all_labels:
        custom_theme["labels"][label] = label_colors.get(label, "#6b7280")
    
    logger.info(f"🎨 Configurando UI con {len(all_labels)} etiquetas")
    logger.info(f"🖥️ View: blocks [html + spans_manual + html_context]")
    logger.info(f"⚙️ Batch size: 1 (para evitar esperas largas)")
    
    # Configurar task router si está habilitado
    router = task_router_iaa if ENABLE_TASK_ROUTING else None
    if ENABLE_TASK_ROUTING:
        logger.info(f"🔀 Task Routing: HABILITADO ({ANNOTATIONS_PER_TASK} anotadores por tarea)")
    else:
        logger.info(f"🔀 Task Routing: DESHABILITADO")
    
    # Usar blocks: html (arriba) + spans_manual
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": prepare_openai_stream(all_examples, label_group=group),
        "task_router": router,  # Task routing para IAA
        "config": {
            "blocks": [
                {"view_id": "html"},                                      # Info + contexto arriba
                {"view_id": "spans_manual"}                               # Área de anotación
            ],
            "labels": all_labels,
            "spans_key": "spans",
            "custom_theme": custom_theme,
            "batch_size": 1,
            "instant_submit": False,
            # Permitir sesiones de anotación (alice, bob, carlos, diana, elena)
            "sessions": ["alice", "bob", "carlos", "diana", "elena"],
            # Si hay routing, no hacer feed_overlap (el router lo maneja)
            "feed_overlap": not ENABLE_TASK_ROUTING,
            # JavaScript personalizado para el panel de contexto
            "javascript": CONTEXT_POPUP_JS
        }
    }


# =============================================================================
# RECIPE: FETCH (Pre-anotar y guardar a archivo)
# =============================================================================
@prodigy.recipe(
    "guarani-openai-fetch",
    source=("Source data (JSONL file)", "positional", None, str),
    output=("Output file (JSONL)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
    no_cache=("Disable cache", "flag", "nc", bool),
)
def guarani_openai_fetch(
    source: str,
    output: str,
    model: str = None,
    no_cache: bool = False
):
    """
    Pre-anota textos con OpenAI y guarda a archivo JSONL.
    
    Útil para preparar datos antes de revisión manual.
    
    Uso:
        prodigy guarani-openai-fetch ./data/texts.jsonl ./data/annotated.jsonl -F recipes/guarani_openai.py
    """
    global OPENAI_MODEL
    if model:
        OPENAI_MODEL = model
    
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY no configurada")
        sys.exit(1)
    
    print(f"🤖 Modelo: {OPENAI_MODEL}")
    print(f"📂 Input: {source}")
    print(f"📂 Output: {output}")
    
    from tqdm import tqdm
    
    # Cargar datos
    source_path = Path(source)
    if not source_path.exists():
        print(f"❌ Archivo no encontrado: {source}")
        sys.exit(1)
    
    examples = list(JSONL(source))
    print(f"📊 {len(examples)} ejemplos a procesar")
    
    # Procesar con OpenAI
    results = []
    for example in tqdm(examples, desc="Procesando"):
        text = example.get("text", "")
        spanish_text = example.get("meta", {}).get("spanish_text", "")
        
        if not text:
            continue
        
        result = call_openai(text, spanish_text, use_cache=not no_cache)
        
        example["spans"] = result.get("spans", [])
        example["_openai_analysis"] = result.get("analysis", "")
        example["_openai_model"] = result.get("model", OPENAI_MODEL)
        example["_from_cache"] = result.get("from_cache", False)
        
        results.append(example)
    
    # Guardar resultados
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for item in results:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"✅ Guardado: {output_path}")
    print(f"   {len(results)} ejemplos anotados")
    
    # Estadísticas
    total_spans = sum(len(ex.get("spans", [])) for ex in results)
    cached = sum(1 for ex in results if ex.get("_from_cache", False))
    print(f"   {total_spans} spans totales")
    print(f"   {cached}/{len(results)} desde cache")


# =============================================================================
# RECIPE: VERSIÓN SIMPLIFICADA (Solo morfemas básicos)
# =============================================================================
BASIC_LABELS = {
    "Raíz": "La raíz o lexema principal",
    "Prefijo": "Prefijo morfológico",
    "Sufijo": "Sufijo morfológico",
    "1ra Persona": "Marcador de primera persona",
    "2da Persona": "Marcador de segunda persona",
    "3ra Persona": "Marcador de tercera persona",
    "Negación": "Marcador de negación",
    "Verbo": "Palabra verbal",
    "Sustantivo": "Sustantivo",
}

@prodigy.recipe(
    "guarani-openai-basic",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
)
def guarani_openai_basic(dataset: str, source: str):
    """
    Versión simplificada con menos etiquetas para principiantes.
    
    Uso:
        prodigy guarani-openai-basic dataset ./data/texts.jsonl -F recipes/guarani_openai.py
    """
    # Usar el recipe principal pero con etiquetas reducidas
    global ANNOTATION_LABELS
    ANNOTATION_LABELS = BASIC_LABELS
    
    return guarani_openai_correct(dataset, source)


# =============================================================================
# RECIPES ESPECIALIZADOS POR GRUPO DE ETIQUETAS
# =============================================================================

@prodigy.recipe(
    "guarani-openai-task-morfemas",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
)
def guarani_openai_task_morfemas(dataset: str, source: str, model: str = None):
    """
    Tarea OpenAI: Morfemas Básicos (Raíz, Prefijo, Sufijo).
    """
    return guarani_openai_correct(dataset, source, model=model, group="morfemas-basicos")


@prodigy.recipe(
    "guarani-openai-task-categorias",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
)
def guarani_openai_task_categorias(dataset: str, source: str, model: str = None):
    """
    Tarea OpenAI: Categorías Gramaticales (Verbo, Sustantivo, etc.).
    """
    return guarani_openai_correct(dataset, source, model=model, group="categorias")


@prodigy.recipe(
    "guarani-openai-task-persona",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
)
def guarani_openai_task_persona(dataset: str, source: str, model: str = None):
    """
    Tarea OpenAI: Marcadores de Persona y Número.
    """
    return guarani_openai_correct(dataset, source, model=model, group="persona-numero")


@prodigy.recipe(
    "guarani-openai-task-tam",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
)
def guarani_openai_task_tam(dataset: str, source: str, model: str = None):
    """
    Tarea OpenAI: Tiempo, Aspecto, Modo.
    """
    return guarani_openai_correct(dataset, source, model=model, group="tam")


@prodigy.recipe(
    "guarani-openai-task-caso",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
)
def guarani_openai_task_caso(dataset: str, source: str, model: str = None):
    """
    Tarea OpenAI: Caso y Relacionales.
    """
    return guarani_openai_correct(dataset, source, model=model, group="caso-relacional")


@prodigy.recipe(
    "guarani-openai-task-voz",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
)
def guarani_openai_task_voz(dataset: str, source: str, model: str = None):
    """
    Tarea OpenAI: Voz y Polaridad.
    """
    return guarani_openai_correct(dataset, source, model=model, group="voz-polaridad")


@prodigy.recipe(
    "guarani-openai-task-nomz",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
)
def guarani_openai_task_nomz(dataset: str, source: str, model: str = None):
    """
    Tarea OpenAI: Nominalizadores y Participios.
    """
    return guarani_openai_correct(dataset, source, model=model, group="nominalizadores")


@prodigy.recipe(
    "guarani-openai-task-otros",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    model=("OpenAI model to use", "option", "m", str),
)
def guarani_openai_task_otros(dataset: str, source: str, model: str = None):
    """
    Tarea OpenAI: Otros Features (Cortesía, Derivación, etc.).
    """
    return guarani_openai_correct(dataset, source, model=model, group="otros-features")


@prodigy.recipe(
    "guarani-openai-task",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    group=("Grupo de etiquetas", "option", "g", str),
    model=("OpenAI model to use", "option", "m", str),
)
def guarani_openai_task(dataset: str, source: str, group: str = None, model: str = None):
    """
    Tarea OpenAI genérica con grupo seleccionable via -g.
    
    Grupos disponibles:
        morfemas-basicos, categorias, persona-numero, tam,
        caso-relacional, voz-polaridad, nominalizadores, otros-features
    
    Uso:
        prodigy guarani-openai-task dataset ./data/texts.jsonl -g morfemas-basicos
    """
    if not group:
        print("❌ Error: Debe especificar un grupo con -g")
        print(f"   Grupos disponibles: {', '.join(list_specialized_groups())}")
        sys.exit(1)
    
    return guarani_openai_correct(dataset, source, model=model, group=group)


# =============================================================================
# TEST DEL MÓDULO
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Test de Guaraní OpenAI Recipe")
    print("=" * 60)
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY no configurada")
        print("   Crear archivo .env con: OPENAI_API_KEY=sk-...")
    else:
        print(f"✅ API Key configurada")
        print(f"✅ Modelo: {OPENAI_MODEL}")
        
        # Test con ejemplo
        test_text = "Ahayhu che sy"
        print(f"\n🧪 Test con: '{test_text}'")
        
        result = call_openai(test_text, "Amo a mi madre")
        print(f"   Spans: {len(result.get('spans', []))}")
        print(f"   Análisis: {result.get('analysis', 'N/A')[:100]}...")
        print(f"   Cache: {result.get('from_cache', False)}")
