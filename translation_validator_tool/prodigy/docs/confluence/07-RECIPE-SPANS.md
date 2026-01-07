# ✏️ Recipe: guarani-spans (Manual)

El recipe `guarani-spans` permite la anotación manual de spans con soporte para overlapping (superposición).

---

## 1. Descripción

Este recipe es ideal para:
- **Análisis morfológico** detallado
- **Prefijos y sufijos** que se superponen
- **Componentes aglutinantes** del Guaraní
- **Múltiples categorías** en el mismo segmento

---

## 2. Uso

### Comando básico

```powershell
prodigy guarani-spans <dataset> <source> -F recipes/guarani_spans.py
```

### Con opciones

```powershell
# Con grupo específico de etiquetas
prodigy guarani-spans dataset_name ./data/texts.jsonl \
  --group pos-tags \
  -F recipes/guarani_spans.py

# Tokenización por palabra (en vez de caracter)
prodigy guarani-spans dataset_name ./data/texts.jsonl \
  --word-level true \
  -F recipes/guarani_spans.py
```

### Parámetros

| Parámetro | Alias | Descripción |
|-----------|-------|-------------|
| `dataset` | - | Nombre del dataset de salida |
| `source` | - | Archivo JSONL de entrada |
| `--group` | `-g` | Grupo de etiquetas (pos-tags, features, morfemas) |
| `--families` | `-f` | Familias de etiquetas (legacy) |
| `--word-level` | `-w` | Tokenizar por palabra |

---

## 3. Grupos de Etiquetas

### Grupos disponibles (`--group`)

| Grupo | Descripción | Etiquetas |
|-------|-------------|-----------|
| `pos-tags` | Categorías gramaticales | VERB, NOUN, PRON, etc. |
| `features` | Todos los features | Persona, Número, Tiempo, etc. |
| `morfemas` | Análisis morfológico | Raíz, Prefijo, Sufijo |
| `features-persona-numero` | Persona y Número | 1ra/2da/3ra Persona, Sing/Plur |
| `features-caso` | Casos | Ablativo, Alativo, Dativo, Loc |
| `features-tam` | Tiempo/Aspecto/Modo | Pasado, Futuro, Imperativo |
| `features-relacional` | Prefijos relacionales | Rel. Absoluto/Contiguo/NCont |

### Ejemplo con grupo específico

```powershell
# Solo POS tags
prodigy guarani-spans pos_manual ./data/texts.jsonl \
  --group pos-tags \
  -F recipes/guarani_spans.py

# Solo morfemas
prodigy guarani-spans morph_manual ./data/texts.jsonl \
  --group morfemas \
  -F recipes/guarani_spans.py
```

---

## 4. Tokenización

### Nivel de caracter (default)

Por defecto, el texto se tokeniza a nivel de caracter, permitiendo seleccionar cualquier substring:

```python
def tokenize_by_char(text: str) -> List[Dict]:
    """Tokeniza cada caracter."""
    return [
        {"text": char, "start": i, "end": i + 1, "id": i}
        for i, char in enumerate(text)
    ]
```

**Ventaja:** Permite seleccionar morfemas exactos.

### Nivel de palabra (`--word-level`)

Con `--word-level`, se tokeniza por palabras:

```python
def tokenize_by_words(text: str) -> List[Dict]:
    """Tokeniza por palabras."""
    tokens = []
    for i, word in enumerate(text.split()):
        start = text.find(word, ...)
        tokens.append({
            "text": word,
            "start": start,
            "end": start + len(word),
            "id": i
        })
    return tokens
```

**Ventaja:** Más rápido para anotación de palabras completas.

---

## 5. Spans Superpuestos (Overlapping)

El recipe usa `spans_manual` que permite spans superpuestos:

```
Texto: "roipota"
        ───────
        │
        ├─ "ro-" → [1ra Persona], [Plural]
        ├─ "-ipo-" → [Raíz]
        └─ "-ta" → [Futuro]
```

**Ejemplo de datos:**

```json
{
    "text": "roipota",
    "spans": [
        {"start": 0, "end": 2, "label": "1ra Persona"},
        {"start": 0, "end": 2, "label": "Plural"},
        {"start": 2, "end": 5, "label": "Raíz"},
        {"start": 5, "end": 7, "label": "Futuro"}
    ]
}
```

---

## 6. Interfaz de Usuario

### HTML Header

El recipe genera un header informativo:

```
┌─────────────────────────────────────────────────────────────────────┐
│ ✏️ Anotación Manual - POS Tags                    📊 25/100 | 🏷️ 11│
├─────────────────────────────────────────────────────────────────────┤
│ 🇵🇾 Che roipota nde rape                                            │
│ 🇪🇸 Yo quiero tu camino                                             │
├─────────────────────────────────────────────────────────────────────┤
│ 🏷️ Etiquetas: [Sustantivo] [Verbo] [Pronombre] ...                 │
├─────────────────────────────────────────────────────────────────────┤
│ 👇 Selecciona texto abajo para anotar. Los spans pueden superponerse│
└─────────────────────────────────────────────────────────────────────┘
```

### Botón de Contexto

Incluye el mismo modal de contexto que `guarani-batch`:
- Atajo: `Ctrl+Shift+C`
- Muestra oración anterior y siguiente

---

## 7. Configuración del Recipe

```python
@prodigy.recipe(
    "guarani-spans",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
    families=("Familias de etiquetas (legacy)", "option", "f", str),
    group=("Grupo UD: pos-tags, features, morfemas", "option", "g", str),
    word_level=("Tokenizar por PALABRA", "option", "w", str),
)
def guarani_spans_manual(dataset, source, families=None, group=None, word_level=None):
    ...
```

### Retorno del Recipe

```python
return {
    "dataset": dataset,
    "view_id": "spans_manual",
    "stream": stream,
    "config": {
        "labels": labels,
        "allow_overlapping": True,
        "javascript": CONTEXT_POPUP_JS,
    }
}
```

---

## 8. Conversión a Universal Dependencies

### Al exportar

```python
from ud_guarani_mapper import map_label

def convert_spans_to_ud(spans):
    """Convierte spans de amigable a UD."""
    return [
        {**span, "label": map_label(span["label"], "to_ud")}
        for span in spans
    ]

# Ejemplo
spans = [{"label": "Sustantivo", "start": 0, "end": 5}]
ud_spans = convert_spans_to_ud(spans)
# [{"label": "NOUN", "start": 0, "end": 5}]
```

---

## 9. Datos de Entrada

### Formato esperado

```json
{"text": "Che roipota", "meta": {"spanish_text": "Yo quiero", "source": "doc1"}}
```

### Campos opcionales en meta

```json
{
    "text": "...",
    "meta": {
        "spanish_text": "...",
        "source": "...",
        "doc_id": "...",
        "sentence_id": 123
    }
}
```

---

## 10. Exportar Anotaciones

```powershell
# Exportar a JSONL
prodigy db-out dataset_name > output.jsonl

# Exportar con conversión a UD
python scripts/export_to_json_with_iaa.py dataset_name \
  --output data/export/output_ud.json
```

---

## 11. Siguiente Paso

Continúa con [08-RECIPE-RELATIONS.md](08-RECIPE-RELATIONS.md) para anotación de relaciones sintácticas.
