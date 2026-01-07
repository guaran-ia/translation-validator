# 🤖 Recipe: guarani-openai (IA Asistida)

El recipe `guarani-openai` utiliza **OpenAI GPT** para pre-anotar automáticamente los textos, que luego son revisados por anotadores humanos.

---

## 1. Descripción

Este recipe implementa un flujo de **Human-in-the-Loop**:

1. **OpenAI** genera anotaciones automáticas
2. **Anotador humano** revisa y corrige
3. **Sistema aprende** de las correcciones

---

## 2. Requisitos

### API Key de OpenAI

```bash
# En .env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4
```

### Instalación de dependencias

```powershell
pip install openai
```

---

## 3. Uso

### Comando básico

```powershell
prodigy guarani-openai <dataset> <source> -F recipes/guarani_openai.py
```

### Con opciones

```powershell
# Especificar grupo de etiquetas
prodigy guarani-openai openai_pos ./data/texts.jsonl \
  --group pos-tags \
  -F recipes/guarani_openai.py

# Especificar modelo
prodigy guarani-openai openai_pos ./data/texts.jsonl \
  --model gpt-4 \
  -F recipes/guarani_openai.py
```

### Parámetros

| Parámetro | Alias | Default | Descripción |
|-----------|-------|---------|-------------|
| `dataset` | - | - | Dataset de salida |
| `source` | - | - | Archivo JSONL de entrada |
| `--group` | `-g` | `pos-tags` | Grupo de etiquetas |
| `--model` | `-m` | `gpt-4` | Modelo de OpenAI |

---

## 4. Flujo de Pre-anotación

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE PRE-ANOTACIÓN                           │
└─────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐
  │ Texto JSONL │
  └──────┬──────┘
         │
         ▼
  ┌─────────────────────────────────────┐
  │           PROMPT A OPENAI            │
  │                                      │
  │  "Analiza el siguiente texto en     │
  │   Guaraní y etiqueta cada palabra   │
  │   con su categoría gramatical..."   │
  │                                      │
  │   Texto: "Che roipota nde rape"     │
  └─────────────────┬───────────────────┘
                    │
                    ▼
  ┌─────────────────────────────────────┐
  │          RESPUESTA OPENAI           │
  │                                      │
  │  [{"text": "Che", "label": "PRON"}, │
  │   {"text": "roipota", "label": "VERB"},│
  │   {"text": "nde", "label": "DET"},  │
  │   {"text": "rape", "label": "NOUN"}]│
  └─────────────────┬───────────────────┘
                    │
                    ▼
  ┌─────────────────────────────────────┐
  │      CONVERSIÓN A SPANS             │
  │                                      │
  │  Calcular start/end para cada span │
  │  Mapear a etiquetas amigables      │
  └─────────────────┬───────────────────┘
                    │
                    ▼
  ┌─────────────────────────────────────┐
  │        INTERFAZ PRODIGY             │
  │                                      │
  │  El anotador ve las pre-anotaciones│
  │  y puede aceptar, corregir o       │
  │  rechazar                           │
  └─────────────────────────────────────┘
```

---

## 5. Prompt de OpenAI

### Estructura del prompt

```python
SYSTEM_PROMPT = """
Eres un lingüista experto en Guaraní antiguo (Old Guaraní).
Tu tarea es etiquetar cada palabra con su categoría gramatical.

Categorías disponibles:
- NOUN: Sustantivos (oga, tape, ava)
- VERB: Verbos (oguata, oñe'ẽ, ojapo)
- PRON: Pronombres (che, nde, ha'e)
- DET: Determinantes (ko, pe, umi)
- ADP: Posposiciones (-pe, -gui, -rehe)
- ADV: Adverbios (ko'ápe, ag̃aite, araka'e)
- NUM: Numerales (peteĩ, mokõi, mbohapy)
- PART: Partículas (katu, niko, ko)
- INTJ: Interjecciones
- PROPN: Nombres propios
- PUNCT: Puntuación

Responde SOLO con un JSON array.
"""

USER_PROMPT_TEMPLATE = """
Analiza el siguiente texto en Guaraní y etiqueta cada palabra:

Texto: "{text}"
Traducción al español: "{spanish_text}"

Responde con un JSON array donde cada elemento tiene:
- "text": la palabra
- "label": la categoría gramatical

Ejemplo de respuesta:
[{{"text": "Che", "label": "PRON"}}, {{"text": "roipota", "label": "VERB"}}]
"""
```

### Llamada a OpenAI

```python
async def get_openai_annotations(text: str, spanish_text: str) -> list:
    """Obtiene anotaciones de OpenAI."""
    
    response = await openai.ChatCompletion.acreate(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                text=text,
                spanish_text=spanish_text
            )}
        ],
        temperature=0.2,  # Baja temperatura para consistencia
        max_tokens=500
    )
    
    # Parsear respuesta JSON
    content = response.choices[0].message.content
    annotations = json.loads(content)
    
    return annotations
```

---

## 6. Caché de Respuestas

Para evitar costos excesivos, el recipe cachea las respuestas de OpenAI:

```python
CACHE_DIR = Path(__file__).parent.parent / "data" / "openai_cache"

def get_cached_response(text_hash: str) -> Optional[list]:
    """Busca respuesta en caché."""
    cache_file = CACHE_DIR / f"{text_hash}.json"
    if cache_file.exists():
        with open(cache_file, "r") as f:
            return json.load(f)
    return None

def save_to_cache(text_hash: str, response: list):
    """Guarda respuesta en caché."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{text_hash}.json"
    with open(cache_file, "w") as f:
        json.dump(response, f)
```

---

## 7. Conversión de Respuesta a Spans

```python
def convert_openai_to_spans(text: str, annotations: list) -> list:
    """Convierte respuesta de OpenAI a spans de Prodigy."""
    spans = []
    current_pos = 0
    
    for ann in annotations:
        word = ann["text"]
        label_ud = ann["label"]
        
        # Encontrar posición en el texto
        start = text.find(word, current_pos)
        if start == -1:
            continue
        end = start + len(word)
        
        # Convertir etiqueta UD a amigable
        label_friendly = UD_TO_FRIENDLY.get(label_ud, label_ud)
        
        spans.append({
            "start": start,
            "end": end,
            "label": label_friendly,
            "source": "openai"  # Marcar como generado por IA
        })
        
        current_pos = end
    
    return spans
```

---

## 8. Interfaz de Usuario

### Header con indicador de IA

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🤖 OpenAI Asistido - POS Tags                     📊 25/100        │
├─────────────────────────────────────────────────────────────────────┤
│ ⚡ Pre-anotación generada automáticamente. Revisa y corrige.       │
├─────────────────────────────────────────────────────────────────────┤
│ 🇵🇾 Che roipota nde rape                                            │
│     ───  ──────  ───  ────                                          │
│    PRON   VERB   DET  NOUN  ← Etiquetas sugeridas por IA           │
└─────────────────────────────────────────────────────────────────────┘
```

### Acciones del anotador

- **[✓ Aceptar]**: Las pre-anotaciones son correctas
- **Corregir**: Modificar etiquetas incorrectas
- **[✗ Rechazar]**: La IA falló completamente

---

## 9. Manejo de Errores

### Respuesta inválida de OpenAI

```python
try:
    annotations = await get_openai_annotations(text, spanish_text)
except json.JSONDecodeError:
    logger.warning(f"OpenAI retornó JSON inválido para: {text[:50]}")
    annotations = []  # Fallback a anotación manual
except openai.error.RateLimitError:
    logger.error("Rate limit alcanzado, esperando...")
    await asyncio.sleep(60)
except Exception as e:
    logger.error(f"Error de OpenAI: {e}")
    annotations = []
```

### Fallback a anotación manual

Si OpenAI falla, el ejemplo se presenta sin pre-anotaciones:

```python
if not annotations:
    # Presentar sin spans pre-anotados
    example["spans"] = []
    example["_openai_failed"] = True
```

---

## 10. Costos y Límites

### Estimación de costos

| Modelo | Costo por 1K tokens | Tokens promedio/oración |
|--------|---------------------|-------------------------|
| GPT-4 | $0.03 input, $0.06 output | ~200 |
| GPT-3.5-turbo | $0.002 | ~200 |

### Recomendaciones

1. **Usar caché** para evitar llamadas duplicadas
2. **GPT-3.5-turbo** para presupuesto limitado
3. **Batch processing** para reducir overhead

---

## 11. Grupos de Etiquetas Soportados

| Grupo | Descripción |
|-------|-------------|
| `pos-tags` | Categorías gramaticales |
| `features` | Características morfológicas |
| `morfemas` | Análisis morfológico |

**Nota:** Relations no está soportado en este recipe (requiere interfaz diferente).

---

## 12. Exportar Anotaciones

```powershell
# Exportar todo
prodigy db-out openai_pos > openai_output.jsonl

# Filtrar solo anotaciones corregidas por humanos
python -c "
import json
with open('openai_output.jsonl') as f:
    for line in f:
        ex = json.loads(line)
        if ex.get('answer') == 'accept':
            print(json.dumps(ex))
" > human_verified.jsonl
```

---

## 13. Siguiente Paso

Continúa con [10-SISTEMA-BATCHES.md](10-SISTEMA-BATCHES.md) para entender el sistema de lotes.
