# 🏗️ Introducción y Arquitectura del Sistema

## 1. Visión General

El **Sistema de Anotación Guaraní** es una plataforma completa para la anotación lingüística de textos en Guaraní antiguo, basada en [Prodigy](https://prodi.gy/) con autenticación JWT y gestión multi-servicio.

### Objetivos del Sistema

1. **Anotación morfológica**: Etiquetar partes del discurso (POS), características morfológicas y relaciones sintácticas
2. **Control de acceso**: Autenticación segura mediante JWT tokens
3. **Trabajo colaborativo**: Múltiples anotadores trabajando en paralelo con cálculo de IAA
4. **Sistema por lotes**: 60 lotes de 50 oraciones (3000 total) para anotación estructurada

---

## 2. Componentes del Sistema

### 2.1 Frontend UI (Puerto 5173)

Aplicación React con Vite que proporciona:
- **Login de usuarios**: Autenticación contra el backend
- **Dashboard**: Vista del progreso de anotación
- **Selección de tareas**: Elegir tipo de anotación y lote

```
ui/
├── src/
│   ├── App.jsx          # Componente principal
│   ├── components/      # Componentes React
│   └── ...
├── package.json
└── vite.config.js
```

### 2.2 Backend API (Puerto 8000)

Servidor FastAPI que maneja:
- **Autenticación**: `/auth/login` - Genera JWT tokens
- **Usuarios**: `/users` - Gestión de anotadores
- **Validación**: Verifica tokens JWT

```
api/
├── app/
│   ├── main.py          # Punto de entrada FastAPI
│   ├── config.py        # Configuración
│   ├── database.py      # Conexión PostgreSQL
│   ├── api/
│   │   └── auth.py      # Endpoints de autenticación
│   └── models/          # Modelos SQLAlchemy
└── requirements.txt
```

### 2.3 JWT Proxy - Prodigy Manager (Puerto 8085)

Servidor proxy que actúa como gateway de autenticación:

- **Valida JWT tokens** contra el backend (puerto 8000)
- **Gestiona servicios Prodigy** (iniciar/detener)
- **Rutea requests** a la instancia Prodigy correcta
- **APIs de estado**: `/api/status`, `/api/batch-progress`

```python
# prodigy_manager.py - Arquitectura principal
┌─────────────────────────────────────────────────────────┐
│                   prodigy_manager.py                     │
│                     Puerto 8085                          │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ JWT Validation  │  │ Service Manager │              │
│  │ via Backend API │  │ Start/Stop      │              │
│  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                        │
│           ▼                    ▼                        │
│  ┌─────────────────────────────────────────┐           │
│  │           Proxy Router                   │           │
│  │   Route to: 8080 | 8081 | 8082          │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

### 2.4 Servicios Prodigy (Puertos 8080-8082)

Tres instancias Prodigy independientes:

| Puerto | Tipo | Recipe | Dataset |
|--------|------|--------|---------|
| **8080** | POS Tags | `guarani-batch pos` | `guarani_pos_batch_XX` |
| **8081** | Features | `guarani-batch features` | `guarani_features_batch_XX` |
| **8082** | Relations | `guarani-batch relations` | `guarani_relations_batch_XX` |

### 2.5 Batch Monitor (Auto-Advance)

Sistema que monitorea el progreso y avanza automáticamente al siguiente lote:

```python
# batch_monitor.py
- Monitorea anotaciones completadas
- Cuando N validadores completan un lote → avanza al siguiente
- Configurable: REQUIRED_VALIDATORS=3, SENTENCES_PER_BATCH=50
```

---

## 3. Flujo de Datos

### 3.1 Flujo de Autenticación

```
Usuario → Frontend (5173) → Backend (8000) → JWT Token
                                    ↓
                            JWT Proxy (8085)
                                    ↓
                            Prodigy (8080-8082)
```

### 3.2 Flujo de Anotación

```
1. Usuario selecciona tipo (POS/Features/Relations) y lote
2. JWT Proxy inicia servicio Prodigy correspondiente
3. Prodigy carga datos del lote desde data/batches/batch_XXX.jsonl
4. Usuario anota oraciones
5. Anotaciones se guardan en prodigy.db
6. Batch Monitor detecta completitud → avanza lote
```

---

## 4. Estructura de Directorios

```
prodigy/
├── prodigy_manager.py       # 🔐 JWT Proxy (8085)
├── batch_monitor.py         # 📊 Auto-advance system
├── .env                     # ⚙️ Variables de entorno
├── .env.example             # 📄 Plantilla de configuración
│
├── recipes/                 # 🍳 Recipes de Prodigy
│   ├── guarani_batch.py     # POS/Features/Relations por lotes
│   ├── guarani_spans.py     # Spans con overlapping
│   ├── guarani_relations.py # Relaciones sintácticas
│   └── guarani_openai.py    # Pre-anotación con IA
│
├── scripts/                 # 🛠️ Utilidades
│   ├── ud_guarani_mapper.py # Mapeo UD ↔ Amigable
│   ├── generate_batches.py  # Generar lotes
│   ├── export_to_json_with_iaa.py
│   └── calculate_iaa.py     # Inter-Annotator Agreement
│
├── data/
│   ├── batches/             # 📦 Lotes generados
│   │   ├── batch_001.jsonl
│   │   ├── batch_002.jsonl
│   │   └── ...
│   ├── prodigy_config.json  # Configuración buffer
│   └── batch_monitor_state.json
│
├── logs/                    # 📋 Logs del sistema
│
├── start_batch_all.ps1      # 🚀 Script inicio completo
├── start_batch_auto.ps1     # Script con auto-advance
└── docs/
    └── confluence/          # 📚 Esta documentación
```

---

## 5. Base de Datos

### 5.1 Prodigy DB (SQLite)

Prodigy utiliza SQLite para almacenar anotaciones:

```
~/.prodigy/prodigy.db
```

**Datasets creados automáticamente:**
- `guarani_pos_batch_01`, `guarani_pos_batch_02`, ...
- `guarani_features_batch_01`, `guarani_features_batch_02`, ...
- `guarani_relations_batch_01`, `guarani_relations_batch_02`, ...

### 5.2 Backend DB (PostgreSQL)

El backend usa PostgreSQL para usuarios:

```
- Tabla: users
- Campos: id, username, email, hashed_password, is_superuser, is_active
```

---

## 6. Tecnologías Utilizadas

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Anotación | Prodigy | 1.11+ |
| Backend API | FastAPI | 0.100+ |
| Frontend | React + Vite | 18.x |
| Base de datos | PostgreSQL + SQLite | 14+ |
| Proxy HTTP | httpx | 0.24+ |
| Tokenización | spaCy | 3.x |
| Autenticación | python-jose (JWT) | - |

---

## 7. Configuración por Defecto

```python
# Valores predeterminados del sistema
TOTAL_BATCHES = 60           # Número total de lotes
SENTENCES_PER_BATCH = 50     # Oraciones por lote
REQUIRED_VALIDATORS = 3      # Anotadores por tarea (IAA)
ANNOTATIONS_PER_TASK = 3     # Anotaciones por ejemplo
AUTO_SAVE_EVERY = 1          # Guardar cada N anotaciones
```

---

## 8. Diagrama de Secuencia

```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────┐
│ Usuario │     │ Frontend │     │ Backend │     │ JWT Proxy   │     │ Prodigy │
└────┬────┘     └────┬─────┘     └────┬────┘     └──────┬──────┘     └────┬────┘
     │               │                │                 │                 │
     │  1. Login     │                │                 │                 │
     │──────────────>│                │                 │                 │
     │               │  2. POST /auth │                 │                 │
     │               │───────────────>│                 │                 │
     │               │  3. JWT Token  │                 │                 │
     │               │<───────────────│                 │                 │
     │               │                │                 │                 │
     │  4. Seleccionar tarea          │                 │                 │
     │──────────────>│                │                 │                 │
     │               │  5. Redirect   │                 │                 │
     │               │   con token    │                 │                 │
     │               │────────────────────────────────>│                 │
     │               │                │                 │                 │
     │               │                │  6. Validar JWT │                 │
     │               │                │<────────────────│                 │
     │               │                │  7. OK/User     │                 │
     │               │                │────────────────>│                 │
     │               │                │                 │                 │
     │               │                │                 │ 8. Proxy request│
     │               │                │                 │────────────────>│
     │               │                │                 │                 │
     │               │                │                 │ 9. Prodigy UI   │
     │<──────────────────────────────────────────────────────────────────│
     │               │                │                 │                 │
```

---

## 9. Siguiente Paso

Continúa con [02-INSTALACION-SETUP.md](02-INSTALACION-SETUP.md) para configurar el sistema.
