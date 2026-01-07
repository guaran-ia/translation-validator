#!/usr/bin/env python3
"""
prodigy_diagnostic.py

Pequeño script de diagnóstico para verificar el estado del entorno Prodigy/Manager
y la coherencia con `data/batch_monitor_state.json`.

Uso:
  python prodigy_diagnostic.py

Salidas:
  - Informe simple por consola con comprobaciones: manager, puertos de servicios,
    lectura del archivo de estado y consistencia básica.
"""
import json
import socket
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "batch_monitor_state.json"
MANAGER_URL = "http://localhost:8085/api/status"
SERVICES = {"pos": 8080, "features": 8081, "relations": 8082}


def check_manager():
    print("[MANAGER] Comprobando manager en http://localhost:8085/api/status ...", end=" ")
    try:
        req = Request(MANAGER_URL, headers={"User-Agent": "prodigy-diagnostic/1.0"})
        with urlopen(req, timeout=3) as resp:
            data = resp.read().decode("utf-8")
            print("OK (HTTP)")
            return True
    except HTTPError as e:
        print(f"HTTP {e.code}")
    except URLError as e:
        print(f"ERROR: {e.reason}")
    except Exception as e:
        print(f"ERROR: {e}")
    return False


def check_ports():
    results = {}
    for name, port in SERVICES.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            s.connect(("127.0.0.1", port))
            results[name] = True
            print(f"[PORT] {name:8} -> 127.0.0.1:{port} -> OPEN")
        except Exception:
            results[name] = False
            print(f"[PORT] {name:8} -> 127.0.0.1:{port} -> CLOSED")
        finally:
            s.close()
    return results


def read_state():
    print("[STATE] Leyendo file:", DATA_FILE)
    if not DATA_FILE.exists():
        print("  -> NO ENCONTRADO")
        return None
    try:
        raw = DATA_FILE.read_text(encoding="utf-8")
        obj = json.loads(raw)
        print("  -> OK: keys:", ", ".join(obj.keys()))
        return obj
    except Exception as e:
        print("  -> ERROR leyendo JSON:", e)
        return None


def check_consistency(state, port_results):
    print("[CONSISTENCY] Verificando current_batch y puertos...")
    if not state or "current_batch" not in state:
        print("  -> No hay información de 'current_batch' para verificar")
        return
    cb = state["current_batch"]
    for svc in SERVICES.keys():
        batch = cb.get(svc, None)
        port_open = port_results.get(svc, False)
        print(f"  - {svc:8}: batch={batch} | puerto_open={port_open}")


def main():
    print("PRODIGY DIAGNOSTIC\n")
    mgr_ok = check_manager()
    ports = check_ports()
    state = read_state()
    check_consistency(state, ports)

    print("\nRECOMENDACIONES:")
    if not mgr_ok:
        print("  - Manager no responde. Revisa que prodigy_manager.py esté corriendo y que el puerto 8085 esté libre.")
    for svc, open_ in ports.items():
        if not open_:
            print(f"  - Servicio {svc} no atiende en el puerto esperado ({SERVICES[svc]}). Revisa logs o inicia el servicio desde Manager.")
    if state is None:
        print("  - Archivo de estado ausente o inválido: data/batch_monitor_state.json")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
        sys.exit(1)
