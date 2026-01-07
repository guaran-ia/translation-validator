# 🎛️ Prodigy Manager - Servidor Central

El archivo `prodigy_manager.py` es el **corazón del sistema de anotación**. Gestiona la autenticación JWT, el proxy a múltiples instancias de Prodigy, y la API de control.

---

## 1. Arquitectura del Manager

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRODIGY MANAGER (Puerto 8085)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      CAPA DE AUTENTICACIÓN                          │   │
│  │                                                                      │   │
│  │  • Extrae token JWT de: Cookie, Header Authorization, Query param   │   │
│  │  • Valida contra Backend API (/api/auth/me)                         │   │
│  │  • Cache de tokens validados (5 min TTL)                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      CAPA DE ROUTING/API                            │   │
│  │                                                                      │   │
│  │  /api/status           → Estado del sistema                         │   │
│  │  /api/types            → Tipos de anotación                         │   │
│  │  /api/services         → Servicios activos                          │   │
│  │  /api/start-prodigy    → Iniciar servicio                           │   │
│  │  /api/stop-prodigy/X   → Detener servicio                           │   │
│  │  /api/batch-progress/X → Progreso de batch                          │   │
│  │  /api/config/buffer    → Configuración buffer                       │   │
│  │  /*                    → Proxy a Prodigy interno                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    GESTIÓN DE SERVICIOS                              │   │
│  │                                                                      │   │
│  │  ProdigyServiceState (por cada tipo):                               │   │
│  │    • process (subprocess.Popen)                                     │   │
│  │    • port (8080/8081/8082)                                          │   │
│  │    • annotation_type                                                │   │
│  │    • batch (número)                                                 │   │
│  │    • config (diccionario)                                           │   │
│  │    • started_at (datetime)                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                    ┌───────────────┼───────────────┐                        │
│                    ▼               ▼               ▼                        │
│              ┌──────────┐   ┌──────────┐   ┌──────────┐                    │
│              │   POS    │   │ FEATURES │   │RELATIONS │                    │
│              │  :8080   │   │  :8081   │   │  :8082   │                    │
│              └──────────┘   └──────────┘   └──────────┘                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Clases Principales

### ProdigyServiceState

Estado de un servicio individual:

```python
class ProdigyServiceState:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None  # Proceso
        self.port: int = 8080                            # Puerto
        self.annotation_type: str = ""                   # Tipo (pos/features/relations)
        self.batch: int = 0                              # Número de batch
        self.config: Dict[str, Any] = {}                 # Configuración
        self.started_at: Optional[datetime] = None       # Inicio
        self.log_handle = None                           # Handle del log
```

### Estructura de Servicios

```python
# Puertos fijos por servicio
SERVICE_PORTS = {
    "pos": 8080,
    "features": 8081,
    "relations": 8082,
}

# Un estado por servicio
prodigy_services: Dict[str, ProdigyServiceState] = {
    "pos": ProdigyServiceState(),
    "features": ProdigyServiceState(),
    "relations": ProdigyServiceState(),
}
```

---

## 3. API Endpoints Detallados

### 3.1 Estado del Sistema

#### GET `/api/status`

Retorna el estado general del manager.

**Response:**
```json
{
  "authenticated": true,
  "user": "alice",
  "prodigy": {
    "running": true,
    "type": "pos",
    "port": 8080,
    "config": {...},
    "started_at": "2024-01-15T10:30:00"
  }
}
```

### 3.2 Tipos de Anotación

#### GET `/api/types`

Lista todos los tipos de anotación disponibles.

**Response:**
```json
{
  "types": [
    {
      "id": "batch-pos",
      "name": "POS Tags (Batch)",
      "description": "Etiquetado de partes del discurso por lotes",
      "icon": "🏷️",
      "color": "#3b82f6",
      "requires_batch": true
    },
    {
      "id": "batch-features",
      "name": "Features (Batch)",
      "description": "Características morfológicas por lotes",
      "icon": "⚙️",
      "color": "#10b981",
      "requires_batch": true
    },
    {
      "id": "batch-relations",
      "name": "Relations (Batch)",
      "description": "Dependencias sintácticas: arcos entre palabras",
      "icon": "🔗",
      "color": "#f59e0b",
      "requires_batch": true
    },
    {
      "id": "spans",
      "name": "Spans Manual",
      "description": "Anotación manual de spans morfológicos",
      "icon": "✏️",
      "color": "#8b5cf6",
      "requires_batch": false,
      "groups": ["pos-tags", "features", "morfemas"]
    },
    {
      "id": "openai",
      "name": "OpenAI Asistido",
      "description": "Pre-anotación automática con IA",
      "icon": "🤖",
      "color": "#ec4899",
      "requires_batch": false
    },
    {
      "id": "relations",
      "name": "Relations Manual",
      "description": "Anotación de dependencias sintácticas",
      "icon": "🌳",
      "color": "#06b6d4",
      "requires_batch": false
    }
  ],
  "total_batches": 60,
  "sentences_per_batch": 50
}
```

### 3.3 Servicios Activos

#### GET `/api/services`

Lista los servicios de Prodigy actualmente en ejecución.

**Response:**
```json
{
  "services": {
    "pos": {
      "running": true,
      "port": 8080,
      "batch": 15,
      "started_at": "2024-01-15T10:30:00"
    },
    "features": {
      "running": true,
      "port": 8081,
      "batch": 12,
      "started_at": "2024-01-15T10:30:05"
    },
    "relations": {
      "running": false
    }
  }
}
```

### 3.4 Control de Servicios

#### POST `/api/start-prodigy`

Inicia un servicio específico.

**Body:**
```json
{
  "annotation_type": "pos",
  "batch_number": 15
}
```

**Response:**
```json
{
  "success": true,
  "message": "Servicio pos iniciado para lote 15",
  "port": 8080,
  "service": "pos",
  "batch": 15,
  "url": "http://localhost:8085/?service=pos&session=alice"
}
```

#### POST `/api/stop-prodigy/{service}`

Detiene un servicio específico.

**Response:**
```json
{
  "success": true,
  "message": "Servicio pos detenido"
}
```

### 3.5 Progreso de Batch

#### GET `/api/batch-progress/{annotation_type}/{batch}`

Obtiene el progreso de anotaciones por sesión.

**Response:**
```json
{
  "dataset": "guarani_pos_batch_015",
  "batch": 15,
  "annotation_type": "pos",
  "progress": {
    "alice": 50,
    "bob": 48,
    "carlos": 45
  },
  "total_annotations": 143,
  "sentences_per_batch": 50
}
```

### 3.6 Estado de Todos los Batches

#### GET `/api/batch-status`

Usado por el batch monitor para obtener estado global.

**Response:**
```json
{
  "services": {
    "pos": {
      "running": true,
      "port": 8080,
      "batch": 15,
      "started_at": "2024-01-15T10:30:00",
      "config": {...}
    },
    "features": {...},
    "relations": {...}
  },
  "timestamp": "2024-01-15T12:45:00"
}
```

### 3.7 Auto-Avance de Batch

#### POST `/api/auto-advance/{annotation_type}`

Avanza automáticamente al siguiente batch. Usado por el batch_monitor.

**Response:**
```json
{
  "success": true,
  "message": "Batch 16 de pos iniciado",
  "previous_batch": 15,
  "current_batch": 16
}
```

### 3.8 Configuración del Buffer

#### GET `/api/config/buffer`

Obtiene la configuración actual del buffer.

**Response:**
```json
{
  "success": true,
  "config": {
    "instant_submit": false,
    "batch_size": 3
  },
  "defaults": {
    "instant_submit": false,
    "batch_size": 3
  }
}
```

#### POST `/api/config/buffer`

Actualiza la configuración (solo admin).

**Body:**
```json
{
  "instant_submit": true,
  "batch_size": 1
}
```

#### POST `/api/config/buffer/reset`

Restablece valores por defecto.

### 3.9 Validadores

#### GET `/api/validators`

Retorna la configuración de validadores por servicio.

**Response:**
```json
{
  "validators_by_service": {
    "pos": ["alice", "bob"],
    "features": ["carlos", "elena"],
    "relations": ["marcos", "nicolas"]
  },
  "all_validators": ["alice", "bob", "carlos", "elena", "marcos", "nicolas"],
  "services": ["pos", "features", "relations"]
}
```

---

## 4. Configuración de Servicios

### Generación de Configuración

```python
def get_prodigy_config_for_service(annotation_type: str, batch: int) -> dict:
    batch_str = str(batch).zfill(3)  # 001, 002, ...
    
    configs = {
        "pos": {
            "recipe": "guarani-batch",
            "dataset": f"guarani_pos_batch_{batch_str}",
            "recipe_file": "recipes/guarani_batch.py",
            "args": ["-t", "pos", "-l", str(batch)]
        },
        "features": {
            "recipe": "guarani-batch",
            "dataset": f"guarani_features_batch_{batch_str}",
            "recipe_file": "recipes/guarani_batch.py",
            "args": ["-t", "features", "-l", str(batch)]
        },
        "relations": {
            "recipe": "guarani-relations",
            "dataset": f"guarani_relations_batch_{batch_str}",
            "recipe_file": "recipes/guarani_relations.py",
            "source": f"data/batches/batch_{batch_str}.jsonl",
            "args": ["-l", "50"]
        },
    }
    return configs.get(annotation_type)
```

### Variables de Entorno para Prodigy

Cuando inicia un proceso Prodigy, el manager configura:

```python
env["PRODIGY_PORT"] = str(port)           # Puerto del servicio
env["PRODIGY_HOST"] = "127.0.0.1"         # Solo acceso local
env["PRODIGY_ALLOWED_SESSIONS"] = "..."   # Sesiones permitidas
```

---

## 5. Proxy a Prodigy

### Flujo del Proxy

```python
@app.api_route("/{path:path}", methods=["GET", "POST", ...])
async def proxy_to_prodigy(request: Request, path: str = ""):
    # 1. Validar token JWT
    token = get_token_from_request(request)
    user = await validate_jwt_token(token)
    
    if not user:
        return HTMLResponse(get_error_page(...))
    
    # 2. Determinar servicio destino
    service = request.query_params.get("service")
    target_state = prodigy_services.get(service)
    
    # 3. Proxy la request
    response = await http_client.request(
        method=request.method,
        url=f"http://127.0.0.1:{target_state.port}/{path}",
        ...
    )
    
    # 4. Setear cookie si token vino de URL
    if token_from_url:
        proxy_response.set_cookie("prodigy_token", token)
    
    return proxy_response
```

### Selección de Servicio

El proxy determina qué servicio usar en este orden:

1. **Query param**: `?service=pos`
2. **Cookie**: `prodigy_service`
3. **Primer servicio activo**

---

## 6. Gestión de Procesos

### Iniciar Proceso

```python
def start_prodigy_process_for_service(service_type, config, port, batch):
    cmd = [
        sys.executable, "-m", "prodigy",
        config["recipe"],
        config["dataset"],
    ]
    
    if "source" in config:
        cmd.append(str(source_path))
    
    cmd.extend(config.get("args", []))
    cmd.extend(["-F", str(recipe_path)])
    
    # Crear proceso
    state.process = subprocess.Popen(
        cmd,
        env=env,
        cwd=str(BASE_DIR),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )
    
    # Esperar inicio (hasta 15 segundos)
    for i in range(30):
        try:
            socket.connect(("127.0.0.1", port))
            return True  # Éxito
        except:
            time.sleep(0.5)
```

### Detener Proceso

```python
async def stop_service_internal(service_type: str):
    state = prodigy_services[service_type]
    
    if state.process:
        state.process.terminate()
        state.process.wait(timeout=5)
    
    if state.log_handle:
        state.log_handle.close()
    
    # Limpiar estado
    state.process = None
    state.batch = 0
```

### Logs de Servicios

Los logs se guardan en `logs/prodigy_{servicio}.log`:

```
logs/
├── prodigy_pos.log
├── prodigy_features.log
└── prodigy_relations.log
```

---

## 7. Páginas de Error

### Acceso Denegado

```python
def get_error_page(title, message, show_login=True):
    return f"""
    <html>
    <body>
        <div class="container">
            <h1>{title}</h1>
            <p>{message}</p>
            <a href="http://localhost:5173/login">Ir al Login</a>
        </div>
    </body>
    </html>
    """
```

### Prodigy No Iniciado

Cuando no hay servicios corriendo, muestra una página con instrucciones:

```python
def get_waiting_page():
    return """
    <html>
    <body>
        <div class="container">
            <h1>Prodigy Manager</h1>
            <p>Para comenzar, ve al Dashboard y selecciona el tipo de anotación.</p>
            <a href="http://localhost:5173/prodigy">Ir al Dashboard</a>
        </div>
    </body>
    </html>
    """
```

---

## 8. Configuración Persistente

### Archivo de Configuración

`data/prodigy_config.json`:

```json
{
  "instant_submit": false,
  "batch_size": 3
}
```

### Funciones de Carga/Guardado

```python
CONFIG_FILE = BASE_DIR / "data" / "prodigy_config.json"

def load_buffer_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_BUFFER_CONFIG

def save_buffer_config(config: dict) -> bool:
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    return True
```

---

## 9. Señales y Limpieza

### Manejo de Señales

```python
def main():
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(0)))
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)

def cleanup():
    """Detiene todos los servicios al cerrar"""
    loop = asyncio.new_event_loop()
    loop.run_until_complete(stop_all_services())
    loop.close()
```

---

## 10. Output de Inicio

Al iniciar el manager, muestra:

```
================================================================
  PRODIGY MANAGER
  Sistema de Anotación por Lotes con JWT
================================================================

  Puerto:      8085
  Backend:     http://localhost:8000

  PUERTOS DE SERVICIOS:
    POS          -> 8080
    FEATURES     -> 8081
    RELATIONS    -> 8082

  ACCESO:
    1. Login en http://localhost:5173
    2. Ir a Dashboard -> Prodigy
    3. Seleccionar lote y tipo de anotación
    4. Click en 'Iniciar Servicio'

  API Endpoints:
    GET  /api/status       - Estado del sistema
    GET  /api/services     - Servicios en ejecución
    GET  /api/types        - Tipos de anotación disponibles
    POST /api/start-prodigy - Iniciar servicio (batch)
    POST /api/stop-prodigy/{service} - Detener servicio

================================================================
```

---

## 11. Documentos Relacionados

- [04-JWT-PROXY.md](04-JWT-PROXY.md) - Funcionamiento del proxy JWT
- [05-FLUJO-AUTENTICACION.md](05-FLUJO-AUTENTICACION.md) - Flujo de autenticación
- [10-SISTEMA-BATCHES.md](10-SISTEMA-BATCHES.md) - Sistema de lotes
- [11-AUTO-ADVANCE.md](11-AUTO-ADVANCE.md) - Batch monitor y auto-avance
