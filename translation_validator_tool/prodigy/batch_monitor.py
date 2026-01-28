#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch Monitor - Sistema de Auto-Avance de Batches
=================================================
Monitorea el progreso de los anotadores y automáticamente
inicia el siguiente batch cuando todos completan sus 50 frases.

Características:
- Monitorea progreso de cada sesión/anotador en tiempo real
- Detecta cuando TODOS los anotadores completaron el batch actual
- Automáticamente reinicia Prodigy con el siguiente batch
- Notificaciones vía API y logs
- Configuración flexible de validadores requeridos

Uso:
    python batch_monitor.py
    python batch_monitor.py --interval 30  # Check cada 30 segundos

Variables de Entorno:
    BATCH_MONITOR_INTERVAL: Intervalo de chequeo en segundos (default: 60)
    SENTENCES_PER_BATCH: Oraciones por batch (default: 50)
"""

import os
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx

# Cargar variables de entorno (buscar .env en carpetas padre si existe)
from dotenv import load_dotenv, find_dotenv
env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)
else:
    # Fallback a .env junto al script si no se encuentra en padres
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

# Configuración
PRODIGY_MANAGER_URL = os.getenv("PRODIGY_MANAGER_URL", "http://localhost:8085")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BATCH_MONITOR_INTERVAL = int(os.getenv("BATCH_MONITOR_INTERVAL", "10"))
SENTENCES_PER_BATCH = int(os.getenv("SENTENCES_PER_BATCH", "50"))
TOTAL_BATCHES = 60  # Hardcodeado: 3000 oraciones / 50 por batch

# Directorio base
BASE_DIR = Path(__file__).parent
BATCHES_DIR = BASE_DIR / "data" / "batches"
STATE_FILE = BASE_DIR / "data" / "batch_monitor_state.json"

# Función para parsear listas de validadores desde .env
def parse_validators_list(env_var: str, default: str) -> list:
    """Parsea una lista de validadores desde variable de entorno"""
    value = os.getenv(env_var, default).strip('"').strip("'")
    return [v.strip() for v in value.split(",") if v.strip()]

# Validadores permitidos por tipo de servicio (desde .env)
SERVICE_VALIDATORS = {
    "pos": parse_validators_list("VALIDATORS_POS", "alice,bob"),
    "features": parse_validators_list("VALIDATORS_FEATURES", "carlos,elena"),
    "relations": parse_validators_list("VALIDATORS_RELATIONS", "marcos,nicolas"),
}

# Lista global de todos los validadores (para compatibilidad)
VALID_SESSIONS = list(set(
    SERVICE_VALIDATORS["pos"] + 
    SERVICE_VALIDATORS["features"] + 
    SERVICE_VALIDATORS["relations"]
))

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class BatchMonitor:
    """
    Monitor de batches que rastrea el progreso y auto-avanza.
    Avanza cuando TODOS los validadores asignados completan sus frases.
    """
    
    def __init__(
        self,
        check_interval: int = 10,
        sentences_per_batch: int = 50,
    ):
        self.check_interval = check_interval
        self.sentences_per_batch = sentences_per_batch
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Estado actual
        self.current_batch: Dict[str, int] = {
            "pos": 1,
            "features": 1,
            "relations": 1,
        }
        self.progress: Dict[str, Dict[str, int]] = {}
        self.last_check: Optional[datetime] = None
        self.running = True
        
        # Cargar estado persistente
        self._load_state()
    
    def _load_state(self):
        """Carga el estado desde el archivo JSON"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    self.current_batch = state.get("current_batch", self.current_batch)
                    self.progress = state.get("progress", {})
                    print(f"{Colors.CYAN}[MONITOR] Estado cargado: Batch actual = {self.current_batch}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.WARNING}[MONITOR] No se pudo cargar estado: {e}{Colors.ENDC}")
    
    def _save_state(self):
        """Guarda el estado actual"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "current_batch": self.current_batch,
            "progress": self.progress,
            "last_updated": datetime.now().isoformat(),
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    async def get_annotations_from_prodigy_db(
        self, 
        annotation_type: str, 
        batch: int
    ) -> Dict[str, int]:
        """
        Obtiene el conteo de anotaciones por sesión desde la DB de Prodigy.
        
        Returns:
            Dict con session_id -> número de anotaciones
        """
        batch_str = str(batch).zfill(3)
        dataset_name = f"guarani_{annotation_type}_batch_{batch_str}"
        
        try:
            # Usar prodigy db-out para obtener las anotaciones
            import subprocess
            
            result = subprocess.run(
                [sys.executable, "-m", "prodigy", "db-out", dataset_name],
                capture_output=True,
                text=True,
                cwd=str(BASE_DIR),
                timeout=30,
            )
            
            if result.returncode != 0:
                # Dataset no existe o vacío
                return {}
            
            # Parsear output JSONL
            counts: Dict[str, int] = {}
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    annotation = json.loads(line)
                    session_id = annotation.get("_session_id", "default")
                    answer = annotation.get("answer", "")
                    
                    # Contar todas las respuestas validas (accept/reject/ignore)
                    # "ignore" tambien cuenta como tarea procesada
                    if answer in ["accept", "reject", "ignore"]:
                        counts[session_id] = counts.get(session_id, 0) + 1
                except json.JSONDecodeError:
                    continue
            
            return counts
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.WARNING}[MONITOR] Timeout obteniendo anotaciones de {dataset_name}{Colors.ENDC}")
            return {}
        except Exception as e:
            print(f"{Colors.FAIL}[MONITOR] Error obteniendo anotaciones: {e}{Colors.ENDC}")
            return {}
    
    async def check_batch_completion(
        self, 
        annotation_type: str, 
        batch: int
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Verifica si un batch está completo.
        
        Returns:
            (is_complete, progress_by_session)
        """
        counts = await self.get_annotations_from_prodigy_db(annotation_type, batch)

        if not counts:
            return False, {}

        # Obtener validadores asignados a este tipo de anotación
        # Avanza cuando TODOS los asignados completan
        assigned_validators = SERVICE_VALIDATORS.get(annotation_type, VALID_SESSIONS)
        required_for_type = len(assigned_validators)

        # Normalizar y mapear los session_ids devueltos por Prodigy a nombres de usuario
        # Ejemplo: 'guarani_features_batch_003-carlos' -> 'carlos'
        mapped_counts: Dict[str, int] = {}
        unassigned: Dict[str, int] = {}

        for raw_session, cnt in counts.items():
            matched_user = None
            # coincidencia exacta
            if raw_session in assigned_validators:
                matched_user = raw_session
            else:
                # intentar extraer sufijo tras '-' o '_' o buscar el nombre dentro del id
                for user in assigned_validators:
                    if raw_session.endswith(f"-{user}") or raw_session.endswith(f"_{user}"):
                        matched_user = user
                        break
                    if f"-{user}-" in raw_session or f"_{user}_" in raw_session:
                        matched_user = user
                        break
                    # como fallback, buscar el nombre dentro del session id (evitar false positives controlando longitud)
                    if user in raw_session:
                        matched_user = user
                        break

            if matched_user:
                mapped_counts[matched_user] = mapped_counts.get(matched_user, 0) + cnt
            else:
                unassigned[raw_session] = cnt

        # Construir un diccionario de progreso amigable para mostrar
        batch_str = str(batch).zfill(3)
        dataset_name = f"guarani_{annotation_type}_batch_{batch_str}"
        progress_display: Dict[str, int] = {}

        # Añadir contadores normalizados para cada validador asignado (incluso si 0)
        for user in assigned_validators:
            display_key = f"{dataset_name}-{user}"
            progress_display[display_key] = mapped_counts.get(user, 0)

        # Añadir sesiones no asignadas tal cual (para diagnóstico)
        for raw_s, raw_cnt in unassigned.items():
            progress_display[raw_s] = raw_cnt

        # Contar validadores asignados que completaron
        completed_validators = 0
        for user, cnt in mapped_counts.items():
            if cnt >= self.sentences_per_batch:
                completed_validators += 1

        is_complete = completed_validators >= required_for_type

        return is_complete, progress_display
    
    async def get_running_services(self) -> Dict[str, dict]:
        """Obtiene los servicios en ejecución desde el manager"""
        try:
            response = await self.http_client.get(
                f"{PRODIGY_MANAGER_URL}/api/services",
                headers={"Authorization": "Bearer internal-monitor"}  # Token especial
            )
            if response.status_code == 200:
                return response.json().get("services", {})
        except Exception as e:
            print(f"{Colors.WARNING}[MONITOR] No se pudo conectar al manager: {e}{Colors.ENDC}")
        return {}
    
    async def start_next_batch(self, annotation_type: str, current_batch: int):
        """Inicia el siguiente batch para un tipo de anotación"""
        next_batch = current_batch + 1
        
        if next_batch > TOTAL_BATCHES:
            print(f"{Colors.GREEN}[MONITOR] ¡COMPLETADO! Todos los batches de {annotation_type} terminados{Colors.ENDC}")
            return False
        
        print(f"{Colors.BOLD}[MONITOR] Iniciando batch {next_batch} para {annotation_type}...{Colors.ENDC}")
        
        # Reintentar hasta 3 veces en caso de 409 Conflict
        max_retries = 3
        retry_delay = 2  # segundos entre reintentos
        
        for attempt in range(max_retries):
            try:
                response = await self.http_client.post(
                    f"{PRODIGY_MANAGER_URL}/api/start-prodigy",
                    json={
                        "recipe": "batch",
                        "annotation_type": annotation_type,
                        "batch_number": next_batch,
                    },
                    headers={"Authorization": "Bearer internal-monitor"}
                )
                
                if response.status_code == 200:
                    self.current_batch[annotation_type] = next_batch
                    # Limpiar el progreso del tipo de anotación para evitar mostrar datos antiguos
                    self.progress[annotation_type] = {}
                    self._save_state()
                    print(f"{Colors.GREEN}[MONITOR] OK - Batch {next_batch} ({annotation_type}) iniciado exitosamente{Colors.ENDC}")
                    return True
                elif response.status_code == 409:
                    # Conflicto: servicio aún se está deteniendo
                    if attempt < max_retries - 1:
                        print(f"{Colors.WARNING}[MONITOR] Conflicto (409) - Reintentando en {retry_delay}s ({attempt+1}/{max_retries-1})...{Colors.ENDC}")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        print(f"{Colors.FAIL}[MONITOR] Error iniciando batch después de {max_retries} intentos: 409 Conflict{Colors.ENDC}")
                        return False
                else:
                    print(f"{Colors.FAIL}[MONITOR] Error iniciando batch: {response.status_code}{Colors.ENDC}")
                    return False
                    
            except Exception as e:
                print(f"{Colors.FAIL}[MONITOR] Error conectando al manager: {e}{Colors.ENDC}")
                return False
        
        return False
    
    async def notify_batch_complete(self, annotation_type: str, batch: int, progress: Dict[str, int]):
        """Envía notificación de batch completado"""
        try:
            # Guardar evento en archivo de log
            log_file = BASE_DIR / "logs" / "batch_completions.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "batch_complete",
                "annotation_type": annotation_type,
                "batch": batch,
                "progress": progress,
            }
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
            # Intentar notificar al backend
            await self.http_client.post(
                f"{BACKEND_URL}/api/notifications",
                json={
                    "type": "batch_complete",
                    "message": f"Batch {batch} de {annotation_type} completado por {len(progress)} anotadores",
                    "data": log_entry,
                },
                timeout=5.0
            )
        except Exception as e:
            # No es crítico si falla la notificación
            pass
    
    def print_status(self, services: Dict[str, dict], all_progress: Dict[str, Dict[str, int]]):
        """Imprime el estado actual en consola"""
        now = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}  BATCH MONITOR - Estado a las {now}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        for atype in ["pos", "features", "relations"]:
            batch = self.current_batch.get(atype, 1)
            is_running = atype in services
            status = f"{Colors.GREEN}[ON]{Colors.ENDC}" if is_running else f"{Colors.FAIL}[OFF]{Colors.ENDC}"
            
            # Mostrar validadores asignados a este tipo
            assigned = SERVICE_VALIDATORS.get(atype, [])
            assigned_str = ", ".join(assigned) if assigned else "ninguno"
            
            print(f"\n  {status} {atype.upper():12} | Batch {batch:02d}/{TOTAL_BATCHES}")
            print(f"      {Colors.BLUE}Validadores: {assigned_str}{Colors.ENDC}")
            
            progress = all_progress.get(atype, {})
            if progress:
                for session_id, count in sorted(progress.items()):
                    pct = min(100, (count / self.sentences_per_batch) * 100)
                    bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
                    completed_icon = "OK" if count >= self.sentences_per_batch else "  "
                    # Marcar si el validador está asignado a este tipo
                    is_assigned = session_id in assigned
                    marker = "" if is_assigned else f" {Colors.WARNING}(!){Colors.ENDC}"
                    color = Colors.GREEN if count >= self.sentences_per_batch else Colors.CYAN
                    print(f"      {color}{session_id:10} [{bar}] {count:3}/{self.sentences_per_batch} {completed_icon}{Colors.ENDC}{marker}")
            else:
                print(f"      {Colors.WARNING}Sin anotaciones aun{Colors.ENDC}")
        
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"  Proximo chequeo en {self.check_interval}s | Ctrl+C para salir")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    async def run_check_cycle(self):
        """Ejecuta un ciclo de verificación"""
        self.last_check = datetime.now()
        
        # Obtener servicios en ejecución
        services = await self.get_running_services()
        
        # Verificar progreso de cada tipo de anotación
        all_progress: Dict[str, Dict[str, int]] = {}
        
        for annotation_type in ["pos", "features", "relations"]:
            batch = self.current_batch.get(annotation_type, 1)
            is_complete, progress = await self.check_batch_completion(annotation_type, batch)
            all_progress[annotation_type] = progress
            
            if is_complete:
                print(f"\n{Colors.GREEN}{'='*60}{Colors.ENDC}")
                print(f"{Colors.BOLD}  ¡BATCH {batch} de {annotation_type.upper()} COMPLETADO!{Colors.ENDC}")
                print(f"{Colors.GREEN}{'='*60}{Colors.ENDC}")
                
                # Notificar
                await self.notify_batch_complete(annotation_type, batch, progress)
                
                # Detener servicio actual
                try:
                    await self.http_client.post(
                        f"{PRODIGY_MANAGER_URL}/api/stop-prodigy/{annotation_type}",
                        headers={"Authorization": "Bearer internal-monitor"}
                    )
                    await asyncio.sleep(5)  # Esperar a que se detenga (5s en Linux puede ser lento)
                except:
                    pass
                
                # Iniciar siguiente batch
                await self.start_next_batch(annotation_type, batch)
                # Limpiar también del diccionario all_progress para evitar mostrar datos antiguos
                all_progress[annotation_type] = {}
        
        # Mostrar estado
        self.print_status(services, all_progress)
        
        # Guardar progreso
        self.progress = all_progress
        self._save_state()
    
    async def run(self):
        """Loop principal del monitor"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}  BATCH MONITOR INICIADO{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"  Intervalo de chequeo: {self.check_interval}s")
        print(f"  Frases por batch: {self.sentences_per_batch}")
        print(f"  Total de batches: {TOTAL_BATCHES}")
        print(f"  Validadores por tipo:")
        for atype, validators in SERVICE_VALIDATORS.items():
            print(f"    - {atype}: {', '.join(validators)} ({len(validators)})")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        while self.running:
            try:
                await self.run_check_cycle()
                await asyncio.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.running = False
                print(f"\n{Colors.WARNING}[MONITOR] Detenido por el usuario{Colors.ENDC}")
                break
            except Exception as e:
                print(f"{Colors.FAIL}[MONITOR] Error en ciclo: {e}{Colors.ENDC}")
                await asyncio.sleep(10)  # Esperar antes de reintentar
        
        await self.http_client.aclose()
    
    def stop(self):
        """Detiene el monitor"""
        self.running = False


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Batch Monitor - Auto-avance de batches para Prodigy"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=BATCH_MONITOR_INTERVAL,
        help=f"Intervalo de chequeo en segundos (default: {BATCH_MONITOR_INTERVAL})"
    )
    parser.add_argument(
        "--sentences", "-s",
        type=int,
        default=SENTENCES_PER_BATCH,
        help=f"Frases por batch (default: {SENTENCES_PER_BATCH})"
    )
    parser.add_argument(
        "--check-once",
        action="store_true",
        help="Ejecutar un solo chequeo y salir"
    )
    
    args = parser.parse_args()
    
    monitor = BatchMonitor(
        check_interval=args.interval,
        sentences_per_batch=args.sentences,
    )
    
    if args.check_once:
        asyncio.run(monitor.run_check_cycle())
    else:
        try:
            asyncio.run(monitor.run())
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[MONITOR] Saliendo...{Colors.ENDC}")


if __name__ == "__main__":
    main()
