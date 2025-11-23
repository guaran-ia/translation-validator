"""
GUÍA DE QUALITY ASSURANCE - Anotaciones POS Multi-Anotador
============================================================

Este documento describe el workflow completo para garantizar anotaciones de alta calidad.
"""

# 📋 Workflow Completo

## 1️⃣ Setup Inicial (una sola vez)

### Exportar oraciones desde PostgreSQL
```powershell
cd translation_validator_tool/prodigy
python scripts/export_to_prodigy.py
```

Esto crea `data/export/original_translations.jsonl` con oraciones Guaraní-Español.

---

## 2️⃣ Anotación Multi-Anotador

### Definir anotadores
```powershell
# En PowerShell
$env:PRODIGY_ALLOWED_SESSIONS="alice,bob,carlos"
```

### Iniciar servidor
```powershell
python -m prodigy guarani-pos-v2 pos_v2 data/export/original_translations.jsonl -F recipes/guarani_pos_v2.py --port 8081
```

### Cada anotador accede con su sesión
- Alice: `http://localhost:8081/?session=alice`
- Bob: `http://localhost:8081/?session=bob`
- Carlos: `http://localhost:8081/?session=carlos`

### ✅ Validación automática
El sistema **requiere obligatoriamente**:
- ✓ Al menos 1 **SUJETO**
- ✓ Al menos 1 **VERBO**

Si intentas aceptar sin cumplir esto, verás un error.

### 🔄 Task Routing
- Cada oración será vista por **2 anotadores** (configurado en `task_router_iaa`).
- Asignación determinista (mismo hash → mismos anotadores).
- Permite calcular **Inter-Annotator Agreement** después.

---

## 3️⃣ Exportar Anotaciones

### Exportar todo el dataset
```powershell
python -m prodigy db-out pos_v2 > data/annotations/pos_v2_export.jsonl
```

### Ver estadísticas rápidas
```powershell
python -m prodigy stats pos_v2
```

---

## 4️⃣ Calcular Inter-Annotator Agreement (IAA)

### Ejecutar análisis
```powershell
python scripts/calculate_iaa.py pos_v2 --output reports/iaa_report.md
```

### Qué obtendrás:
- **Cohen's Kappa** por par de anotadores
- Acuerdo por etiqueta (SUJETO, VERBO, etc.)
- Detección de **outliers** (anotadores con bajo acuerdo)
- Reporte markdown completo

### Interpretación de Kappa:
| Valor | Interpretación |
|-------|----------------|
| < 0.20 | Acuerdo pobre |
| 0.21 - 0.40 | Acuerdo bajo |
| 0.41 - 0.60 | Acuerdo moderado |
| 0.61 - 0.80 | Acuerdo sustancial |
| 0.81 - 1.00 | Acuerdo casi perfecto |

**Meta recomendada:** Kappa > 0.70

---

## 5️⃣ Identificar y Resolver Conflictos

### Exportar oraciones con desacuerdo
```powershell
python scripts/export_conflicts.py pos_v2 --output data/export/conflicts.jsonl --threshold 0.3
```

Parámetros:
- `--threshold 0.3` = desacuerdo ≥ 30% (ajustable)

### Qué obtendrás:
- JSONL con oraciones donde anotadores difirieron
- Score de desacuerdo por oración
- Anotaciones de cada anotador lado-a-lado

### Revisar conflictos (supervisor)
```powershell
python -m prodigy guarani-pos-review conflicts_review data/export/conflicts.jsonl -F recipes/guarani_pos_v2.py
```

El supervisor ve:
- Texto original
- Anotaciones de cada anotador
- Puede crear versión "gold-standard"

---

## 6️⃣ Exportar Dataset Final (Gold Standard)

### Opción A: Solo anotaciones con alto acuerdo
```powershell
# Exportar solo accept + Kappa > 0.70
python -m prodigy db-out pos_v2 | python scripts/filter_high_quality.py > data/annotations/gold_standard.jsonl
```

### Opción B: Incluir reviews de conflictos
```powershell
# Combinar pos_v2 + conflicts_review
python -m prodigy db-out pos_v2 > temp1.jsonl
python -m prodigy db-out conflicts_review > temp2.jsonl
cat temp1.jsonl temp2.jsonl | python scripts/deduplicate.py > data/annotations/gold_standard.jsonl
```

---

## 7️⃣ Entrenar Modelo spaCy

### Convertir a formato spaCy
```powershell
python -m prodigy data-to-spacy data/training --ner pos_v2
```

### Entrenar
```powershell
python -m spacy train config.cfg --output models/ --paths.train data/training/train.spacy --paths.dev data/training/dev.spacy
```

---

## 📊 Métricas de Calidad Recomendadas

### Durante anotación:
- ✅ **Validación en tiempo real** (requiere SUJETO + VERBO)
- ✅ **Task routing** (2 anotadores por oración)
- ✅ **Sesiones nombradas** (trazabilidad)

### Post-anotación:
- 📈 **IAA (Kappa) > 0.70**
- 🎯 **Agreement por label > 80%** (al menos en SUJETO y VERBO)
- ⚠️ **< 10% outliers** (anotadores con bajo acuerdo)
- 🔍 **Review de conflictos** (desacuerdo > 30%)

### Dataset final:
- ✅ **Mínimo 500 oraciones** anotadas
- ✅ **Distribución balanceada** de etiquetas
- ✅ **Conflictos resueltos** por supervisor

---

## 🚨 Troubleshooting

### "No hay suficientes anotaciones multi-anotador para IAA"
**Causa:** Solo 1 anotador anotó cada oración.
**Solución:** Asegúrate de:
1. Definir `PRODIGY_ALLOWED_SESSIONS` antes de iniciar server
2. Cada anotador usa `?session=nombre` diferente
3. El recipe usa `task_router_iaa` (ya incluido en v2)

### "Cohen's Kappa muy bajo (< 0.50)"
**Causa:** Anotadores no están alineados en criterios.
**Solución:**
1. Revisar `POS_ANNOTATION_GUIDE.md` con el equipo
2. Hacer sesión de calibración (anotar 10-20 oraciones juntos)
3. Añadir ejemplos claros al guide
4. Re-entrenar anotadores con bajo acuerdo

### "Muchos conflictos (> 30%)"
**Causa:** Guidelines ambiguos o ejemplos difíciles.
**Solución:**
1. Revisar top 10 conflictos con `export_conflicts.py`
2. Identificar patrones (ej: siempre discrepan en "pe", "ha")
3. Añadir reglas específicas al guide
4. Considerar aumentar `annotations_per_task` a 3

---

## 🎯 Checklist Pre-Entrenamiento

Antes de usar las anotaciones para entrenar un modelo, verifica:

- [ ] IAA (Kappa) > 0.70
- [ ] Conflictos revisados y resueltos
- [ ] Mínimo 500 oraciones anotadas
- [ ] Distribución de etiquetas verificada
- [ ] Outliers re-entrenados o removidos
- [ ] Dataset final exportado y respaldado

---

## 📚 Referencias

- `POS_ANNOTATION_GUIDE.md` — Guidelines detallados para anotadores
- `recipes/guarani_pos_v2.py` — Recipe con validación y task routing
- `scripts/calculate_iaa.py` — Análisis de acuerdos
- `scripts/export_conflicts.py` — Exportar desacuerdos
- Prodigy docs: https://prodi.gy/docs/task-routing

---

*Última actualización: 2025-11-21*
