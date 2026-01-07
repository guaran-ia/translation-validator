# 🏷️ Etiquetas POS - Referencia Completa

Este documento detalla las **categorías gramaticales (POS Tags)** disponibles en el sistema, basadas en Universal Dependencies para Old Guaraní.

---

## 1. Resumen

| Etiqueta Amigable | Código UD | Color | Descripción |
|-------------------|-----------|-------|-------------|
| Sustantivo | NOUN | 🔴 | Palabras que denotan entidades |
| Verbo | VERB | 🔴 | Palabras que denotan acciones o estados |
| Pronombre | PRON | 🔴 | Palabras que sustituyen sustantivos |
| Adverbio | ADV | 🔴 | Modificadores de verbos, adjetivos u otros adverbios |
| Posposición | ADP | 🔴 | Marcadores de relaciones gramaticales (posposiciones) |
| Determinante | DET | 🔴 | Modificadores de sustantivos que los determinan |
| Numeral | NUM | 🔴 | Palabras que expresan cantidad numérica |
| Partícula | PART | 🔴 | Palabras función que no encajan en otras categorías |
| Interjección | INTJ | 🔴 | Expresiones exclamativas |
| Nombre Propio | PROPN | 🔴 | Nombres de entidades específicas |
| Puntuación | PUNCT | 🔴 | Signos de puntuación |

---

## 2. Categorías Detalladas

### 2.1 Sustantivo (NOUN)

**Descripción:** Palabras que denotan entidades concretas o abstractas.

**Ejemplos en Guaraní Antiguo:**
- **óga** - casa
- **avá** - hombre
- **tapé** - camino
- **ñeʼẽ** - palabra/voz

**Características:**
- Pueden recibir marcas de posesión
- Se modifican con determinantes
- Pueden funcionar como sujeto u objeto

**Mapeo UD:**
```
Sustantivo → NOUN
```

---

### 2.2 Verbo (VERB)

**Descripción:** Palabras que denotan acciones, procesos o estados.

**Ejemplos en Guaraní Antiguo:**
- **oguatá** - camina (3sg)
- **oñeʼẽ** - habla (3sg)
- **ojapo** - hace (3sg)
- **oú** - viene (3sg)

**Características:**
- Reciben marcas de persona y número
- Pueden tener marcas de tiempo, modo y aspecto
- Toman causativo y otros afijos

**Mapeo UD:**
```
Verbo → VERB
```

---

### 2.3 Pronombre (PRON)

**Descripción:** Palabras que sustituyen o refieren a sustantivos.

**Ejemplos en Guaraní Antiguo:**
- **che** - yo/mi
- **nde** - tú/tu
- **haʼe** - él/ella
- **ñande** - nosotros (inclusivo)
- **ore** - nosotros (exclusivo)

**Tipos de pronombres:**
- **Personales:** che, nde, haʼe, ñande, ore, peẽ, haʼekuéra
- **Demostrativos:** ko, pe, umi
- **Interrogativos:** mba'e, máva, moõ

**Mapeo UD:**
```
Pronombre → PRON
```

---

### 2.4 Adverbio (ADV)

**Descripción:** Palabras que modifican verbos, adjetivos u otros adverbios.

**Ejemplos en Guaraní Antiguo:**
- **koápe** - aquí
- **agãite** - ahora
- **arakaʼe** - entonces/antes
- **ikatuhápe** - completamente

**Tipos de adverbios:**
- **Lugar:** koápe, pépe, mombyrýpe
- **Tiempo:** aníte, ko'ãga, akue
- **Manera:** porã, vai

**Mapeo UD:**
```
Adverbio → ADV
```

---

### 2.5 Posposición (ADP)

**Descripción:** Palabras que marcan relaciones gramaticales entre constituyentes. En Guaraní son **posposiciones** (van después del nombre).

**Ejemplos en Guaraní Antiguo:**
- **-pe** - en/a (locativo, dativo)
- **-gui** - de/desde (ablativo)
- **-rehe** - sobre/acerca de (referencial)
- **-rupi** - por/a través de

**Importante:** En UD se usa la etiqueta `ADP` (adposition), que incluye tanto preposiciones como posposiciones.

**Mapeo UD:**
```
Posposición → ADP
```

---

### 2.6 Determinante (DET)

**Descripción:** Palabras que determinan o especifican un sustantivo.

**Ejemplos en Guaraní Antiguo:**
- **ko** - este/esta
- **pe** - ese/esa
- **umi** - aquellos
- **heta** - muchos
- **opaite** - todos

**Mapeo UD:**
```
Determinante → DET
```

---

### 2.7 Numeral (NUM)

**Descripción:** Palabras que expresan cantidad numérica.

**Ejemplos en Guaraní Antiguo:**
- **peteĩ** - uno
- **mokõi** - dos
- **mbohapy** - tres
- **irundy** - cuatro
- **po** - cinco

**Mapeo UD:**
```
Numeral → NUM
```

---

### 2.8 Partícula (PART)

**Descripción:** Palabras función que no encajan en otras categorías. En Guaraní incluyen partículas de énfasis, interrogación y otras.

**Ejemplos en Guaraní Antiguo:**
- **katu** - (énfasis)
- **niko** - (evidencialidad)
- **ko** - (demostrativo enfático)
- **pa** - (interrogación)
- **piko** - (interrogación)

**Mapeo UD:**
```
Partícula → PART
```

---

### 2.9 Interjección (INTJ)

**Descripción:** Expresiones exclamativas que expresan emociones o reacciones.

**Ejemplos:**
- **¡há!** - (sorpresa)
- **¡ápe!** - (llamada)
- **¡añetéke!** - (afirmación enfática)

**Mapeo UD:**
```
Interjección → INTJ
```

---

### 2.10 Nombre Propio (PROPN)

**Descripción:** Nombres de entidades específicas (personas, lugares, etc.).

**Ejemplos:**
- **Tupã** - Dios (Tupã)
- **Paraguái** - Paraguay
- **Paraná** - (Río) Paraná

**Mapeo UD:**
```
Nombre Propio → PROPN
```

---

### 2.11 Puntuación (PUNCT)

**Descripción:** Signos de puntuación en el texto.

**Ejemplos:**
- **.** - punto
- **,** - coma
- **;** - punto y coma
- **¿?** - signos de interrogación
- **¡!** - signos de exclamación

**Mapeo UD:**
```
Puntuación → PUNCT
```

---

## 3. Etiquetas NO Usadas en Old Guaraní

Las siguientes etiquetas UD **no se usan** en el treebank de Old Guaraní:

| Etiqueta | Código UD | Razón |
|----------|-----------|-------|
| Adjetivo | ADJ | En Guaraní clásico, las funciones adjetivales las cumplen sustantivos en composición o verbos estativos |
| Auxiliar | AUX | No existe categoría auxiliar en Guaraní clásico |
| Conj. Coordinante | CCONJ | No documentada en el corpus |
| Conj. Subordinante | SCONJ | No documentada en el corpus |
| Símbolo | SYM | No aplicable al corpus histórico |

---

## 4. Distribución en el Corpus

Basado en el treebank de Universal Dependencies para Old Guaraní:

```
VERB    ████████████████████  35%
NOUN    ██████████████        25%
PRON    ██████████            15%
PART    ████████               10%
ADP     █████                   8%
ADV     ███                     4%
DET     ██                      2%
PUNCT   █                       1%
Otros   █                      <1%
```

---

## 5. Atajos de Teclado

Durante la anotación de POS en Prodigy:

| Atajo | Acción |
|-------|--------|
| `1`-`9` | Seleccionar etiqueta por número |
| `←` `→` | Navegar entre palabras |
| `Enter` | Confirmar selección |
| `Backspace` | Borrar última selección |
| `Ctrl+Shift+C` | Abrir contexto modal |

---

## 6. Uso en el Sistema

### Configuración del Recipe

```python
from scripts.ud_guarani_mapper import SPECIALIZED_GROUPS

_POS_GROUP = SPECIALIZED_GROUPS.get("pos-tags", {})
POS_LABELS = _POS_GROUP.get("labels", [])

# POS_LABELS contiene:
# ["Posposición", "Adverbio", "Determinante", "Interjección", 
#  "Sustantivo", "Numeral", "Partícula", "Pronombre", 
#  "Nombre Propio", "Puntuación", "Verbo"]
```

### Convertir a UD para Exportación

```python
from scripts.ud_guarani_mapper import map_label

# Convertir de amigable a UD
pos_ud = map_label("Sustantivo", direction="to_ud")  # "NOUN"
pos_ud = map_label("Verbo", direction="to_ud")       # "VERB"

# Convertir de UD a amigable
pos_friendly = map_label("NOUN", direction="to_friendly")  # "Sustantivo"
```

---

## 7. Referencias

- [Universal Dependencies POS Tags](https://universaldependencies.org/u/pos/)
- [Old Guaraní Treebank](https://universaldependencies.org/treebanks/gn_oldtudet/index.html)
- [13-UD-MAPPER.md](13-UD-MAPPER.md) - Documentación del mapper centralizado

---

## 8. Documentos Relacionados

- [15-ETIQUETAS-FEATURES.md](15-ETIQUETAS-FEATURES.md) - Features morfológicos
- [16-ETIQUETAS-RELATIONS.md](16-ETIQUETAS-RELATIONS.md) - Relaciones sintácticas
