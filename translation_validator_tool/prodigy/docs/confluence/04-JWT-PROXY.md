# 🔐 JWT Proxy (Puerto 8085)

El **JWT Proxy** (`prodigy_manager.py`) es el componente central de seguridad que actúa como gateway entre los usuarios y los servicios Prodigy.

---

## 1. Propósito

El JWT Proxy cumple tres funciones principales:

1. **Autenticación**: Valida tokens JWT contra el backend
2. **Gestión de servicios**: Inicia/detiene instancias Prodigy
3. **Proxy**: Rutea requests a la instancia Prodigy correcta

---

## 2. Arquitectura

```
                    ┌─────────────────────────────────────────┐
                    │         prodigy_manager.py              │
                    │              Puerto 8085                │
                    ├─────────────────────────────────────────┤
Usuario ──────────> │  1. Recibe request con JWT token       │
                    │  2. Valida token contra Backend (8000) │
                    │  3. Determina servicio destino         │
                    │  4. Proxy a Prodigy (8080-8082)        │
                    └──────────────────┬──────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
        ┌──────────┐            ┌──────────┐            ┌──────────┐
        │ Prodigy  │            │ Prodigy  │            │ Prodigy  │
        │   POS    │            │ Features │            │Relations │
        │  :8080   │            │  :8081   │            │  :8082   │
        └──────────┘            └──────────┘            └──────────┘
```

---

## 3. Endpoints de la API

### 3.1 Estado del Sistema

#### `GET /api/status`

Retorna el estado de todos los servicios Prodigy.

**Request:**
```bash
curl http://localhost:8085/api/status
```

**Response:**
```json
{
  "services": {
    "pos": {
      "running": true,
      "port": 8080,
      "batch": 1,
      "dataset": "guarani_pos_batch_01"
    },
    "features": {
      "running": true,
      "port": 8081,
      "batch": 1,
      "dataset": "guarani_features_batch_01"
    },
    "relations": {
      "running": false,
      "port": 8082,
      "batch": null,
      "dataset": null
    }
  },
  "proxy_port": 8085
}
```

### 3.2 Tipos de Anotación

#### `GET /api/types`

Lista los tipos de anotación disponibles.

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
    }
  ],
  "total_batches": 60,
  "sentences_per_batch": 50
}
```

### 3.3 Iniciar Servicio Prodigy

#### `POST /api/start-prodigy`

Inicia una instancia de Prodigy para un tipo de anotación.

**Request:**
```bash
curl -X POST http://localhost:8085/api/start-prodigy \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"annotation_type": "pos", "batch": 1}'
```

**Body:**
```json
{
  "annotation_type": "pos|features|relations",
  "batch": 1
}
```

**Response (éxito):**
```json
{
  "success": true,
  "message": "Servicio pos iniciado",
  "port": 8080,
  "dataset": "guarani_pos_batch_01"
}
```

### 3.4 Progreso de Lotes

#### `GET /api/batch-progress`

Obtiene el progreso de anotación por lote.

**Request:**
```bash
curl http://localhost:8085/api/batch-progress \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response:**
```json
{
  "pos": {
    "current_batch": 1,
    "completed_batches": 0,
    "annotators_progress": {
      "alice": {"completed": 25, "total": 50},
      "bob": {"completed": 50, "total": 50},
      "carlos": {"completed": 30, "total": 50}
    }
  },
  "features": {
    "current_batch": 1,
    "completed_batches": 0,
    "annotators_progress": {}
  },
  "relations": {
    "current_batch": 1,
    "completed_batches": 0,
    "annotators_progress": {}
  }
}
```

### 3.5 Control de Auto-Advance

#### `GET /api/auto-advance`

Obtiene el estado del sistema de auto-avance.

#### `POST /api/auto-advance`

Activa/desactiva el auto-avance.

```json
{
  "enabled": true
}
```

### 3.6 Configuración del Buffer

#### `GET /api/config/buffer`

Obtiene la configuración del buffer de anotaciones.

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

#### `POST /api/config/buffer`

Actualiza la configuración (solo admins).

```json
{
  "instant_submit": true,
  "batch_size": 1
}
```

---

## 4. Flujo de Autenticación

### 4.1 Validación de Token

```python
async def validate_jwt_token(token: str) -> Optional[dict]:
    """Valida JWT contra el backend."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()  # Usuario válido
        return None  # Token inválido
```

### 4.2 Obtención del Token

El proxy busca el token en este orden:

1. **Header Authorization:** `Authorization: Bearer <token>`
2. **Cookie:** `prodigy_token`
3. **Query parameter:** `?token=<token>`

```python
def get_token_from_request(request: Request) -> Optional[str]:
    # 1. Header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    
    # 2. Cookie
    token = request.cookies.get("prodigy_token")
    if token:
        return token
    
    # 3. Query param
    return request.query_params.get("token")
```

---

## 5. Proxy a Prodigy

### 5.1 Ruteo de Requests

```python
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_prodigy(request: Request, path: str = ""):
    # 1. Validar token
    token = get_token_from_request(request)
    user = await validate_jwt_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # 2. Determinar servicio destino
    service = request.query_params.get("service")
    if not service:
        service = request.cookies.get("prodigy_service")
    
    # 3. Obtener puerto del servicio
    target_state = prodigy_services.get(service)
    
    # 4. Proxy request
    url = f"http://127.0.0.1:{target_state.port}/{path}"
    response = await http_client.request(
        method=request.method,
        url=url,
        headers=request.headers,
        content=await request.body()
    )
    
    return Response(content=response.content)
```

### 5.2 Selección de Servicio

El servicio se determina por:

1. Query param: `?service=pos`
2. Cookie: `prodigy_service`
3. Primer servicio activo (fallback)

---

## 6. Gestión de Servicios Prodigy

### 6.1 Estado del Servicio

```python
@dataclass
class ProdigyServiceState:
    process: Optional[subprocess.Popen] = None
    port: int = 0
    batch: int = 0
    dataset: str = ""
    annotation_type: str = ""
```

### 6.2 Iniciar Servicio

```python
def start_prodigy_service(annotation_type: str, batch: int) -> bool:
    port = PORTS[annotation_type]
    dataset = f"guarani_{annotation_type}_batch_{batch:02d}"
    
    cmd = [
        "prodigy",
        "guarani-batch",
        annotation_type,
        str(batch),
        "-F", "recipes/guarani_batch.py",
        "--port", str(port)
    ]
    
    process = subprocess.Popen(cmd, ...)
    prodigy_services[annotation_type] = ProdigyServiceState(
        process=process,
        port=port,
        batch=batch,
        dataset=dataset
    )
    return True
```

### 6.3 Detener Servicio

```python
def stop_prodigy_service(annotation_type: str) -> bool:
    state = prodigy_services.get(annotation_type)
    if state and state.process:
        state.process.terminate()
        state.process.wait(timeout=5)
        prodigy_services[annotation_type] = ProdigyServiceState()
    return True
```

---

## 7. Páginas HTML Especiales

### 7.1 Página de Espera

Cuando no hay servicio activo:

```python
def get_waiting_page():
    return """
    <html>
    <head><title>Esperando...</title></head>
    <body>
        <h1>🕐 Esperando servicio Prodigy</h1>
        <p>El servicio está iniciando. Por favor espera...</p>
        <script>setTimeout(() => location.reload(), 3000);</script>
    </body>
    </html>
    """
```

### 7.2 Página de Error

Cuando el token es inválido:

```python
def get_error_page(title: str, message: str):
    return f"""
    <html>
    <head><title>{title}</title></head>
    <body>
        <h1>❌ {title}</h1>
        <p>{message}</p>
        <a href="http://localhost:5173">Volver al login</a>
    </body>
    </html>
    """
```

---

## 8. Configuración del Proxy

### Variables de entorno

```bash
BACKEND_URL=http://localhost:8000
PORT_PROXY=8085
PORT_POS=8080
PORT_FEATURES=8081
PORT_RELATIONS=8082
```

### Constantes en código

```python
# prodigy_manager.py
PORTS = {
    "pos": int(os.getenv("PORT_POS", "8080")),
    "features": int(os.getenv("PORT_FEATURES", "8081")),
    "relations": int(os.getenv("PORT_RELATIONS", "8082")),
}

PROXY_PORT = int(os.getenv("PORT_PROXY", "8085"))
```

---

## 9. Iniciar el Proxy

### Comando directo

```powershell
python prodigy_manager.py
```

### Con uvicorn

```powershell
uvicorn prodigy_manager:app --host 0.0.0.0 --port 8085 --reload
```

### Verificar funcionamiento

```powershell
# Verificar estado
curl http://localhost:8085/api/status

# Debe responder con JSON de estado de servicios
```

---

## 10. Logs del Proxy

Los logs se escriben en:
- **Consola:** Información de requests
- **Archivo:** `logs/prodigy_manager_YYYYMMDD.log`

Formato de log:
```
2025-01-15 10:30:45 | INFO | [AUTH] Usuario 'alice' autenticado
2025-01-15 10:30:45 | INFO | [PROXY] GET /project -> :8080
2025-01-15 10:30:46 | INFO | [SERVICE] Iniciando pos en puerto 8080
```

---

## 11. Siguiente Paso

Continúa con [05-FLUJO-AUTENTICACION.md](05-FLUJO-AUTENTICACION.md) para entender el flujo completo de autenticación.
