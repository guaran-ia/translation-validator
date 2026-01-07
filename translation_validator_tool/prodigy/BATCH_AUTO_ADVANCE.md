# 🔄 Sistema de Auto-Avance de Batches

Este sistema automatiza el proceso de anotación por batches, detectando cuando todos los validadores completan sus tareas e iniciando automáticamente el siguiente batch.

## ¿Qué hace?

Cuando **todos los validadores requeridos** completan sus **50 frases** del batch actual, el sistema:

1. ✅ Detecta automáticamente la completación
2. ⏹️ Detiene el batch actual de forma ordenada
3. ▶️ Inicia automáticamente el siguiente batch
4. 🔁 Continúa hasta completar los 60 batches (3000 oraciones)

## Inicio Rápido

```powershell
# En la carpeta prodigy/
.\start_batch_auto.ps1
```

Esto inicia:
- **Prodigy Manager** (puerto 8085) - Proxy y gestión de servicios
- **Batch Monitor** - Monitoreo y auto-avance
- **POS Service** (puerto 8080) - Etiquetado POS
- **Features Service** (puerto 8081) - Características morfológicas
- **Relations Service** (puerto 8082) - Relaciones sintácticas

## Opciones de Configuración

```powershell
# Empezar desde un batch específico
.\start_batch_auto.ps1 -Batch 5

# Cambiar número de validadores requeridos (default: 3)
.\start_batch_auto.ps1 -Validators 2

# Cambiar intervalo de chequeo (default: 60 segundos)
.\start_batch_auto.ps1 -Interval 30

# Sin el monitor (solo servicios)
.\start_batch_auto.ps1 -NoMonitor

# Ver ayuda
.\start_batch_auto.ps1 -Help

# Combinaciones
.\start_batch_auto.ps1 -Batch 10 -Validators 2 -Interval 45
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    BATCH AUTO-ADVANCE SYSTEM                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PRODIGY MANAGER (Puerto 8085)                            │   │
│  │  ├─ Proxy JWT seguro                                      │   │
│  │  ├─ API de gestión de servicios                           │   │
│  │  ├─ Endpoints de progreso (/api/batch-progress/...)       │   │
│  │  └─ Auto-advance endpoint (/api/auto-advance/...)         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  BATCH MONITOR (batch_monitor.py)                         │   │
│  │  ├─ Chequea progreso cada N segundos                      │   │
│  │  ├─ Consulta DB de Prodigy por anotaciones                │   │
│  │  ├─ Detecta cuando todos completan 50 frases              │   │
│  │  └─ Dispara auto-avance vía API                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│          ┌────────────────┼────────────────┐                     │
│          ▼                ▼                ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ POS (8080)  │  │ FEAT (8081) │  │ REL (8082)  │              │
│  │ Etiquetado  │  │ Morfología  │  │ Relaciones  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo de Trabajo

```
                    ┌─────────────────┐
                    │  BATCH 1 INICIO │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼              ▼              ▼
         ┌────────┐    ┌────────┐    ┌────────┐
         │ Alice  │    │  Bob   │    │ Carlos │
         │ 0/50   │    │ 0/50   │    │ 0/50   │
         └────────┘    └────────┘    └────────┘
              │              │              │
              │   (Anotando...)             │
              │              │              │
              ▼              ▼              ▼
         ┌────────┐    ┌────────┐    ┌────────┐
         │ Alice  │    │  Bob   │    │ Carlos │
         │ 50/50 ✓│    │ 50/50 ✓│    │ 50/50 ✓│
         └────────┘    └────────┘    └────────┘
                             │
              ┌──────────────┴──────────────┐
              │  MONITOR DETECTA COMPLETADO  │
              │  "3 validadores completaron" │
              └──────────────┬──────────────┘
                             │
                    ┌────────┴────────┐
                    │   AUTO-AVANCE   │
                    │ Detiene Batch 1 │
                    │ Inicia Batch 2  │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  BATCH 2 INICIO │
                    └─────────────────┘
```

## Variables de Entorno (.env)

```env
# =============================================================================
# BATCH AUTO-ADVANCE CONFIGURATION
# =============================================================================

# Intervalo de chequeo del monitor (segundos)
# Cada cuánto tiempo verificar si todos completaron el batch
BATCH_MONITOR_INTERVAL=60

# Número de validadores requeridos para considerar un batch completo
# Cuando N validadores completen sus 50 frases, se avanza al siguiente batch
REQUIRED_VALIDATORS=3

# Oraciones por batch
SENTENCES_PER_BATCH=50

# Total de batches disponibles (3000 oraciones / 50 = 60 batches)
TOTAL_BATCHES=60

# URL del Prodigy Manager (para el batch monitor)
PRODIGY_MANAGER_URL=http://localhost:8085
```

## Sesiones de Anotadores

Las sesiones permitidas son:
- `alice`
- `bob`
- `carlos`
- `diana`
- `elena`

### Acceso
```
http://localhost:8085/?session=<nombre>&token=<JWT>
```

Por ejemplo:
```
http://localhost:8085/?session=alice&token=eyJhbGci...
```

## Detener el Sistema

```powershell
# Opción 1: Script de detención
.\stop_batch_auto.ps1

# Opción 2: Ctrl+C en la terminal donde se ejecuta
```

## Scripts Individuales

### Batch Monitor (si ya tienes Prodigy corriendo)
```powershell
# Loop continuo
python batch_monitor.py --interval 30 --validators 2

# Chequeo único (sin loop)
python batch_monitor.py --check-once
```

### Ver estado actual
```powershell
# Consultar progreso vía API
curl http://localhost:8085/api/batch-progress/pos/1

# Ver todos los servicios
curl http://localhost:8085/api/batch-status
```

## API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/batch-progress/{type}/{batch}` | GET | Progreso de un batch específico |
| `/api/batch-status` | GET | Estado de todos los servicios |
| `/api/auto-advance/{type}` | POST | Avanzar al siguiente batch |
| `/api/services` | GET | Servicios en ejecución |
| `/api/start-prodigy` | POST | Iniciar servicio específico |
| `/api/stop-prodigy/{service}` | POST | Detener servicio específico |

## Logs y Estado

### Archivo de estado
```
prodigy/data/batch_monitor_state.json
```
Contiene el batch actual de cada tipo de anotación y el progreso.

### Log de completaciones
```
prodigy/logs/batch_completions.log
```
Registro histórico de batches completados.

### Logs de servicios
```
prodigy/logs/prodigy_pos.log
prodigy/logs/prodigy_features.log
prodigy/logs/prodigy_relations.log
```

## Troubleshooting

### El monitor no detecta anotaciones
1. Verificar que los anotadores usen el formato de sesión correcto (`?session=alice`)
2. Comprobar que las anotaciones se guardan (ver `AUTO_SAVE_EVERY` en .env)
3. Ejecutar manualmente: `python -m prodigy db-out guarani_pos_batch_001`

### Los servicios no inician
1. Verificar que los puertos 8080, 8081, 8082 estén libres
2. Revisar logs en `prodigy/logs/`
3. Asegurar que los archivos de batches existen en `data/batches/`

### El auto-avance no funciona
1. Verificar `REQUIRED_VALIDATORS` vs número de anotadores activos
2. Comprobar que todos tengan exactamente 50 anotaciones (accept/reject)
3. Revisar conexión al Prodigy Manager en `PRODIGY_MANAGER_URL`

## Estructura de Archivos

```
prodigy/
├── batch_monitor.py          # Monitor de progreso y auto-avance
├── prodigy_manager.py        # Proxy y gestión de servicios
├── start_batch_auto.ps1      # Script de inicio completo
├── stop_batch_auto.ps1       # Script de detención
├── .env                      # Configuración
├── data/
│   ├── batches/              # Archivos batch_001.jsonl ... batch_060.jsonl
│   │   └── batches_index.json
│   └── batch_monitor_state.json  # Estado persistente del monitor
├── logs/
│   ├── batch_completions.log
│   └── prodigy_*.log
└── recipes/
    └── guarani_batch.py      # Recipe de anotación por batches
```
