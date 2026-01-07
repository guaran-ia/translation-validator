# 📊 Cálculo de Inter-Annotator Agreement (IAA)

Este documento detalla cómo se calcula y se interpreta el **acuerdo entre anotadores** en el proyecto.

---

## 1. ¿Qué es IAA?

**Inter-Annotator Agreement (IAA)** mide la consistencia entre diferentes anotadores al etiquetar los mismos datos. Es fundamental para:

- **Validar la calidad** de las anotaciones
- **Identificar** etiquetas problemáticas o ambiguas
- **Detectar** anotadores que necesitan más entrenamiento
- **Establecer** un gold standard

---

## 2. Script Principal

### Ubicación

```
prodigy/scripts/calculate_iaa.py
```

### Uso

```powershell
# Cálculo básico
python scripts/calculate_iaa.py guarani_pos_batch_001

# Con archivo de salida específico
python scripts/calculate_iaa.py guarani_pos_batch_001 --output reports/iaa_batch_001.md

# Para múltiples batches
python scripts/calculate_iaa.py guarani_pos_batch_001 -o reports/iaa_001.md
python scripts/calculate_iaa.py guarani_pos_batch_002 -o reports/iaa_002.md
```

---

## 3. Métricas Calculadas

### 3.1 Acuerdo Simple (Raw Agreement)

**Fórmula:**
$$
\text{Agreement} = \frac{|\text{Spans coincidentes}|}{|\text{Unión de spans}|}
$$

**Características:**
- Rango: 0.0 (ningún acuerdo) a 1.0 (acuerdo perfecto)
- Intuitivo y fácil de interpretar
- No considera acuerdo por azar

### 3.2 Cohen's Kappa

**Fórmula:**
$$
\kappa = \frac{P_o - P_e}{1 - P_e}
$$

Donde:
- $P_o$ = Proporción de acuerdo observado
- $P_e$ = Proporción de acuerdo esperado por azar

**Interpretación:**

| Kappa | Nivel de Acuerdo |
|-------|------------------|
| < 0.20 | Pobre |
| 0.21 - 0.40 | Bajo |
| 0.41 - 0.60 | Moderado |
| 0.61 - 0.80 | Sustancial |
| 0.81 - 1.00 | Casi perfecto |

### 3.3 Acuerdo por Etiqueta

Se calcula el acuerdo para cada etiqueta individualmente:

$$
\text{Agreement}_{\text{label}} = \frac{|\text{Spans con label L coincidentes}|}{|\text{Unión de spans con label L}|}
$$

Útil para identificar etiquetas problemáticas.

---

## 4. Implementación del Cálculo

### Agrupación de Datos

```python
def group_by_task_and_session(examples: List[Dict]) -> Dict[int, Dict[str, Dict]]:
    """
    Agrupa anotaciones por task_hash y session_id.
    
    Returns:
        {task_hash: {session_id: example, ...}, ...}
    """
    grouped = defaultdict(dict)
    
    for ex in examples:
        if ex.get("answer") != "accept":
            continue  # Solo considerar anotaciones aceptadas
        
        task_hash = ex.get("_task_hash")
        session_id = ex.get("_session_id")
        
        if task_hash and session_id:
            grouped[task_hash][session_id] = ex
    
    return grouped
```

### Extracción de Spans

```python
def extract_span_tuples(example: Dict) -> Set[Tuple[int, int, str]]:
    """
    Extrae spans como tuplas (start, end, label) para comparación.
    """
    spans = example.get("spans", [])
    return {(span["start"], span["end"], span["label"]) for span in spans}
```

### Cálculo de Cohen's Kappa

```python
def cohen_kappa_spans(spans_a: Set[Tuple], spans_b: Set[Tuple], text_length: int) -> float:
    """
    Calcula Cohen's Kappa para spans.
    """
    # Extraer posiciones marcadas por cada anotador
    positions_a = set()
    positions_b = set()
    
    for start, end, label in spans_a:
        positions_a.update(range(start, end))
    
    for start, end, label in spans_b:
        positions_b.update(range(start, end))
    
    # Total de posiciones posibles
    total_positions = text_length
    
    # Calcular acuerdos
    both_marked = len(positions_a & positions_b)
    both_unmarked = total_positions - len(positions_a | positions_b)
    
    # Acuerdo observado
    p_o = (both_marked + both_unmarked) / total_positions
    
    # Acuerdo esperado por azar
    p_a_marked = len(positions_a) / total_positions
    p_b_marked = len(positions_b) / total_positions
    p_e = p_a_marked * p_b_marked + (1 - p_a_marked) * (1 - p_b_marked)
    
    # Cohen's Kappa
    kappa = (p_o - p_e) / (1 - p_e) if p_e != 1.0 else 1.0
    return max(0.0, min(1.0, kappa))
```

---

## 5. Formato del Reporte

El script genera un reporte Markdown con:

```markdown
# 📊 Reporte de Inter-Annotator Agreement (IAA)

**Dataset:** `guarani_pos_batch_001`  
**Fecha:** 2024-01-15

---

## 🎯 Resumen General

- **Acuerdo promedio (simple):** 85.2%
- **Cohen's Kappa promedio:** 0.782
- **Total de pares evaluados:** 3

---

## 👥 Acuerdo por Par de Anotadores

### `alice` ↔ `bob`

- **Acuerdo simple:** 88.5%
- **Cohen's Kappa:** 0.835
- **Oraciones comparadas:** 45

**Acuerdo por etiqueta:**

| Etiqueta | Acuerdo |
|----------|---------|
| Sustantivo | 92.3% |
| Verbo | 87.5% |
| Pronombre | 78.9% |

---

## ⚠️ Outliers Detectados

✅ No se detectaron anotadores con acuerdo consistentemente bajo.

---

## 📈 Recomendaciones

1. Kappa < 0.60: Revisar guidelines
2. Desacuerdo en etiquetas específicas: Añadir ejemplos
3. Outliers detectados: Sesión 1-on-1
```

---

## 6. Requisitos para Calcular IAA

### Configuración de Task Router

Para que el IAA funcione, se necesita **overlap** entre anotadores:

```python
# En prodigy.json o en el recipe
{
    "task_router": {
        "annotations_per_task": 3  # Cada tarea a 3 anotadores
    }
}
```

### Mínimo de Tareas Compartidas

- Al menos **10-20 tareas** compartidas por par de anotadores
- Idealmente **50+** para resultados estadísticamente significativos

---

## 7. Casos Especiales

### Acuerdo en Spans vs. Labels

El cálculo diferencia entre:

1. **Span Agreement**: ¿Marcaron la misma porción de texto?
2. **Label Agreement**: ¿Asignaron la misma etiqueta al mismo span?

### Manejo de Spans Parcialmente Coincidentes

```
Anotador A:    [---Sustantivo---]
Anotador B:        [--Sustantivo--]

→ No cuenta como coincidencia exacta
→ Se considera desacuerdo de segmentación
```

### Spans Anidados u Overlapping

Si se permiten spans overlapping (como en morfología):

```
Texto:    "mboguatávo"
Alice:    [mbo][guatá][vo]
Bob:      [mboguatá][vo]

→ Compara cada span como entidad separada
```

---

## 8. Interpretación de Resultados

### Kappa Alto (> 0.80)

✅ **Buenas noticias:**
- Guidelines claras
- Anotadores bien entrenados
- Tarea bien definida

**Acción:** Puede reducirse overlap para aumentar velocidad.

### Kappa Moderado (0.41 - 0.60)

⚠️ **Revisión necesaria:**
- Identificar etiquetas problemáticas
- Revisar ejemplos dudosos con el equipo
- Actualizar guidelines

**Acción:** Sesión de calibración, agregar ejemplos.

### Kappa Bajo (< 0.40)

❌ **Problemas serios:**
- Guidelines ambiguas
- Entrenamiento insuficiente
- Tarea demasiado compleja

**Acción:** Reformular la tarea, reentrenar, más ejemplos.

---

## 9. Visualización de Desacuerdos

### Exportar casos de desacuerdo

```powershell
python scripts/export_conflicts.py \
  --dataset guarani_pos_batch_001 \
  --output conflicts.json
```

### Revisar en Prodigy

```powershell
# Crear dataset de revisión con conflictos
prodigy review guarani_review conflicts.json
```

---

## 10. Métricas Adicionales

### Fleiss' Kappa (para 3+ anotadores)

Para múltiples anotadores simultáneos:

$$
\kappa = \frac{\bar{P} - \bar{P_e}}{1 - \bar{P_e}}
$$

### Krippendorff's Alpha

Más robusto para datos incompletos:
- Maneja valores faltantes
- Funciona con cualquier número de anotadores
- Más conservador que Kappa

---

## 11. Automatización

### Calcular IAA después de cada batch

```powershell
# En start_batch_auto.ps1
# ... después de completar un batch ...

Write-Host "Calculando IAA para batch completado..."
python scripts/calculate_iaa.py "guarani_pos_batch_$batchNumber" `
  --output "reports/iaa_batch_$batchNumber.md"
```

### Monitoreo continuo

```powershell
# Script para calcular IAA de todos los batches
$batches = Get-ChildItem ".\data\batches\batch_*.jsonl" | Select-Object -First 10
foreach ($batch in $batches) {
    $num = $batch.Name -replace 'batch_(\d+)\.jsonl','$1'
    python scripts/calculate_iaa.py "guarani_pos_batch_$num" `
      --output "reports/iaa_$num.md"
}
```

---

## 12. Documentos Relacionados

- [18-SCRIPTS-EXPORTACION.md](18-SCRIPTS-EXPORTACION.md) - Scripts de exportación
- [21-GUIA-ANOTADOR.md](21-GUIA-ANOTADOR.md) - Guía del anotador
- [10-SISTEMA-BATCHES.md](10-SISTEMA-BATCHES.md) - Sistema de lotes
