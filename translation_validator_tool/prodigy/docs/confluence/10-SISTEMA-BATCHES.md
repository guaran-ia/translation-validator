# 📦 Sistema de Batches (Lotes)

El sistema de lotes divide el corpus en bloques manejables de 50 oraciones para anotación estructurada.

---

## 1. Configuración de Lotes

### Parámetros por defecto

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `TOTAL_BATCHES` | 60 | Número total de lotes |
| `SENTENCES_PER_BATCH` | 50 | Oraciones por lote |
| Total | 3000 | Oraciones totales |

---

## 2. Generación de Lotes

### 2.1 Script: `generate_batches.py`

Ubicación: `scripts/generate_batches.py`

#### Uso básico

```powershell
# Generar 60 lotes de 50 oraciones (orden original)
python scripts/generate_batches.py --total 3000 --batch-size 50

# Con mezcla aleatoria (reproducible)
python scripts/generate_batches.py --total 3000 --batch-size 50 --shuffle --seed 42
```

#### Parámetros

| Parámetro | Alias | Default | Descripción |
|-----------|-------|---------|-------------|
| `--input` | `-i` | `data/export/original_translations.jsonl` | Archivo de entrada |
| `--output` | `-o` | `data/batches` | Directorio de salida |
| `--total` | `-t` | 3000 | Total de oraciones |
| `--batch-size` | `-b` | 50 | Oraciones por lote |
| `--seed` | `-s` | 42 | Semilla aleatoria |
| `--shuffle` | - | false | Mezclar aleatoriamente |

### 2.2 Formato de Entrada

Archivo JSONL con formato:

```json
{"text": "Ore roipota aña'nga", "meta": {"spanish_text": "Nosotros queremos espíritu", "source": "doc1"}}
{"text": "Ha'e oguata", "meta": {"spanish_text": "Él camina", "source": "doc1"}}
```

### 2.3 Salida Generada

```
data/batches/
├── batch_001.jsonl      # Lote 1: oraciones 1-50
├── batch_002.jsonl      # Lote 2: oraciones 51-100
├── batch_003.jsonl      # Lote 3: oraciones 101-150
├── ...
├── batch_060.jsonl      # Lote 60: oraciones 2951-3000
└── batches_index.json   # Índice de lotes
```

---

## 3. Estructura de Archivos de Lote

### 3.1 Archivo de lote (batch_XXX.jsonl)

Cada línea es un ejemplo con metadata del lote:

```json
{
  "text": "Ore roipota aña'nga",
  "meta": {
    "spanish_text": "Nosotros queremos espíritu",
    "source": "doc1",
    "batch_id": 1,
    "batch_index": 1,
    "global_index": 1
  }
}
```

### 3.2 Índice de lotes (batches_index.json)

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

---

## 4. Flujo de Anotación por Lotes

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FLUJO DE ANOTACIÓN POR LOTES                    │
└─────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │   LOTE 1    │────>│   LOTE 2    │────>│   LOTE 3    │───> ...
  │  (50 sent)  │     │  (50 sent)  │     │  (50 sent)  │
  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │  Alice    │       │  Alice    │       │  Alice    │
   │   Bob     │       │   Bob     │       │   Bob     │
   │  Carlos   │       │  Carlos   │       │  Carlos   │
   └───────────┘       └───────────┘       └───────────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │ 3 anot.   │       │ 3 anot.   │       │ 3 anot.   │
   │ completas │       │ completas │       │ completas │
   └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │AUTO-ADVANCE│       │AUTO-ADVANCE│       │AUTO-ADVANCE│
   │  → Lote 2 │       │  → Lote 3 │       │  → Lote 4 │
   └───────────┘       └───────────┘       └───────────┘
```

---

## 5. Datasets de Prodigy

### 5.1 Nomenclatura

Cada tipo de anotación genera datasets separados:

```
guarani_{tipo}_batch_{numero:02d}
```

| Tipo | Ejemplo Dataset | Puerto |
|------|-----------------|--------|
| POS | `guarani_pos_batch_01` | 8080 |
| Features | `guarani_features_batch_01` | 8081 |
| Relations | `guarani_relations_batch_01` | 8082 |

### 5.2 Listar datasets

```powershell
# Ver todos los datasets
prodigy stats

# Ver dataset específico
prodigy stats guarani_pos_batch_01
```

### 5.3 Exportar dataset

```powershell
# Exportar a JSONL
prodigy db-out guarani_pos_batch_01 > export_pos_01.jsonl

# Exportar múltiples
for ($i = 1; $i -le 10; $i++) {
    $num = "{0:D2}" -f $i
    prodigy db-out "guarani_pos_batch_$num" > "export_pos_$num.jsonl"
}
```

---

## 6. Estado de los Lotes

### 6.1 Archivo de estado

Ubicación: `data/batch_monitor_state.json`

```json
{
  "pos": {
    "current_batch": 5,
    "completed_batches": [1, 2, 3, 4],
    "in_progress": {
      "5": {
        "alice": {"completed": 50, "total": 50},
        "bob": {"completed": 45, "total": 50},
        "carlos": {"completed": 50, "total": 50}
      }
    }
  },
  "features": {
    "current_batch": 3,
    "completed_batches": [1, 2],
    "in_progress": {}
  },
  "relations": {
    "current_batch": 1,
    "completed_batches": [],
    "in_progress": {}
  }
}
```

### 6.2 API de progreso

```bash
# Obtener progreso vía API
curl http://localhost:8085/api/batch-progress \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 7. Variables de Entorno

```bash
# Lotes actuales (actualizado por batch_monitor)
CURRENT_BATCH_POS=1
CURRENT_BATCH_FEATURES=1
CURRENT_BATCH_RELATIONS=1

# Configuración
TOTAL_BATCHES=60
SENTENCES_PER_BATCH=50
```

---

## 8. Carga de Lotes en Recipes

### Función `load_batch`

```python
def load_batch(batch_dir: str, batch_id: int) -> list:
    """Carga un lote específico."""
    batch_file = Path(batch_dir) / f"batch_{batch_id:03d}.jsonl"
    
    if not batch_file.exists():
        print(f"[ERROR] No existe {batch_file}")
        return []
    
    examples = []
    with open(batch_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    
    print(f"[OK] Cargado lote {batch_id}: {len(examples)} oraciones")
    return examples
```

---

## 9. Comandos Útiles

### Ver contenido de un lote

```powershell
# Primera oración del lote 1
Get-Content data/batches/batch_001.jsonl | Select-Object -First 1 | ConvertFrom-Json

# Contar oraciones
(Get-Content data/batches/batch_001.jsonl).Count
```

### Regenerar lotes

```powershell
# Eliminar lotes existentes
Remove-Item data/batches/*.jsonl

# Regenerar
python scripts/generate_batches.py --total 3000 --batch-size 50
```

### Verificar integridad

```powershell
# Verificar que todos los lotes existen
for ($i = 1; $i -le 60; $i++) {
    $file = "data/batches/batch_{0:D3}.jsonl" -f $i
    if (!(Test-Path $file)) {
        Write-Host "FALTA: $file" -ForegroundColor Red
    }
}
Write-Host "Verificación completa" -ForegroundColor Green
```

---

## 10. Siguiente Paso

Continúa con [11-AUTO-ADVANCE.md](11-AUTO-ADVANCE.md) para entender el sistema de avance automático.
