# ⚙️ Variables de Entorno

Este documento describe todas las variables de configuración del sistema de anotación.

---

## 1. Archivo `.env`

El archivo `.env` debe estar en el directorio raíz de Prodigy:

```
prodigy/
├── .env              # ← Tu configuración
├── .env.example      # ← Plantilla de referencia
└── ...
```

---

## 2. Variables del Backend

### `BACKEND_URL`

URL del servidor backend de autenticación.

```bash
BACKEND_URL=http://localhost:8000
```

| Valor | Descripción |
|-------|-------------|
| `http://localhost:8000` | Desarrollo local |
| `https://api.tudominio.com` | Producción |

**Usado por:** `prodigy_manager.py` para validar JWT tokens.

---

## 3. Variables de Validadores

### `VALIDATORS_POS`, `VALIDATORS_FEATURES`, `VALIDATORS_RELATIONS`

Lista de usernames de anotadores para cada tipo de tarea.

```bash
VALIDATORS_POS=alice,bob,carlos
VALIDATORS_FEATURES=diana,elena,felipe
VALIDATORS_RELATIONS=gabriel,helena,ivan
```

**Formato:** Nombres separados por comas, sin espacios.

**Usado por:** 
- `batch_monitor.py` - Verificar quiénes han completado un lote
- Task routing - Distribuir tareas entre anotadores

---

## 4. Variables de Tareas

### `ANNOTATIONS_PER_TASK`

Número de anotadores requeridos por cada tarea (para IAA).

```bash
ANNOTATIONS_PER_TASK=3
```

| Valor | Descripción |
|-------|-------------|
| `1` | Sin IAA, una anotación por tarea |
| `2` | IAA básico, dos anotadores |
| `3` | IAA estándar (recomendado) |

### `ENABLE_TASK_ROUTING`

Activa/desactiva el enrutamiento de tareas entre anotadores.

```bash
ENABLE_TASK_ROUTING=true
```

| Valor | Comportamiento |
|-------|----------------|
| `true` | Cada tarea se asigna a N anotadores específicos |
| `false` | Cualquier anotador puede ver cualquier tarea |

---

## 5. Variables de Lotes

### `CURRENT_BATCH_POS`, `CURRENT_BATCH_FEATURES`, `CURRENT_BATCH_RELATIONS`

Lote actual para cada tipo de anotación.

```bash
CURRENT_BATCH_POS=1
CURRENT_BATCH_FEATURES=1
CURRENT_BATCH_RELATIONS=1
```

**Rango válido:** 1-60 (basado en `TOTAL_BATCHES`)

**Actualizado por:** `batch_monitor.py` cuando se completa un lote.

### `TOTAL_BATCHES`

Número total de lotes disponibles.

```bash
TOTAL_BATCHES=60
```

### `SENTENCES_PER_BATCH`

Oraciones por lote.

```bash
SENTENCES_PER_BATCH=50
```

---

## 6. Variables de Puertos

### Puertos de Servicios

```bash
PORT_POS=8080
PORT_FEATURES=8081
PORT_RELATIONS=8082
PORT_PROXY=8085
```

| Variable | Puerto | Servicio |
|----------|--------|----------|
| `PORT_POS` | 8080 | Prodigy POS Tags |
| `PORT_FEATURES` | 8081 | Prodigy Features |
| `PORT_RELATIONS` | 8082 | Prodigy Relations |
| `PORT_PROXY` | 8085 | JWT Proxy Manager |

**Importante:** Estos puertos deben estar libres antes de iniciar el sistema.

---

## 7. Variables de OpenAI (Opcional)

### `OPENAI_API_KEY`

API key de OpenAI para pre-anotación automática.

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Requerido por:** `guarani_openai.py` recipe.

### `OPENAI_MODEL`

Modelo de OpenAI a usar.

```bash
OPENAI_MODEL=gpt-4
```

| Valor | Descripción |
|-------|-------------|
| `gpt-4` | Mayor precisión, más lento |
| `gpt-3.5-turbo` | Más rápido, menor costo |

---

## 8. Variables de Configuración del Buffer

### `INSTANT_SUBMIT`

Si es `true`, envía cada anotación inmediatamente.

```bash
INSTANT_SUBMIT=false
```

| Valor | Comportamiento |
|-------|----------------|
| `true` | Cada anotación se guarda al instante |
| `false` | Las anotaciones se acumulan en buffer |

### `BATCH_SIZE`

Número de anotaciones en el buffer antes de guardar.

```bash
BATCH_SIZE=3
```

**Nota:** Solo aplica si `INSTANT_SUBMIT=false`.

---

## 9. Variables de Logging

### `LOG_LEVEL`

Nivel de detalle de los logs.

```bash
LOG_LEVEL=INFO
```

| Valor | Descripción |
|-------|-------------|
| `DEBUG` | Máximo detalle |
| `INFO` | Información general |
| `WARNING` | Solo advertencias |
| `ERROR` | Solo errores |

### `LOG_DIR`

Directorio para archivos de log.

```bash
LOG_DIR=./logs
```

---

## 10. Ejemplo Completo `.env`

```bash
# =============================================================================
# CONFIGURACIÓN DEL SISTEMA DE ANOTACIÓN PRODIGY - GUARANÍ CORPUS
# =============================================================================

# --- Backend API (Autenticación) ---
BACKEND_URL=http://localhost:8000

# --- Validadores por tipo de anotación ---
# Formato: usernames separados por coma
VALIDATORS_POS=alice,bob,carlos,diana
VALIDATORS_FEATURES=elena,felipe,gabriel,helena
VALIDATORS_RELATIONS=ivan,julia,kevin,laura

# --- Configuración de tareas IAA ---
ANNOTATIONS_PER_TASK=3
ENABLE_TASK_ROUTING=true

# --- Lotes actuales (actualizado automáticamente por batch_monitor) ---
CURRENT_BATCH_POS=1
CURRENT_BATCH_FEATURES=1
CURRENT_BATCH_RELATIONS=1

# --- Configuración de lotes ---
TOTAL_BATCHES=60
SENTENCES_PER_BATCH=50

# --- Puertos de servicios ---
PORT_POS=8080
PORT_FEATURES=8081
PORT_RELATIONS=8082
PORT_PROXY=8085

# --- Buffer de anotaciones ---
INSTANT_SUBMIT=false
BATCH_SIZE=3

# --- OpenAI (opcional) ---
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4

# --- Logging ---
LOG_LEVEL=INFO
LOG_DIR=./logs

# --- Base de datos Prodigy ---
# Prodigy usa ~/.prodigy/prodigy.db por defecto
# PRODIGY_HOME=./prodigy_data  # Descomentar para usar directorio personalizado
```

---

## 11. Variables de Entorno del Sistema

### Variables que Prodigy lee automáticamente

```bash
# Licencia de Prodigy
PRODIGY_KEY=XXXX-XXXX-XXXX-XXXX

# Directorio de datos de Prodigy
PRODIGY_HOME=~/.prodigy

# Puerto por defecto (sobrescrito por nuestros scripts)
PRODIGY_PORT=8080
```

---

## 12. Validación de Configuración

### Script de verificación

```powershell
# Verificar que todas las variables están configuradas
python -c "
from dotenv import load_dotenv
import os

load_dotenv()

required = [
    'BACKEND_URL',
    'VALIDATORS_POS',
    'VALIDATORS_FEATURES', 
    'VALIDATORS_RELATIONS',
]

missing = [v for v in required if not os.getenv(v)]
if missing:
    print(f'❌ Variables faltantes: {missing}')
else:
    print('✅ Todas las variables requeridas están configuradas')
"
```

---

## 13. Siguiente Paso

Continúa con [04-JWT-PROXY.md](04-JWT-PROXY.md) para entender el servidor proxy de autenticación.
