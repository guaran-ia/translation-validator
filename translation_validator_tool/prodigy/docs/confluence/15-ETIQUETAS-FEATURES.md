# ⚙️ Etiquetas Features - Referencia Completa

Este documento detalla las **características morfológicas (Features)** disponibles en el sistema, basadas en Universal Dependencies para Old Guaraní.

---

## 1. Resumen por Categorías

| Categoría | Features | Descripción |
|-----------|----------|-------------|
| Persona | Person=1,2,3 | Persona gramatical |
| Número | Number=Sing,Plur | Número gramatical |
| Clusividad | Clusivity=In,Ex | Inclusivo/Exclusivo (1ra plural) |
| Caso | Case=Abl,All,Dat,Loc,Ref | Casos gramaticales |
| Relacional | Rel=Abs,Cont,NCont | Prefijos relacionales |
| Tiempo | Tense=Past,Fut,FutPast | Tiempo verbal |
| Modo | Mood=Imp,Perm | Modo verbal |
| Voz | Voice=Cau,Com | Voz verbal |
| Aspecto | Aspect=Perf,Iter,Hab | Aspecto verbal |
| Polaridad | Polarity=Neg | Negación |
| Nominalizadores | Nomzr=Ag,Circ,Pas,etc | Sufijos nominalizadores |
| Otros | Reflex, Emph, Priv, etc | Otros rasgos |

---

## 2. Categorías Detalladas

### 2.1 Persona (Person)

**Descripción:** Indica la persona gramatical del participante.

| Etiqueta Amigable | Código UD | Descripción |
|-------------------|-----------|-------------|
| 1ra Persona | Person=1 | Hablante (che, ore, ñande) |
| 2da Persona | Person=2 | Oyente (nde, peẽ) |
| 3ra Persona | Person=3 | Tercero (haʼe, haʼekuéra) |

**Prefijos verbales en Guaraní Antiguo:**

```
Person=1: a- (intransitivo), ai- (transitivo)
Person=2: re- (intransitivo), ere- (transitivo)
Person=3: o- (intransitivo), o- (transitivo)
```

---

### 2.2 Número (Number)

**Descripción:** Indica el número gramatical.

| Etiqueta Amigable | Código UD | Descripción |
|-------------------|-----------|-------------|
| Singular | Number=Sing | Una entidad |
| Plural | Number=Plur | Múltiples entidades |

**Marcadores en Guaraní Antiguo:**
- Singular: sin marca (default)
- Plural: **-kuéra** (sustantivos), **-ro-** (verbos)

---

### 2.3 Clusividad (Clusivity)

**Descripción:** Distinción específica de lenguas tupí-guaraníes para la primera persona plural.

| Etiqueta Amigable | Código UD | Descripción |
|-------------------|-----------|-------------|
| Inclusivo | Clusivity=In | "Nosotros" incluyendo al oyente (ñande) |
| Exclusivo | Clusivity=Ex | "Nosotros" excluyendo al oyente (ore) |

**Ejemplo:**
- **ñandéve** - a nosotros (tú incluido) → Clusivity=In
- **oréve** - a nosotros (sin ti) → Clusivity=Ex

---

### 2.4 Caso (Case)

**Descripción:** Función gramatical del sustantivo/pronombre marcada por posposiciones.

| Etiqueta Amigable | Código UD | Sufijo | Descripción |
|-------------------|-----------|--------|-------------|
| Ablativo | Case=Abl | -gui | Origen, "desde" |
| Alativo | Case=All | -pe | Dirección, "hacia" |
| Locativo | Case=Loc | -pe | Ubicación, "en" |
| Dativo | Case=Dat | -pe | Beneficiario, "a/para" |
| Referencial | Case=Ref | -rehe | Referencia, "sobre/acerca de" |

**Ejemplos:**
- **ogágui** - desde la casa → Case=Abl
- **ogápe** - a/en la casa → Case=Loc/All
- **cherehe** - sobre mí → Case=Ref

---

### 2.5 Relacional (Rel)

**Descripción:** Sistema de prefijos relacionales específico de las lenguas tupí-guaraníes.

| Etiqueta Amigable | Código UD | Prefijo | Descripción |
|-------------------|-----------|---------|-------------|
| Rel. Absoluto | Rel=Abs | t- | Sin poseedor (forma absoluta) |
| Rel. Contiguo | Rel=Cont | r- | Poseedor contiguo (adyacente) |
| Rel. No-Contiguo | Rel=NCont | h-/i- | Poseedor no contiguo |

**Ejemplos:**
- **tapé** - camino (sin poseedor) → Rel=Abs
- **che rapé** - mi camino → Rel=Cont
- **hapé** - su camino (de él) → Rel=NCont

---

### 2.6 Tiempo (Tense)

**Descripción:** Tiempo verbal que sitúa la acción en relación al momento del habla.

| Etiqueta Amigable | Código UD | Sufijo | Descripción |
|-------------------|-----------|--------|-------------|
| Pasado | Tense=Past | -kue/-akue | Acción en el pasado |
| Futuro | Tense=Fut | -ne/-ta | Acción en el futuro |
| Futuro-Pasado | Tense=FutPast | - | Futuro del pasado |

**Ejemplos:**
- **oúkue** - vino (pasado) → Tense=Past
- **oúne** - vendrá → Tense=Fut

---

### 2.7 Modo (Mood)

**Descripción:** Actitud del hablante hacia la acción.

| Etiqueta Amigable | Código UD | Forma | Descripción |
|-------------------|-----------|-------|-------------|
| Imperativo | Mood=Imp | e-/pe- | Orden/mandato |
| Permisivo | Mood=Perm | t-/ta- | Permiso/deseo |

**Ejemplos:**
- **ejú** - ven (tú) → Mood=Imp
- **tajá** - que vaya → Mood=Perm

---

### 2.8 Voz (Voice)

**Descripción:** Relación entre el verbo y sus argumentos.

| Etiqueta Amigable | Código UD | Prefijo | Descripción |
|-------------------|-----------|---------|-------------|
| Causativo | Voice=Cau | mo-/mbo- | Hacer que alguien haga algo |
| Comitativo | Voice=Com | ro- | Hacer algo con alguien |

**Ejemplos:**
- **mboguatá** - hacer caminar → Voice=Cau
- **roguatá** - caminar con (alguien) → Voice=Com

---

### 2.9 Aspecto (Aspect)

**Descripción:** Cómo se desarrolla la acción en el tiempo.

| Etiqueta Amigable | Código UD | Descripción |
|-------------------|-----------|-------------|
| Completivo | Aspect=Perf | Acción completada |
| Iterativo | Aspect=Iter | Acción repetida |
| Habitual | Aspect=Hab | Acción habitual |
| Sucesivo | Aspect=Prosp | Acción inminente |

---

### 2.10 Polaridad (Polarity)

**Descripción:** Marca de negación.

| Etiqueta Amigable | Código UD | Forma | Descripción |
|-------------------|-----------|-------|-------------|
| Negación | Polarity=Neg | nd-...-i | Negación circunfija |

**Ejemplo:**
- **ndoúi** - no viene → Polarity=Neg

---

### 2.11 Posesión (Poss)

**Descripción:** Marca de posesivo.

| Etiqueta Amigable | Código UD | Descripción |
|-------------------|-----------|-------------|
| Poseedor | Poss=Yes | Indica posesión |

---

### 2.12 Nominalizadores (Nomzr)

**Descripción:** Sufijos que convierten verbos en sustantivos.

| Etiqueta Amigable | Código UD | Sufijo | Descripción |
|-------------------|-----------|--------|-------------|
| Agentivo | Nomzr=Ag | -sar | El que hace X |
| Circunstancial | Nomzr=Circ | -saβ | Lugar/tiempo/instrumento de X |
| Pasivo | Nomzr=Pas | -pɨr | Lo que es X-ado |
| C-Circunstancial | Nomzr=CCirc | - | Circunstancial compuesto |
| Derivación Pasiva | Nomzr=DevPass | - | Derivación pasiva |
| Relativo | Nomzr=Rel | - | Nominalizador relativo |

**Ejemplos:**
- **mboʼesar** - el que enseña (maestro) → Nomzr=Ag
- **ñemboʼesaβ** - lugar de aprendizaje (escuela) → Nomzr=Circ

---

### 2.13 Otros Features

| Etiqueta Amigable | Código UD | Descripción |
|-------------------|-----------|-------------|
| Reflexivo | Reflex=Yes | Acción sobre sí mismo |
| Correferencial | Corf=Yes | Correferencia |
| No-Primera Mano | Evident=Nfh | Información no presenciada |
| Enfático | Emph=Yes | Énfasis |
| Intensificador | Intens=Yes | Intensificación |
| Privativo | Priv=Yes | Ausencia de algo |
| Reduplicación | Red=Di | Reduplicación distributiva |
| Interrogativo | Int=Yes | Marca de pregunta |
| Gerundio | VerbForm=Ger | Forma verbal gerundiva |

---

## 3. Tabla Completa de Mapeo

```
┌─────────────────────┬─────────────────────────┐
│ ETIQUETA AMIGABLE   │ CÓDIGO UD              │
├─────────────────────┼─────────────────────────┤
│ 1ra Persona         │ Person=1               │
│ 2da Persona         │ Person=2               │
│ 3ra Persona         │ Person=3               │
├─────────────────────┼─────────────────────────┤
│ Singular            │ Number=Sing            │
│ Plural              │ Number=Plur            │
├─────────────────────┼─────────────────────────┤
│ Inclusivo           │ Clusivity=In           │
│ Exclusivo           │ Clusivity=Ex           │
├─────────────────────┼─────────────────────────┤
│ Ablativo            │ Case=Abl               │
│ Alativo             │ Case=All               │
│ Locativo            │ Case=Loc               │
│ Dativo              │ Case=Dat               │
│ Referencial         │ Case=Ref               │
├─────────────────────┼─────────────────────────┤
│ Rel. Absoluto       │ Rel=Abs                │
│ Rel. Contiguo       │ Rel=Cont               │
│ Rel. No-Contiguo    │ Rel=NCont              │
├─────────────────────┼─────────────────────────┤
│ Pasado              │ Tense=Past             │
│ Futuro              │ Tense=Fut              │
│ Futuro-Pasado       │ Tense=FutPast          │
├─────────────────────┼─────────────────────────┤
│ Imperativo          │ Mood=Imp               │
│ Permisivo           │ Mood=Perm              │
├─────────────────────┼─────────────────────────┤
│ Causativo           │ Voice=Cau              │
│ Comitativo          │ Voice=Com              │
├─────────────────────┼─────────────────────────┤
│ Completivo          │ Aspect=Perf            │
│ Iterativo           │ Aspect=Iter            │
│ Habitual            │ Aspect=Hab             │
│ Sucesivo            │ Aspect=Prosp           │
├─────────────────────┼─────────────────────────┤
│ Negación            │ Polarity=Neg           │
├─────────────────────┼─────────────────────────┤
│ Agentivo (-sar)     │ Nomzr=Ag               │
│ Circunstancial      │ Nomzr=Circ             │
│ Pasivo (-pɨr)       │ Nomzr=Pas              │
├─────────────────────┼─────────────────────────┤
│ Reflexivo           │ Reflex=Yes             │
│ Enfático            │ Emph=Yes               │
│ Privativo           │ Priv=Yes               │
│ Reduplicación       │ Red=Di                 │
│ Interrogativo       │ Int=Yes                │
└─────────────────────┴─────────────────────────┘
```

---

## 4. Uso en el Sistema

### Obtener Etiquetas de Features

```python
from scripts.ud_guarani_mapper import SPECIALIZED_GROUPS

_FEATURES_GROUP = SPECIALIZED_GROUPS.get("features", {})
FEATURE_LABELS = _FEATURES_GROUP.get("labels", [])
```

### Convertir entre Formatos

```python
from scripts.ud_guarani_mapper import map_label

# Amigable → UD
ud = map_label("Causativo", "to_ud")  # "Voice=Cau"
ud = map_label("Pasado", "to_ud")     # "Tense=Past"

# UD → Amigable
friendly = map_label("Voice=Cau", "to_friendly")  # "Causativo"
```

---

## 5. Referencias

- [Universal Dependencies Features](https://universaldependencies.org/u/feat/)
- [Old Guaraní Features](https://universaldependencies.org/treebanks/gn_oldtudet/index.html)
- [Tupian Features](https://universaldependencies.org/tpn/)

---

## 6. Documentos Relacionados

- [14-ETIQUETAS-POS.md](14-ETIQUETAS-POS.md) - Categorías gramaticales
- [16-ETIQUETAS-RELATIONS.md](16-ETIQUETAS-RELATIONS.md) - Relaciones sintácticas
- [13-UD-MAPPER.md](13-UD-MAPPER.md) - Mapper centralizado
