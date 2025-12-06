"""
Recipe para anotación de SPANS con soporte para overlapping en textos Guaraní
Permite anotar morfemas, prefijos, sufijos y componentes que pueden superponerse

Ideal para:
- Análisis morfológico (prefijos/sufijos que se superponen)
- Anotación de componentes aglutinantes del Guaraní
- Marcar múltiples categorías en el mismo segmento de texto

Características:
- Etiquetas AMIGABLES en español para el usuario
- Agrupadas por FAMILIA (Morfema, Persona, Tiempo, etc.)
- Mapeo automático a UNIVERSAL DEPENDENCIES al exportar
- Mapper centralizado en scripts/ud_guarani_mapper.py

Referencia: https://prodi.gy/docs/api-interfaces#spans_manual
Mapper UD: https://universaldependencies.org/treebanks/gn_oldtudet/index.html
"""

import sys
from pathlib import Path

import prodigy
from prodigy.components.loaders import JSONL
from prodigy.util import set_hashes
import spacy

# Cargar modelo de spaCy para tokenización
nlp = spacy.blank("es")  # Modelo vacío español (funciona para Guaraní)

# =============================================================================
# IMPORTAR MAPPER CENTRALIZADO
# =============================================================================
# El mapper centralizado está en: scripts/ud_guarani_mapper.py
# Contiene todas las definiciones de etiquetas y funciones de mapeo
# =============================================================================
_scripts_dir = Path(__file__).parent.parent / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from ud_guarani_mapper import (
    FRIENDLY_TO_UD,
    UD_TO_FRIENDLY,
    LABEL_FAMILIES,
    LABEL_COLORS,
    FAMILY_KEYS,
    VALID_UPOS,
    VALID_FEATURES,
    map_label,
    get_family_labels,
    get_all_friendly_labels,
    SPECIALIZED_GROUPS,
    get_specialized_group,
    get_specialized_labels,
    list_specialized_groups,
    # Grupos UD principales
    UD_MAIN_GROUPS,
    get_ud_main_group,
    get_ud_main_labels,
    list_ud_main_groups,
    get_all_ud_ordered_labels,
    get_ud_label_colors,
)

# =============================================================================
# JAVASCRIPT PARA DIALOG DE CONTEXTO (igual que guarani_openai.py)
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
# VARIABLES LOCALES DERIVADAS DEL MAPPER CENTRALIZADO
# =============================================================================
ALL_FRIENDLY_LABELS = get_all_friendly_labels()

# Etiquetas básicas recomendadas para empezar
BASIC_FRIENDLY_LABELS = [
    "Raíz", "Prefijo", "Sufijo",
    "1ra Persona", "2da Persona", "3ra Persona",
    "Pasado", "Futuro",
    "Negación", "Plural",
]

# =============================================================================
# FUNCIONES DE CONVERSIÓN (wrappers del mapper centralizado)
# =============================================================================

def friendly_to_ud(friendly_label):
    """Convierte etiqueta amigable a Universal Dependencies"""
    return map_label(friendly_label, "to_ud")

def ud_to_friendly(ud_label):
    """Convierte etiqueta UD a amigable"""
    return map_label(ud_label, "to_friendly")

def convert_spans_to_ud(spans):
    """Convierte lista de spans de etiquetas amigables a UD"""
    converted = []
    for span in spans:
        new_span = span.copy()
        if "label" in new_span:
            new_span["label"] = friendly_to_ud(new_span["label"])
        converted.append(new_span)
    return converted

def convert_spans_to_friendly(spans):
    """Convierte lista de spans de UD a etiquetas amigables"""
    converted = []
    for span in spans:
        new_span = span.copy()
        if "label" in new_span:
            new_span["label"] = ud_to_friendly(new_span["label"])
        converted.append(new_span)
    return converted


# =============================================================================
# GENERADOR DE HTML PARA FAMILIAS DE ETIQUETAS
# =============================================================================

def generate_family_html(selected_families=None):
    """Genera HTML con etiquetas agrupadas por familia"""
    if selected_families is None:
        selected_families = list(LABEL_FAMILIES.keys())
    
    html_parts = []
    for family_name in selected_families:
        if family_name not in LABEL_FAMILIES:
            continue
        family = LABEL_FAMILIES[family_name]
        color = family["color"]
        labels = family["labels"]
        
        # Crear badges para cada etiqueta
        badges = " ".join([
            f'<span style="background:{color};color:white;padding:2px 6px;margin:1px;font-size:11px;border-radius:3px;display:inline-block;">{l}</span>'
            for l in labels
        ])
        
        html_parts.append(f'''
        <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:6px 10px;font-weight:bold;color:#374151;white-space:nowrap;vertical-align:top;width:140px;">
                {family_name}
            </td>
            <td style="padding:6px 10px;">
                {badges}
            </td>
        </tr>
        ''')
    
    return f'''
    <table style="width:100%;border-collapse:collapse;font-size:12px;">
        {"".join(html_parts)}
    </table>
    '''


def generate_html_with_context(example: dict, labels: list, context: dict = None, group_name: str = None) -> str:
    """Genera HTML con info de contexto + botón para modal (igual que guarani_openai.py)."""
    guarani_text = example.get("text", "N/A")
    spanish_text = example.get("meta", {}).get("spanish_text", "N/A")
    
    ctx = context or {}
    sentence_index = ctx.get("index", "?")
    total_sentences = ctx.get("total", "?")
    prev_gn = ctx.get("prev_guarani", "")
    prev_es = ctx.get("prev_spanish", "")
    next_gn = ctx.get("next_guarani", "")
    next_es = ctx.get("next_spanish", "")
    
    # Título según grupo
    if group_name:
        group_info = get_specialized_group(group_name) or get_ud_main_group(group_name)
        if group_info:
            title = f"✏️ {group_info.get('name', 'Anotación Manual')} - {group_info.get('description', '')}"
        else:
            title = f"✏️ Anotación Manual - {group_name}"
    else:
        title = "✏️ Anotación Manual - Todas las etiquetas"
    
    # Generar badges de etiquetas disponibles
    labels_html = ""
    for label in labels[:20]:  # Mostrar máximo 20 para no sobrecargar
        color = LABEL_COLORS.get(label, "#6b7280")
        labels_html += f'<span style="display:inline-block;margin:1px 2px;padding:1px 4px;background:{color}20;border:1px solid {color};border-radius:3px;font-size:10px;">{label}</span>'
    
    if len(labels) > 20:
        labels_html += f'<span style="color:#666;font-size:10px;margin-left:4px;">+{len(labels)-20} más</span>'
    
    return f"""
<div style="margin-bottom:8px;">
    <div style="background:linear-gradient(135deg, #10b981 0%, #059669 100%);color:white;padding:8px 12px;border-radius:6px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:bold;">{title}</span>
        <span style="font-size:11px;opacity:0.9;">📊 {sentence_index}/{total_sentences} | 🏷️ {len(labels)} etiquetas</span>
    </div>
    <div style="background:#e0f2fe;padding:8px 10px;border-left:3px solid #0284c7;margin-bottom:4px;">
        <b>🇵🇾</b> <span style="font-size:16px;font-weight:bold;color:#0c4a6e;">{guarani_text}</span>
        <span style="margin-left:12px;color:#92400e;"><b>🇪🇸</b> {spanish_text}</span>
    </div>
    <div style="background:#fdf4ff;padding:6px 10px;border-left:3px solid #a855f7;margin-bottom:4px;">
        <b style="font-size:11px;">🏷️ Etiquetas:</b> {labels_html}
    </div>
    <div style="background:#f5f5f5;padding:6px;text-align:center;font-size:12px;color:#6b7280;border-radius:4px;">
        👇 Selecciona texto abajo para anotar. Los spans pueden superponerse.
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
@prodigy.recipe(
    "guarani-spans",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    families=("Familias de etiquetas separadas por coma (legacy)", "option", "f", str),
    group=("Grupo UD: pos-tags, features, morfemas, features-tam, etc.", "option", "g", str),
    word_level=("Tokenizar por PALABRA en vez de caracter", "option", "w", str),
)
def guarani_spans_manual(dataset, source, families=None, group=None, word_level=None):
    """
    Anotación de SPANS con overlapping - ETIQUETAS AMIGABLES con soporte para grupos UD
    
    Por defecto tokeniza a nivel de CARACTER (permite seleccionar morfemas).
    Usa -w/--word-level para tokenizar por palabra.
    
    Incluye botón de contexto y atajo Ctrl+Shift+C.
    
    Grupos UD disponibles (-g/--group):
        pos-tags              POS Tags (VERB, NOUN, PRON, etc.)
        features              Todos los features morfológicos
        morfemas              Raíz, Prefijo, Sufijo
        features-persona-numero   Persona, Número, Clusividad
        features-caso             Casos
        features-tam              Tiempo, Aspecto, Modo
        features-relacional       Prefijos relacionales
        features-nominalizadores  Nominalizadores
        features-otros            Otros features
    
    Uso:
        # Por caracter (default) - para morfemas
        prodigy guarani-spans dataset ./data/texts.jsonl -g morfemas -F recipes/guarani_spans.py
        
        # Por palabra - para POS tags
        prodigy guarani-spans dataset ./data/texts.jsonl -g pos-tags -w -F recipes/guarani_spans.py
    """
    
    # Determinar etiquetas a usar
    selected_group_name = None
    if group:
        # Primero buscar en grupos UD principales
        group_info = get_ud_main_group(group)
        if group_info:
            labels = group_info["labels"]
            selected_group_name = group
            print(f"📋 Grupo UD: {group} - {group_info['description']}")
            print(f"   {len(labels)} etiquetas")
        else:
            # Buscar en grupos especializados
            group_info = get_specialized_group(group)
            if group_info:
                labels = group_info["labels"]
                selected_group_name = group
                print(f"📋 Grupo: {group} - {group_info['description']}")
                print(f"   {len(labels)} etiquetas")
            else:
                available_ud = ", ".join(list_ud_main_groups().keys())
                available_spec = ", ".join(list_specialized_groups().keys())
                print(f"❌ Error: Grupo '{group}' no encontrado")
                print(f"   Grupos UD: {available_ud}")
                print(f"   Grupos especializados: {available_spec}")
                import sys
                sys.exit(1)
    elif families:
        # Legacy: usar familias
        selected_family_keys = [f.strip().lower() for f in families.split(",")]
        selected_families = [FAMILY_KEYS.get(k) for k in selected_family_keys if k in FAMILY_KEYS]
        labels = []
        for family_name in selected_families:
            if family_name and family_name in LABEL_FAMILIES:
                labels.extend(LABEL_FAMILIES[family_name]["labels"])
        if not labels:
            labels = ALL_FRIENDLY_LABELS
        print(f"📋 Familias: {len(labels)} etiquetas de {len(selected_families)} familias")
    else:
        # Sin grupo: usar todas las etiquetas ordenadas por grupos UD
        labels = get_all_ud_ordered_labels()
        print(f"📋 Usando todas las etiquetas ordenadas por grupos UD: {len(labels)}")
        print(f"   Grupos disponibles: {', '.join(list_ud_main_groups().keys())}")
    
    # Pre-cargar todas las oraciones para contexto
    all_examples = list(JSONL(source))
    print(f"📚 Cargadas {len(all_examples)} oraciones")
    
    # Convertir word_level a booleano (viene como string "true"/"false" o None)
    use_word_tokens = word_level is not None and word_level.lower() in ("true", "yes", "1", "si")
    
    if use_word_tokens:
        print(f"📝 Tokenización a nivel de PALABRA (selecciona palabras completas)")
    else:
        print(f"📝 Tokenización a nivel de CARACTER (permite seleccionar cualquier substring)")
    
    # Crear índice de contexto
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
    
    def prepare_spans_stream(examples_list, active_labels, group_name, use_word_tokens):
        for example in examples_list:
            guarani_text = example.get('text', '')
            spanish_text = example.get('meta', {}).get('spanish_text', '')
            
            if not guarani_text:
                continue
            
            # Tokenizar según modo
            tokens = []
            if use_word_tokens:
                # Tokenizar por PALABRA usando spaCy
                doc = nlp(guarani_text)
                for i, token in enumerate(doc):
                    tokens.append({
                        "text": token.text,
                        "start": token.idx,
                        "end": token.idx + len(token.text),
                        "id": i,
                        "ws": token.whitespace_ != ""
                    })
            else:
                # Tokenizar por CARACTER (default, igual que guarani_openai.py)
                for i, char in enumerate(guarani_text):
                    tokens.append({
                        "text": char,
                        "start": i,
                        "end": i + 1,
                        "id": i,
                        "ws": False
                    })
            
            example["text"] = guarani_text
            example["tokens"] = tokens
            example["spans"] = []
            
            # Obtener contexto
            ctx = context_index.get(guarani_text, {})
            
            # Generar HTML con contexto (igual que guarani_openai.py)
            example["html"] = generate_html_with_context(example, active_labels, ctx, group_name)
            
            example = set_hashes(example)
            yield example
    
    # Construir custom_theme con colores por etiqueta
    label_colors = get_ud_label_colors()
    custom_theme = {"labels": {}}
    for label in labels:
        custom_theme["labels"][label] = label_colors.get(label, LABEL_COLORS.get(label, "#6b7280"))
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": prepare_spans_stream(all_examples, labels, selected_group_name, use_word_tokens),
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "spans_manual"}
            ],
            "labels": labels,
            "spans_key": "spans",
            "custom_theme": custom_theme,
            "javascript": CONTEXT_POPUP_JS,
        }
    }


@prodigy.recipe(
    "guarani-morphemes",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
)
def guarani_morphemes(dataset, source):
    """
    Versión simplificada para análisis de morfemas básicos del Guaraní
    Compatible con Universal Dependencies
    
    Etiquetas:
    - Root, Prefix, Suffix (estructura morfológica)
    - Person=1/2/3 (marcadores de persona)
    - Tense=Past/Fut (tiempo)
    - Polarity=Neg (negación)
    - Number=Plur (plural)
    
    Uso:
        prodigy guarani-morphemes dataset ./data/texts.jsonl -F recipes/guarani_spans.py
    """
    
    # Etiquetas UD simplificadas para morfología
    simple_labels = [
        "Root",           # Raíz/lexema
        "Prefix",         # Prefijo
        "Suffix",         # Sufijo
        "Person=1",       # 1ra persona (a-, che-)
        "Person=2",       # 2da persona (re-, nde-)
        "Person=3",       # 3ra persona (o-, i-)
        "Tense=Fut",      # Futuro (-ta)
        "Tense=Past",     # Pasado (-kue)
        "Polarity=Neg",   # Negación (nd-...-i)
        "Number=Plur",    # Plural (-kuéra)
    ]
    
    stream = JSONL(source)
    
    def prepare_morpheme_stream(stream):
        for example in stream:
            guarani_text = example.get('text', '')
            spanish_text = example.get('meta', {}).get('spanish_text', '')
            
            if not guarani_text:
                continue
            
            # Tokenizar
            doc = nlp(guarani_text)
            tokens = []
            for i, token in enumerate(doc):
                tokens.append({
                    "text": token.text,
                    "start": token.idx,
                    "end": token.idx + len(token.text),
                    "id": i,
                    "ws": token.whitespace_ != ""
                })
            
            example["text"] = guarani_text
            example["tokens"] = tokens
            example["spans"] = []
            example = set_hashes(example)
            
            example["html"] = f"""
<div style="margin-bottom:15px;">
    <table style="width:100%;border-collapse:collapse;margin-bottom:10px;">
        <tr style="background:#0ea5e9;color:white;">
            <td style="padding:10px;font-weight:bold;font-size:16px;">
                🔍 Morfemas - Universal Dependencies
            </td>
        </tr>
    </table>
    <table style="width:100%;border-collapse:collapse;background:#f0f9ff;margin-bottom:8px;">
        <tr>
            <td style="padding:10px;border-left:4px solid #0ea5e9;">
                <b>🇪🇸 Español:</b> {spanish_text or 'N/A'}
            </td>
        </tr>
    </table>
    <table style="width:100%;border-collapse:collapse;background:#ecfeff;">
        <tr>
            <td style="padding:8px;font-size:12px;">
                <span style="background:#3b82f6;color:white;padding:2px 6px;">Root</span>
                <span style="background:#60a5fa;color:white;padding:2px 6px;">Prefix</span>
                <span style="background:#93c5fd;padding:2px 6px;">Suffix</span>
                <span style="background:#22c55e;color:white;padding:2px 6px;">Person=1/2/3</span>
                <span style="background:#facc15;padding:2px 6px;">Tense</span>
                <span style="background:#ef4444;color:white;padding:2px 6px;">Polarity=Neg</span>
            </td>
        </tr>
    </table>
</div>
            """
            yield example
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": prepare_morpheme_stream(stream),
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "spans_manual"}
            ],
            "labels": simple_labels,
            "spans_key": "spans",
            "custom_theme": {
                "labels": {
                    "Root": "#3b82f6",
                    "Prefix": "#60a5fa",
                    "Suffix": "#93c5fd",
                    "Person=1": "#22c55e",
                    "Person=2": "#4ade80",
                    "Person=3": "#86efac",
                    "Tense=Fut": "#facc15",
                    "Tense=Past": "#eab308",
                    "Polarity=Neg": "#ef4444",
                    "Number=Plur": "#14b8a6",
                }
            }
        }
    }


@prodigy.recipe(
    "guarani-char-spans",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    families=("Familias de etiquetas separadas por coma (legacy)", "option", "f", str),
    group=("Grupo UD: pos-tags, features, morfemas, features-tam, etc.", "option", "g", str),
)
def guarani_char_spans(dataset, source, families=None, group=None):
    """
    Anotación por CARACTERES - con soporte para grupos UD
    
    Tokeniza a nivel de caracter para anotación precisa de morfemas.
    Incluye botón de contexto y atajo Ctrl+Shift+C.
    
    Grupos UD disponibles (-g/--group):
        pos-tags              POS Tags (VERB, NOUN, PRON, etc.)
        features              Todos los features morfológicos
        morfemas              Raíz, Prefijo, Sufijo
        features-persona-numero   Persona, Número, Clusividad
        features-caso             Casos
        features-tam              Tiempo, Aspecto, Modo
        features-relacional       Prefijos relacionales
        features-nominalizadores  Nominalizadores
        features-otros            Otros features
    
    Uso:
        prodigy guarani-char-spans dataset ./data/texts.jsonl -F recipes/guarani_spans.py
        prodigy guarani-char-spans dataset ./data/texts.jsonl -g pos-tags -F recipes/guarani_spans.py
        prodigy guarani-char-spans dataset ./data/texts.jsonl -f "morfema,persona,tiempo" -F recipes/guarani_spans.py
    """
    
    # Determinar etiquetas a usar (igual que guarani-spans)
    selected_group_name = None
    if group:
        group_info = get_ud_main_group(group) or get_specialized_group(group)
        if group_info:
            labels = group_info["labels"]
            selected_group_name = group
            print(f"📋 Grupo: {group} - {group_info['description']}")
            print(f"   {len(labels)} etiquetas")
        else:
            available_ud = ", ".join(list_ud_main_groups().keys())
            available_spec = ", ".join(list_specialized_groups().keys())
            print(f"❌ Error: Grupo '{group}' no encontrado")
            print(f"   Grupos UD: {available_ud}")
            print(f"   Grupos especializados: {available_spec}")
            import sys
            sys.exit(1)
    elif families:
        selected_family_keys = [f.strip().lower() for f in families.split(",")]
        selected_families = [FAMILY_KEYS.get(k) for k in selected_family_keys if k in FAMILY_KEYS]
        labels = []
        for family_name in selected_families:
            if family_name and family_name in LABEL_FAMILIES:
                labels.extend(LABEL_FAMILIES[family_name]["labels"])
        if not labels:
            labels = BASIC_FRIENDLY_LABELS
        print(f"📋 Familias: {len(labels)} etiquetas")
    else:
        labels = get_all_ud_ordered_labels()
        print(f"📋 Usando todas las etiquetas: {len(labels)}")
    
    # Pre-cargar oraciones para contexto
    all_examples = list(JSONL(source))
    print(f"📚 Cargadas {len(all_examples)} oraciones")
    
    # Crear índice de contexto
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
    
    def prepare_char_stream(examples_list, active_labels, group_name):
        for example in examples_list:
            guarani_text = example.get('text', '')
            
            if not guarani_text:
                continue
            
            # Crear tokens a nivel de CARACTER
            tokens = []
            for i, char in enumerate(guarani_text):
                tokens.append({
                    "text": char,
                    "start": i,
                    "end": i + 1,
                    "id": i,
                    "ws": False
                })
            
            example["text"] = guarani_text
            example["tokens"] = tokens
            example["spans"] = []
            
            # Obtener contexto
            ctx = context_index.get(guarani_text, {})
            
            # Generar HTML con contexto
            example["html"] = generate_html_with_context(example, active_labels, ctx, group_name)
            
            example = set_hashes(example)
            yield example
    
    # Construir custom_theme
    label_colors = get_ud_label_colors()
    custom_theme = {"labels": {}}
    for label in labels:
        custom_theme["labels"][label] = label_colors.get(label, LABEL_COLORS.get(label, "#6b7280"))
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": prepare_char_stream(all_examples, labels, selected_group_name),
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "spans_manual"}
            ],
            "labels": labels,
            "spans_key": "spans",
            "custom_theme": custom_theme,
            "javascript": CONTEXT_POPUP_JS,
        }
    }


# =============================================================================
# RECIPE PARA VALIDAR/CORREGIR SPANS EXISTENTES
# =============================================================================

@prodigy.recipe(
    "guarani-spans-correct",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data with existing spans (JSONL)", "positional", None, str),
)
def guarani_spans_correct(dataset, source):
    """
    Corregir spans existentes - útil para QA y revisión
    
    Carga datos que ya tienen spans anotados para corrección/validación.
    Usa etiquetas amigables en español.
    
    Uso:
        prodigy guarani-spans-correct corrected_spans ./data/annotated.jsonl -F recipes/guarani_spans.py
    """
    
    # Usar todas las etiquetas amigables
    all_labels = ALL_FRIENDLY_LABELS
    
    stream = JSONL(source)
    
    def prepare_correction_stream(stream):
        for example in stream:
            guarani_text = example.get('text', '')
            spanish_text = example.get('meta', {}).get('spanish_text', '')
            existing_spans = example.get('spans', [])
            
            if not guarani_text:
                continue
            
            # Re-tokenizar si no hay tokens
            if 'tokens' not in example:
                doc = nlp(guarani_text)
                tokens = []
                for i, token in enumerate(doc):
                    tokens.append({
                        "text": token.text,
                        "start": token.idx,
                        "end": token.idx + len(token.text),
                        "id": i,
                        "ws": token.whitespace_ != ""
                    })
                example["tokens"] = tokens
            
            # Mantener spans existentes
            example["spans"] = existing_spans
            example = set_hashes(example)
            
            span_count = len(existing_spans)
            span_labels = set(s.get('label', '') for s in existing_spans)
            
            example["html"] = f"""
<div style="margin-bottom:15px;">
    <table style="width:100%;border-collapse:collapse;margin-bottom:10px;">
        <tr style="background:#f59e0b;color:white;">
            <td style="padding:10px;font-weight:bold;font-size:16px;">
                ✏️ Correccion de Spans
            </td>
        </tr>
    </table>
    <table style="width:100%;border-collapse:collapse;background:#fef3c7;margin-bottom:8px;">
        <tr>
            <td style="padding:10px;border-left:4px solid #f59e0b;">
                <b>🇪🇸 Español:</b> {spanish_text or 'N/A'}
            </td>
        </tr>
    </table>
    <table style="width:100%;border-collapse:collapse;background:#fff7ed;margin-bottom:8px;">
        <tr>
            <td style="padding:8px;font-size:12px;">
                <b>📊</b> {span_count} spans existentes | Etiquetas: {', '.join(span_labels) if span_labels else 'ninguna'}
            </td>
        </tr>
    </table>
    <table style="width:100%;border-collapse:collapse;background:#fef9c3;">
        <tr>
            <td style="padding:8px;font-size:12px;">
                <b>✅</b> Revisa y corrige los spans. Click en span + X para eliminar.
            </td>
        </tr>
    </table>
</div>
            """
            yield example
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": prepare_correction_stream(stream),
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "spans_manual"}
            ],
            "labels": all_labels,
            "spans_key": "spans"
        }
    }


# =============================================================================
# RECIPES ESPECIALIZADOS POR GRUPO DE ETIQUETAS
# =============================================================================
# Cada recipe se enfoca en un conjunto específico de etiquetas para facilitar
# la anotación por tareas especializadas.
# =============================================================================

def _create_specialized_stream(stream, group_key: str, char_level: bool = False):
    """
    Función auxiliar para crear streams especializados.
    
    Args:
        stream: Stream de datos JSONL
        group_key: Clave del grupo especializado
        char_level: Si True, tokeniza por caracteres
    
    Yields:
        Ejemplos preparados para el recipe
    """
    group = get_specialized_group(group_key)
    if not group:
        raise ValueError(f"Grupo no encontrado: {group_key}")
    
    for example in stream:
        guarani_text = example.get('text', '')
        spanish_text = example.get('meta', {}).get('spanish_text', '')
        
        if not guarani_text:
            continue
        
        # Tokenizar según nivel
        if char_level:
            tokens = []
            for i, char in enumerate(guarani_text):
                tokens.append({
                    "text": char,
                    "start": i,
                    "end": i + 1,
                    "id": i,
                    "ws": False
                })
        else:
            doc = nlp(guarani_text)
            tokens = []
            for i, token in enumerate(doc):
                tokens.append({
                    "text": token.text,
                    "start": token.idx,
                    "end": token.idx + len(token.text),
                    "id": i,
                    "ws": token.whitespace_ != ""
                })
        
        example["text"] = guarani_text
        example["tokens"] = tokens
        example["spans"] = []
        example = set_hashes(example)
        
        # Generar HTML con información del grupo
        labels_html = " ".join([
            f'<span style="background:{group["color"]};color:white;padding:2px 6px;margin:1px;font-size:11px;border-radius:3px;display:inline-block;">{l}</span>'
            for l in group["labels"]
        ])
        
        mode_text = "por caracteres" if char_level else "por tokens"
        
        example["html"] = f"""
<div style="margin-bottom:15px;">
    <table style="width:100%;border-collapse:collapse;margin-bottom:10px;">
        <tr style="background:{group['color']};color:white;">
            <td style="padding:10px;font-weight:bold;font-size:16px;">
                {group['emoji']} {group['name']} - Anotación {mode_text}
            </td>
        </tr>
    </table>
    <table style="width:100%;border-collapse:collapse;background:#fef3c7;margin-bottom:8px;">
        <tr>
            <td style="padding:10px;border-left:4px solid {group['color']};">
                <b>🇪🇸 Español:</b> {spanish_text or 'No disponible'}
            </td>
        </tr>
    </table>
    <table style="width:100%;border-collapse:collapse;background:#f0fdf4;margin-bottom:8px;">
        <tr>
            <td style="padding:8px;font-size:13px;color:#166534;">
                <b>📋 Tarea:</b> {group['description']}
            </td>
        </tr>
    </table>
    <table style="width:100%;border-collapse:collapse;background:#f8fafc;border:1px solid #e2e8f0;">
        <tr>
            <td style="padding:8px;">
                <b style="color:#475569;">🏷️ Etiquetas ({len(group['labels'])}):</b>
            </td>
        </tr>
        <tr>
            <td style="padding:8px;">
                {labels_html}
            </td>
        </tr>
    </table>
</div>
        """
        yield example


def _get_specialized_config(group_key: str):
    """Obtiene la configuración para un recipe especializado."""
    group = get_specialized_group(group_key)
    if not group:
        return None
    
    custom_theme = {"labels": {}}
    for label in group["labels"]:
        custom_theme["labels"][label] = LABEL_COLORS.get(label, group["color"])
    
    return {
        "blocks": [
            {"view_id": "html"},
            {"view_id": "spans_manual"}
        ],
        "labels": group["labels"],
        "spans_key": "spans",
        "custom_theme": custom_theme
    }


# =============================================================================
# RECIPE: MORFEMAS BÁSICOS (Raíz, Prefijo, Sufijo)
# =============================================================================

@prodigy.recipe(
    "guarani-task-morfemas",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    char_level=("Anotación por caracteres (yes/no)", "option", "c", str),
)
def guarani_task_morfemas(dataset, source, char_level="no"):
    """
    TAREA ESPECIALIZADA: Morfemas Básicos
    
    Etiquetas: Raíz, Prefijo, Sufijo (3 etiquetas)
    
    Ideal para:
    - Identificar la estructura morfológica de las palabras
    - Separar raíces de afijos
    - Primera pasada de análisis morfológico
    
    Uso:
        # Por tokens
        prodigy guarani-task-morfemas morfemas ./data/texts.jsonl -F recipes/guarani_spans.py
        
        # Por caracteres (más fino)
        prodigy guarani-task-morfemas morfemas ./data/texts.jsonl -c -F recipes/guarani_spans.py
    """
    stream = JSONL(source)
    config = _get_specialized_config("morfemas-basicos")
    use_chars = char_level.lower() in ("yes", "y", "true", "1", "si", "sí")
    
    print(f"📦 Cargando recipe: Morfemas Básicos")
    print(f"   Etiquetas: Raíz, Prefijo, Sufijo")
    print(f"   Modo: {'Caracteres' if use_chars else 'Tokens'}")
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": _create_specialized_stream(stream, "morfemas-basicos", use_chars),
        "config": config
    }


# =============================================================================
# RECIPE: CATEGORÍAS GRAMATICALES (POS Tagging)
# =============================================================================

@prodigy.recipe(
    "guarani-task-categorias",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    char_level=("Anotación por caracteres (yes/no)", "option", "c", str),
)
def guarani_task_categorias(dataset, source, char_level="no"):
    """
    TAREA ESPECIALIZADA: Categorías Gramaticales (POS Tagging)
    
    Etiquetas: Verbo, Sustantivo, Pronombre, Adverbio, Posposición,
               Determinante, Numeral, Partícula, Interjección, 
               Nombre Propio, Puntuación (11 etiquetas)
    
    Ideal para:
    - Clasificación de partes del discurso
    - POS tagging del guaraní
    - Análisis sintáctico básico
    
    Uso:
        prodigy guarani-task-categorias pos ./data/texts.jsonl -F recipes/guarani_spans.py
    """
    stream = JSONL(source)
    config = _get_specialized_config("categorias")
    use_chars = char_level.lower() in ("yes", "y", "true", "1", "si", "sí")
    
    print(f"🏷️ Cargando recipe: Categorías Gramaticales")
    print(f"   Etiquetas: VERB, NOUN, PRON, ADV, ADP, DET, NUM, PART, INTJ, PROPN, PUNCT")
    print(f"   Modo: {'Caracteres' if use_chars else 'Tokens'}")
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": _create_specialized_stream(stream, "categorias", use_chars),
        "config": config
    }


# =============================================================================
# RECIPE: PERSONA Y NÚMERO
# =============================================================================

@prodigy.recipe(
    "guarani-task-persona",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    char_level=("Anotación por caracteres (yes/no)", "option", "c", str),
)
def guarani_task_persona(dataset, source, char_level="no"):
    """
    TAREA ESPECIALIZADA: Persona y Número
    
    Etiquetas: 1ra Persona, 2da Persona, 3ra Persona,
               Singular, Plural, Inclusivo, Exclusivo (7 etiquetas)
    
    Ideal para:
    - Identificar marcadores de persona
    - Marcar número gramatical
    - Análisis de clusividad (1ra plural inclusivo/exclusivo)
    
    Uso:
        prodigy guarani-task-persona persona ./data/texts.jsonl -c yes -F recipes/guarani_spans.py
    """
    stream = JSONL(source)
    config = _get_specialized_config("persona-numero")
    use_chars = char_level.lower() in ("yes", "y", "true", "1", "si", "sí")
    
    print(f"👤 Cargando recipe: Persona y Número")
    print(f"   Etiquetas: 1P, 2P, 3P, Sing, Plur, Incl, Excl")
    print(f"   Modo: {'Caracteres' if use_chars else 'Tokens'}")
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": _create_specialized_stream(stream, "persona-numero", use_chars),
        "config": config
    }


# =============================================================================
# RECIPE: TIEMPO, ASPECTO Y MODO (TAM)
# =============================================================================

@prodigy.recipe(
    "guarani-task-tam",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    char_level=("Anotación por caracteres (yes/no)", "option", "c", str),
)
def guarani_task_tam(dataset, source, char_level="no"):
    """
    TAREA ESPECIALIZADA: Tiempo, Aspecto y Modo (TAM)
    
    Etiquetas: Pasado, Futuro, Futuro-Pasado,
               Completivo, Iterativo, Sucesivo, Habitual,
               Imperativo, Permisivo, Gerundio (10 etiquetas)
    
    Ideal para:
    - Identificar marcadores temporales
    - Marcar aspecto verbal
    - Análisis de modo verbal
    
    Uso:
        prodigy guarani-task-tam tam ./data/texts.jsonl -c yes -F recipes/guarani_spans.py
    """
    stream = JSONL(source)
    config = _get_specialized_config("tam")
    use_chars = char_level.lower() in ("yes", "y", "true", "1", "si", "sí")
    
    print(f"⏰ Cargando recipe: Tiempo, Aspecto y Modo")
    print(f"   Etiquetas: Past, Fut, Perf, Iter, Imp, Perm, Ger...")
    print(f"   Modo: {'Caracteres' if use_chars else 'Tokens'}")
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": _create_specialized_stream(stream, "tam", use_chars),
        "config": config
    }


# =============================================================================
# RECIPE: CASO Y RELACIONAL
# =============================================================================

@prodigy.recipe(
    "guarani-task-caso",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    char_level=("Anotación por caracteres (yes/no)", "option", "c", str),
)
def guarani_task_caso(dataset, source, char_level="no"):
    """
    TAREA ESPECIALIZADA: Caso y Relacional
    
    Etiquetas: Ablativo, Alativo, Locativo, Dativo, Referencial,
               Rel. Absoluto, Rel. Contiguo, Rel. No-Contiguo, 
               Correferencial (9 etiquetas)
    
    Ideal para:
    - Identificar casos gramaticales
    - Marcar relacionales del Tupí-Guaraní
    - Análisis de argumentos verbales
    
    Uso:
        prodigy guarani-task-caso caso ./data/texts.jsonl -c yes -F recipes/guarani_spans.py
    """
    stream = JSONL(source)
    config = _get_specialized_config("caso-relacional")
    use_chars = char_level.lower() in ("yes", "y", "true", "1", "si", "sí")
    
    print(f"📍 Cargando recipe: Caso y Relacional")
    print(f"   Etiquetas: Abl, All, Loc, Dat, Ref, Rel...")
    print(f"   Modo: {'Caracteres' if use_chars else 'Tokens'}")
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": _create_specialized_stream(stream, "caso-relacional", use_chars),
        "config": config
    }


# =============================================================================
# RECIPE: VOZ Y POLARIDAD
# =============================================================================

@prodigy.recipe(
    "guarani-task-voz",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    char_level=("Anotación por caracteres (yes/no)", "option", "c", str),
)
def guarani_task_voz(dataset, source, char_level="no"):
    """
    TAREA ESPECIALIZADA: Voz y Polaridad
    
    Etiquetas: Causativo, Comitativo, Negación (3 etiquetas)
    
    Ideal para:
    - Identificar voz verbal (causativo, comitativo)
    - Marcar negación
    
    Uso:
        prodigy guarani-task-voz voz ./data/texts.jsonl -c yes -F recipes/guarani_spans.py
    """
    stream = JSONL(source)
    config = _get_specialized_config("voz-polaridad")
    use_chars = char_level.lower() in ("yes", "y", "true", "1", "si", "sí")
    
    print(f"🔊 Cargando recipe: Voz y Polaridad")
    print(f"   Etiquetas: Cau, Com, Neg")
    print(f"   Modo: {'Caracteres' if use_chars else 'Tokens'}")
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": _create_specialized_stream(stream, "voz-polaridad", use_chars),
        "config": config
    }


# =============================================================================
# RECIPE: NOMINALIZADORES
# =============================================================================

@prodigy.recipe(
    "guarani-task-nomz",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    char_level=("Anotación por caracteres (yes/no)", "option", "c", str),
)
def guarani_task_nominalizadores(dataset, source, char_level="no"):
    """
    TAREA ESPECIALIZADA: Nominalizadores
    
    Etiquetas: Agentivo (-sar), Circunstancial (-saβ), Pasivo (-pɨr), 
               C-Circunstancial, Derivación Pasiva, Relativo (6 etiquetas)
    
    Ideal para:
    - Identificar sufijos nominalizadores
    - Análisis de derivación verbal→nominal
    
    Uso:
        prodigy guarani-task-nomz nomz ./data/texts.jsonl -c yes -F recipes/guarani_spans.py
    """
    stream = JSONL(source)
    config = _get_specialized_config("nominalizadores")
    use_chars = char_level.lower() in ("yes", "y", "true", "1", "si", "sí")
    
    print(f"🔧 Cargando recipe: Nominalizadores")
    print(f"   Etiquetas: Ag, Circ, Pas, CCirc, DevPass, Rel")
    print(f"   Modo: {'Caracteres' if use_chars else 'Tokens'}")
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": _create_specialized_stream(stream, "nominalizadores", use_chars),
        "config": config
    }


# =============================================================================
# RECIPE: OTROS FEATURES
# =============================================================================

@prodigy.recipe(
    "guarani-task-otros",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    char_level=("Anotación por caracteres (yes/no)", "option", "c", str),
)
def guarani_task_otros(dataset, source, char_level="no"):
    """
    TAREA ESPECIALIZADA: Otros Features
    
    Etiquetas: No-Primera Mano, Enfático, Intensificador, Privativo, 
               Reduplicación, Interrogativo, Correferencia, Reflexivo,
               Poseedor (9 etiquetas)
    
    Ideal para:
    - Features menos comunes
    - Evidencialidad
    - Énfasis e intensificación
    
    Uso:
        prodigy guarani-task-otros otros ./data/texts.jsonl -c yes -F recipes/guarani_spans.py
    """
    stream = JSONL(source)
    config = _get_specialized_config("otros-features")
    use_chars = char_level.lower() in ("yes", "y", "true", "1", "si", "sí")
    
    print(f"✨ Cargando recipe: Otros Features")
    print(f"   Etiquetas: Evident, Emph, Intens, Priv, Red, Int, Corf, Refl, Poss")
    print(f"   Modo: {'Caracteres' if use_chars else 'Tokens'}")
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": _create_specialized_stream(stream, "otros-features", use_chars),
        "config": config
    }


# =============================================================================
# RECIPE GENÉRICO POR GRUPO
# =============================================================================

@prodigy.recipe(
    "guarani-task",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    group=("Grupo de etiquetas", "option", "g", str),
    char_level=("Anotación por caracteres (yes/no)", "option", "c", str),
)
def guarani_task_generic(dataset, source, group=None, char_level="no"):
    """
    RECIPE GENÉRICO POR GRUPO DE ETIQUETAS
    
    Grupos disponibles (-g/--group):
        morfemas-basicos  : Raíz, Prefijo, Sufijo (3)
        categorias        : VERB, NOUN, PRON, etc. (11)
        persona-numero    : 1P, 2P, 3P, Sing, Plur (7)
        tam               : Tiempo, Aspecto, Modo (10)
        caso-relacional   : Casos y relacionales (9)
        voz-polaridad     : Voz y negación (3)
        nominalizadores   : Sufijos nomz (6)
        otros-features    : Otros features (9)
    
    Uso:
        prodigy guarani-task dataset ./data/texts.jsonl -g morfemas-basicos -F recipes/guarani_spans.py
        prodigy guarani-task dataset ./data/texts.jsonl -g categorias -c yes -F recipes/guarani_spans.py
    """
    if not group:
        # Mostrar grupos disponibles
        print("\n❌ Error: Debes especificar un grupo con -g/--group\n")
        print("Grupos disponibles:")
        for key, name in list_specialized_groups().items():
            g = get_specialized_group(key)
            print(f"  {key:20} : {name} ({len(g['labels'])} etiquetas)")
        print("\nEjemplo:")
        print(f"  prodigy guarani-task {dataset} {source} -g morfemas-basicos -F recipes/guarani_spans.py")
        raise SystemExit(1)
    
    if group not in SPECIALIZED_GROUPS:
        print(f"\n❌ Error: Grupo '{group}' no existe\n")
        print("Grupos válidos:")
        for key in SPECIALIZED_GROUPS.keys():
            print(f"  - {key}")
        raise SystemExit(1)
    
    stream = JSONL(source)
    config = _get_specialized_config(group)
    group_info = get_specialized_group(group)
    use_chars = char_level.lower() in ("yes", "y", "true", "1", "si", "sí")
    
    print(f"\n{group_info['emoji']} Cargando recipe: {group_info['name']}")
    print(f"   Etiquetas: {len(group_info['labels'])}")
    print(f"   Modo: {'Caracteres' if use_chars else 'Tokens'}")
    print()
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": _create_specialized_stream(stream, group, use_chars),
        "config": config
    }
