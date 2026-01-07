# 📦 Scripts de Generación

Este documento detalla los scripts utilizados para **generar y preparar datos** para la anotación en Prodigy.

---

## 1. generate_batches.py

### Descripción

Script principal para dividir el corpus en lotes manejables para anotación.

### Ubicación

```
prodigy/scripts/generate_batches.py
```

### Uso

```powershell
# Uso básico (60 lotes × 50 oraciones = 3000 oraciones)
python scripts/generate_batches.py --total 3000 --batch-size 50

# Orden aleatorio con semilla
python scripts/generate_batches.py --total 3000 --batch-size 50 --shuffle --seed 42

# Especificar archivos
python scripts/generate_batches.py \
  --input data/export/original_translations.jsonl \
  --output data/batches \
  --total 3000 \
  --batch-size 50
```

### Parámetros

| Parámetro | Alias | Default | Descripción |
|-----------|-------|---------|-------------|
| `--input` | `-i` | `data/export/original_translations.jsonl` | Archivo JSONL de entrada |
| `--output` | `-o` | `data/batches` | Directorio de salida |
| `--total` | `-t` | 3000 | Total de oraciones |
| `--batch-size` | `-b` | 50 | Oraciones por lote |
| `--seed` | `-s` | 42 | Semilla para aleatorización |
| `--shuffle` | - | False | Mezclar aleatoriamente |

### Modos de Ordenamiento

#### Modo Secuencial (Default)

```powershell
python scripts/generate_batches.py --total 3000 --batch-size 50
```

Mantiene el **orden original** del archivo JSONL:
- Preserva el contexto narrativo
- Las oraciones consecutivas se mantienen juntas
- Útil para textos con continuidad

#### Modo Aleatorio

```powershell
python scripts/generate_batches.py --total 3000 --batch-size 50 --shuffle --seed 42
```

Mezcla aleatoriamente con semilla:
- Distribución uniforme de dificultad
- Reproducible con la misma semilla
- Evita sesgos de posición

### Estructura de Salida

```
data/batches/
├── batch_001.jsonl      # Primer lote (oraciones 1-50)
├── batch_002.jsonl      # Segundo lote (oraciones 51-100)
├── batch_003.jsonl      # ...
├── ...
├── batch_060.jsonl      # Último lote (oraciones 2951-3000)
└── batches_index.json   # Índice con metadata
```

### Formato de batch_XXX.jsonl

Cada línea contiene un ejemplo:

```json
{
  "text": "Oguatá avá ogápe",
  "meta": {
    "original_id": "doc_123",
    "source": "corpus_guarani",
    "batch_id": 1,
    "batch_index": 15,
    "global_index": 15
  }
}
```

### Formato de batches_index.json

```json
{
  "seed": null,
  "shuffle": false,
  "total_sentences": 3000,
  "batch_size": 50,
  "num_batches": 60,
  "source_file": "data/export/original_translations.jsonl",
  "order": "sequential",
  "batches": [
    {
      "batch_id": 1,
      "file": "batch_001.jsonl",
      "sentences": 50,
      "global_start": 1,
      "global_end": 50
    },
    {
      "batch_id": 2,
      "file": "batch_002.jsonl",
      "sentences": 50,
      "global_start": 51,
      "global_end": 100
    }
  ]
}
```

### Output del Script

```
📂 Cargando datos de: data/export/original_translations.jsonl
   Total disponible: 5234 oraciones

📋 Modo SECUENCIAL - manteniendo orden original del JSONL

📊 Configuración:
   Total oraciones: 3000
   Tamaño de lote: 50
   Número de lotes: 60
   Orden: secuencial (original)

📦 Generando lotes en: data/batches
   ✅ Lote 01: 50 oraciones → batch_001.jsonl
   ✅ Lote 02: 50 oraciones → batch_002.jsonl
   ...
   ✅ Lote 60: 50 oraciones → batch_060.jsonl

📋 Índice guardado en: data/batches/batches_index.json

✅ ¡Listo! 60 lotes generados.
```

---

## 2. export_to_prodigy.py

### Descripción

Convierte datos del formato del backend API al formato JSONL que Prodigy espera.

### Uso

```powershell
python scripts/export_to_prodigy.py --input translations.csv --output data/export/
```

### Formato de Entrada (CSV)

```csv
id,guarani_text,spanish_text,document_id
1,"Oguatá avá","El hombre camina",doc_123
2,"Oñeʼẽ porã","Habla bien",doc_123
```

### Formato de Salida (JSONL)

```json
{"text": "Oguatá avá", "meta": {"id": 1, "spanish": "El hombre camina", "doc_id": "doc_123"}}
{"text": "Oñeʼẽ porã", "meta": {"id": 2, "spanish": "Habla bien", "doc_id": "doc_123"}}
```

---

## 3. Flujo de Preparación de Datos

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE PREPARACIÓN DE DATOS                    │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  Backend API     │
    │  (PostgreSQL)    │
    └────────┬─────────┘
             │
             │ GET /api/translations/export
             ▼
    ┌──────────────────┐
    │ translations.csv │
    └────────┬─────────┘
             │
             │ export_to_prodigy.py
             ▼
    ┌──────────────────────────────┐
    │ original_translations.jsonl  │
    │ (5234 oraciones)             │
    └────────┬─────────────────────┘
             │
             │ generate_batches.py
             ▼
    ┌──────────────────────────────┐
    │ data/batches/                │
    │ ├── batch_001.jsonl (50)     │
    │ ├── batch_002.jsonl (50)     │
    │ ├── ...                      │
    │ ├── batch_060.jsonl (50)     │
    │ └── batches_index.json       │
    └──────────────────────────────┘
             │
             │ Prodigy Recipes
             ▼
    ┌──────────────────────────────┐
    │        ANOTACIÓN             │
    └──────────────────────────────┘
```

---

## 4. Scripts de Utilidad

### Ver información de un lote

```powershell
# Contar oraciones en un lote
python -c "import json; print(len(open('data/batches/batch_001.jsonl').readlines()))"

# Ver primera oración
python -c "
import json
with open('data/batches/batch_001.jsonl') as f:
    ex = json.loads(f.readline())
    print(json.dumps(ex, indent=2, ensure_ascii=False))
"
```

### Verificar integridad de lotes

```powershell
# Verificar que todos los lotes existen
python -c "
from pathlib import Path
batches = list(Path('data/batches').glob('batch_*.jsonl'))
print(f'Lotes encontrados: {len(batches)}')
for b in sorted(batches)[:5]:
    print(f'  {b.name}')
print('  ...')
"
```

### Regenerar lotes (si es necesario)

```powershell
# 1. Hacer backup
mv data/batches data/batches_backup

# 2. Regenerar
python scripts/generate_batches.py --total 3000 --batch-size 50

# 3. Verificar
ls data/batches/
```

---

## 5. Consideraciones

### Tamaño de Lote

- **50 oraciones**: Recomendado para sesiones de ~30-45 minutos
- **100 oraciones**: Para anotadores experimentados
- **25 oraciones**: Para oraciones complejas o nuevos anotadores

### Consistencia

- **No modificar** los lotes después de empezar la anotación
- Si necesitas regenerar, **hacer backup** de anotaciones primero
- Usar siempre la **misma semilla** para reproducibilidad

### Verificación Pre-Anotación

```powershell
# Verificar que hay suficientes datos
python -c "
import json
with open('data/export/original_translations.jsonl') as f:
    count = sum(1 for _ in f)
print(f'Oraciones disponibles: {count}')
print(f'Lotes posibles (50/lote): {count // 50}')
"
```

---

## 6. Documentos Relacionados

- [10-SISTEMA-BATCHES.md](10-SISTEMA-BATCHES.md) - Sistema de lotes
- [18-SCRIPTS-EXPORTACION.md](18-SCRIPTS-EXPORTACION.md) - Scripts de exportación
- [06-RECIPE-BATCH.md](06-RECIPE-BATCH.md) - Recipe de batch
