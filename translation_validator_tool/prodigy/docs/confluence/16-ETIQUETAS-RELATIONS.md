# 🔗 Etiquetas Relations - Referencia Completa

Este documento detalla las **relaciones de dependencia sintáctica** disponibles en el sistema, basadas en Universal Dependencies.

---

## 1. Resumen

| Etiqueta Amigable | Código UD | Descripción |
|-------------------|-----------|-------------|
| RAÍZ (Verbo Principal) | root | Elemento raíz de la oración |
| SUJETO | nsubj | Sujeto nominal |
| OBJETO DIRECTO | obj | Objeto directo |
| OBJETO INDIRECTO | iobj | Objeto indirecto |
| COMPLEMENTO OBLICUO | obl | Complemento oblicuo |
| OBLICUO-OBJETO | obl:obj | Oblicuo con rol de objeto |
| OBLICUO-SUJETO | obl:subj | Oblicuo con rol de sujeto |
| MODIFICADOR ADVERBIAL | advmod | Modificador adverbial |
| CLÁUSULA ADVERBIAL | advcl | Cláusula subordinada adverbial |
| MODIFICADOR NOMINAL | nmod | Modificador nominal |
| DETERMINANTE (Rel) | det | Determinante |
| MARCADOR DE CASO | case | Marcador de caso (posposición) |
| PALABRA COMPUESTA | compound | Elemento de compuesto |
| APOSICIÓN | appos | Aposición |
| COMPLEMENTO VERBAL | xcomp | Complemento abierto |
| ELEMENTO DE DISCURSO | discourse | Partícula de discurso |
| PARATAXIS | parataxis | Construcción paratáctica |
| MODIFICADOR NUMÉRICO | nummod | Modificador numérico |
| PUNTUACIÓN (Rel) | punct | Puntuación |
| DEPENDENCIA (General) | dep | Dependencia sin clasificar |

---

## 2. Categorías Detalladas

### 2.1 RAÍZ (root)

**Descripción:** El elemento principal de la oración, típicamente el verbo principal.

**Características:**
- No tiene cabeza (head = 0)
- Solo puede haber una raíz por oración
- Generalmente es un verbo finito

**Ejemplo:**
```
Oguatá    avá
──────    ───
 root    nsubj
```
*"Camina el hombre"*

---

### 2.2 SUJETO (nsubj)

**Descripción:** El argumento nominal que realiza o experimenta la acción del verbo.

**Características:**
- Típicamente un sustantivo o pronombre
- En Guaraní, frecuentemente marcado en el verbo
- Puede aparecer antes o después del verbo

**Ejemplo:**
```
Avá     oguatá
───     ──────
nsubj    root
```
*"El hombre camina"*

---

### 2.3 OBJETO DIRECTO (obj)

**Descripción:** El argumento nominal que recibe directamente la acción del verbo transitivo.

**Ejemplo:**
```
Ogueroú    tapé    avá
───────    ────    ───
  root      obj   nsubj
```
*"El hombre hace venir al camino" (construye el camino)*

---

### 2.4 OBJETO INDIRECTO (iobj)

**Descripción:** El argumento nominal que indica el beneficiario o receptor secundario.

**Ejemplo:**
```
Omeʼẽ    aʼyra      cheʼúpe    
──────   ─────      ────────   
 root     obj        iobj      
```
*"Da al niño a mí"*

---

### 2.5 COMPLEMENTO OBLICUO (obl)

**Descripción:** Argumento no central del verbo, típicamente marcado con posposición.

**Subtipos:**
- **obl**: Oblicuo general
- **obl:obj**: Oblicuo con función de objeto
- **obl:subj**: Oblicuo con función de sujeto

**Ejemplo:**
```
Oguatá    tapérupi
──────    ────────
 root       obl
```
*"Camina por el camino"*

---

### 2.6 MODIFICADOR ADVERBIAL (advmod)

**Descripción:** Palabra que modifica al verbo indicando circunstancias.

**Ejemplo:**
```
Oguatá    porã
──────    ────
 root    advmod
```
*"Camina bien"*

---

### 2.7 CLÁUSULA ADVERBIAL (advcl)

**Descripción:** Cláusula subordinada que funciona como modificador adverbial.

**Ejemplo:**
```
Oúvo                osẽ
─────               ────
advcl               root
```
*"Al venir, sale"*

---

### 2.8 MODIFICADOR NOMINAL (nmod)

**Descripción:** Sustantivo que modifica a otro sustantivo.

**Ejemplo:**
```
avá     rape
───     ────
head    nmod
```
*"camino del hombre"*

---

### 2.9 DETERMINANTE (det)

**Descripción:** Palabra que determina o especifica un sustantivo.

**Ejemplo:**
```
ko      avá
──      ───
det     head
```
*"este hombre"*

---

### 2.10 MARCADOR DE CASO (case)

**Descripción:** Posposición que marca la función gramatical del sustantivo.

**Ejemplo:**
```
ogá     pe
───     ──
head   case
```
*"en la casa"*

---

### 2.11 PALABRA COMPUESTA (compound)

**Descripción:** Elemento de una palabra compuesta.

**Ejemplo:**
```
ñeʼẽ      rendá
────      ─────
head     compound
```
*"lugar de la palabra"*

---

### 2.12 APOSICIÓN (appos)

**Descripción:** Elemento que renombra o explica al sustantivo.

**Ejemplo:**
```
Tupã     Ñandejára
────     ─────────
head       appos
```
*"Tupã, Nuestro Señor"*

---

### 2.13 COMPLEMENTO VERBAL (xcomp)

**Descripción:** Complemento clausal abierto (comparte argumento con el verbo principal).

---

### 2.14 ELEMENTO DE DISCURSO (discourse)

**Descripción:** Partículas que marcan el discurso sin función sintáctica.

**Ejemplo:**
```
Oguatá    katu
──────    ────
 root   discourse
```
*"Camina (enfático)"*

---

### 2.15 PARATAXIS (parataxis)

**Descripción:** Construcción donde oraciones se yuxtaponen sin subordinación explícita.

---

### 2.16 MODIFICADOR NUMÉRICO (nummod)

**Descripción:** Numeral que modifica a un sustantivo.

**Ejemplo:**
```
mokõi    avá
─────    ───
nummod   head
```
*"dos hombres"*

---

### 2.17 PUNTUACIÓN (punct)

**Descripción:** Signo de puntuación adjunto a un elemento.

---

### 2.18 DEPENDENCIA GENERAL (dep)

**Descripción:** Relación de dependencia sin especificar (usar cuando no hay categoría apropiada).

---

## 3. Tabla de Mapeo Completa

```
┌────────────────────────────┬───────────────┐
│ ETIQUETA AMIGABLE          │ CÓDIGO UD     │
├────────────────────────────┼───────────────┤
│ RAÍZ (Verbo Principal)     │ root          │
│ SUJETO                     │ nsubj         │
│ OBJETO DIRECTO             │ obj           │
│ OBJETO INDIRECTO           │ iobj          │
│ COMPLEMENTO OBLICUO        │ obl           │
│ OBLICUO-OBJETO             │ obl:obj       │
│ OBLICUO-SUJETO             │ obl:subj      │
│ MODIFICADOR ADVERBIAL      │ advmod        │
│ CLÁUSULA ADVERBIAL         │ advcl         │
│ MODIFICADOR NOMINAL        │ nmod          │
│ DETERMINANTE (Rel)         │ det           │
│ MARCADOR DE CASO           │ case          │
│ PALABRA COMPUESTA          │ compound      │
│ APOSICIÓN                  │ appos         │
│ COMPLEMENTO VERBAL         │ xcomp         │
│ ELEMENTO DE DISCURSO       │ discourse     │
│ PARATAXIS                  │ parataxis     │
│ MODIFICADOR NUMÉRICO       │ nummod        │
│ PUNTUACIÓN (Rel)           │ punct         │
│ DEPENDENCIA (General)      │ dep           │
└────────────────────────────┴───────────────┘
```

---

## 4. Interfaz de Anotación

### Representación Visual

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ANOTACIÓN DE RELACIONES                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                         ┌─── root ───┐                              │
│                         │            │                              │
│                         ▼            │                              │
│     nsubj ──────►   [ Oguatá ]      │                              │
│         │                           │                              │
│         │                           │                              │
│     [ Avá ]                   [ porã ] ◄────── advmod              │
│                                                                     │
│     "El hombre camina bien"                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Crear Arcos

1. **Click** en la palabra dependiente
2. **Arrastrar** hacia la cabeza
3. **Seleccionar** la relación del menú

### Atajos

| Atajo | Acción |
|-------|--------|
| `1`-`9` | Seleccionar relación por número |
| `R` | Marcar como root |
| `Delete` | Eliminar arco seleccionado |
| `Ctrl+Z` | Deshacer último cambio |

---

## 5. Uso en el Sistema

### Obtener Etiquetas de Relaciones

```python
from scripts.ud_guarani_mapper import SPECIALIZED_GROUPS

_RELATIONS_GROUP = SPECIALIZED_GROUPS.get("relations", {})
RELATION_LABELS = _RELATIONS_GROUP.get("labels", [])

# Contiene:
# ["RAÍZ (Verbo Principal)", "SUJETO", "OBJETO DIRECTO", ...]
```

### Convertir para Exportación

```python
from scripts.ud_guarani_mapper import map_label

# Amigable → UD
ud = map_label("SUJETO", "to_ud")  # "nsubj"
ud = map_label("OBJETO DIRECTO", "to_ud")  # "obj"

# UD → Amigable
friendly = map_label("nsubj", "to_friendly")  # "SUJETO"
```

---

## 6. Formato CoNLL-U

Las relaciones se exportan en formato CoNLL-U:

```
# sent_id = 1
# text = Avá oguatá porã
1   Avá      avá      NOUN   _   _   2   nsubj   _   _
2   oguatá   oguata   VERB   _   _   0   root    _   _
3   porã     porã     ADV    _   _   2   advmod  _   _
```

Columnas:
- **7**: HEAD (índice de la cabeza)
- **8**: DEPREL (relación de dependencia)

---

## 7. Validación de Árboles

### Reglas de Validación

1. **Una raíz**: Solo un elemento puede ser `root`
2. **Sin ciclos**: Los arcos no pueden formar ciclos
3. **Conectividad**: Todos los elementos deben conectarse al árbol
4. **Proyectividad**: Preferir árboles proyectivos (sin cruces)

### Script de Validación

```python
def validate_tree(tokens: list, relations: list) -> bool:
    """Valida que las relaciones formen un árbol válido."""
    roots = [r for r in relations if r["label"] == "root"]
    
    if len(roots) != 1:
        return False  # Debe haber exactamente una raíz
    
    # Verificar que todos los tokens estén conectados
    connected = {roots[0]["token"]}
    for rel in relations:
        if rel["head"] in connected:
            connected.add(rel["token"])
    
    return len(connected) == len(tokens)
```

---

## 8. Referencias

- [Universal Dependencies Relations](https://universaldependencies.org/u/dep/)
- [Old Guaraní Treebank](https://universaldependencies.org/treebanks/gn_oldtudet/index.html)
- [Guidelines UD Español](https://universaldependencies.org/es/)

---

## 9. Documentos Relacionados

- [14-ETIQUETAS-POS.md](14-ETIQUETAS-POS.md) - Categorías gramaticales
- [15-ETIQUETAS-FEATURES.md](15-ETIQUETAS-FEATURES.md) - Features morfológicos
- [08-RECIPE-RELATIONS.md](08-RECIPE-RELATIONS.md) - Recipe de relaciones
- [13-UD-MAPPER.md](13-UD-MAPPER.md) - Mapper centralizado
