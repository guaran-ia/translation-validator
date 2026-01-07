# 🔗 Recipe: guarani-relations (Sintaxis)

El recipe `guarani-relations` permite la anotación de **relaciones sintácticas** (dependencias) entre tokens.

---

## 1. Descripción

Este recipe usa la interfaz `relations` de Prodigy para anotar:
- **Dependencias sintácticas** entre palabras
- **Relaciones semánticas** 
- **Estructura de árbol** de la oración

---

## 2. Uso

### Comando básico

```powershell
prodigy guarani-relations <dataset> <source> -F recipes/guarani_relations.py
```

### Con opciones

```powershell
# Con grupo específico
prodigy guarani-relations relations_data ./data/texts.jsonl \
  --group relations \
  -F recipes/guarani_relations.py
```

### Parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `dataset` | Nombre del dataset de salida |
| `source` | Archivo JSONL de entrada |
| `--group` | Grupo de etiquetas (default: relations) |

---

## 3. Etiquetas de Relaciones

### Lista completa (20 etiquetas)

| Etiqueta Amigable | Código UD | Descripción |
|-------------------|-----------|-------------|
| RAÍZ (Verbo Principal) | `root` | Verbo principal de la oración |
| SUJETO | `nsubj` | Sujeto nominal |
| OBJETO DIRECTO | `obj` | Objeto directo |
| OBJETO INDIRECTO | `iobj` | Objeto indirecto |
| COMPLEMENTO OBLICUO | `obl` | Complemento oblicuo |
| OBLICUO-OBJETO | `obl:obj` | Oblicuo con rol de objeto |
| OBLICUO-SUJETO | `obl:subj` | Oblicuo con rol de sujeto |
| MODIFICADOR ADVERBIAL | `advmod` | Adverbio modificador |
| CLÁUSULA ADVERBIAL | `advcl` | Cláusula adverbial |
| MODIFICADOR NOMINAL | `nmod` | Modificador nominal |
| MODIFICADOR NUMÉRICO | `nummod` | Numeral modificador |
| DETERMINANTE (Rel) | `det` | Determinante |
| MARCADOR DE CASO | `case` | Posposición/marcador |
| PALABRA COMPUESTA | `compound` | Compuesto |
| APOSICIÓN | `appos` | Aposición |
| COMPLEMENTO VERBAL | `xcomp` | Complemento clausal |
| ELEMENTO DE DISCURSO | `discourse` | Partícula de discurso |
| PARATAXIS | `parataxis` | Yuxtaposición |
| PUNTUACIÓN (Rel) | `punct` | Puntuación |
| DEPENDENCIA (General) | `dep` | Dependencia no clasificada |

---

## 4. Cómo Anotar Relaciones

### Proceso

1. **Identifica la RAÍZ**: Normalmente el verbo principal
2. **Conecta cada palabra** a su "head" (palabra de la que depende)
3. **Selecciona el tipo de relación**

### Ejemplo Visual

```
         RAÍZ
           │
       ┌───┴───┐
       │       │
    SUJETO    OBJ
       │       │
      Che   roipota
              │
           ┌──┴──┐
           │     │
          DET   NMOD
           │     │
          nde   rape
```

### Interfaz Prodigy

1. **Haz clic en la palabra dependiente**
2. **Haz clic en la palabra head**
3. **Selecciona la etiqueta de relación** del menú

```
┌─────────────────────────────────────────────────────────────────────┐
│   Che     roipota     nde      rape                                 │
│    │         │         │        │                                   │
│    └────────►│◄────────┼────────┘                                   │
│    SUJETO    │   DET   │  OBJ                                       │
│              │         │                                             │
│              └─────────┘                                             │
│                 NMOD                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Tokenización

El recipe tokeniza a nivel de **palabra** (no caracter):

```python
def tokenize_by_words(text: str) -> List[Dict]:
    """Tokeniza por palabras."""
    tokens = []
    words = text.split()
    current_pos = 0
    
    for i, word in enumerate(words):
        start = text.find(word, current_pos)
        end = start + len(word)
        
        token = {
            "text": word,
            "start": start,
            "end": end,
            "id": i,
            "ws": end < len(text) and text[end] == ' '
        }
        
        # Deshabilitar puntuación
        if word in '.,;:!?()[]{}"\'-':
            token["disabled"] = True
            
        tokens.append(token)
        current_pos = end
    
    return tokens
```

---

## 6. Colores de Relaciones

Cada tipo de relación tiene un color distintivo:

```python
RELATION_COLORS = {
    "RAÍZ (Verbo Principal)": "#ef4444",    # Rojo
    "SUJETO": "#22c55e",                     # Verde
    "OBJETO DIRECTO": "#3b82f6",             # Azul
    "OBJETO INDIRECTO": "#8b5cf6",           # Púrpura
    "COMPLEMENTO OBLICUO": "#f97316",        # Naranja
    "MODIFICADOR ADVERBIAL": "#06b6d4",      # Cyan
    "MODIFICADOR NOMINAL": "#84cc16",        # Lima
    "DETERMINANTE (Rel)": "#a855f7",         # Violeta
    "MARCADOR DE CASO": "#ec4899",           # Rosa
    "PUNTUACIÓN (Rel)": "#6b7280",           # Gris
}
```

---

## 7. Mapeo a Universal Dependencies

### Desde el mapper centralizado

```python
from ud_guarani_mapper import SPECIALIZED_GROUPS

# Obtener grupo de relaciones
_RELATIONS_GROUP = SPECIALIZED_GROUPS.get("relations", {})

# Etiquetas amigables
RELATION_LABELS = _RELATIONS_GROUP.get("labels", [])

# Mapeo a UD
RELATION_TO_UD = _RELATIONS_GROUP.get("ud_mapping", {})

# Ejemplo:
# RELATION_TO_UD["SUJETO"] → "nsubj"
# RELATION_TO_UD["OBJETO DIRECTO"] → "obj"
```

### Conversión al exportar

```python
def convert_relations_to_ud(relations):
    """Convierte relaciones de amigable a UD."""
    converted = []
    for rel in relations:
        new_rel = rel.copy()
        if "label" in new_rel:
            new_rel["label"] = RELATION_TO_UD.get(
                new_rel["label"], 
                new_rel["label"]
            )
        converted.append(new_rel)
    return converted
```

---

## 8. Estructura de Datos

### Entrada (JSONL)

```json
{
    "text": "Che roipota nde rape",
    "meta": {
        "spanish_text": "Yo quiero tu camino",
        "source": "doc1"
    }
}
```

### Salida (con relaciones)

```json
{
    "text": "Che roipota nde rape",
    "tokens": [
        {"text": "Che", "start": 0, "end": 3, "id": 0},
        {"text": "roipota", "start": 4, "end": 11, "id": 1},
        {"text": "nde", "start": 12, "end": 15, "id": 2},
        {"text": "rape", "start": 16, "end": 20, "id": 3}
    ],
    "relations": [
        {"head": 1, "child": 0, "label": "SUJETO"},
        {"head": 1, "child": 3, "label": "OBJETO DIRECTO"},
        {"head": 3, "child": 2, "label": "DETERMINANTE (Rel)"}
    ],
    "answer": "accept",
    "_session_id": "alice"
}
```

---

## 9. Task Routing (IAA)

El recipe soporta distribución de tareas para Inter-Annotator Agreement:

```python
ANNOTATIONS_PER_TASK = int(os.getenv("ANNOTATIONS_PER_TASK", "2"))
ENABLE_TASK_ROUTING = os.getenv("ENABLE_TASK_ROUTING", "true").lower() == "true"

def task_router_iaa(ctrl, session_id: str, item: Dict) -> List[str]:
    """Distribuye tareas entre anotadores."""
    pool = list(ctrl.session_ids)
    task_hash = item.get("_task_hash")
    
    n_annotators = min(ANNOTATIONS_PER_TASK, len(pool))
    start_idx = task_hash % len(pool)
    
    assigned = []
    for i in range(n_annotators):
        idx = (start_idx + i) % len(pool)
        assigned.append(pool[idx])
    
    return assigned
```

---

## 10. Logging

El recipe genera logs detallados:

```
logs/relations_recipe_20250115_103000.log
```

Formato:
```
10:30:00 | INFO    | LOG INICIADO: logs/relations_recipe_20250115.log
10:30:01 | INFO    | Cargando datos de: ./data/texts.jsonl
10:30:01 | INFO    | 100 ejemplos cargados
10:30:02 | DEBUG   | Ejemplo preparado: hash=123456
```

---

## 11. Configuración del Buffer

```python
BUFFER_CONFIG = load_buffer_config()
INSTANT_SUBMIT = BUFFER_CONFIG.get("instant_submit", False)
BATCH_SIZE = BUFFER_CONFIG.get("batch_size", 3)
```

---

## 12. Exportar Anotaciones

```powershell
# Exportar a JSONL
prodigy db-out relations_data > relations_output.jsonl

# Exportar con conversión a UD
python -c "
from scripts.export_relations import export_with_ud_mapping
export_with_ud_mapping('relations_data', 'output_ud.json')
"
```

---

## 13. Siguiente Paso

Continúa con [09-RECIPE-OPENAI.md](09-RECIPE-OPENAI.md) para pre-anotación con IA.
