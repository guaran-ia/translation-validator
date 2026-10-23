#!/bin/bash

set -e

# Use the active Python environment, or set METRICS_PYTHON to an interpreter path.
# Optional uploads use METRICS_DRIVE_REMOTE (an rclone remote and folder).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METRICS_SCRIPT="$SCRIPT_DIR/metrics_report.py"
GUARANI_PROBLEMS_SCRIPT="$SCRIPT_DIR/generar_problemas_guarani.py"
RANKING_TRANSLATIONS_FILE="$SCRIPT_DIR/documents/Ranking_Traducciones_Por_Fecha.docx"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements_metrics.txt"

LOG_DIR="$SCRIPT_DIR/logsMetrics"
LOG_FILE="$LOG_DIR/metrics_report.log"

PYTHON_CMD="${METRICS_PYTHON:-python3}"

REPORT_FILE="$SCRIPT_DIR/documents/Metricas_Plataforma.docx"
USERS_FILE="$SCRIPT_DIR/documents/Listado_Usuarios.xlsx"
USER_TRANSLATIONS_FILE="$SCRIPT_DIR/documents/Traducciones_Por_Usuario.xlsx"
USER_TRANSLATIONS_RAW_FILE="$SCRIPT_DIR/documents/Traducciones_Por_Usuario_Datos_Completos.csv"
USER_VALIDATIONS_FILE="$SCRIPT_DIR/documents/Validaciones_Por_Usuario.xlsx"
USER_VALIDATIONS_RAW_FILE="$SCRIPT_DIR/documents/Validaciones_Por_Usuario_Datos_Completos.csv"
COMPLETE_LIST_FILE="$SCRIPT_DIR/documents/Listado_Completo.xlsx"
VALIDATION_STATUS_FILE="$SCRIPT_DIR/documents/Estado_Validaciones_Premisas.xlsx"
GUARANI_PROBLEMS_FILE="$SCRIPT_DIR/documents/problemas_matematicos_guarani.json"
ACTIVIDAD_GLOBAL_IMG="$SCRIPT_DIR/documents/actividad_global_por_dia.png"
PREMISAS_DIA_IMG="$SCRIPT_DIR/documents/premisas_por_dia.png"
TRADUCCIONES_DIA_IMG="$SCRIPT_DIR/documents/traducciones_por_dia.png"
ACTIVIDAD_GLOBAL_DIARIA_IMG="$SCRIPT_DIR/documents/actividad_global_diaria.png"
ACTIVIDAD_GLOBAL_DIA_HORA_IMG="$SCRIPT_DIR/documents/actividad_global_por_dia_hora.png"

DRIVE_REMOTE="${METRICS_DRIVE_REMOTE:-}"

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

# verificar python
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    log_error "Python no encontrado. Activa tu entorno o configura METRICS_PYTHON."
    exit 1
fi

# verificar script
if [ ! -f "$METRICS_SCRIPT" ]; then
    log_error "Script de métricas no encontrado: $METRICS_SCRIPT"
    exit 1
fi

if [ ! -f "$GUARANI_PROBLEMS_SCRIPT" ]; then
    log_error "Generador de problemas en guaraní no encontrado: $GUARANI_PROBLEMS_SCRIPT"
    exit 1
fi



# ============================================
# EJECUCIÓN
# ============================================

log_message "=== Iniciando generación de métricas ==="

if "$PYTHON_CMD" "$METRICS_SCRIPT" >> "$LOG_FILE" 2>&1; then
    log_message "Métricas generadas exitosamente"

    GUARANI_PROBLEMS_GENERATED=false
    log_message "Generando JSON de problemas matemáticos en guaraní..."
    if "$PYTHON_CMD" "$GUARANI_PROBLEMS_SCRIPT" >> "$LOG_FILE" 2>&1; then
        GUARANI_PROBLEMS_GENERATED=true
        log_message "JSON de problemas matemáticos generado exitosamente"
    else
        log_error "No se generó el JSON de problemas matemáticos; se omite su subida"
    fi

    if [ -z "$DRIVE_REMOTE" ]; then
        log_message "Reportes guardados localmente. Configura METRICS_DRIVE_REMOTE para subirlos con rclone."
        exit 0
    fi
    if ! command -v rclone &> /dev/null; then
        log_error "rclone no está instalado; los reportes se conservaron localmente."
        exit 1
    fi

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
    # SUBIDA EXCEL TRADUCCIONES POR USUARIO
    # ============================================

    if [ -f "$USER_TRANSLATIONS_FILE" ]; then
        log_message "Subiendo traducciones por usuario a Google Drive..."

        rclone copyto \
            "$USER_TRANSLATIONS_FILE" \
            "$DRIVE_REMOTE/Traducciones_Por_Usuario.xlsx" \
            >> "$LOG_FILE" 2>&1

        log_message "Excel de traducciones por usuario actualizado en Google Drive"
    else
        log_error "El archivo Excel no fue generado: $USER_TRANSLATIONS_FILE"
        exit 1
    fi

    # ============================================
    # SUBIDA CSV TRADUCCIONES CRUDAS POR USUARIO
    # ============================================

    if [ -f "$USER_TRANSLATIONS_RAW_FILE" ]; then
        log_message "Subiendo CSV crudo de traducciones por usuario a Google Drive..."

        rclone copyto \
            "$USER_TRANSLATIONS_RAW_FILE" \
            "$DRIVE_REMOTE/Traducciones_Por_Usuario_Datos_Completos.csv" \
            >> "$LOG_FILE" 2>&1

        log_message "CSV crudo de traducciones por usuario actualizado en Google Drive"
    else
        log_error "El archivo CSV no fue generado: $USER_TRANSLATIONS_RAW_FILE"
        exit 1
    fi

    # ============================================
    # SUBIDA EXCEL VALIDACIONES POR USUARIO
    # ============================================

    if [ -f "$USER_VALIDATIONS_FILE" ]; then
        log_message "Subiendo validaciones por usuario a Google Drive..."

        rclone copyto \
            "$USER_VALIDATIONS_FILE" \
            "$DRIVE_REMOTE/Validaciones_Por_Usuario.xlsx" \
            >> "$LOG_FILE" 2>&1

        log_message "Excel de validaciones por usuario actualizado en Google Drive"
    else
        log_error "El archivo Excel no fue generado: $USER_VALIDATIONS_FILE"
        exit 1
    fi

    # ============================================
    # SUBIDA CSV VALIDACIONES CRUDAS POR USUARIO
    # ============================================

    if [ -f "$USER_VALIDATIONS_RAW_FILE" ]; then
        log_message "Subiendo CSV crudo de validaciones por usuario a Google Drive..."

        rclone copyto \
            "$USER_VALIDATIONS_RAW_FILE" \
            "$DRIVE_REMOTE/Validaciones_Por_Usuario_Datos_Completos.csv" \
            >> "$LOG_FILE" 2>&1

        log_message "CSV crudo de validaciones por usuario actualizado en Google Drive"
    else
        log_error "El archivo CSV no fue generado: $USER_VALIDATIONS_RAW_FILE"
        exit 1
    fi

    # ============================================
    # SUBIDA EXCEL LISTADO COMPLETO
    # ============================================

    if [ -f "$COMPLETE_LIST_FILE" ]; then
        log_message "Subiendo listado completo a Google Drive..."

        rclone copyto \
            "$COMPLETE_LIST_FILE" \
            "$DRIVE_REMOTE/Listado_Completo.xlsx" \
            >> "$LOG_FILE" 2>&1

        log_message "Excel de listado completo actualizado en Google Drive"
    else
        log_error "El archivo Excel no fue generado: $COMPLETE_LIST_FILE"
        exit 1
    fi

    # ============================================
    # SUBIDA EXCEL ESTADO DE VALIDACIONES POR PREMISA
    # ============================================

    if [ -f "$VALIDATION_STATUS_FILE" ]; then
        log_message "Subiendo estado de validaciones por premisa a Google Drive..."

        rclone copyto \
            "$VALIDATION_STATUS_FILE" \
            "$DRIVE_REMOTE/Estado_Validaciones_Premisas.xlsx" \
            >> "$LOG_FILE" 2>&1

        log_message "Excel de estado de validaciones por premisa actualizado en Google Drive"
    else
        log_error "El archivo Excel no fue generado: $VALIDATION_STATUS_FILE"
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

# ============================================
# SUBIDA WORD RANKING TRADUCCIONES POR FECHA
# ============================================

if [ -f "$RANKING_TRANSLATIONS_FILE" ]; then
    log_message "Subiendo reporte ranking de traducciones a Google Drive..."

    rclone copyto \
        "$RANKING_TRANSLATIONS_FILE" \
        "$DRIVE_REMOTE/Ranking_Traducciones_Por_Fecha.docx" \
        >> "$LOG_FILE" 2>&1

    log_message "Reporte ranking de traducciones actualizado en Google Drive"
else
    log_message "Reporte ranking de traducciones no existe, se omite subida"
fi

# ============================================
# SUBIDA JSON PROBLEMAS MATEMÁTICOS EN GUARANÍ
# ============================================

if [ "$GUARANI_PROBLEMS_GENERATED" = true ] && [ -f "$GUARANI_PROBLEMS_FILE" ]; then
    log_message "Subiendo problemas matemáticos en guaraní a Google Drive..."

    rclone copyto \
        "$GUARANI_PROBLEMS_FILE" \
        "$DRIVE_REMOTE/problemas_matematicos_guarani.json" \
        >> "$LOG_FILE" 2>&1

    log_message "JSON de problemas matemáticos actualizado en Google Drive"
else
    log_message "JSON de problemas matemáticos no disponible, se omite subida"
fi

exit 0

else
    EXIT_CODE=$?
    log_error "❌ Error al generar métricas (código: $EXIT_CODE)"
    exit $EXIT_CODE
fi
