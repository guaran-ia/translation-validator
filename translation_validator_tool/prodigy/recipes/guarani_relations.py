"""
Recipe para anotacion de RELACIONES SINTACTICAS en textos Guarani
==================================================================

Este recipe usa la interfaz 'relations' de Prodigy para anotar
dependencias sintacticas y relaciones semanticas entre tokens.

Tokenizacion a nivel de PALABRA.

Basado en Universal Dependencies:
https://universaldependencies.org/treebanks/gn_oldtudet/index.html

Uso:
    prodigy guarani-relations dataset ./data/texts.jsonl -F recipes/guarani_relations.py
    prodigy guarani-relations dataset ./data/texts.jsonl --group relations -F recipes/guarani_relations.py
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from prodigy.core import Controller

import prodigy
from prodigy.components.loaders import JSONL
from prodigy.util import set_hashes

# =============================================================================
# CONFIGURACION DE LOGGING
# =============================================================================
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / f"relations_recipe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("guarani_relations")
logger.info("="*60)
logger.info(f"LOG INICIADO: {log_file}")
logger.info("="*60)

print(f"\nLOGS en: {log_file}\n")

# Cargar variables de entorno
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Importar mapper centralizado
_scripts_dir = Path(__file__).parent.parent / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from ud_guarani_mapper import (
    LABEL_COLORS,
    SPECIALIZED_GROUPS,
    UD_MAIN_GROUPS,
    get_specialized_group,
    get_ud_main_group,
    list_specialized_groups,
    list_ud_main_groups,
    get_all_ud_ordered_labels,
    get_ud_label_colors,
)

# =============================================================================
# CONFIGURACION DE TASK ROUTING (para Inter-Annotator Agreement)
# =============================================================================
ANNOTATIONS_PER_TASK = int(os.getenv("ANNOTATIONS_PER_TASK", "2"))
ENABLE_TASK_ROUTING = os.getenv("ENABLE_TASK_ROUTING", "true").lower() == "true"


# =============================================================================
# ETIQUETAS DE RELACIONES - AMIGABLES PARA EL USUARIO
# =============================================================================
# Etiquetas en español que luego se mapean a Universal Dependencies
# Basado en: https://universaldependencies.org/treebanks/gn_oldtudet/index.html

# Mapeo: Etiqueta amigable -> Codigo UD
RELATION_TO_UD = {
    "RAÍZ (Verbo Principal)": "root",
    "SUJETO": "nsubj",
    "OBJETO DIRECTO": "obj",
    "OBJETO INDIRECTO": "iobj",
    "COMPLEMENTO OBLICUO": "obl",
    "OBLICUO-OBJETO": "obl:obj",
    "OBLICUO-SUJETO": "obl:subj",
    "MODIFICADOR ADVERBIAL": "advmod",
    "CLÁUSULA ADVERBIAL": "advcl",
    "MODIFICADOR NOMINAL": "nmod",
    "DETERMINANTE": "det",
    "MARCADOR DE CASO": "case",
    "PALABRA COMPUESTA": "compound",
    "APOSICIÓN": "appos",
    "COMPLEMENTO VERBAL": "xcomp",
    "ELEMENTO DE DISCURSO": "discourse",
    "PARATAXIS": "parataxis",
    "MODIFICADOR NUMÉRICO": "nummod",
    "PUNTUACIÓN": "punct",
    "DEPENDENCIA (General)": "dep",
}

# Mapeo inverso: Codigo UD -> Etiqueta amigable
UD_TO_RELATION = {v: k for k, v in RELATION_TO_UD.items()}

# Las etiquetas que se muestran al usuario (amigables)
RELATION_LABELS = list(RELATION_TO_UD.keys())

# Colores para relaciones (usando etiquetas amigables)
RELATION_COLORS = {
    "RAÍZ (Verbo Principal)": "#dc2626",      # Rojo - raiz
    "SUJETO": "#2563eb",                       # Azul - sujeto
    "OBJETO DIRECTO": "#16a34a",               # Verde - objeto
    "OBJETO INDIRECTO": "#65a30d",             # Verde claro - objeto indirecto
    "COMPLEMENTO OBLICUO": "#ca8a04",          # Amarillo - oblicuo
    "OBLICUO-OBJETO": "#ca8a04",
    "OBLICUO-SUJETO": "#ca8a04",
    "MODIFICADOR ADVERBIAL": "#7c3aed",        # Violeta - modificador adverbial
    "CLÁUSULA ADVERBIAL": "#a855f7",           # Violeta claro - clausula adverbial
    "MODIFICADOR NOMINAL": "#0891b2",          # Cyan - modificador nominal
    "DETERMINANTE": "#64748b",                 # Gris - determinante
    "MARCADOR DE CASO": "#78716c",             # Gris oscuro - caso
    "PALABRA COMPUESTA": "#ea580c",            # Naranja - compuesto
    "APOSICIÓN": "#db2777",                    # Rosa - aposicion
    "COMPLEMENTO VERBAL": "#059669",           # Esmeralda - complemento abierto
    "ELEMENTO DE DISCURSO": "#94a3b8",         # Gris claro - discurso
    "PARATAXIS": "#f97316",                    # Naranja - parataxis
    "MODIFICADOR NUMÉRICO": "#0d9488",         # Teal - modificador numerico
    "PUNTUACIÓN": "#d4d4d4",                   # Gris muy claro - puntuacion
    "DEPENDENCIA (General)": "#a1a1aa",        # Gris - dependencia generica
}


def tokenize_by_words(text: str) -> List[Dict[str, Any]]:
    """
    Tokeniza el texto a nivel de PALABRA.
    Cada palabra es un token independiente.
    
    Args:
        text: Texto a tokenizar
        
    Returns:
        Lista de tokens con estructura Prodigy
    """
    tokens = []
    words = text.split()
    current_pos = 0
    
    for i, word in enumerate(words):
        # Encontrar la posicion real de la palabra en el texto original
        start = text.find(word, current_pos)
        end = start + len(word)
        
        # ws=True si hay espacio despues
        has_ws = end < len(text) and text[end] == ' '
        
        token = {
            "text": word,
            "start": start,
            "end": end,
            "id": i,
            "ws": has_ws,
        }
        
        # Deshabilitar puntuacion para que no sea seleccionable como head/child
        if word in '.,;:!?()[]{}"\'-':
            token["disabled"] = True
            
        tokens.append(token)
        current_pos = end
    
    return tokens


def generate_html_info(example: Dict, context: Dict) -> str:
    """
    Genera HTML informativo para mostrar arriba del area de anotacion.
    Igual que guarani_openai para mantener consistencia.
    
    Args:
        example: Ejemplo con texto y metadata
        context: Contexto de oraciones anterior/siguiente
        
    Returns:
        HTML string
    """
    guarani_text = example.get("text", "")
    spanish_text = example.get("meta", {}).get("spanish_text", "")
    
    ctx = context or {}
    sentence_index = ctx.get("index", "?")
    total_sentences = ctx.get("total", "?")
    prev_gn = ctx.get("prev_guarani", "")
    prev_es = ctx.get("prev_spanish", "")
    next_gn = ctx.get("next_guarani", "")
    next_es = ctx.get("next_spanish", "")
    
    return f"""
<div style="margin-bottom:8px;">
    <div style="background:linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);color:white;padding:8px 12px;border-radius:6px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:bold;">🔗 Relaciones Sintácticas</span>
        <span style="font-size:11px;opacity:0.9;">📊 {sentence_index}/{total_sentences}</span>
    </div>
    <div style="background:#e0f2fe;padding:8px 10px;border-left:3px solid #0284c7;margin-bottom:4px;">
        <b>🇵🇾</b> <span style="font-size:16px;font-weight:bold;color:#0c4a6e;">{guarani_text}</span>
        <span style="margin-left:12px;color:#92400e;"><b>🇪🇸</b> {spanish_text if spanish_text else "(sin traducción)"}</span>
    </div>
    <div style="background:#f5f5f5;padding:6px;text-align:center;font-size:12px;color:#6b7280;border-radius:4px;">
        👇 Click en palabra origen → Click en palabra destino → Selecciona relación
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


# JavaScript para el popup de contexto (igual que guarani_openai)
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


def task_router_iaa(ctrl, session_id: str, item: Dict) -> List[str]:
    """
    Router para distribuir tareas entre anotadores (Inter-Annotator Agreement).
    
    Asigna cada tarea a N anotadores de forma deterministica basada en el hash.
    
    Args:
        ctrl: Controller de Prodigy
        session_id: ID de la sesion actual (alice, bob, etc.)
        item: El ejemplo a enrutar
    
    Returns:
        Lista de session_ids que deben ver este ejemplo
    """
    # Obtener pool de anotadores disponibles
    pool = list(ctrl.session_ids)
    if not pool:
        return []
    
    # Obtener hash del task
    task_hash = item.get("_task_hash")
    if task_hash is None:
        return []
    
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
# RECIPE PRINCIPAL: guarani-relations
# =============================================================================
@prodigy.recipe(
    "guarani-relations",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    group=("Label group to use", "option", "g", str),
    limit=("Limit number of examples", "option", "l", int),
    port=("Port for Prodigy server", "option", "p", int),
)
def guarani_relations(
    dataset: str,
    source: str,
    group: str = None,
    limit: int = 100,
    port: int = 8080,
):
    """
    Anotacion de relaciones sintacticas para Guarani.
    
    Tokenizacion a nivel de caracter para maxima precision.
    
    Grupos disponibles:
      - relations: Todas las relaciones UD (default)
      - pos-tags: Categorias gramaticales
      - features: Rasgos morfologicos
    
    Uso:
        prodigy guarani-relations dataset ./data.jsonl -F recipes/guarani_relations.py
        prodigy guarani-relations dataset ./data.jsonl -g relations -F recipes/guarani_relations.py
    """
    logger.info("="*60)
    logger.info("INICIANDO RECIPE: guarani-relations")
    logger.info("="*60)
    
    # Determinar etiquetas a usar
    if group:
        # Buscar en grupos UD principales
        group_info = get_ud_main_group(group)
        if group_info:
            all_labels = group_info["labels"]
            group_color = group_info.get("color", "#6b7280")
            label_colors = {lbl: RELATION_COLORS.get(lbl, group_color) for lbl in all_labels}
            print(f"Grupo UD: {group} - {group_info['description']}")
            logger.info(f"Grupo UD: {group} - {len(all_labels)} etiquetas")
        else:
            # Buscar en grupos especializados
            group_info = get_specialized_group(group)
            if not group_info:
                available_ud = ", ".join(list_ud_main_groups())
                available_spec = ", ".join(list_specialized_groups())
                print(f"Error: Grupo '{group}' no encontrado")
                print(f"   Grupos UD: {available_ud}")
                print(f"   Grupos especializados: {available_spec}")
                sys.exit(1)
            all_labels = group_info["labels"]
            label_colors = {lbl: RELATION_COLORS.get(lbl, group_info.get("color", "#6b7280")) for lbl in all_labels}
            print(f"Grupo: {group} - {group_info['description']}")
            logger.info(f"Grupo: {group} - {len(all_labels)} etiquetas")
    else:
        # Por defecto: usar etiquetas de relaciones
        all_labels = RELATION_LABELS
        label_colors = RELATION_COLORS
        print("Usando etiquetas de relaciones UD (default)")
        logger.info(f"Etiquetas de relaciones: {len(all_labels)}")
    
    logger.info(f"Source: {source}")
    logger.info(f"Dataset: {dataset}")
    logger.info(f"Labels: {len(all_labels)}")
    logger.info(f"Limit: {limit}")
    
    print(f"Source: {source}")
    print(f"Dataset: {dataset}")
    print(f"Limite: {limit} oraciones")
    
    # Pre-cargar todas las oraciones para contexto
    all_examples = list(JSONL(source))
    logger.info(f"Cargadas {len(all_examples)} oraciones")
    
    # Crear indice de contexto
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
    
    def prepare_stream(examples_list):
        """Prepara el stream de ejemplos con tokenizacion a nivel de caracter."""
        count = 0
        
        for example in examples_list:
            if limit and count >= limit:
                break
            
            text = example.get("text", "")
            if not text or not text.strip():
                continue
            
            count += 1
            
            # Tokenizar a nivel de palabra
            tokens = tokenize_by_words(text)
            
            # Obtener contexto
            ctx = context_index.get(text, {})
            
            # Construir ejemplo
            task = {
                "text": text,
                "tokens": tokens,
                "relations": [],  # Sin relaciones pre-anotadas
                "spans": [],      # Sin spans pre-anotados
                "meta": example.get("meta", {}),
                "_context": ctx,
                "html": generate_html_info(example, ctx),
            }
            
            task = set_hashes(task)
            
            logger.debug(f"Ejemplo {count}: '{text[:50]}...' - {len(tokens)} tokens")
            
            yield task
        
        logger.info(f"Stream completado: {count} ejemplos")
    
    # Construir tema con colores
    custom_theme = {"labels": {}}
    for label in all_labels:
        custom_theme["labels"][label] = label_colors.get(label, "#6b7280")
    
    # Router para IAA
    router = task_router_iaa if ENABLE_TASK_ROUTING else None
    if ENABLE_TASK_ROUTING:
        logger.info(f"Task Routing: HABILITADO ({ANNOTATIONS_PER_TASK} anotadores)")
    
    logger.info(f"View: blocks [html + relations]")
    logger.info(f"Labels: {all_labels}")
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": prepare_stream(all_examples),
        "task_router": router,
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "relations"},
            ],
            "labels": all_labels,
            "relations_span_labels": None,  # No span labels adicionales
            "wrap_relations": True,         # Wrap texto en multiples lineas
            "show_relations": True,         # Mostrar todas las relaciones
            "show_relations_labels": True,  # Mostrar labels de relaciones
            "hide_relations_arrow": False,  # Mostrar flechas
            "custom_theme": custom_theme,
            "batch_size": 1,
            "instant_submit": False,
            "sessions": ["alice", "bob", "carlos", "diana", "elena"],
            "feed_overlap": not ENABLE_TASK_ROUTING,
            "javascript": CONTEXT_POPUP_JS,
            "port": port,
        }
    }


# =============================================================================
# RECIPE SEGURO: guarani-relations-secure
# =============================================================================
@prodigy.recipe(
    "guarani-relations-secure",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    group=("Label group to use", "option", "g", str),
    limit=("Limit number of examples", "option", "l", int),
    port=("Port for Prodigy server", "option", "p", int),
)
def guarani_relations_secure(
    dataset: str,
    source: str,
    group: str = None,
    limit: int = 100,
    port: int = 8082,
):
    """
    Version segura con autenticacion JWT.
    
    Igual que guarani-relations pero configurado para proxy JWT.
    """
    # Delegar al recipe principal
    return guarani_relations(
        dataset=dataset,
        source=source,
        group=group,
        limit=limit,
        port=port,
    )


# =============================================================================
# EJEMPLO DE USO
# =============================================================================
if __name__ == "__main__":
    print("="*60)
    print("Guarani Relations Recipe")
    print("="*60)
    print()
    print("Uso:")
    print("  prodigy guarani-relations dataset ./data.jsonl -F recipes/guarani_relations.py")
    print()
    print("Grupos disponibles:")
    for key, name in list_ud_main_groups().items():
        print(f"  -g {key:20} - {name}")
    print()
    print("Etiquetas de relaciones:")
    for label in RELATION_LABELS:
        print(f"  {label}")
