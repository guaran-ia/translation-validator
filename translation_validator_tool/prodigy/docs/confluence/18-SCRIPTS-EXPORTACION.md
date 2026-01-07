# 📤 Scripts de Exportación

Este documento detalla los scripts utilizados para **exportar anotaciones** desde Prodigy.

---

## 1. export_to_json_with_iaa.py

### Descripción

Script principal de exportación que:
- Exporta anotaciones desde Prodigy
- Calcula métricas de Inter-Annotator Agreement (IAA)
- Genera JSON estructurado con estadísticas

### Ubicación

```
prodigy/scripts/export_to_json_with_iaa.py
```

### Uso

```powershell
# Exportar con IAA
python scripts/export_to_json_with_iaa.py \
  --dataset guarani_pos_batch_001 \
  --output resultados/export_batch_001.json

# Exportar múltiples datasets
python scripts/export_to_json_with_iaa.py \
  --pattern "guarani_pos_batch_*" \
  --output resultados/export_pos_all.json

# Con opciones de formato
python scripts/export_to_json_with_iaa.py \
  --dataset guarani_pos_batch_001 \
  --output export.json \
  --format ud \
  --include-conflicts
```

### Parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `--dataset` | Nombre del dataset de Prodigy |
| `--pattern` | Patrón glob para múltiples datasets |
| `--output` | Archivo de salida |
| `--format` | Formato: `json` (default), `ud` (Universal Dependencies) |
| `--include-conflicts` | Incluir anotaciones en conflicto |
| `--min-annotators` | Mínimo de anotadores para incluir |

### Formato de Salida

```json
{
  "metadata": {
    "exported_at": "2024-01-15T10:30:00",
    "total_examples": 150,
    "total_annotations": 450,
    "datasets": ["guarani_pos_batch_001", "guarani_pos_batch_002"],
    "iaa_scores": {
      "overall": 0.85,
      "by_label": {
        "NOUN": 0.92,
        "VERB": 0.88,
        "PRON": 0.79
      }
    }
  },
  "examples": [
    {
      "id": 1,
      "text": "Oguatá avá",
      "annotations": {
        "alice": {
          "spans": [
            {"start": 0, "end": 6, "label": "VERB"},
            {"start": 7, "end": 10, "label": "NOUN"}
          ],
          "answer": "accept"
        },
        "bob": {
          "spans": [
            {"start": 0, "end": 6, "label": "VERB"},
            {"start": 7, "end": 10, "label": "NOUN"}
          ],
          "answer": "accept"
        }
      },
      "consensus": {
        "spans": [
          {"start": 0, "end": 6, "label": "VERB", "agreement": 1.0},
          {"start": 7, "end": 10, "label": "NOUN", "agreement": 1.0}
        ]
      }
    }
  ]
}
```

---

## 2. export_conflicts.py

### Descripción

Exporta específicamente los casos donde hay **desacuerdo** entre anotadores.

### Uso

```powershell
python scripts/export_conflicts.py \
  --dataset guarani_pos_batch_001 \
  --output resultados/conflicts_batch_001.json \
  --threshold 0.5
```

### Parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `--dataset` | Dataset de Prodigy |
| `--output` | Archivo de salida |
| `--threshold` | Umbral de acuerdo (exportar si < threshold) |

### Formato de Salida

```json
{
  "total_conflicts": 15,
  "conflicts": [
    {
      "id": 42,
      "text": "Che roipota",
      "position": {"start": 0, "end": 3},
      "annotations": {
        "alice": "PRON",
        "bob": "DET"
      },
      "agreement_score": 0.33
    }
  ]
}
```

---

## 3. convert_pos_tags.py

### Descripción

Convierte etiquetas entre formato amigable y Universal Dependencies.

### Uso

```powershell
# Convertir de amigable a UD
python scripts/convert_pos_tags.py \
  --input export.json \
  --output export_ud.json \
  --direction to_ud

# Convertir de UD a amigable
python scripts/convert_pos_tags.py \
  --input export_ud.json \
  --output export_friendly.json \
  --direction to_friendly
```

### Ejemplo de Conversión

**Entrada (Amigable):**
```json
{"label": "Sustantivo"}
```

**Salida (UD):**
```json
{"label": "NOUN"}
```

---

## 4. Exportación desde Prodigy CLI

### Exportar dataset completo

```powershell
# JSONL básico
prodigy db-out guarani_pos_batch_001 > export.jsonl

# JSON pretty
prodigy db-out guarani_pos_batch_001 --json > export.json
```

### Filtrar por respuesta

```powershell
# Solo aceptados
prodigy db-out guarani_pos_batch_001 | python -c "
import sys, json
for line in sys.stdin:
    ex = json.loads(line)
    if ex.get('answer') == 'accept':
        print(line.strip())
" > accepted_only.jsonl
```

### Exportar con sesión específica

```powershell
# Filtrar por anotador
prodigy db-out guarani_pos_batch_001 | python -c "
import sys, json
for line in sys.stdin:
    ex = json.loads(line)
    if ex.get('_session_id') == 'alice':
        print(line.strip())
" > alice_annotations.jsonl
```

---

## 5. Formato CoNLL-U

### Exportar a CoNLL-U

```powershell
python scripts/export_to_conllu.py \
  --input export.json \
  --output corpus.conllu
```

### Formato de Salida

```conllu
# sent_id = 1
# text = Avá oguatá porã
1	Avá	avá	NOUN	_	_	2	nsubj	_	_
2	oguatá	oguata	VERB	_	_	0	root	_	_
3	porã	porã	ADV	_	_	2	advmod	_	_

# sent_id = 2
# text = Che roipota nde
1	Che	che	PRON	_	Person=1|Number=Sing	2	nsubj	_	_
2	roipota	roipota	VERB	_	_	0	root	_	_
3	nde	nde	PRON	_	Person=2|Number=Sing	2	obj	_	_
```

---

## 6. Flujo de Exportación

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE EXPORTACIÓN                             │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────┐
    │     Prodigy Database             │
    │  (SQLite: ~/.prodigy/prodigy.db) │
    └────────────────┬─────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
  ┌──────────────┐      ┌──────────────────────┐
  │ prodigy      │      │ export_to_json_      │
  │ db-out       │      │ with_iaa.py          │
  └──────┬───────┘      └──────────┬───────────┘
         │                         │
         ▼                         ▼
  ┌──────────────┐      ┌──────────────────────┐
  │ JSONL básico │      │ JSON con métricas    │
  │              │      │ + IAA + consenso     │
  └──────┬───────┘      └──────────┬───────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
              ┌──────────────────────┐
              │ convert_pos_tags.py  │
              │ (Amigable ↔ UD)      │
              └──────────┬───────────┘
                         │
           ┌─────────────┴─────────────┐
           │                           │
           ▼                           ▼
    ┌────────────────┐         ┌────────────────┐
    │ JSON (Amigable)│         │ CoNLL-U (UD)   │
    │ para análisis  │         │ para NLP       │
    └────────────────┘         └────────────────┘
```

---

## 7. Métricas de IAA

### Cálculo de Acuerdo

El script `export_to_json_with_iaa.py` calcula:

1. **Span Agreement**: Acuerdo en la segmentación
2. **Label Agreement**: Acuerdo en las etiquetas (dado mismo span)
3. **Overall IAA**: Combinación ponderada

### Fórmulas

```
Span Agreement = |Spans coincidentes| / |Unión de spans|

Label Agreement = |Labels coincidentes| / |Spans coincidentes|

Overall IAA = α * Span_Agreement + β * Label_Agreement
```

### Ejemplo de Métricas

```json
{
  "iaa_scores": {
    "overall": 0.85,
    "span_agreement": 0.90,
    "label_agreement": 0.94,
    "by_annotator_pair": {
      "alice-bob": 0.88,
      "alice-carlos": 0.82,
      "bob-carlos": 0.85
    },
    "by_label": {
      "NOUN": {"agreement": 0.92, "count": 245},
      "VERB": {"agreement": 0.88, "count": 312},
      "PRON": {"agreement": 0.79, "count": 156}
    }
  }
}
```

---

## 8. Scripts de Respaldo

### Backup de base de datos

```powershell
# Copiar base de datos de Prodigy
Copy-Item "$HOME\.prodigy\prodigy.db" "backups\prodigy_$(Get-Date -Format 'yyyyMMdd').db"
```

### Exportar todos los datasets

```powershell
# Listar y exportar todos
prodigy stats | Select-String "guarani" | ForEach-Object {
    $dataset = $_.Line.Split()[0]
    prodigy db-out $dataset > "backups\$dataset.jsonl"
    Write-Host "Exportado: $dataset"
}
```

---

## 9. Validación de Exportación

### Verificar integridad

```powershell
python -c "
import json
with open('export.json') as f:
    data = json.load(f)
    
print(f'Total ejemplos: {len(data[\"examples\"])}')
print(f'IAA overall: {data[\"metadata\"][\"iaa_scores\"][\"overall\"]:.2f}')
print(f'Anotadores: {len(set(a for ex in data[\"examples\"] for a in ex[\"annotations\"].keys()))}')
"
```

### Verificar formato UD

```powershell
# Validar CoNLL-U con ud-validator
python -m conllu validate corpus.conllu
```

---

## 10. Documentos Relacionados

- [17-SCRIPTS-GENERACION.md](17-SCRIPTS-GENERACION.md) - Scripts de generación
- [19-CALCULO-IAA.md](19-CALCULO-IAA.md) - Cálculo de IAA
- [13-UD-MAPPER.md](13-UD-MAPPER.md) - Mapper de etiquetas
