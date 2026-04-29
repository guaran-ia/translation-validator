#!/bin/bash

set -e

# ============================================
# PYENV CONFIG
# ============================================

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

eval "$(pyenv init -)"

# ============================================
# CONFIGURACIÓN
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METRICS_SCRIPT="$SCRIPT_DIR/metrics_report.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements_metrics.txt"

LOG_DIR="/logsMetrics"
LOG_FILE="$LOG_DIR/metrics_report.log"

PYTHON_CMD="python"

REPORT_FILE="$SCRIPT_DIR/Metricas_Plataforma.docx"
DRIVE_REMOTE="drive:Estadisticas Mbo'ehara Digital"

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# ============================================
# FUNCIONES
# ============================================

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# ============================================
# VALIDACIONES
# ============================================

cd "$SCRIPT_DIR"

# activar entorno pyenv del proyecto (usa .python-version si existe)
if ! pyenv version &> /dev/null; then
    log_error "pyenv no está correctamente configurado"
    exit 1
fi

# verificar python
if ! command -v $PYTHON_CMD &> /dev/null; then
    log_error "Python no encontrado en pyenv"
    exit 1
fi

# verificar script
if [ ! -f "$METRICS_SCRIPT" ]; then
    log_error "Script de métricas no encontrado: $METRICS_SCRIPT"
    exit 1
fi

# ============================================
# INSTALACIÓN DE DEPENDENCIAS
# ============================================

if [ -f "$REQUIREMENTS_FILE" ]; then
    log_message "Instalando/verificando dependencias..."
    $PYTHON_CMD -m pip install -r "$REQUIREMENTS_FILE" >> "$LOG_FILE" 2>&1
else
    log_error "No se encontró requirements_metrics.txt"
    exit 1
fi

# ============================================
# EJECUCIÓN
# ============================================

log_message "=== Iniciando generación de métricas ==="

if $PYTHON_CMD "$METRICS_SCRIPT" >> "$LOG_FILE" 2>&1; then
    log_message "Métricas generadas exitosamente"

    # ============================================
    # SUBIDA A GOOGLE DRIVE (REEMPLAZA)
    # ============================================

    if [ -f "$REPORT_FILE" ]; then
        log_message "Subiendo reporte a Google Drive..."
        rclone copyto "$REPORT_FILE" "$DRIVE_REMOTE/Metricas_Plataforma.docx" >> "$LOG_FILE" 2>&1
        log_message "Reporte actualizado en Google Drive"
    else
        log_error "El archivo no fue generado: $REPORT_FILE"
        exit 1
    fi

    exit 0
else
    EXIT_CODE=$?
    log_error "❌ Error al generar métricas (código: $EXIT_CODE)"
    exit $EXIT_CODE
fi