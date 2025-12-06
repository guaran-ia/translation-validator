"""
Servidor Proxy con Autenticación JWT para Prodigy + OpenAI
==========================================================
Igual que start_prodigy_spans_secure.py pero con pre-anotación automática
de OpenAI antes de mostrar al usuario.

El flujo es:
1. Usuario se autentica via JWT
2. OpenAI analiza la oración y genera spans automáticamente
3. Usuario ve los spans ya marcados y puede corregir/agregar/eliminar

Uso:
    python start_prodigy_openai_secure.py
    python start_prodigy_openai_secure.py -m gpt-4o --port 8082

El servidor corre en puerto 8082 (proxy) y Prodigy en 8080 (interno).
"""

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import subprocess
import sys
import os
import csv
import json
from pathlib import Path
import argparse
import signal
import socket
import time

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configuración desde variables de entorno
PRODIGY_INTERNAL_PORT = int(os.getenv("PRODIGY_PORT", 8080))
PROXY_PORT = int(os.getenv("PRODIGY_PROXY_PORT", 8082))
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app = FastAPI(title="Prodigy OpenAI Secure Proxy")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente HTTP para hacer requests a Prodigy y al Backend
http_client = httpx.AsyncClient(timeout=30.0)

# Variable global para el proceso de Prodigy
prodigy_process = None

# Almacena tokens validados (cache simple)
validated_tokens = {}


def get_error_page(title: str, message: str, show_login: bool = True) -> str:
    """Genera página HTML de error"""
    login_button = ""
    if show_login:
        login_button = '<a href="http://localhost:5173" class="btn">Ir al Login</a>'
    
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 450px;
            }}
            h1 {{ color: #dc2626; margin-bottom: 15px; font-size: 24px; }}
            p {{ color: #555; line-height: 1.6; margin-bottom: 25px; }}
            .btn {{
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: background 0.3s;
            }}
            .btn:hover {{ background: #5563d4; }}
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


async def validate_jwt_token(token: str) -> dict:
    """Valida un token JWT contra el backend"""
    if not token or token.count('.') != 2:
        return None
    
    # Cache simple para no validar cada request
    if token in validated_tokens:
        cache_time, user_data = validated_tokens[token]
        if time.time() - cache_time < 300:  # Cache por 5 minutos
            return user_data
    
    try:
        response = await http_client.get(
            f"{BACKEND_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            user_data = response.json()
            validated_tokens[token] = (time.time(), user_data)
            return user_data
        return None
    except Exception as e:
        print(f"[ERROR] Validando token: {e}")
        return None


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_prodigy(request: Request, path: str = ""):
    """Proxy todas las requests a Prodigy después de validar el token"""
    
    # SOLO aceptar token del parámetro "token" o header Authorization
    # La cookie solo se usa para requests subsecuentes (CSS, JS, API)
    token_from_url = request.query_params.get("token")
    token_from_header = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token_from_header = auth_header[7:]
    token_from_cookie = request.cookies.get("prodigy_token")
    
    # Para la página principal (raíz), SIEMPRE requerir token en URL o header
    # NO aceptar solo cookie para acceso inicial
    if path == "" or path == "/":
        token = token_from_url or token_from_header
        
        if not token:
            # Borrar cookie antigua si existe (forzar re-login)
            response = HTMLResponse(
                content=get_error_page(
                    "Acceso Restringido",
                    "Necesitas un token de acceso válido para usar Prodigy. "
                    "Inicia sesión en la aplicación principal y accede desde el Dashboard de Prodigy."
                ),
                status_code=403
            )
            response.delete_cookie("prodigy_token")
            return response
        
        # Validar que el token sea un JWT válido
        user_data = await validate_jwt_token(token)
        if not user_data:
            response = HTMLResponse(
                content=get_error_page(
                    "Token Inválido o Expirado",
                    "Tu sesión ha expirado o el token no es válido. "
                    "Por favor, inicia sesión nuevamente."
                ),
                status_code=403
            )
            response.delete_cookie("prodigy_token")
            return response
        
        print(f"[AUTH] ✓ Usuario validado: {user_data.get('username')}")
    else:
        # Para recursos (CSS, JS, API), aceptar cookie válida
        token = token_from_url or token_from_header or token_from_cookie
        if token and token.count('.') == 2:
            # Validar token de cookie también
            user_data = await validate_jwt_token(token)
            if not user_data:
                # Cookie inválida, pero dejamos cargar recursos estáticos
                pass
    
    # Construir URL de destino (Prodigy interno)
    target_url = f"http://localhost:{PRODIGY_INTERNAL_PORT}/{path}"
    
    # Copiar query params (excepto token para no pasarlo a Prodigy)
    query_params = dict(request.query_params)
    query_params.pop("token", None)
    
    try:
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        headers = {}
        for key, value in request.headers.items():
            if key.lower() not in ["host", "authorization"]:
                headers[key] = value
        
        response = await http_client.request(
            method=request.method,
            url=target_url,
            params=query_params,
            content=body,
            headers=headers
        )
        
        # Crear respuesta
        proxy_response = Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
        
        # Guardar token en cookie SOLO si viene de URL/header (no de cookie vieja)
        if (path == "" or path == "/") and (token_from_url or token_from_header):
            proxy_response.set_cookie(
                key="prodigy_token",
                value=token_from_url or token_from_header,
                httponly=True,
                max_age=3600  # 1 hora
            )
        
        return proxy_response
        
    except httpx.ConnectError:
        return HTMLResponse(
            content=get_error_page(
                "Prodigy No Disponible",
                "El servidor de Prodigy no está respondiendo. "
                "Espera unos segundos y recarga la página.",
                show_login=False
            ),
            status_code=503
        )
    except Exception as e:
        print(f"[ERROR] Proxy: {e}")
        return HTMLResponse(
            content=get_error_page(
                "Error del Servidor",
                f"Ocurrió un error: {str(e)}",
                show_login=False
            ),
            status_code=500
        )


def find_free_port(start=8080):
    """Encuentra un puerto libre"""
    for port in range(start, start + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return None


def csv_to_jsonl(csv_path: Path, jsonl_path: Path, limit: int = None):
    """Convierte el CSV de traducciones a JSONL para Prodigy"""
    print(f"[DATA] Convirtiendo {csv_path} a {jsonl_path}")
    
    count = 0
    with open(csv_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        
        with open(jsonl_path, "w", encoding="utf-8") as jsonlfile:
            for row in reader:
                if limit and count >= limit:
                    break
                
                gn_text = row.get("gn", "").strip()
                es_text = row.get("es", "").strip()
                source = row.get("source", "unknown")
                split = row.get("split", "")
                
                if not gn_text:
                    continue
                
                example = {
                    "text": gn_text,
                    "meta": {
                        "spanish_text": es_text,
                        "source": source,
                        "split": split,
                        "id": count + 1
                    }
                }
                
                jsonlfile.write(json.dumps(example, ensure_ascii=False) + "\n")
                count += 1
    
    print(f"[DATA] Convertidas {count} oraciones")
    return count


def start_prodigy(dataset: str, source: str, model: str, port: int, no_cache: bool = False, group: str = None):
    """Inicia Prodigy con el recipe de OpenAI"""
    global prodigy_process
    
    recipe_file = Path(__file__).parent / "recipes" / "guarani_openai.py"
    logs_dir = Path(__file__).parent / "logs"
    
    # IMPORTANTE: Usar rutas absolutas
    source_abs = str(Path(source).resolve())
    recipe_abs = str(recipe_file.resolve())
    
    print(f"[PRODIGY] Recipe: {recipe_abs}")
    print(f"[PRODIGY] Source: {source_abs}")
    if group:
        print(f"[PRODIGY] Grupo: {group}")
    print(f"[LOGS] Ver logs detallados en: {logs_dir}")
    
    cmd = [
        sys.executable, "-m", "prodigy",
        "guarani-openai",
        dataset,
        source_abs,
        "-m", model,
        "-F", recipe_abs
    ]
    
    if no_cache:
        cmd.append("--no-cache")
    
    if group:
        cmd.extend(["-g", group])
    
    env = os.environ.copy()
    env["PRODIGY_PORT"] = str(port)
    env["PRODIGY_HOST"] = "127.0.0.1"  # Solo local, el proxy expone
    # NO configurar PRODIGY_ALLOWED_SESSIONS - permitir todas por defecto
    
    print(f"[PRODIGY] Iniciando: {' '.join(cmd)}")
    
    prodigy_process = subprocess.Popen(
        cmd,
        env=env,
        stdout=None,  # Mostrar salida en consola
        stderr=None,  # Mostrar errores en consola
        text=True
    )
    
    # Esperar a que Prodigy inicie
    print("[PRODIGY] Esperando a que inicie...")
    time.sleep(5)
    for i in range(30):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(("127.0.0.1", port))
                print(f"[PRODIGY] ✓ Listo en puerto {port}")
                return True
        except:
            if i % 5 == 0:
                print(f"[PRODIGY] Esperando... ({i}s)")
            time.sleep(1)
    
    print("[PRODIGY] ✗ No se pudo iniciar (timeout)")
    return False


def cleanup():
    """Limpia procesos al cerrar"""
    global prodigy_process
    if prodigy_process:
        print("\n[CLEANUP] Deteniendo Prodigy...")
        prodigy_process.terminate()
        prodigy_process.wait()
        print("[CLEANUP] Prodigy detenido")


def main():
    parser = argparse.ArgumentParser(description="Prodigy + OpenAI con autenticación JWT")
    parser.add_argument("--dataset", "-d", default="guarani_openai_secure",
                       help="Nombre del dataset en Prodigy")
    parser.add_argument("--source", "-s", default="",
                       help="Archivo JSONL de entrada (o se usa translations.csv)")
    parser.add_argument("--model", "-m", default="gpt-4o-mini",
                       help="Modelo de OpenAI")
    parser.add_argument("--port", "-p", type=int, default=8082,
                       help="Puerto del proxy (default: 8082)")
    parser.add_argument("--limit", "-l", type=int, default=100,
                       help="Límite de oraciones a cargar")
    parser.add_argument("--no-cache", action="store_true",
                       help="Desactivar cache de OpenAI")
    parser.add_argument("--group", "-g", default=None,
                       help="Grupo de etiquetas: morfemas-basicos, categorias, persona-numero, tam, caso-relacional, voz-polaridad, nominalizadores, otros-features")
    
    args = parser.parse_args()
    
    # Configurar señales para cleanup
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(0)))
    
    print("")
    print("=" * 64)
    print("  PRODIGY + OpenAI SECURE")
    print("  Anotación Morfológica Asistida por IA con Autenticación JWT")
    print("=" * 64)
    print("")
    
    # Determinar fuente de datos
    source_path = args.source
    if not source_path:
        # Buscar translations.csv y convertir a JSONL
        base_dir = Path(__file__).parent.parent.parent
        csv_path = base_dir / "data" / "translations.csv"
        
        if csv_path.exists():
            jsonl_path = Path(__file__).parent / "data" / "export" / "translations_for_openai.jsonl"
            jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            
            csv_to_jsonl(csv_path, jsonl_path, limit=args.limit)
            source_path = str(jsonl_path)
        else:
            # Usar ejemplos
            source_path = str(Path(__file__).parent / "data" / "examples" / "sample_sentences.jsonl")
    
    if not Path(source_path).exists():
        print(f"[ERROR] Archivo no encontrado: {source_path}")
        sys.exit(1)
    
    # Contar oraciones
    with open(source_path, "r", encoding="utf-8") as f:
        line_count = sum(1 for _ in f)
    
    print(f"  Dataset:     {args.dataset}")
    print(f"  Fuente:      {source_path}")
    print(f"  Oraciones:   {line_count}")
    print(f"  Modelo:      {args.model}")
    print(f"  Cache:       {'Desactivado' if args.no_cache else 'Activado'}")
    if args.group:
        print(f"  Grupo:       {args.group}")
    print(f"  Puerto:      {args.port} (proxy JWT)")
    print("")
    
    # Encontrar puerto para Prodigy interno
    prodigy_port = find_free_port(8080)
    if not prodigy_port:
        print("[ERROR] No se encontró puerto libre para Prodigy")
        sys.exit(1)
    
    global PRODIGY_INTERNAL_PORT
    PRODIGY_INTERNAL_PORT = prodigy_port
    
    print(f"  Prodigy interno en puerto: {prodigy_port}")
    print("")
    
    # Iniciar Prodigy
    if not start_prodigy(args.dataset, source_path, args.model, prodigy_port, args.no_cache, args.group):
        print("[ERROR] Prodigy no se inició correctamente")
        sys.exit(1)
    
    print("")
    print("=" * 64)
    print("  SISTEMA LISTO")
    print("=" * 64)
    print("")
    print("  ACCESO:")
    print("    1. Login en http://localhost:5173")
    print("    2. Dashboard -> Prodigy")
    print("    3. Click en 'Abrir Prodigy'")
    print("")
    print(f"  O directamente: http://localhost:{args.port}?token=<tu_jwt>")
    print("")
    print("  OpenAI pre-anotará automáticamente cada oración!")
    print("  Tú solo corriges lo que esté mal.")
    print("")
    print("=" * 64)
    print("  Ctrl+C para detener")
    print("=" * 64)
    print("")
    
    # Iniciar servidor proxy
    try:
        uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="warning")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
