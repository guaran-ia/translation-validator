# 🍳 Recipe: guarani-batch (POS/Features/Relations)

El recipe `guarani-batch` es el componente principal para la anotación por lotes del corpus Guaraní.

---

## 1. Descripción General

Este recipe unificado soporta tres tipos de anotación:

| Tipo | Descripción | Puerto |
|------|-------------|--------|
| **POS** | Etiquetas de partes del discurso | 8080 |
| **Features** | Características morfológicas | 8081 |
| **Relations** | Relaciones sintácticas | 8082 |

---

## 2. Uso

### Comando básico

```powershell
prodigy guarani-batch <tipo> <lote> -F recipes/guarani_batch.py --port <puerto>
```

### Ejemplos

```powershell
# POS Tags - Lote 1
prodigy guarani-batch pos 1 -F recipes/guarani_batch.py --port 8080

# Features - Lote 5
prodigy guarani-batch features 5 -F recipes/guarani_batch.py --port 8081

# Relations - Lote 10
prodigy guarani-batch relations 10 -F recipes/guarani_batch.py --port 8082
```

---

## 3. Etiquetas por Tipo

### 3.1 POS Tags (11 etiquetas)

Basado en [Universal Dependencies - Old Guaraní](https://universaldependencies.org/treebanks/gn_oldtudet/index.html):

| Etiqueta Amigable | Código UD | Descripción |
|-------------------|-----------|-------------|
| Sustantivo | NOUN | Nombres comunes |
| Verbo | VERB | Acciones y estados |
| Pronombre | PRON | Pronombres personales |
| Nombre Propio | PROPN | Nombres propios |
| Determinante | DET | Artículos, demostrativos |
| Posposición | ADP | Posposiciones (no preposiciones) |
| Adverbio | ADV | Modificadores verbales |
| Numeral | NUM | Números |
| Partícula | PART | Partículas gramaticales |
| Interjección | INTJ | Exclamaciones |
| Puntuación | PUNCT | Signos de puntuación |

### 3.2 Features Morfológicos (30+ etiquetas)

```python
FEATURE_LABELS = [
    # Persona
    "1ra Persona", "2da Persona", "3ra Persona",
    # Número
    "Singular", "Plural",
    # Clusividad
    "Inclusivo", "Exclusivo",
    # Caso
    "Ablativo", "Alativo", "Dativo", "Locativo", "Referencial",
    # Relacional (específico Tupí-Guaraní)
    "Rel. Absoluto", "Rel. Contiguo", "Rel. No-Contiguo",
    # Tiempo
    "Pasado", "Futuro", "Futuro-Pasado",
    # Modo
    "Imperativo", "Permisivo",
    # Voz
    "Causativo", "Comitativo",
    # Forma verbal
    "Gerundio",
    # Polaridad
    "Negación",
    # Posesión
    "Reflexivo", "Poseedor",
    # Nominalizadores
    "Agentivo (-sar)", "Circunstancial (-saβ)", "Pasivo (-pɨr)",
    # Otros
    "Enfático", "Intensificador", "Interrogativo", "Privativo", "Reduplicación",
]
```

### 3.3 Relaciones Sintácticas (20 etiquetas)

```python
RELATION_LABELS = [
    "RAÍZ (Verbo Principal)",    # root
    "SUJETO",                     # nsubj
    "OBJETO DIRECTO",             # obj
    "OBJETO INDIRECTO",           # iobj
    "COMPLEMENTO OBLICUO",        # obl
    "OBLICUO-OBJETO",             # obl:obj
    "OBLICUO-SUJETO",             # obl:subj
    "MODIFICADOR ADVERBIAL",      # advmod
    "CLÁUSULA ADVERBIAL",         # advcl
    "MODIFICADOR NOMINAL",        # nmod
    "MODIFICADOR NUMÉRICO",       # nummod
    "DETERMINANTE (Rel)",         # det
    "MARCADOR DE CASO",           # case
    "PALABRA COMPUESTA",          # compound
    "APOSICIÓN",                  # appos
    "COMPLEMENTO VERBAL",         # xcomp
    "ELEMENTO DE DISCURSO",       # discourse
    "PARATAXIS",                  # parataxis
    "PUNTUACIÓN (Rel)",           # punct
    "DEPENDENCIA (General)",      # dep
]
```

---

## 4. Interfaz de Usuario

### 4.1 Header Informativo

El recipe genera un header HTML con:
- Tipo de anotación y paso actual (1/3, 2/3, 3/3)
- Número de lote y oración actual
- Botón de contexto

```
┌────────────────────────────────────────────────────────┐
│ 🏷️ POS Tags (UD) - Universal Dependencies UPOS        │
│                          Lote 5 | Paso 1/3 | #25/50   │
├────────────────────────────────────────────────────────┤
│ 📖 Ver Contexto                        Ctrl+Shift+C   │
└────────────────────────────────────────────────────────┘
```

### 4.2 Modal de Contexto

Muestra oraciones adyacentes para contexto:

```
┌─────────────────────────────────────────────────────────┐
│ 📖 Contexto - Oración #25/50                       [X] │
├─────────────────────────────────────────────────────────┤
│  ...oración anterior. [ORACIÓN ACTUAL RESALTADA]       │
│  oración siguiente...                                   │
├─────────────────────────────────────────────────────────┤
│  La oración actual está resaltada en amarillo          │
└─────────────────────────────────────────────────────────┘
```

**Atajo:** `Ctrl+Shift+C` para abrir/cerrar el modal.

---

## 5. Sistema de Exclusión por Sesión

Cada anotador tiene su propio progreso. El sistema evita mostrar ejemplos ya anotados:

```python
def get_session_completed_hashes(dataset_name: str, session_id: str) -> Set[int]:
    """Obtiene los hashes de ejemplos completados por un anotador específico."""
    db = connect()
    examples = db.get_dataset_examples(dataset_name)
    
    completed = set()
    for ex in examples:
        if ex.get("_session_id") == session_id:
            if ex.get("answer") in ["accept", "reject"]:
                completed.add(ex.get("_task_hash"))
    
    return completed
```

---

## 6. Configuración del Buffer

El buffer controla cómo se guardan las anotaciones:

```python
# Cargar desde prodigy_config.json
BUFFER_CONFIG = load_buffer_config()
INSTANT_SUBMIT = BUFFER_CONFIG.get("instant_submit", False)
BATCH_SIZE = BUFFER_CONFIG.get("batch_size", 3)
```

| Configuración | Comportamiento |
|---------------|----------------|
| `instant_submit: true` | Cada anotación se guarda inmediatamente |
| `instant_submit: false` | Las anotaciones se acumulan en buffer de tamaño `batch_size` |

---

## 7. Carga de Datos

### 7.1 Función `load_batch`

```python
def load_batch(batch_dir: str, batch_id: int) -> list:
    """Carga un lote específico desde archivo JSONL."""
    batch_file = Path(batch_dir) / f"batch_{batch_id:03d}.jsonl"
    
    if not batch_file.exists():
        print(f"[ERROR] No existe el archivo {batch_file}")
        return []
    
    examples = []
    with open(batch_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    
    return examples
```

### 7.2 Preparación de Ejemplos

```python
def prepare_examples(examples: list, annotation_type: str, batch_id: int) -> list:
    """Prepara ejemplos para Prodigy con contexto."""
    prepared = []
    
    for idx, ex in enumerate(examples):
        text = ex.get("text", "")
        
        # Generar contexto (2 oraciones antes y después)
        context_sentences = []
        for offset in range(-2, 3):
            ctx_idx = idx + offset
            if 0 <= ctx_idx < len(examples):
                context_sentences.append({
                    "text": examples[ctx_idx]["text"],
                    "is_current": offset == 0
                })
        
        # Tokenizar con spaCy
        doc = nlp(text)
        tokens = [
            {"text": t.text, "start": t.idx, "end": t.idx + len(t.text), "id": i}
            for i, t in enumerate(doc)
        ]
        
        # Crear ejemplo con HTML
        eg = {
            "text": text,
            "tokens": tokens,
            "spans": [],
            "meta": ex.get("meta", {}),
            "html": generate_html_header(ex, annotation_type, batch_id, context)
        }
        
        eg = set_hashes(eg)
        prepared.append(eg)
    
    return prepared
```

---

## 8. Colores de Etiquetas

Cada etiqueta tiene un color asignado para facilitar la identificación visual:

```python
LABEL_COLORS = {
    # POS
    "Sustantivo": "#22c55e",    # Verde
    "Verbo": "#ef4444",         # Rojo
    "Pronombre": "#3b82f6",     # Azul
    
    # Features
    "1ra Persona": "#8b5cf6",   # Púrpura
    "Pasado": "#f97316",        # Naranja
    "Negación": "#ef4444",      # Rojo
    
    # Relations
    "SUJETO": "#22c55e",        # Verde
    "OBJETO DIRECTO": "#3b82f6", # Azul
}
```

---

## 9. Configuración del Recipe

El recipe retorna un diccionario de configuración para Prodigy:

```python
return {
    "dataset": dataset_name,              # guarani_pos_batch_01
    "view_id": "spans_manual",            # Interfaz de spans
    "stream": stream,                     # Generador de ejemplos
    "update": None,                       # Sin modelo activo
    "config": {
        "labels": config["labels"],       # Etiquetas según tipo
        "auto_count_stream": True,
        "javascript": CONTEXT_JS,         # JS para modal de contexto
        "instant_submit": INSTANT_SUBMIT,
        "batch_size": BATCH_SIZE,
    }
}
```

---

## 10. Task Routing (IAA)

Para Inter-Annotator Agreement, el recipe puede distribuir tareas:

```python
def task_router(ctrl, session_id: str, item: dict) -> List[str]:
    """Asigna cada tarea a N anotadores específicos."""
    pool = list(ctrl.session_ids)
    task_hash = item.get("_task_hash")
    
    n_annotators = min(ANNOTATIONS_PER_TASK, len(pool))
    
    # Usar hash para distribución determinística
    start_idx = task_hash % len(pool)
    assigned = []
    for i in range(n_annotators):
        idx = (start_idx + i) % len(pool)
        assigned.append(pool[idx])
    
    return assigned
```

---

## 11. Datasets Generados

El recipe crea datasets con el formato:

```
guarani_{tipo}_batch_{numero:02d}
```

Ejemplos:
- `guarani_pos_batch_01`
- `guarani_features_batch_15`
- `guarani_relations_batch_60`

---

## 12. Ejemplo Completo

### Iniciar POS para lote 1

```powershell
prodigy guarani-batch pos 1 -F recipes/guarani_batch.py --port 8080
```

### Verificar dataset

```powershell
prodigy stats guarani_pos_batch_01
```

### Exportar anotaciones

```powershell
prodigy db-out guarani_pos_batch_01 > output.jsonl
```

---

## 13. Siguiente Paso

Continúa con [07-RECIPE-SPANS.md](07-RECIPE-SPANS.md) para la anotación manual de spans.
