#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# BATCH AUTO-ADVANCE SYSTEM (Linux / Bash)
# =============================================================================

# -------------------------
# Defaults
# -------------------------
BATCH=1
INTERVAL=60
NO_MONITOR=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -------------------------
# Colores
# -------------------------
C_HEADER="\033[36m"
C_SUCCESS="\033[32m"
C_WARNING="\033[33m"
C_ERROR="\033[31m"
C_INFO="\033[37m"
C_RESET="\033[0m"

# -------------------------
# Helpers
# -------------------------
header() {
  echo
  echo -e "${C_HEADER}================================================================${C_RESET}"
  echo -e "${C_HEADER}  $1${C_RESET}"
  echo -e "${C_HEADER}================================================================${C_RESET}"
  echo
}

step() {
  local num="$1"
  local text="$2"
  local status="${3:-...}"

  case "$status" in
    OK)    icon="[OK]";   color="$C_SUCCESS" ;;
    SKIP)  icon="[SKIP]"; color="$C_WARNING" ;;
    FAIL)  icon="[FAIL]"; color="$C_ERROR" ;;
    *)     icon="[...]";  color="$C_INFO" ;;
  esac

  echo -e "  ${color}${icon}${C_RESET} ${num}. ${text}"
}

show_help() {
  header "BATCH AUTO-ADVANCE SYSTEM - Ayuda"
  cat <<EOF
Uso:
  ./start_batch_auto.sh
  ./start_batch_auto.sh --batch 5
  ./start_batch_auto.sh --interval 30
  ./start_batch_auto.sh --no-monitor

Parámetros:
  --batch N        Batch inicial (default: 1)
  --interval N     Intervalo de chequeo en segundos (default: 60)
  --no-monitor     No iniciar batch monitor
  --help           Mostrar ayuda

Servicios:
  - Prodigy Manager : 8085
  - POS             : 8080
  - Features        : 8081
  - Relations       : 8082
EOF
}

# -------------------------
# Parse args
# -------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --batch)     BATCH="$2"; shift 2 ;;
    --interval)  INTERVAL="$2"; shift 2 ;;
    --no-monitor) NO_MONITOR=true; shift ;;
    --help)      show_help; exit 0 ;;
    *) echo "Argumento desconocido: $1"; exit 1 ;;
  esac
done

cd "$SCRIPT_DIR"

header "BATCH AUTO-ADVANCE SYSTEM"

echo -e "${C_INFO}  Configuración:${C_RESET}"
echo "    Batch inicial:     $BATCH"
echo "    Intervalo:         ${INTERVAL}s"
echo "    Batch Monitor:     $( $NO_MONITOR && echo Deshabilitado || echo Habilitado )"
echo

# -------------------------
# Load .env
# -------------------------
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
  step 0 "Variables de entorno cargadas" OK
fi

# -------------------------
# Python check
# -------------------------
if command -v python3 >/dev/null; then
  PYTHON=python3
elif command -v python >/dev/null; then
  PYTHON=python
else
  step 1 "Python no encontrado" FAIL
  exit 1
fi
step 1 "Python encontrado: $PYTHON" OK

# -------------------------
# Prodigy check
# -------------------------
if ! $PYTHON -m prodigy --help >/dev/null 2>&1; then
  step 2 "Prodigy no instalado" FAIL
  exit 1
fi
step 2 "Prodigy disponible" OK

# -------------------------
# Start Prodigy Manager
# -------------------------
echo
echo -e "${C_INFO}  Iniciando servicios...${C_RESET}"
echo

$PYTHON prodigy_manager.py --port 8085 &
MANAGER_PID=$!

sleep 3

if ps -p $MANAGER_PID >/dev/null; then
  step 3 "Prodigy Manager iniciado (puerto 8085)" OK
else
  step 3 "Error iniciando Prodigy Manager" FAIL
  exit 1
fi

# -------------------------
# Wait for manager
# -------------------------
echo -e "${C_INFO}  Esperando que el manager esté listo...${C_RESET}"

READY=false
for i in {1..60}; do
  if curl -sf http://localhost:8085/api/status >/dev/null; then
    READY=true
    break
  fi
  sleep 1
  [[ $((i % 10)) -eq 0 ]] && echo -e "${C_WARNING}    ... esperando ($i segundos)${C_RESET}"
done

if ! $READY; then
  step 4 "Manager no responde" FAIL
  kill $MANAGER_PID
  exit 1
fi
step 4 "Manager listo" OK

# -------------------------
# Servicios
# -------------------------
SERVICES=(pos features relations)
declare -A PORTS=( [pos]=8080 [features]=8081 [relations]=8082 )
declare -A SERVICE_BATCH

for s in "${SERVICES[@]}"; do
  SERVICE_BATCH[$s]=$BATCH
done

STATE_FILE="$SCRIPT_DIR/data/batch_monitor_state.json"
if [[ -f "$STATE_FILE" ]]; then
  if jq -e '.current_batch' "$STATE_FILE" >/dev/null 2>&1; then
    for s in "${SERVICES[@]}"; do
      val=$(jq -r ".current_batch.$s // empty" "$STATE_FILE")
      [[ "$val" =~ ^[0-9]+$ ]] && SERVICE_BATCH[$s]=$val
    done
    step "5a" "Batch cargado desde batch_monitor_state.json" OK
  else
    step "5a" "Estado inválido, usando --batch" SKIP
  fi
else
  step "5a" "No existe batch_monitor_state.json" SKIP
fi

# -------------------------
# Start Prodigy services
# -------------------------
for s in "${SERVICES[@]}"; do
  payload=$(jq -n \
    --arg r "batch" \
    --arg a "$s" \
    --argjson b "${SERVICE_BATCH[$s]}" \
    '{recipe:$r, annotation_type:$a, batch_number:$b}')

  if curl -sf \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer internal-monitor" \
    -d "$payload" \
    http://localhost:8085/api/start-prodigy \
    | jq -e '.success' >/dev/null; then

    step 5 "Servicio ${s^^} iniciado (puerto ${PORTS[$s]}, batch ${SERVICE_BATCH[$s]})" OK
  else
    step 5 "Error iniciando $s" FAIL
  fi

  sleep 2
done

# -------------------------
# Cleanup handler
# -------------------------
cleanup() {
  echo
  echo -e "${C_WARNING}  Deteniendo servicios...${C_RESET}"

  for s in "${SERVICES[@]}"; do
    curl -sf -X POST \
      -H "Authorization: Bearer internal-monitor" \
      http://localhost:8085/api/stop-prodigy/$s >/dev/null || true
  done

  kill $MANAGER_PID 2>/dev/null || true
  echo -e "${C_SUCCESS}  Sistema detenido.${C_RESET}"
}
trap cleanup INT TERM

# -------------------------
# Monitor
# -------------------------
header "SISTEMA INICIADO"

if ! $NO_MONITOR; then
  echo -e "${C_INFO}  Iniciando Batch Monitor...${C_RESET}"
  echo
  exec $PYTHON batch_monitor.py --interval "$INTERVAL"
else
  echo -e "${C_WARNING}  Presiona Ctrl+C para detener...${C_RESET}"
  while true; do sleep 5; done
fi
