#!/bin/bash

set -e

# ============================================
# PYENV CONFIG
# ============================================

export HOME="/home/clugo"
export PYENV_ROOT="/opt/pyenv"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:/usr/local/bin:/usr/bin:/bin:$PATH"

eval "$("$PYENV_ROOT/bin/pyenv" init -)"


# ============================================
# CONFIGURACIÓN
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METRICS_SCRIPT="$SCRIPT_DIR/metrics_report.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements_metrics.txt"

LOG_DIR="$SCRIPT_DIR/logsMetrics"
LOG_FILE="$LOG_DIR/metrics_report.log"

PYTHON_CMD="$PYENV_ROOT/shims/python"

REPORT_FILE="$SCRIPT_DIR/documents/Metricas_Plataforma.docx"
USERS_FILE="$SCRIPT_DIR/documents/Listado_Usuarios.xlsx"
ACTIVIDAD_GLOBAL_IMG="$SCRIPT_DIR/documents/actividad_global_por_dia.png"
PREMISAS_DIA_IMG="$SCRIPT_DIR/documents/premisas_por_dia.png"
TRADUCCIONES_DIA_IMG="$SCRIPT_DIR/documents/traducciones_por_dia.png"
ACTIVIDAD_GLOBAL_DIARIA_IMG="$SCRIPT_DIR/documents/actividad_global_diaria.png"
ACTIVIDAD_GLOBAL_DIA_HORA_IMG="$SCRIPT_DIR/documents/actividad_global_por_dia_hora.png"

DRIVE_REMOTE="gdrive:Mboehara/Estadisticas"

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
if ! "$PYENV_ROOT/bin/pyenv" version &> /dev/null; then
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
# EJECUCIÓN
# ============================================

log_message "=== Iniciando generación de métricas ==="

if $PYTHON_CMD "$METRICS_SCRIPT" >> "$LOG_FILE" 2>&1; then
    log_message "Métricas generadas exitosamente"

   # ============================================
# SUBIDA WORD
# ============================================

if [ -f "$REPORT_FILE" ]; then
    log_message "Subiendo documento de métricas a Google Drive..."

    rclone copyto \
        "$REPORT_FILE" \
        "$DRIVE_REMOTE/Metricas_Plataforma.docx" \
        >> "$LOG_FILE" 2>&1

        log_message "Documento Word actualizado en Google Drive"
    else
        log_error "El archivo Word no fue generado: $REPORT_FILE"
        exit 1
    fi

    # ============================================
    # SUBIDA EXCEL USUARIOS
    # ============================================

    if [ -f "$USERS_FILE" ]; then
        log_message "Subiendo listado de usuarios a Google Drive..."

        rclone copyto \
            "$USERS_FILE" \
            "$DRIVE_REMOTE/Listado_Usuarios.xlsx" \
            >> "$LOG_FILE" 2>&1

        log_message "Excel de usuarios actualizado en Google Drive"
    else
        log_error "El archivo Excel no fue generado: $USERS_FILE"
        exit 1
    fi

   # ============================================
# SUBIDA PNG ACTIVIDAD GLOBAL
# ============================================

if [ -f "$ACTIVIDAD_GLOBAL_IMG" ]; then
    log_message "Subiendo gráfico actividad_global_por_dia.png a Google Drive..."

    rclone copyto \
        "$ACTIVIDAD_GLOBAL_IMG" \
        "$DRIVE_REMOTE/actividad_global_por_dia.png" \
        >> "$LOG_FILE" 2>&1

    log_message "Gráfico actividad_global_por_dia.png actualizado en Google Drive"
else
    log_error "El gráfico no fue generado: $ACTIVIDAD_GLOBAL_IMG"
    exit 1
fi


# ============================================
# SUBIDA PNG PREMISAS POR DÍA
# ============================================

if [ -f "$PREMISAS_DIA_IMG" ]; then
    log_message "Subiendo gráfico premisas_por_dia.png a Google Drive..."

    rclone copyto \
        "$PREMISAS_DIA_IMG" \
        "$DRIVE_REMOTE/premisas_por_dia.png" \
        >> "$LOG_FILE" 2>&1

    log_message "Gráfico premisas_por_dia.png actualizado en Google Drive"
else
    log_error "El gráfico no fue generado: $PREMISAS_DIA_IMG"
    exit 1
fi


# ============================================
# SUBIDA PNG TRADUCCIONES POR DÍA
# ============================================

if [ -f "$TRADUCCIONES_DIA_IMG" ]; then
    log_message "Subiendo gráfico traducciones_por_dia.png a Google Drive..."

    rclone copyto \
        "$TRADUCCIONES_DIA_IMG" \
        "$DRIVE_REMOTE/traducciones_por_dia.png" \
        >> "$LOG_FILE" 2>&1

    log_message "Gráfico traducciones_por_dia.png actualizado en Google Drive"
else
    log_error "El gráfico no fue generado: $TRADUCCIONES_DIA_IMG"
    exit 1
fi

# ============================================
# SUBIDA PNG ACTIVIDAD GLOBAL DIARIA
# ============================================

if [ -f "$ACTIVIDAD_GLOBAL_DIARIA_IMG" ]; then
    log_message "Subiendo gráfico actividad_global_diaria.png a Google Drive..."

    rclone copyto \
        "$ACTIVIDAD_GLOBAL_DIARIA_IMG" \
        "$DRIVE_REMOTE/actividad_global_diaria.png" \
        >> "$LOG_FILE" 2>&1

    log_message "Gráfico actividad_global_diaria.png actualizado en Google Drive"
else
    log_error "El gráfico no fue generado: $ACTIVIDAD_GLOBAL_DIARIA_IMG"
    exit 1
fi

# ============================================
# SUBIDA PNG ACTIVIDAD GLOBAL POR DÍA Y HORA
# ============================================

if [ -f "$ACTIVIDAD_GLOBAL_DIA_HORA_IMG" ]; then
    log_message "Subiendo mapa de calor actividad_global_por_dia_hora.png a Google Drive..."

    rclone copyto \
        "$ACTIVIDAD_GLOBAL_DIA_HORA_IMG" \
        "$DRIVE_REMOTE/actividad_global_por_dia_hora.png" \
        >> "$LOG_FILE" 2>&1

    log_message "Mapa de calor actividad_global_por_dia_hora.png actualizado en Google Drive"
else
    log_error "El mapa de calor no fue generado: $ACTIVIDAD_GLOBAL_DIA_HORA_IMG"
    exit 1
fi

exit 0

else
    EXIT_CODE=$?
    log_error "❌ Error al generar métricas (código: $EXIT_CODE)"
    exit $EXIT_CODE
fi
