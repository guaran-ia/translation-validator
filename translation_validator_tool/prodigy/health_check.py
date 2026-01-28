#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Health Check - Diagnóstico Completo del Sistema Prodigy
=======================================================
Verifica el estado de todos los componentes del sistema.

Uso:
    python health_check.py
    python health_check.py --verbose
    python health_check.py --fix  # Intenta corregir problemas comunes
"""

import os
import sys
import json
import socket
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Intentar cargar httpx, si no está disponible usar requests
try:
    import httpx
    HTTP_CLIENT = "httpx"
except ImportError:
    try:
        import requests
        HTTP_CLIENT = "requests"
    except ImportError:
        HTTP_CLIENT = None

# Cargar variables de entorno
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configuración
BASE_DIR = Path(__file__).parent
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
PRODIGY_PORT = int(os.getenv("PRODIGY_PORT", "8080"))
PROXY_PORT = int(os.getenv("PRODIGY_PROXY_PORT", "8085"))

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def color(text, c):
    """Aplica color si terminal soporta"""
    if sys.platform == 'win32':
        # Habilitar colores en Windows
        os.system('')
    return f"{c}{text}{Colors.END}"

def check_icon(status):
    """Retorna ícono según estado"""
    if status == True:
        return color("✅", Colors.GREEN)
    elif status == False:
        return color("❌", Colors.RED)
    else:
        return color("⚠️", Colors.YELLOW)


def http_get(url, timeout=5):
    """Hace GET request con el cliente disponible"""
    if HTTP_CLIENT == "httpx":
        return httpx.get(url, timeout=timeout)
    elif HTTP_CLIENT == "requests":
        return requests.get(url, timeout=timeout)
    else:
        raise ImportError("No HTTP client available (install httpx or requests)")


class HealthChecker:
    """Verificador de salud del sistema"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {}
        self.issues = []
    
    def log(self, msg, level="info"):
        """Log con nivel"""
        if level == "info":
            print(f"  {msg}")
        elif level == "verbose" and self.verbose:
            print(f"    {color(msg, Colors.BLUE)}")
        elif level == "error":
            print(f"  {color(msg, Colors.RED)}")
        elif level == "warning":
            print(f"  {color(msg, Colors.YELLOW)}")
    
    def check_port(self, port, name):
        """Verifica si un puerto está en uso"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    def check_backend_api(self):
        """Verifica Backend API"""
        print(f"\n{color('1. Backend API', Colors.BOLD)} ({BACKEND_URL})")
        
        # Puerto
        port = int(BACKEND_URL.split(':')[-1].split('/')[0])
        port_open = self.check_port(port, "Backend")
        self.log(f"Puerto {port}: {'Abierto' if port_open else 'Cerrado'}")
        
        if not port_open:
            self.results["backend_api"] = False
            self.issues.append("Backend API no está corriendo")
            return
        
        # Health endpoint
        try:
            r = http_get(f"{BACKEND_URL}/api/health", timeout=5)
            health_ok = r.status_code == 200
            self.log(f"Health check: {check_icon(health_ok)} ({r.status_code})")
            self.results["backend_api"] = health_ok
        except Exception as e:
            self.log(f"Health check: {check_icon(False)} - {e}", "error")
            self.results["backend_api"] = False
            self.issues.append(f"Backend API no responde: {e}")
    
    def check_prodigy_internal(self):
        """Verifica Prodigy interno"""
        print(f"\n{color('2. Prodigy Interno', Colors.BOLD)} (puerto {PRODIGY_PORT})")
        
        port_open = self.check_port(PRODIGY_PORT, "Prodigy")
        self.log(f"Puerto {PRODIGY_PORT}: {'Abierto' if port_open else 'Cerrado'}")
        
        if port_open:
            self.results["prodigy_internal"] = True
            self.log(f"Estado: {check_icon(True)} Corriendo")
        else:
            self.results["prodigy_internal"] = None  # No crítico si se usa proxy
            self.log(f"Estado: {check_icon(None)} No corriendo (normal si no hay sesión activa)")
    
    def check_proxy(self):
        """Verifica Prodigy Proxy/Manager"""
        print(f"\n{color('3. Prodigy Manager/Proxy', Colors.BOLD)} (puerto {PROXY_PORT})")
        
        port_open = self.check_port(PROXY_PORT, "Proxy")
        self.log(f"Puerto {PROXY_PORT}: {'Abierto' if port_open else 'Cerrado'}")
        
        if not port_open:
            self.results["prodigy_proxy"] = False
            self.issues.append("Prodigy Manager no está corriendo")
            return
        
        try:
            r = http_get(f"http://localhost:{PROXY_PORT}/api/status", timeout=5)
            # 200 = OK, 401 = OK pero sin auth
            ok = r.status_code in [200, 401]
            self.log(f"API status: {check_icon(ok)} ({r.status_code})")
            self.results["prodigy_proxy"] = ok
        except Exception as e:
            self.log(f"API status: {check_icon(False)} - {e}", "error")
            self.results["prodigy_proxy"] = False
    
    def check_prodigy_db(self):
        """Verifica base de datos de Prodigy"""
        print(f"\n{color('4. Base de Datos Prodigy', Colors.BOLD)}")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "prodigy", "stats", "-ls"],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(BASE_DIR)
            )
            
            if result.returncode == 0:
                self.log(f"Conexión: {check_icon(True)} OK")
                
                # Contar datasets
                lines = result.stdout.strip().split('\n')
                datasets = [l for l in lines if l.strip() and not l.startswith('=')]
                self.log(f"Datasets: {len(datasets)} encontrados", "verbose")
                
                # Buscar datasets de guaraní
                guarani_ds = [l for l in lines if 'guarani' in l.lower()]
                if guarani_ds:
                    self.log(f"Datasets Guaraní: {len(guarani_ds)}", "verbose")
                
                self.results["prodigy_db"] = True
            else:
                self.log(f"Conexión: {check_icon(False)}", "error")
                self.log(f"Error: {result.stderr[:200]}", "verbose")
                self.results["prodigy_db"] = False
                self.issues.append("No se puede acceder a la DB de Prodigy")
        except subprocess.TimeoutExpired:
            self.log(f"Conexión: {check_icon(False)} - Timeout", "error")
            self.results["prodigy_db"] = False
            self.issues.append("Timeout al acceder a DB de Prodigy")
        except Exception as e:
            self.log(f"Conexión: {check_icon(False)} - {e}", "error")
            self.results["prodigy_db"] = False
    
    def check_data_files(self):
        """Verifica archivos de datos"""
        print(f"\n{color('5. Archivos de Datos', Colors.BOLD)}")
        
        # Directorio de batches
        batches_dir = BASE_DIR / "data" / "batches"
        batches_exist = batches_dir.exists()
        self.log(f"Directorio batches: {'Existe' if batches_exist else 'No existe'}")
        
        if batches_exist:
            batch_files = list(batches_dir.glob("*.jsonl"))
            self.log(f"Archivos batch: {len(batch_files)} encontrados")
            
            if batch_files:
                # Verificar primer archivo
                first = batch_files[0]
                try:
                    with open(first, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)
                    self.log(f"Ejemplo ({first.name}): {line_count} líneas", "verbose")
                    self.results["batch_files"] = True
                except Exception as e:
                    self.log(f"Error leyendo batch: {e}", "error")
                    self.results["batch_files"] = False
            else:
                self.results["batch_files"] = False
                self.issues.append("No hay archivos de batch generados")
        else:
            self.results["batch_files"] = False
            self.issues.append("Directorio de batches no existe")
        
        # Directorio de exportación
        export_dir = BASE_DIR / "data" / "export"
        self.log(f"Directorio export: {'Existe' if export_dir.exists() else 'No existe'}")
    
    def check_env_vars(self):
        """Verifica variables de entorno"""
        print(f"\n{color('6. Variables de Entorno', Colors.BOLD)}")
        
        required_vars = {
            "PRODIGY_PORT": os.getenv("PRODIGY_PORT"),
            "PRODIGY_PROXY_PORT": os.getenv("PRODIGY_PROXY_PORT"),
            "BACKEND_URL": os.getenv("BACKEND_URL"),
        }
        
        optional_vars = {
            "REQUIRED_VALIDATORS": os.getenv("REQUIRED_VALIDATORS", "3"),
            "SENTENCES_PER_BATCH": os.getenv("SENTENCES_PER_BATCH", "50"),
            "BATCH_MONITOR_INTERVAL": os.getenv("BATCH_MONITOR_INTERVAL", "60"),
        }
        
        # Verificar requeridas
        missing = []
        for var, value in required_vars.items():
            status = check_icon(value is not None)
            display_value = value if value else "(no definida)"
            self.log(f"{var}: {status} {display_value}")
            if not value:
                missing.append(var)
        
        if missing:
            self.results["env_vars"] = False
            self.issues.append(f"Variables faltantes: {', '.join(missing)}")
        else:
            self.results["env_vars"] = True
        
        # Mostrar opcionales en verbose
        if self.verbose:
            self.log("\nOpcionales:", "verbose")
            for var, value in optional_vars.items():
                self.log(f"  {var}: {value}", "verbose")
    
    def check_recipes(self):
        """Verifica que los recipes estén disponibles"""
        print(f"\n{color('7. Recipes de Prodigy', Colors.BOLD)}")
        
        recipes_dir = BASE_DIR / "recipes"
        if not recipes_dir.exists():
            self.log(f"Directorio recipes: {check_icon(False)} No existe", "error")
            self.results["recipes"] = False
            self.issues.append("Directorio de recipes no existe")
            return
        
        expected_recipes = [
            "guarani_batch.py",
            "guarani_spans.py",
            "guarani_relations.py",
            "guarani_openai.py",
        ]
        
        found = 0
        for recipe in expected_recipes:
            exists = (recipes_dir / recipe).exists()
            if exists:
                found += 1
            self.log(f"{recipe}: {check_icon(exists)}")
        
        self.results["recipes"] = found >= 2  # Al menos 2 deben existir
    
    def check_python_packages(self):
        """Verifica paquetes Python necesarios"""
        print(f"\n{color('8. Paquetes Python', Colors.BOLD)}")
        
        packages = [
            ("prodigy", "prodigy"),
            ("spacy", "spacy"),
            ("httpx", "httpx"),
            ("fastapi", "fastapi"),
            ("uvicorn", "uvicorn"),
            ("python-dotenv", "dotenv"),
        ]
        
        missing = []
        for name, import_name in packages:
            try:
                __import__(import_name)
                self.log(f"{name}: {check_icon(True)}")
            except ImportError:
                self.log(f"{name}: {check_icon(False)}")
                missing.append(name)
        
        if missing:
            self.results["packages"] = False
            self.issues.append(f"Paquetes faltantes: {', '.join(missing)}")
        else:
            self.results["packages"] = True
    
    def run_all_checks(self):
        """Ejecuta todas las verificaciones"""
        print(f"\n{'='*60}")
        print(f"{color('🔍 HEALTH CHECK - Sistema Prodigy', Colors.BOLD)}")
        print(f"{'='*60}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.check_backend_api()
        self.check_prodigy_internal()
        self.check_proxy()
        self.check_prodigy_db()
        self.check_data_files()
        self.check_env_vars()
        self.check_recipes()
        self.check_python_packages()
        
        # Resumen
        print(f"\n{'='*60}")
        print(f"{color('📊 RESUMEN', Colors.BOLD)}")
        print(f"{'='*60}")
        
        total = len(self.results)
        passed = sum(1 for v in self.results.values() if v == True)
        failed = sum(1 for v in self.results.values() if v == False)
        warnings = sum(1 for v in self.results.values() if v is None)
        
        print(f"\n  {check_icon(True)} Pasaron: {passed}/{total}")
        print(f"  {check_icon(False)} Fallaron: {failed}/{total}")
        if warnings:
            print(f"  {check_icon(None)} Advertencias: {warnings}/{total}")
        
        if self.issues:
            print(f"\n{color('⚠️ PROBLEMAS DETECTADOS:', Colors.YELLOW)}")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        else:
            print(f"\n{color('✅ Todo OK - Sistema listo para usar', Colors.GREEN)}")
        
        print(f"\n{'='*60}\n")
        
        return failed == 0


def main():
    parser = argparse.ArgumentParser(description="Health Check del Sistema Prodigy")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mostrar más detalles")
    parser.add_argument("--fix", action="store_true", help="Intentar corregir problemas (no implementado)")
    args = parser.parse_args()
    
    checker = HealthChecker(verbose=args.verbose)
    success = checker.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
