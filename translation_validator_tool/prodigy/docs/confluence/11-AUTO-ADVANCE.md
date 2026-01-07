# 🔄 Auto-Advance (batch_monitor)

El sistema **Auto-Advance** monitorea el progreso de anotación y automáticamente avanza al siguiente lote cuando los validadores completan el lote actual.

---

## 1. Descripción

`batch_monitor.py` es un proceso que:

1. **Monitorea** el progreso de cada anotador en el lote actual
2. **Detecta** cuando N validadores han completado el lote
3. **Avanza** automáticamente al siguiente lote
4. **Reinicia** los servicios Prodigy con el nuevo lote

---

## 2. Configuración

### Variables de entorno

```bash
# Validadores por tipo
VALIDATORS_POS=alice,bob,carlos
VALIDATORS_FEATURES=diana,elena,felipe
VALIDATORS_RELATIONS=gabriel,helena,ivan

# Validadores requeridos para avanzar
REQUIRED_VALIDATORS=3

# Configuración de lotes
SENTENCES_PER_BATCH=50
TOTAL_BATCHES=60

# Lotes actuales
CURRENT_BATCH_POS=1
CURRENT_BATCH_FEATURES=1
CURRENT_BATCH_RELATIONS=1
```

### Constantes en código

```python
# batch_monitor.py
REQUIRED_VALIDATORS = int(os.getenv("REQUIRED_VALIDATORS", "3"))
SENTENCES_PER_BATCH = int(os.getenv("SENTENCES_PER_BATCH", "50"))
TOTAL_BATCHES = int(os.getenv("TOTAL_BATCHES", "60"))
CHECK_INTERVAL = 60  # segundos entre verificaciones
```

---

## 3. Flujo de Auto-Advance

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FLUJO DE AUTO-ADVANCE                          │
└─────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐
  │  batch_monitor  │
  │  (loop infinito)│
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐     ┌─────────────────┐
  │ Consultar DB    │────>│ Contar progreso │
  │ prodigy db-out  │     │ por anotador    │
  └─────────────────┘     └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ ¿N validadores  │
                          │ completaron?    │
                          └────────┬────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
              ┌──────────┐                  ┌──────────┐
              │   SÍ     │                  │   NO     │
              │ Avanzar  │                  │ Esperar  │
              │ lote     │                  │ 60s      │
              └─────┬────┘                  └──────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ 1. Detener      │
           │    Prodigy      │
           │ 2. Actualizar   │
           │    CURRENT_BATCH│
           │ 3. Reiniciar    │
           │    Prodigy      │
           └─────────────────┘
```

---

## 4. Verificación de Progreso

### 4.1 Consulta a Prodigy DB

```python
def get_batch_progress(annotation_type: str, batch_id: int) -> dict:
    """Obtiene el progreso de cada anotador en un lote."""
    dataset_name = f"guarani_{annotation_type}_batch_{batch_id:02d}"
    
    # Obtener anotaciones del dataset
    db = connect()
    examples = list(db.get_dataset_examples(dataset_name))
    
    # Contar por anotador
    progress = {}
    for ex in examples:
        session_id = ex.get("_session_id", "unknown")
        if session_id not in progress:
            progress[session_id] = {"completed": 0, "total": SENTENCES_PER_BATCH}
        
        if ex.get("answer") in ["accept", "reject"]:
            progress[session_id]["completed"] += 1
    
    return progress
```

### 4.2 Verificar Completitud

```python
def is_batch_complete(annotation_type: str, batch_id: int) -> bool:
    """Verifica si el lote está completo."""
    validators = get_validators(annotation_type)
    progress = get_batch_progress(annotation_type, batch_id)
    
    completed_validators = 0
    for validator in validators:
        if validator in progress:
            if progress[validator]["completed"] >= SENTENCES_PER_BATCH:
                completed_validators += 1
    
    return completed_validators >= REQUIRED_VALIDATORS
```

---

## 5. Avance de Lote

### 5.1 Proceso de Avance

```python
async def advance_batch(annotation_type: str):
    """Avanza al siguiente lote."""
    current = get_current_batch(annotation_type)
    next_batch = current + 1
    
    if next_batch > TOTAL_BATCHES:
        logger.info(f"[{annotation_type}] Todos los lotes completados!")
        return False
    
    logger.info(f"[{annotation_type}] Avanzando lote {current} → {next_batch}")
    
    # 1. Detener servicio actual
    await stop_prodigy_service(annotation_type)
    
    # 2. Actualizar lote actual
    set_current_batch(annotation_type, next_batch)
    
    # 3. Iniciar con nuevo lote
    await start_prodigy_service(annotation_type, next_batch)
    
    # 4. Notificar (opcional)
    await notify_batch_advance(annotation_type, current, next_batch)
    
    return True
```

### 5.2 Actualización de Estado

El estado se guarda en `data/batch_monitor_state.json`:

```python
def save_state():
    state = {
        "pos": {
            "current_batch": CURRENT_BATCH_POS,
            "completed_batches": list(completed_pos),
            "last_check": datetime.now().isoformat()
        },
        "features": {
            "current_batch": CURRENT_BATCH_FEATURES,
            "completed_batches": list(completed_features)
        },
        "relations": {
            "current_batch": CURRENT_BATCH_RELATIONS,
            "completed_batches": list(completed_relations)
        }
    }
    
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
```

---

## 6. Iniciar Batch Monitor

### 6.1 Script PowerShell

```powershell
# start_batch_auto.ps1

# Activar entorno
.\venv\Scripts\Activate.ps1

# Iniciar batch monitor en background
Start-Process -NoNewWindow python -ArgumentList "batch_monitor.py"

# O con logging
python batch_monitor.py 2>&1 | Tee-Object -FilePath logs/batch_monitor.log
```

### 6.2 Ejecución directa

```powershell
python batch_monitor.py
```

### 6.3 Verificar estado

```powershell
# Ver estado actual
Get-Content data/batch_monitor_state.json | ConvertFrom-Json | Format-List

# Ver logs
Get-Content logs/batch_monitor_*.log -Tail 50
```

---

## 7. API de Auto-Advance

El JWT Proxy expone endpoints para controlar el auto-advance:

### GET /api/auto-advance

```bash
curl http://localhost:8085/api/auto-advance \
  -H "Authorization: Bearer <TOKEN>"
```

**Response:**
```json
{
  "enabled": true,
  "check_interval": 60,
  "required_validators": 3,
  "status": {
    "pos": {"current_batch": 5, "validators_complete": 2},
    "features": {"current_batch": 3, "validators_complete": 3},
    "relations": {"current_batch": 1, "validators_complete": 0}
  }
}
```

### POST /api/auto-advance

```bash
# Activar/desactivar
curl -X POST http://localhost:8085/api/auto-advance \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### POST /api/advance-batch

Avanzar manualmente un lote:

```bash
curl -X POST http://localhost:8085/api/advance-batch \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"annotation_type": "pos"}'
```

---

## 8. Logs del Batch Monitor

### Formato de log

```
2025-01-15 10:30:00 | INFO | [MONITOR] Iniciando batch_monitor
2025-01-15 10:30:01 | INFO | [POS] Batch 5 - Progreso: alice=50, bob=45, carlos=50
2025-01-15 10:30:01 | INFO | [POS] Validadores completos: 2/3
2025-01-15 10:31:00 | INFO | [POS] Batch 5 - Progreso: alice=50, bob=50, carlos=50
2025-01-15 10:31:00 | INFO | [POS] ✅ Lote completo! Avanzando a batch 6
2025-01-15 10:31:02 | INFO | [POS] Servicio reiniciado en puerto 8080
```

### Ubicación de logs

```
logs/
├── batch_monitor_20250115_103000.log
├── batch_monitor_20250115_140000.log
└── ...
```

---

## 9. Manejo de Errores

### 9.1 Servicio no responde

```python
async def check_service_health(annotation_type: str) -> bool:
    try:
        port = PORTS[annotation_type]
        response = await http_client.get(f"http://localhost:{port}")
        return response.status_code == 200
    except:
        return False

# En el loop principal
if not await check_service_health(atype):
    logger.warning(f"[{atype}] Servicio no responde, reiniciando...")
    await restart_prodigy_service(atype)
```

### 9.2 Base de datos bloqueada

```python
def get_progress_with_retry(annotation_type: str, batch_id: int, retries: int = 3):
    for attempt in range(retries):
        try:
            return get_batch_progress(annotation_type, batch_id)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                raise
```

---

## 10. Configuración Avanzada

### Cambiar intervalo de verificación

```python
# batch_monitor.py
CHECK_INTERVAL = 30  # Verificar cada 30 segundos (default: 60)
```

### Cambiar validadores requeridos

```bash
# .env
REQUIRED_VALIDATORS=2  # Solo 2 de 3 deben completar
```

### Desactivar auto-advance

```bash
# .env
AUTO_ADVANCE_ENABLED=false
```

---

## 11. Siguiente Paso

Continúa con [12-PRODIGY-MANAGER.md](12-PRODIGY-MANAGER.md) para la gestión unificada de servicios.
