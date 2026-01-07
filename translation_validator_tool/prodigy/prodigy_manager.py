#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prodigy Manager - Servidor Proxy Unificado con JWT
==================================================
Gestiona múltiples instancias de Prodigy desde una sola interfaz.

Características:
- Proxy seguro con validación JWT en puerto 8085
- API para iniciar/detener diferentes tipos de anotación
- Soporta: Batch (POS/Features/Relations), OpenAI, Spans, Relations
- UI integrada para seleccionar qué anotar

Uso:
    python prodigy_manager.py
    python prodigy_manager.py --port 8085

Acceso:
    1. Login en http://localhost:5173 (UI principal)
    2. Ir a Dashboard -> Prodigy
    3. Seleccionar tipo de anotación
    4. Click en "Iniciar"
"""

import os
import sys
import json
import time
import signal
import socket
import asyncio
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

import httpx
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Cargar variables de entorno
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configuración
PROXY_PORT = int(os.getenv("PRODIGY_PROXY_PORT", 8085))
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BASE_DIR = Path(__file__).parent

# App FastAPI
app = FastAPI(title="Prodigy Manager - Proxy Seguro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente HTTP
http_client = httpx.AsyncClient(timeout=30.0)

# Puertos para cada tipo de servicio
SERVICE_PORTS = {
    "pos": 8080,
    "features": 8081,
    "relations": 8082,
}

# Usuarios permitidos por tipo de servicio (desde .env)
def parse_validators_list(env_var: str, default: str) -> list:
    """Parsea una lista de validadores desde variable de entorno"""
    value = os.getenv(env_var, default).strip('"').strip("'")
    return [v.strip() for v in value.split(",") if v.strip()]

SERVICE_VALIDATORS = {
    "pos": parse_validators_list("VALIDATORS_POS", "alice,bob"),
    "features": parse_validators_list("VALIDATORS_FEATURES", "carlos,elena"),
    "relations": parse_validators_list("VALIDATORS_RELATIONS", "marcos,nicolas"),
}

# Lista global de todas las sesiones permitidas
ALL_ALLOWED_SESSIONS = list(set(
    SERVICE_VALIDATORS["pos"] + 
    SERVICE_VALIDATORS["features"] + 
    SERVICE_VALIDATORS["relations"]
))

# Estado global para múltiples servicios
class ProdigyServiceState:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.port: int = 8080
        self.annotation_type: str = ""
        self.batch: int = 0
        self.config: Dict[str, Any] = {}
        self.started_at: Optional[datetime] = None
        self.log_handle = None

# Un estado por cada tipo de servicio
prodigy_services: Dict[str, ProdigyServiceState] = {
    "pos": ProdigyServiceState(),
    "features": ProdigyServiceState(),
    "relations": ProdigyServiceState(),
}

# Para compatibilidad con proxy single-service
prodigy_state = ProdigyServiceState()
validated_tokens: Dict[str, dict] = {}

# =============================================================================
# CONFIGURACIÓN DE BUFFER GLOBAL
# =============================================================================
# Archivo de configuración persistente
CONFIG_FILE = BASE_DIR / "data" / "prodigy_config.json"

# Configuración por defecto del buffer
DEFAULT_BUFFER_CONFIG = {
    "instant_submit": False,
    "batch_size": 3,
}

def load_buffer_config() -> dict:
    """Carga la configuración del buffer desde archivo"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Merge con defaults para asegurar todas las claves
                return {**DEFAULT_BUFFER_CONFIG, **config}
    except Exception as e:
        print(f"[CONFIG] Error cargando configuración: {e}")
    return DEFAULT_BUFFER_CONFIG.copy()

def save_buffer_config(config: dict) -> bool:
    """Guarda la configuración del buffer a archivo"""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"[CONFIG] Error guardando configuración: {e}")
        return False

# Cargar configuración al inicio
buffer_config: Dict[str, Any] = load_buffer_config()


# =============================================================================
# AUTENTICACIÓN JWT
# =============================================================================

async def validate_jwt_token(token: str) -> dict:
    """Valida un token JWT contra el backend"""
    if not token or token.count('.') != 2:
        return None
    
    # Cache
    if token in validated_tokens:
        cached = validated_tokens[token]
        if datetime.now() < cached.get("expires", datetime.min):
            return cached.get("user")
    
    try:
        response = await http_client.get(
            f"{BACKEND_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            user = response.json()
            validated_tokens[token] = {
                "user": user,
                "expires": datetime.now() + timedelta(minutes=5)
            }
            return user
    except Exception as e:
        print(f"[AUTH] Error validando token: {e}")
    
    return None


def get_token_from_request(request: Request) -> Optional[str]:
    """Extrae el token JWT de la request"""
    # 1. Cookie
    token = request.cookies.get("prodigy_token")
    if token:
        return token
    
    # 2. Header Authorization
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    
    # 3. Query param
    token = request.query_params.get("token")
    if token:
        return token
    
    return None


def get_error_page(title: str, message: str, show_login: bool = True) -> str:
    """Genera página HTML de error"""
    login_button = ""
    if show_login:
        login_button = '<a href="http://localhost:5173/login" class="btn">Ir al Login</a>'
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Prodigy - {title}</title>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 500px;
            }}
            h1 {{ color: #dc2626; margin-bottom: 15px; font-size: 24px; }}
            p {{ color: #555; line-height: 1.6; margin-bottom: 25px; }}
            .btn {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s;
            }}
            .btn:hover {{ transform: scale(1.05); box-shadow: 0 4px 15px rgba(59,130,246,0.4); }}
            .icon {{ font-size: 48px; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">🔒</div>
            <h1>{title}</h1>
            <p>{message}</p>
            {login_button}
        </div>
    </body>
    </html>
    """


# =============================================================================
# API DE GESTIÓN
# =============================================================================

@app.get("/api/validators")
async def get_validators_config():
    """Retorna la configuración de validadores por tipo de servicio"""
    return {
        "validators_by_service": SERVICE_VALIDATORS,
        "all_validators": ALL_ALLOWED_SESSIONS,
        "services": list(SERVICE_VALIDATORS.keys()),
    }


@app.get("/api/status")
async def get_status(request: Request):
    """Estado del sistema"""
    token = get_token_from_request(request)
    user = await validate_jwt_token(token) if token else None
    
    return {
        "authenticated": user is not None,
        "user": user.get("username") if user else None,
        "prodigy": {
            "running": prodigy_state.process is not None and prodigy_state.process.poll() is None,
            "type": prodigy_state.annotation_type,
            "port": prodigy_state.port,
            "config": prodigy_state.config,
            "started_at": prodigy_state.started_at.isoformat() if prodigy_state.started_at else None
        }
    }


# =============================================================================
# API DE PROGRESO PARA BATCH MONITOR
# =============================================================================

@app.get("/api/batch-progress/{annotation_type}/{batch}")
async def get_batch_progress(annotation_type: str, batch: int, request: Request):
    """
    Obtiene el progreso de anotaciones para un batch específico.
    
    Retorna el número de anotaciones por sesión/anotador.
    """
    token = get_token_from_request(request)
    # Permitir acceso interno del monitor sin token válido
    is_internal = token == "internal-monitor"
    user = await validate_jwt_token(token) if token and not is_internal else None
    
    if not user and not is_internal:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    batch_str = str(batch).zfill(3)
    dataset_name = f"guarani_{annotation_type}_batch_{batch_str}"
    
    try:
        # Obtener anotaciones desde la DB de Prodigy
        result = subprocess.run(
            [sys.executable, "-m", "prodigy", "db-out", dataset_name],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR),
            timeout=30,
        )
        
        if result.returncode != 0:
            return {
                "dataset": dataset_name,
                "batch": batch,
                "annotation_type": annotation_type,
                "progress": {},
                "total_annotations": 0,
                "error": "Dataset no existe o está vacío"
            }
        
        # Contar anotaciones por sesión
        counts = {}
        total = 0
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                annotation = json.loads(line)
                session_id = annotation.get("_session_id", "default")
                answer = annotation.get("answer", "")
                
                if answer in ["accept", "reject"]:
                    counts[session_id] = counts.get(session_id, 0) + 1
                    total += 1
            except json.JSONDecodeError:
                continue
        
        return {
            "dataset": dataset_name,
            "batch": batch,
            "annotation_type": annotation_type,
            "progress": counts,
            "total_annotations": total,
            "sentences_per_batch": 50,
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Timeout obteniendo anotaciones")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch-status")
async def get_all_batch_status(request: Request):
    """
    Obtiene el estado de todos los servicios de batch actuales.
    Incluye información de progreso para el batch monitor.
    """
    token = get_token_from_request(request)
    is_internal = token == "internal-monitor"
    user = await validate_jwt_token(token) if token and not is_internal else None
    
    if not user and not is_internal:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    status = {}
    
    for service_type, state in prodigy_services.items():
        is_running = state.process and state.process.poll() is None
        
        status[service_type] = {
            "running": is_running,
            "port": state.port if is_running else None,
            "batch": state.batch if is_running else None,
            "started_at": state.started_at.isoformat() if state.started_at else None,
            "config": state.config if is_running else None,
        }
    
    return {
        "services": status,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/auto-advance/{annotation_type}")
async def auto_advance_batch(annotation_type: str, request: Request):
    """
    Avanza automáticamente al siguiente batch.
    Usado por el batch_monitor cuando se completa un batch.
    """
    token = get_token_from_request(request)
    is_internal = token == "internal-monitor"
    user = await validate_jwt_token(token) if token and not is_internal else None
    
    if not user and not is_internal:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    if annotation_type not in SERVICE_PORTS:
        raise HTTPException(status_code=400, detail=f"Tipo de anotación desconocido: {annotation_type}")
    
    # Obtener batch actual
    state = prodigy_services.get(annotation_type)
    current_batch = state.batch if state else 1
    next_batch = current_batch + 1
    
    if next_batch > 60:  # Máximo de batches
        return {
            "success": False,
            "message": f"Todos los batches de {annotation_type} completados",
            "current_batch": current_batch,
            "next_batch": None,
        }
    
    # Detener servicio actual
    await stop_service_internal(annotation_type)
    await asyncio.sleep(2)
    
    # Iniciar siguiente batch
    port = SERVICE_PORTS[annotation_type]
    config = get_prodigy_config_for_service(annotation_type, next_batch)
    success = start_prodigy_process_for_service(annotation_type, config, port, next_batch)
    
    if success:
        return {
            "success": True,
            "message": f"Batch {next_batch} de {annotation_type} iniciado",
            "previous_batch": current_batch,
            "current_batch": next_batch,
        }
    else:
        raise HTTPException(
            status_code=500, 
            detail=f"Error iniciando batch {next_batch}"
        )


@app.post("/api/start")
async def start_prodigy(request: Request):
    """Inicia una instancia de Prodigy"""
    token = get_token_from_request(request)
    user = await validate_jwt_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    body = await request.json()
    annotation_type = body.get("type", "batch-pos")
    batch = body.get("batch", 1)
    group = body.get("group", "")
    limit = body.get("limit", 100)
    
    # Detener instancia anterior si existe
    await stop_prodigy_internal()
    
    # Encontrar puerto libre
    port = find_free_port(8080)
    if not port:
        raise HTTPException(status_code=500, detail="No hay puertos disponibles")
    
    # Configurar según tipo
    config = get_prodigy_config(annotation_type, batch, group, limit)
    
    # Iniciar Prodigy
    success = start_prodigy_process(config, port)
    
    if success:
        prodigy_state.port = port
        prodigy_state.type = annotation_type
        prodigy_state.config = config
        prodigy_state.started_at = datetime.now()
        
        return {
            "success": True,
            "message": f"Prodigy iniciado: {annotation_type}",
            "port": port,
            "url": f"http://localhost:{PROXY_PORT}/?session={user.get('username', 'default')}"
        }
    else:
        raise HTTPException(status_code=500, detail="Error iniciando Prodigy")


@app.post("/api/stop")
async def stop_prodigy(request: Request):
    """Detiene la instancia de Prodigy"""
    token = get_token_from_request(request)
    user = await validate_jwt_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    await stop_prodigy_internal()
    
    return {"success": True, "message": "Prodigy detenido"}


@app.get("/api/services")
async def get_running_services(request: Request):
    """Lista los servicios de Prodigy en ejecución"""
    token = get_token_from_request(request)
    user = await validate_jwt_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    services = {}
    for service_type, state in prodigy_services.items():
        if state.process and state.process.poll() is None:
            services[service_type] = {
                "running": True,
                "port": state.port,
                "batch": state.batch,
                "started_at": state.started_at.isoformat() if state.started_at else None,
            }
    
    return {"services": services}


@app.post("/api/stop-prodigy/{service}")
async def stop_specific_service(service: str, request: Request):
    """Detiene un servicio específico de Prodigy"""
    token = get_token_from_request(request)
    is_internal = token == "internal-monitor"
    user = await validate_jwt_token(token) if token and not is_internal else None
    
    if not user and not is_internal:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    if service not in prodigy_services:
        raise HTTPException(status_code=400, detail=f"Servicio desconocido: {service}")
    
    await stop_service_internal(service)
    
    return {"success": True, "message": f"Servicio {service} detenido"}


@app.post("/api/start-prodigy")
async def start_prodigy_service(request: Request):
    """Inicia un servicio específico de Prodigy (para la UI)"""
    token = get_token_from_request(request)
    is_internal = token == "internal-monitor"
    user = await validate_jwt_token(token) if token and not is_internal else None
    
    if not user and not is_internal:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    body = await request.json()
    recipe = body.get("recipe", "batch")
    annotation_type = body.get("annotation_type", "pos")  # pos, features, relations
    batch_number = body.get("batch_number", 1)
    
    # Validar tipo de anotación
    if annotation_type not in SERVICE_PORTS:
        raise HTTPException(status_code=400, detail=f"Tipo de anotación desconocido: {annotation_type}")
    
    # Detener servicio anterior del mismo tipo si existe
    await stop_service_internal(annotation_type)
    
    # Puerto fijo por tipo
    port = SERVICE_PORTS[annotation_type]
    
    # Verificar que el puerto esté libre
    if not is_port_free(port):
        raise HTTPException(status_code=409, detail=f"Puerto {port} ya está en uso")
    
    # Configurar según tipo
    config = get_prodigy_config_for_service(annotation_type, batch_number)
    
    # Iniciar Prodigy
    success = start_prodigy_process_for_service(annotation_type, config, port, batch_number)
    
    if success:
        session_name = user.get('username', 'default') if user else 'system'
        return {
            "success": True,
            "message": f"Servicio {annotation_type} iniciado para lote {batch_number}",
            "port": port,
            "service": annotation_type,
            "batch": batch_number,
            "url": f"http://localhost:{PROXY_PORT}/?service={annotation_type}&session={session_name}"
        }
    else:
        raise HTTPException(status_code=500, detail=f"Error iniciando servicio {annotation_type}")


@app.get("/api/types")
async def get_annotation_types():
    """Lista los tipos de anotación disponibles"""
    return {
        "types": [
            {
                "id": "batch-pos",
                "name": "POS Tags (Batch)",
                "description": "Etiquetado de partes del discurso por lotes",
                "icon": "🏷️",
                "color": "#3b82f6",
                "requires_batch": True
            },
            {
                "id": "batch-features",
                "name": "Features (Batch)",
                "description": "Características morfológicas por lotes",
                "icon": "⚙️",
                "color": "#10b981",
                "requires_batch": True
            },
            {
                "id": "batch-relations",
                "name": "Relations (Batch)",
                "description": "Dependencias sintácticas: arcos entre palabras",
                "icon": "🔗",
                "color": "#f59e0b",
                "requires_batch": True
            },
            {
                "id": "spans",
                "name": "Spans Manual",
                "description": "Anotación manual de spans morfológicos",
                "icon": "✏️",
                "color": "#8b5cf6",
                "requires_batch": False,
                "groups": ["pos-tags", "features", "morfemas"]
            },
            {
                "id": "openai",
                "name": "OpenAI Asistido",
                "description": "Pre-anotación automática con IA",
                "icon": "🤖",
                "color": "#ec4899",
                "requires_batch": False,
                "groups": ["pos-tags", "features", "morfemas"]
            },
            {
                "id": "relations",
                "name": "Relations Manual",
                "description": "Anotación de dependencias sintácticas",
                "icon": "🌳",
                "color": "#06b6d4",
                "requires_batch": False,
                "groups": ["relations", "pos-tags"]
            }
        ],
        "total_batches": 60,
        "sentences_per_batch": 50
    }


# =============================================================================
# API DE CONFIGURACIÓN DE BUFFER
# =============================================================================

@app.get("/api/config/buffer")
async def get_buffer_config(request: Request):
    """
    Obtiene la configuración actual del buffer de anotaciones.
    Accesible para cualquier usuario autenticado.
    """
    token = get_token_from_request(request)
    user = await validate_jwt_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    return {
        "success": True,
        "config": buffer_config,
        "defaults": DEFAULT_BUFFER_CONFIG,
    }


@app.post("/api/config/buffer")
async def update_buffer_config(request: Request):
    """
    Actualiza la configuración del buffer de anotaciones.
    Solo accesible para administradores (is_superuser).
    
    Body esperado:
    {
        "instant_submit": true/false,
        "batch_size": 1-20
    }
    """
    global buffer_config
    
    token = get_token_from_request(request)
    user = await validate_jwt_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # Solo admins pueden cambiar configuración
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="Solo administradores pueden modificar la configuración")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="JSON inválido")
    
    # Validar y actualizar campos
    new_config = buffer_config.copy()
    
    if "instant_submit" in body:
        new_config["instant_submit"] = bool(body["instant_submit"])
    
    if "batch_size" in body:
        batch_size = int(body["batch_size"])
        if batch_size < 1 or batch_size > 20:
            raise HTTPException(status_code=400, detail="batch_size debe estar entre 1 y 20")
        new_config["batch_size"] = batch_size
    
    # Guardar a archivo
    if save_buffer_config(new_config):
        buffer_config = new_config
        return {
            "success": True,
            "message": "Configuración actualizada",
            "config": buffer_config,
        }
    else:
        raise HTTPException(status_code=500, detail="Error guardando configuración")


@app.post("/api/config/buffer/reset")
async def reset_buffer_config(request: Request):
    """
    Restablece la configuración del buffer a valores por defecto.
    Solo accesible para administradores.
    """
    global buffer_config
    
    token = get_token_from_request(request)
    user = await validate_jwt_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="Solo administradores pueden modificar la configuración")
    
    buffer_config = DEFAULT_BUFFER_CONFIG.copy()
    save_buffer_config(buffer_config)
    
    return {
        "success": True,
        "message": "Configuración restablecida a valores por defecto",
        "config": buffer_config,
    }


# =============================================================================
# PROXY A PRODIGY
# =============================================================================

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_prodigy(request: Request, path: str = ""):
    """Proxy todas las requests a Prodigy interno"""
    
    # Rutas de API no requieren autenticación para OPTIONS
    if request.method == "OPTIONS":
        return Response(status_code=200)
    
    # Rutas de API del manager
    if path.startswith("api/"):
        return Response(status_code=404)
    
    # Validar token
    token = get_token_from_request(request)
    token_from_url = request.query_params.get("token")  # Track if token came from URL
    user = await validate_jwt_token(token)
    
    if not user:
        # Si es una request de página, mostrar error HTML
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return HTMLResponse(
                content=get_error_page(
                    "Acceso Denegado",
                    "Necesitas iniciar sesión para acceder a Prodigy."
                ),
                status_code=401
            )
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # Flag para setear cookie si el token vino de la URL
    should_set_cookie = bool(token_from_url)
    
    # Determinar qué servicio usar basado en query param o cookie
    service = request.query_params.get("service")
    if not service:
        service = request.cookies.get("prodigy_service")
    if not service:
        # Por defecto usar el primer servicio activo
        for svc_type, state in prodigy_services.items():
            if state.process and state.process.poll() is None:
                service = svc_type
                break
    
    # Verificar que hay un servicio corriendo
    target_state = prodigy_services.get(service) if service else None
    
    if not target_state or not target_state.process or target_state.process.poll() is not None:
        # Fallback: buscar cualquier servicio activo
        target_state = None
        for svc_type, state in prodigy_services.items():
            if state.process and state.process.poll() is None:
                target_state = state
                break
        
        if not target_state:
            accept = request.headers.get("accept", "")
            if "text/html" in accept:
                return HTMLResponse(
                    content=get_waiting_page(),
                    status_code=200
                )
            raise HTTPException(status_code=503, detail="Ningún servicio de Prodigy está corriendo")
    
    # Proxy a Prodigy
    try:
        # Limpiar query params de autenticación antes de pasar a Prodigy
        query_params = dict(request.query_params)
        query_params.pop("token", None)
        query_params.pop("service", None)
        
        url = f"http://127.0.0.1:{target_state.port}/{path}"
        if query_params:
            query_str = "&".join(f"{k}={v}" for k, v in query_params.items())
            url += f"?{query_str}"
        
        body = await request.body()
        
        response = await http_client.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers.items() 
                    if k.lower() not in ["host", "connection"]},
            content=body if body else None,
        )
        
        # Copiar headers de respuesta
        headers = dict(response.headers)
        headers.pop("transfer-encoding", None)
        headers.pop("content-encoding", None)
        
        # Crear respuesta
        proxy_response = Response(
            content=response.content,
            status_code=response.status_code,
            headers=headers,
            media_type=response.headers.get("content-type")
        )
        
        # Si el token vino de la URL, setearlo como cookie para requests futuras
        if should_set_cookie and token:
            proxy_response.set_cookie(
                key="prodigy_token",
                value=token,
                httponly=True,
                max_age=86400,  # 24 horas
                samesite="lax",
                path="/"
            )
            # También guardar el servicio seleccionado
            service_from_url = request.query_params.get("service")
            if service_from_url:
                proxy_response.set_cookie(
                    key="prodigy_service",
                    value=service_from_url,
                    httponly=True,
                    max_age=86400,
                    samesite="lax",
                    path="/"
                )
        
        return proxy_response
        
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Prodigy no responde")
    except Exception as e:
        print(f"[PROXY] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_waiting_page() -> str:
    """Página cuando Prodigy no está iniciado"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Prodigy - Seleccionar Anotación</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: rgba(255,255,255,0.95);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 600px;
                width: 100%;
            }
            h1 {
                color: #1e3a5f;
                margin-bottom: 10px;
                font-size: 2em;
            }
            .subtitle {
                color: #64748b;
                margin-bottom: 30px;
            }
            .info-box {
                background: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }
            .info-box h3 {
                color: #0369a1;
                margin-bottom: 10px;
            }
            .info-box p {
                color: #0c4a6e;
                line-height: 1.6;
            }
            .btn {
                display: inline-block;
                padding: 14px 32px;
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 1.1em;
                transition: all 0.3s;
                margin-top: 10px;
            }
            .btn:hover {
                transform: scale(1.05);
                box-shadow: 0 8px 25px rgba(59,130,246,0.4);
            }
            .icon { font-size: 64px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">📝</div>
            <h1>Prodigy Manager</h1>
            <p class="subtitle">Sistema de Anotación del Corpus Guaraní</p>
            
            <div class="info-box">
                <h3>🚀 Cómo empezar</h3>
                <p>
                    Para comenzar a anotar, ve al <strong>Dashboard</strong> de la aplicación
                    y selecciona el tipo de anotación que deseas realizar.
                </p>
            </div>
            
            <a href="http://localhost:5173/prodigy" class="btn">
                Ir al Dashboard ->
            </a>
        </div>
    </body>
    </html>
    """


# =============================================================================
# GESTIÓN DE PROCESOS
# =============================================================================

def find_free_port(start: int = 8080) -> Optional[int]:
    """Encuentra un puerto libre"""
    for port in range(start, start + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return None


def is_port_free(port: int) -> bool:
    """Verifica si un puerto está libre"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False


def get_prodigy_config_for_service(annotation_type: str, batch: int) -> dict:
    """Genera la configuración para iniciar un servicio específico"""
    batch_str = str(batch).zfill(3)  # 3 dígitos: 001, 002, etc.
    
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
            "args": ["-l", "50"]  # 50 oraciones por lote
        },
    }
    
    return configs.get(annotation_type, configs["pos"])


def start_prodigy_process_for_service(service_type: str, config: dict, port: int, batch: int) -> bool:
    """Inicia el proceso de Prodigy para un servicio específico"""
    global prodigy_services
    
    state = prodigy_services[service_type]
    recipe_path = BASE_DIR / config["recipe_file"]
    
    cmd = [
        sys.executable, "-m", "prodigy",
        config["recipe"],
        config["dataset"],
    ]
    
    # Agregar source si existe (para recipes que requieren archivo de entrada)
    if "source" in config:
        source_path = BASE_DIR / config["source"]
        cmd.append(str(source_path.resolve()))
    
    # Agregar argumentos adicionales
    cmd.extend(config.get("args", []))
    
    # Agregar recipe file
    cmd.extend(["-F", str(recipe_path.resolve())])
    
    print(f"[PRODIGY-{service_type.upper()}] Comando: {' '.join(cmd)}")
    
    env = os.environ.copy()
    env["PRODIGY_PORT"] = str(port)
    env["PRODIGY_HOST"] = "127.0.0.1"
    
    # Configurar sesiones permitidas para este tipo de servicio
    allowed_sessions = SERVICE_VALIDATORS.get(service_type, ALL_ALLOWED_SESSIONS)
    env["PRODIGY_ALLOWED_SESSIONS"] = ",".join(allowed_sessions)
    print(f"[PRODIGY-{service_type.upper()}] Sesiones permitidas: {allowed_sessions}")
    
    try:
        # Crear archivo de log para este servicio
        log_dir = BASE_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"prodigy_{service_type}.log"
        
        # Abrir archivo de log
        log_handle = open(log_file, "w", encoding="utf-8")
        
        state.process = subprocess.Popen(
            cmd,
            env=env,
            cwd=str(BASE_DIR),
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        
        # Guardar handle del log para cerrar después
        state.log_handle = log_handle
        
        # Esperar a que inicie
        print(f"[PRODIGY-{service_type.upper()}] Esperando inicio...")
        time.sleep(4)
        
        for i in range(30):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(("127.0.0.1", port))
                    print(f"[PRODIGY-{service_type.upper()}] OK - Iniciado en puerto {port}")
                    state.port = port
                    state.annotation_type = service_type
                    state.batch = batch
                    state.config = config
                    state.started_at = datetime.now()
                    return True
            except:
                # Verificar si el proceso sigue vivo
                if state.process.poll() is not None:
                    print(f"[PRODIGY-{service_type.upper()}] ERROR - Proceso termino inesperadamente")
                    # Leer log para debug
                    try:
                        log_handle.flush()
                        with open(log_file, "r", encoding="utf-8") as f:
                            log_content = f.read()
                            if log_content:
                                print(f"[PRODIGY-{service_type.upper()}] Log: {log_content[:500]}")
                    except:
                        pass
                    return False
                time.sleep(0.5)
        
        print(f"[PRODIGY-{service_type.upper()}] ERROR - Timeout esperando inicio")
        return False
        
    except Exception as e:
        print(f"[PRODIGY-{service_type.upper()}] Error: {e}")
        return False


async def stop_service_internal(service_type: str):
    """Detiene un servicio específico de Prodigy"""
    global prodigy_services
    
    if service_type not in prodigy_services:
        return
    
    state = prodigy_services[service_type]
    
    if state.process:
        try:
            state.process.terminate()
            state.process.wait(timeout=5)
        except:
            state.process.kill()
        
        # Cerrar log handle si existe
        if state.log_handle:
            try:
                state.log_handle.close()
            except:
                pass
            state.log_handle = None
        
        state.process = None
        state.annotation_type = ""
        state.batch = 0
        state.config = {}
        state.started_at = None
        print(f"[PRODIGY-{service_type.upper()}] Detenido")


def get_prodigy_config(annotation_type: str, batch: int, group: str, limit: int) -> dict:
    """Genera la configuración para iniciar Prodigy"""
    
    batch_str = str(batch).zfill(3)  # 3 dígitos: 001, 002, etc.
    
    configs = {
        "batch-pos": {
            "recipe": "guarani-batch",
            "dataset": f"guarani_pos_batch_{batch_str}",
            "recipe_file": "recipes/guarani_batch.py",
            "args": ["-t", "pos", "-l", str(batch)]
        },
        "batch-features": {
            "recipe": "guarani-batch",
            "dataset": f"guarani_features_batch_{batch_str}",
            "recipe_file": "recipes/guarani_batch.py",
            "args": ["-t", "features", "-l", str(batch)]
        },
        "batch-relations": {
            "recipe": "guarani-relations",
            "dataset": f"guarani_relations_batch_{batch_str}",
            "recipe_file": "recipes/guarani_relations.py",
            "source": f"data/batches/batch_{batch_str}.jsonl",
            "args": ["-l", "50"]
        },
        "spans": {
            "recipe": "guarani-spans",
            "dataset": f"guarani_spans_{group or 'all'}",
            "recipe_file": "recipes/guarani_spans.py",
            "source": "data/export/original_translations.jsonl",
            "args": ["-g", group] if group else []
        },
        "openai": {
            "recipe": "guarani-openai",
            "dataset": f"guarani_openai_{group or 'all'}",
            "recipe_file": "recipes/guarani_openai.py",
            "source": "data/export/original_translations.jsonl",
            "args": ["-g", group, "-m", "gpt-4o-mini"] if group else ["-m", "gpt-4o-mini"]
        },
        "relations": {
            "recipe": "guarani-relations",
            "dataset": f"guarani_relations_{group or 'all'}",
            "recipe_file": "recipes/guarani_relations.py",
            "source": "data/export/original_translations.jsonl",
            "args": ["-g", group or "relations", "-l", str(limit)]
        }
    }
    
    return configs.get(annotation_type, configs["batch-pos"])


def start_prodigy_process(config: dict, port: int) -> bool:
    """Inicia el proceso de Prodigy"""
    global prodigy_state
    
    recipe_path = BASE_DIR / config["recipe_file"]
    
    cmd = [
        sys.executable, "-m", "prodigy",
        config["recipe"],
        config["dataset"],
    ]
    
    # Agregar source si existe
    if "source" in config:
        source_path = BASE_DIR / config["source"]
        cmd.append(str(source_path.resolve()))
    
    # Agregar argumentos adicionales
    cmd.extend(config.get("args", []))
    
    # Agregar recipe file
    cmd.extend(["-F", str(recipe_path.resolve())])
    
    print(f"[PRODIGY] Comando: {' '.join(cmd)}")
    
    env = os.environ.copy()
    env["PRODIGY_PORT"] = str(port)
    env["PRODIGY_HOST"] = "127.0.0.1"
    
    try:
        prodigy_state.process = subprocess.Popen(
            cmd,
            env=env,
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # Esperar a que inicie
        print("[PRODIGY] Esperando inicio...")
        time.sleep(3)
        
        for i in range(20):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(("127.0.0.1", port))
                    print(f"[PRODIGY] OK - Iniciado en puerto {port}")
                    return True
            except:
                time.sleep(0.5)
        
        print("[PRODIGY] ERROR - Timeout esperando inicio")
        return False
        
    except Exception as e:
        print(f"[PRODIGY] Error: {e}")
        return False


async def stop_prodigy_internal():
    """Detiene el proceso de Prodigy"""
    global prodigy_state
    
    if prodigy_state.process:
        try:
            prodigy_state.process.terminate()
            prodigy_state.process.wait(timeout=5)
        except:
            prodigy_state.process.kill()
        
        prodigy_state.process = None
        prodigy_state.type = ""
        prodigy_state.config = {}
        prodigy_state.started_at = None
        print("[PRODIGY] Detenido")


async def stop_all_services():
    """Detiene todos los servicios"""
    for service_type in prodigy_services:
        await stop_service_internal(service_type)


def cleanup():
    """Limpieza al cerrar"""
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(stop_all_services())
    loop.run_until_complete(stop_prodigy_internal())
    loop.close()


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Prodigy Manager - Proxy Seguro")
    parser.add_argument("--port", "-p", type=int, default=8085,
                       help="Puerto del proxy (default: 8085)")
    
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(0)))
    
    print("")
    print("=" * 64)
    print("  PRODIGY MANAGER")
    print("  Sistema de Anotación por Lotes con JWT")
    print("=" * 64)
    print("")
    print(f"  Puerto:      {args.port}")
    print(f"  Backend:     {BACKEND_URL}")
    print("")
    print("  PUERTOS DE SERVICIOS:")
    for svc, port in SERVICE_PORTS.items():
        print(f"    {svc.upper():12} -> {port}")
    print("")
    print("  ACCESO:")
    print(f"    1. Login en http://localhost:5173")
    print(f"    2. Ir a Dashboard -> Prodigy")
    print(f"    3. Seleccionar lote y tipo de anotación")
    print(f"    4. Click en 'Iniciar Servicio'")
    print("")
    print("  API Endpoints:")
    print(f"    GET  /api/status       - Estado del sistema")
    print(f"    GET  /api/services     - Servicios en ejecución")
    print(f"    GET  /api/types        - Tipos de anotación disponibles")
    print(f"    POST /api/start-prodigy - Iniciar servicio (batch)")
    print(f"    POST /api/stop-prodigy/{{service}} - Detener servicio")
    print("")
    print("=" * 64)
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
