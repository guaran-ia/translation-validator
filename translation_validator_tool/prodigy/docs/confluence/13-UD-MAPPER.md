# 🏷️ Universal Dependencies Mapper

El archivo `ud_guarani_mapper.py` es la **única fuente de verdad** para el mapeo entre etiquetas amigables en español y códigos Universal Dependencies.

---

## 1. Propósito

El mapper centralizado permite:

1. **Etiquetas amigables** para anotadores (ej: "Sustantivo")
2. **Códigos UD estándar** para exportación (ej: "NOUN")
3. **Conversión bidireccional** entre formatos
4. **Colores consistentes** en la interfaz

---

## 2. Ubicación

```
prodigy/
└── scripts/
    └── ud_guarani_mapper.py   # ← Mapper centralizado
```

---

## 3. Importar el Mapper

```python
# En cualquier recipe o script
import sys
from pathlib import Path

# Agregar scripts al path
scripts_dir = Path(__file__).parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from ud_guarani_mapper import (
    FRIENDLY_TO_UD,           # Dict: Amigable → UD
    UD_TO_FRIENDLY,           # Dict: UD → Amigable
    map_label,                # Función de conversión
    LABEL_COLORS,             # Colores por etiqueta
    VALID_UPOS,               # Set de UPOS válidos
    VALID_FEATURES,           # Set de Features válidos
    SPECIALIZED_GROUPS,       # Grupos de etiquetas
)
```

---

## 4. Mapeo Principal

### 4.1 FRIENDLY_TO_UD

Diccionario que mapea etiquetas amigables a códigos UD:

```python
FRIENDLY_TO_UD = {
    # === MORFEMAS ===
    "Raíz": "Root",
    "Prefijo": "Prefix",
    "Sufijo": "Suffix",
    
    # === PERSONA ===
    "1ra Persona": "Person=1",
    "2da Persona": "Person=2",
    "3ra Persona": "Person=3",
    
    # === NÚMERO ===
    "Singular": "Number=Sing",
    "Plural": "Number=Plur",
    
    # === CLUSIVIDAD (específico Guaraní) ===
    "Inclusivo": "Clusivity=In",
    "Exclusivo": "Clusivity=Ex",
    
    # === CASO ===
    "Ablativo": "Case=Abl",
    "Alativo": "Case=All",
    "Dativo": "Case=Dat",
    "Locativo": "Case=Loc",
    "Referencial": "Case=Ref",
    
    # === RELACIONAL (Tupí-Guaraní) ===
    "Rel. Absoluto": "Rel=Abs",
    "Rel. Contiguo": "Rel=Cont",
    "Rel. No-Contiguo": "Rel=NCont",
    
    # === TIEMPO ===
    "Pasado": "Tense=Past",
    "Futuro": "Tense=Fut",
    "Futuro-Pasado": "Tense=FutPast",
    
    # === MODO ===
    "Imperativo": "Mood=Imp",
    "Permisivo": "Mood=Perm",
    
    # === VOZ ===
    "Causativo": "Voice=Cau",
    "Comitativo": "Voice=Com",
    
    # === FORMA VERBAL ===
    "Gerundio": "VerbForm=Ger",
    
    # === POLARIDAD ===
    "Negación": "Polarity=Neg",
    
    # === NOMINALIZADORES ===
    "Agentivo (-sar)": "Nomzr=Ag",
    "Circunstancial (-saβ)": "Nomzr=Circ",
    "Pasivo (-pɨr)": "Nomzr=Pas",
    
    # === CATEGORÍAS GRAMATICALES (UPOS) ===
    "Verbo": "VERB",
    "Sustantivo": "NOUN",
    "Pronombre": "PRON",
    "Adverbio": "ADV",
    "Posposición": "ADP",
    "Determinante": "DET",
    "Numeral": "NUM",
    "Partícula": "PART",
    "Interjección": "INTJ",
    "Nombre Propio": "PROPN",
    "Puntuación": "PUNCT",
    
    # === RELACIONES SINTÁCTICAS ===
    "RAÍZ (Verbo Principal)": "root",
    "SUJETO": "nsubj",
    "OBJETO DIRECTO": "obj",
    "OBJETO INDIRECTO": "iobj",
    "COMPLEMENTO OBLICUO": "obl",
    "MODIFICADOR ADVERBIAL": "advmod",
    "MODIFICADOR NOMINAL": "nmod",
    "DETERMINANTE (Rel)": "det",
    "MARCADOR DE CASO": "case",
    # ... etc
}
```

### 4.2 UD_TO_FRIENDLY

Diccionario inverso generado automáticamente:

```python
UD_TO_FRIENDLY = {v: k for k, v in FRIENDLY_TO_UD.items()}

# Resultado:
# {
#     "NOUN": "Sustantivo",
#     "VERB": "Verbo",
#     "Person=1": "1ra Persona",
#     "nsubj": "SUJETO",
#     ...
# }
```

---

## 5. Función de Conversión

### `map_label(label, direction)`

```python
def map_label(label: str, direction: str = "to_ud") -> str:
    """
    Convierte una etiqueta entre formato amigable y UD.
    
    Args:
        label: Etiqueta a convertir
        direction: "to_ud" o "to_friendly"
    
    Returns:
        Etiqueta convertida, o la original si no hay mapeo
    """
    if direction == "to_ud":
        return FRIENDLY_TO_UD.get(label, label)
    elif direction == "to_friendly":
        return UD_TO_FRIENDLY.get(label, label)
    return label
```

### Ejemplos de uso

```python
# Amigable → UD
map_label("Sustantivo", "to_ud")       # "NOUN"
map_label("1ra Persona", "to_ud")      # "Person=1"
map_label("SUJETO", "to_ud")           # "nsubj"

# UD → Amigable
map_label("VERB", "to_friendly")       # "Verbo"
map_label("Tense=Past", "to_friendly") # "Pasado"
map_label("obj", "to_friendly")        # "OBJETO DIRECTO"
```

---

## 6. Grupos Especializados

### SPECIALIZED_GROUPS

Grupos de etiquetas organizados por función:

```python
SPECIALIZED_GROUPS = {
    "pos-tags": {
        "name": "POS Tags",
        "description": "Categorías gramaticales UD",
        "labels": [
            "Sustantivo", "Verbo", "Pronombre", "Nombre Propio",
            "Determinante", "Posposición", "Adverbio", "Numeral",
            "Partícula", "Interjección", "Puntuación"
        ],
        "colors": {...}
    },
    
    "features": {
        "name": "Features Morfológicos",
        "description": "Características morfológicas completas",
        "labels": [
            "1ra Persona", "2da Persona", "3ra Persona",
            "Singular", "Plural", "Inclusivo", "Exclusivo",
            # ... 30+ etiquetas
        ],
        "colors": {...}
    },
    
    "relations": {
        "name": "Relaciones Sintácticas",
        "description": "Dependencias UD para Old Guaraní",
        "labels": [
            "RAÍZ (Verbo Principal)", "SUJETO", "OBJETO DIRECTO",
            "OBJETO INDIRECTO", "COMPLEMENTO OBLICUO",
            # ... 20 etiquetas
        ],
        "ud_mapping": {
            "RAÍZ (Verbo Principal)": "root",
            "SUJETO": "nsubj",
            "OBJETO DIRECTO": "obj",
            # ...
        },
        "colors": {...}
    },
    
    "morfemas": {
        "name": "Morfemas",
        "description": "Análisis morfológico",
        "labels": ["Raíz", "Prefijo", "Sufijo"],
        "colors": {...}
    }
}
```

### Acceder a grupos

```python
from ud_guarani_mapper import get_specialized_group, get_specialized_labels

# Obtener grupo completo
pos_group = get_specialized_group("pos-tags")
# {"name": "POS Tags", "labels": [...], "colors": {...}}

# Solo etiquetas
pos_labels = get_specialized_labels("pos-tags")
# ["Sustantivo", "Verbo", "Pronombre", ...]
```

---

## 7. Colores de Etiquetas

### LABEL_COLORS

Colores consistentes para todas las etiquetas:

```python
LABEL_COLORS = {
    # POS
    "Sustantivo": "#22c55e",     # Verde
    "Verbo": "#ef4444",          # Rojo
    "Pronombre": "#3b82f6",      # Azul
    "Adverbio": "#f97316",       # Naranja
    
    # Features
    "1ra Persona": "#8b5cf6",    # Púrpura
    "2da Persona": "#06b6d4",    # Cyan
    "3ra Persona": "#84cc16",    # Lima
    "Pasado": "#f97316",         # Naranja
    "Futuro": "#14b8a6",         # Teal
    "Negación": "#ef4444",       # Rojo
    
    # Relations
    "SUJETO": "#22c55e",         # Verde
    "OBJETO DIRECTO": "#3b82f6", # Azul
    "OBJETO INDIRECTO": "#8b5cf6", # Púrpura
}
```

### Uso en recipes

```python
from ud_guarani_mapper import LABEL_COLORS

# En la configuración del recipe
config = {
    "labels": ["Sustantivo", "Verbo", "Pronombre"],
    "colors": LABEL_COLORS,  # Colores automáticos
}
```

---

## 8. Validación de Etiquetas

### VALID_UPOS

Set de categorías gramaticales válidas:

```python
VALID_UPOS = {
    # Documentados en Old Guaraní
    "ADP", "ADV", "DET", "INTJ", "NOUN", "NUM", 
    "PART", "PRON", "PROPN", "PUNCT", "VERB",
    # No documentados pero posibles
    "ADJ", "AUX", "CCONJ", "SCONJ", "SYM", "X",
}
```

### VALID_FEATURES

Set de features morfológicos válidos:

```python
VALID_FEATURES = {
    "Case", "Clusivity", "Corf", "Dev", "Emph", "Evident",
    "Int", "Intens", "Mood", "Nomzr", "Number", "Number[psor]",
    "Number[subj]", "Person", "Person[obj]", "Person[psor]",
    "Person[subj]", "Polarity", "Poss", "Priv", "PronType",
    "Red", "Reflex", "Rel", "Tense", "Voice", "VerbForm",
}
```

### Validar etiquetas

```python
def is_valid_upos(label: str) -> bool:
    ud_label = map_label(label, "to_ud")
    return ud_label in VALID_UPOS

# Ejemplo
is_valid_upos("Sustantivo")  # True (→ NOUN)
is_valid_upos("Adjetivo")    # False (ADJ no usado en Old Guaraní)
```

---

## 9. Conversión de Spans

### Convertir spans amigables a UD

```python
def convert_spans_to_ud(spans: list) -> list:
    """Convierte lista de spans de amigable a UD."""
    converted = []
    for span in spans:
        new_span = span.copy()
        if "label" in new_span:
            new_span["label"] = map_label(new_span["label"], "to_ud")
        converted.append(new_span)
    return converted

# Ejemplo
spans = [
    {"start": 0, "end": 5, "label": "Sustantivo"},
    {"start": 6, "end": 10, "label": "Verbo"}
]

ud_spans = convert_spans_to_ud(spans)
# [
#     {"start": 0, "end": 5, "label": "NOUN"},
#     {"start": 6, "end": 10, "label": "VERB"}
# ]
```

### Convertir UD a amigable

```python
def convert_spans_to_friendly(spans: list) -> list:
    """Convierte lista de spans de UD a amigable."""
    converted = []
    for span in spans:
        new_span = span.copy()
        if "label" in new_span:
            new_span["label"] = map_label(new_span["label"], "to_friendly")
        converted.append(new_span)
    return converted
```

---

## 10. Referencia UD

El mapper está basado en la documentación oficial de Universal Dependencies para Old Guaraní:

**URL:** https://universaldependencies.org/treebanks/gn_oldtudet/index.html

### UPOS usados en Old Guaraní

| UPOS | Descripción | Frecuencia |
|------|-------------|------------|
| VERB | Verbos | Alta |
| NOUN | Sustantivos | Alta |
| PRON | Pronombres | Media |
| ADP | Posposiciones | Media |
| ADV | Adverbios | Media |
| DET | Determinantes | Baja |
| NUM | Numerales | Baja |
| PART | Partículas | Media |
| INTJ | Interjecciones | Baja |
| PROPN | Nombres propios | Baja |
| PUNCT | Puntuación | Alta |

### UPOS NO usados

- `ADJ` - No existe categoría adjetivo en Guaraní clásico
- `AUX` - No documentado
- `CCONJ`, `SCONJ` - No documentados
- `SYM` - No documentado

---

## 11. Siguiente Paso

Consulta [14-ETIQUETAS-POS.md](14-ETIQUETAS-POS.md) para detalles de las etiquetas POS.
