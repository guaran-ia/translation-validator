#!/usr/bin/env python3
"""
Script para generar métricas de la base de datos Translation Validator.
Genera reportes sobre usuarios, anotaciones, asignaciones y traducciones.
"""

import psycopg2
from psycopg2 import sql, Error
from datetime import datetime
import sys
import os
import csv
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


# Configuración de la base de datos
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/translation_validator"

# está 3 horas adelantado
SERVER_AHEAD_HOURS = 3

TIME_SUB_SQL = f" - INTERVAL '{SERVER_AHEAD_HOURS} hours'"


def get_connection():
    """
    Establece conexión con PostgreSQL.
    
    Returns:
        psycopg2.connection: Conexión a la base de datos
        
    Raises:
        Error: Si hay problemas al conectarse
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        sys.exit(1)


def execute_query(conn, query):
    """
    Ejecuta una query y retorna el resultado.
    
    Args:
        conn: Conexión a la base de datos
        query: Query SQL a ejecutar
        
    Returns:
        list: Resultados de la query
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as e:
        print(f"❌ Error ejecutando query: {e}")
        return None


def get_user_metrics(conn):
    """
    Obtiene métricas de usuarios.
    
    Args:
        conn: Conexión a la base de datos
        
    Returns:
        dict: Métricas de usuarios
    """
    metrics = {}
    
    # Total de usuarios
    result = execute_query(conn, "SELECT COUNT(*) FROM users;")
    metrics['total_usuarios'] = result[0][0] if result else 0
    
    # Usuarios nuevos en los últimos 2 días agrupados por fecha
    query_new_users = f"""
    SELECT DATE(created_at{TIME_SUB_SQL}) AS fecha, COUNT(*) AS total
    FROM users
    WHERE (created_at{TIME_SUB_SQL}) >= NOW() - INTERVAL '2 days'
    GROUP BY DATE(created_at{TIME_SUB_SQL})
    ORDER BY fecha;
    """
    result = execute_query(conn, query_new_users)
    metrics['usuarios_nuevos_2dias'] = {
        str(row[0]): row[1] for row in result
    } if result else {}
    
    return metrics


def get_annotation_metrics(conn):
    """
    Obtiene métricas de anotaciones y traducciones.
    
    Args:
        conn: Conexión a la base de datos
        
    Returns:
        dict: Métricas de anotaciones
    """
    metrics = {}
    
    # Traducciones completadas en total
    result = execute_query(
        conn,
        "SELECT COUNT(*) FROM annotations WHERE translated = true;"
    )
    metrics['traducciones_completadas_total'] = result[0][0] if result else 0
    
    # Traducciones completadas en los últimos 2 días
    query_recent = f"""
    SELECT COUNT(*)
    FROM annotations
    WHERE translated = true
    AND (updated_at{TIME_SUB_SQL}) >= NOW() - INTERVAL '2 days';
    """
    result = execute_query(conn, query_recent)
    metrics['traducciones_completadas_2dias'] = result[0][0] if result else 0
    
    return metrics


def get_assignment_metrics(conn):
    """
    Obtiene métricas de asignaciones de anotaciones.
    
    Args:
        conn: Conexión a la base de datos
        
    Returns:
        dict: Métricas de asignaciones
    """
    metrics = {}
    
    # Total de asignaciones
    result = execute_query(
        conn,
        "SELECT COUNT(*) FROM annotation_assignments;"
    )
    metrics['asignaciones_totales'] = result[0][0] if result else 0

    # Total de premisas disponibles en la plataforma
    result = execute_query(conn, "SELECT COUNT(*) FROM annotations;")
    metrics['annotations_totales'] = result[0][0] if result else 0
    
    # Asignaciones en los últimos 2 días
    query_recent = f"""
    SELECT COUNT(*)
    FROM annotation_assignments
    WHERE (assigned_at{TIME_SUB_SQL}) >= NOW() - INTERVAL '2 days';
    """
    result = execute_query(conn, query_recent)
    metrics['asignaciones_2dias'] = result[0][0] if result else 0
    
    # Annotations distintas tomadas por usuarios
    result = execute_query(
        conn,
        "SELECT COUNT(DISTINCT annotation_id) FROM annotation_assignments;"
    )
    metrics['annotations_tomadas_usuarios'] = result[0][0] if result else 0
    
    return metrics


def get_translation_metrics(conn):
    """
    Obtiene métricas de traducciones y detección de tareas abandonadas.
    
    Args:
        conn: Conexión a la base de datos
        
    Returns:
        dict: Métricas de traducciones
    """
    metrics = {}
    
    # Anotaciones con al menos una traducción
    result = execute_query(
        conn,
        "SELECT COUNT(DISTINCT annotation_id) FROM annotation_translations;"
    )
    metrics['annotations_con_traduccion'] = result[0][0] if result else 0
    
    # Anotaciones sin traducciones
    query_no_trans = """
    SELECT COUNT(*)
    FROM annotations a
    LEFT JOIN annotation_translations t ON t.annotation_id = a.id
    WHERE t.id IS NULL;
    """
    result = execute_query(conn, query_no_trans)
    metrics['annotations_sin_traduccion'] = result[0][0] if result else 0
    
    # Anotaciones asignadas pero sin traducción (tareas abandonadas)
    query_abandoned = """
    SELECT COUNT(DISTINCT aa.annotation_id)
    FROM annotation_assignments aa
    LEFT JOIN annotation_translations t ON t.annotation_id = aa.annotation_id
    WHERE t.id IS NULL;
    """
    result = execute_query(conn, query_abandoned)
    metrics['annotations_asignadas_sin_traduccion'] = result[0][0] if result else 0
    
    return metrics


def get_user_breakdown_metrics(conn):
    """
    Obtiene métricas desglosadas sobre usuarios y sus actividades.
    
    Args:
        conn: Conexión a la base de datos
        
    Returns:
        dict: Métricas desglosadas de usuarios
    """
    metrics = {}
    
    # Usuarios que se registraron pero no se asignaron ninguna premisa
    query_no_assignments = """
    SELECT COUNT(*) AS users_without_assignments
    FROM users u
    LEFT JOIN annotation_assignments aa
      ON aa.user_id = u.id
    WHERE aa.id IS NULL;
    """
    result = execute_query(conn, query_no_assignments)
    metrics['users_without_assignments'] = result[0][0] if result else 0
    
    # Usuarios que se asignaron una premisa pero no completaron ninguna traducción
    query_no_translations = """
    SELECT COUNT(DISTINCT u.id) AS users_with_assignments_without_translations
    FROM users u
    INNER JOIN annotation_assignments aa
        ON aa.user_id = u.id
    LEFT JOIN annotation_translations at
        ON at.annotation_id = aa.annotation_id
       AND at.user_id = u.id
    WHERE at.id IS NULL;
    """
    result = execute_query(conn, query_no_translations)
    metrics['users_with_assignments_without_translations'] = result[0][0] if result else 0
    
    # Usuarios que completaron al menos una traducción
    query_with_translations = """
    SELECT COUNT(DISTINCT u.id) AS users_with_completed_translations
    FROM users u
    INNER JOIN annotation_translations at
      ON at.user_id = u.id;
    """
    result = execute_query(conn, query_with_translations)
    metrics['users_with_completed_translations'] = result[0][0] if result else 0
    
    return metrics


def generate_report(metrics_data):
    """
    Genera un reporte formateado con las métricas.
    
    Args:
        metrics_data: Diccionario con todas las métricas
    """
    report = f"""
{'='*70}
REPORTE DE MÉTRICAS - TRANSLATION VALIDATOR
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}

MÉTRICAS DE USUARIOS
{'-'*70}
  Total de usuarios: {metrics_data['usuarios']['total_usuarios']}
  
  Usuarios nuevos (últimos 2 días):
  {_format_dict(metrics_data['usuarios']['usuarios_nuevos_2dias'])}

MÉTRICAS DE ANOTACIONES
{'-'*70}
  Traducciones completadas (total): {metrics_data['anotaciones']['traducciones_completadas_total']}
  Traducciones completadas (últimos 2 días): {metrics_data['anotaciones']['traducciones_completadas_2dias']}

MÉTRICAS DE ASIGNACIONES
{'-'*70}
  Total de asignaciones: {metrics_data['asignaciones']['asignaciones_totales']}
  Asignaciones (últimos 2 días): {metrics_data['asignaciones']['asignaciones_2dias']}
  Annotations distintas tomadas por usuarios: {metrics_data['asignaciones']['annotations_tomadas_usuarios']}

MÉTRICAS DE TRADUCCIONES
{'-'*70}
  Annotations con al menos una traducción: {metrics_data['traducciones']['annotations_con_traduccion']}
  Annotations sin traducciones: {metrics_data['traducciones']['annotations_sin_traduccion']}
   Annotations asignadas pero SIN traducción (tareas abandonadas): {metrics_data['traducciones']['annotations_asignadas_sin_traduccion']}

{'='*70}
"""
    print(report)
    return report


def _format_dict(d):
    """
    Formatea un diccionario para visualización.
    
    Args:
        d: Diccionario a formatear
        
    Returns:
        str: Diccionario formateado
    """
    if not d:
        return "    Sin datos"
    return "\n  ".join([f"{k}: {v}" for k, v in d.items()])


def ensure_documents_folder():
    """
    Asegura que existe la carpeta 'documents' en la raíz del proyecto.
    
    Returns:
        Path: Ruta a la carpeta documents
    """
    documents_folder = Path(__file__).parent / "documents"
    documents_folder.mkdir(exist_ok=True)
    return documents_folder


def create_metrics_table_in_docx(doc, metrics_data):
    """
    Crea una tabla con las métricas en el documento Word.
    
    Args:
        doc: Documento de python-docx
        metrics_data: Diccionario con las métricas
    """
    # Título con fecha
    title = doc.add_paragraph()
    title_run = title.add_run(f" REPORTE DE MÉTRICAS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    title_run.bold = True
    title_run.font.size = Pt(14)
    title_run.font.color.rgb = RGBColor(0, 102, 204)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Separador
    doc.add_paragraph("_" * 80)
    
    # USUARIOS
    heading_users = doc.add_paragraph(" MÉTRICAS DE USUARIOS DE LA PLATAFORMA")
    heading_users_run = heading_users.runs[0]
    heading_users_run.bold = True
    heading_users_run.font.size = Pt(12)
    
    p = doc.add_paragraph(f"Total de usuarios: {metrics_data['usuarios']['total_usuarios']}")
    
    if metrics_data['usuarios']['usuarios_nuevos_2dias']:
        doc.add_paragraph("Usuarios nuevos (últimos 2 días):")
        for fecha, total in metrics_data['usuarios']['usuarios_nuevos_2dias'].items():
            doc.add_paragraph(f"  • {fecha}: {total}", style='List Bullet 2')
    else:
        doc.add_paragraph("Usuarios nuevos (últimos 2 días): Sin usuarios nuevos")
    
    # ANOTACIONES
    heading_annot = doc.add_paragraph(" MÉTRICAS DE ANOTACIONES")
    heading_annot_run = heading_annot.runs[0]
    heading_annot_run.bold = True
    heading_annot_run.font.size = Pt(12)
    
    doc.add_paragraph(f"Traducciones completadas (total): {metrics_data['anotaciones']['traducciones_completadas_total']}")
    doc.add_paragraph(f"Traducciones completadas (últimos 2 días): {metrics_data['anotaciones']['traducciones_completadas_2dias']}")
    
    # ASIGNACIONES
    heading_assign = doc.add_paragraph(" MÉTRICAS DE ASIGNACIONES")
    heading_assign_run = heading_assign.runs[0]
    heading_assign_run.bold = True
    heading_assign_run.font.size = Pt(12)
    
    doc.add_paragraph(f"Total de premisas asignadas: {metrics_data['asignaciones']['asignaciones_totales']}")
    doc.add_paragraph(f"Premisas asignadas (últimos 2 días): {metrics_data['asignaciones']['asignaciones_2dias']}")
    doc.add_paragraph(f"Premisas tomadas por usuarios: {metrics_data['asignaciones']['annotations_tomadas_usuarios']}/{metrics_data['asignaciones']['annotations_totales']}")
    
    # TRADUCCIONES
    heading_trans = doc.add_paragraph(" MÉTRICAS DE TRADUCCIONES")
    heading_trans_run = heading_trans.runs[0]
    heading_trans_run.bold = True
    heading_trans_run.font.size = Pt(12)
    
    doc.add_paragraph(f"Premisas con al menos una traducción: {metrics_data['traducciones']['annotations_con_traduccion']}")
    doc.add_paragraph(f"Premisas sin traducciones: {metrics_data['traducciones']['annotations_sin_traduccion']}")
    
    # Tareas abandonadas en rojo
    p_abandoned = doc.add_paragraph()
    run_abandoned = p_abandoned.add_run(f"Premisas asignadas pero SIN traducción por el momento: {metrics_data['traducciones']['annotations_asignadas_sin_traduccion']}")
    # MÉTRICAS DE USUARIOS
    heading_user_breakdown = doc.add_paragraph(" MÉTRICAS DE USUARIOS")
    heading_user_breakdown_run = heading_user_breakdown.runs[0]
    heading_user_breakdown_run.bold = True
    heading_user_breakdown_run.font.size = Pt(12)
    # Agregar las 3 métricas como lista o párrafos
    doc.add_paragraph(
        f"Usuarios que se registraron en la plataforma, pero no se asignaron ninguna premisa: {metrics_data['user_breakdown']['users_without_assignments']}",
        style='List Bullet'
    )
    doc.add_paragraph(
        f"Usuarios que se asignaron una premisa, pero no completaron ninguna traducción: {metrics_data['user_breakdown']['users_with_assignments_without_translations']}",
        style='List Bullet'
    )
    doc.add_paragraph(
        f"Usuarios que completaron al menos una traducción en la plataforma: {metrics_data['user_breakdown']['users_with_completed_translations']}",
        style='List Bullet'
    )
    
    final_note = doc.add_paragraph("Se puede ver el desglose de usuarios en el otro documento word situado en el drive")
    final_note_run = final_note.runs[0]
    final_note_run.italic = True
    final_note_run.font.size = Pt(10)
    
    # Separador final
    doc.add_paragraph("_" * 80)
    doc.add_paragraph()  # Espacio en blanco
    doc.add_paragraph()
    doc.add_paragraph()


def update_metrics_docx(metrics_data, documents_folder):
    """
    Actualiza el documento de métricas en Word.
    Prepende las nuevas métricas al principio del documento.
    
    Args:
        metrics_data: Diccionario con las métricas
        documents_folder: Ruta a la carpeta documents
    """
    try:
        docx_path = documents_folder / "Metricas_Plataforma.docx"
        
        # Si el documento existe, leer su contenido anterior
        if docx_path.exists():
            old_doc = Document(docx_path)
            old_paragraphs = []
            old_tables = []
            
            # Guardar paragrafos anteriores
            for para in old_doc.paragraphs:
                old_paragraphs.append({
                    'text': para.text,
                    'style': para.style,
                    'alignment': para.alignment,
                    'runs': [(run.text, run.bold, run.italic, run.font.size, run.font.color.rgb if run.font.color.rgb else None) for run in para.runs]
                })
            
            # Crear documento nuevo
            doc = Document()
        else:
            doc = Document()
            old_paragraphs = []
        
        # Agregar las nuevas métricas al inicio
        create_metrics_table_in_docx(doc, metrics_data)
        
        # Si había contenido anterior, agregarlo después de las nuevas métricas
        if old_paragraphs:
            doc.add_paragraph()  # Espacio
            heading_previous = doc.add_paragraph("REPORTES ANTERIORES")
            heading_previous_run = heading_previous.runs[0]
            heading_previous_run.bold = True
            heading_previous_run.font.size = Pt(11)
            heading_previous_run.font.color.rgb = RGBColor(128, 128, 128)
            doc.add_paragraph()
            
            # Agregar los párrafos anteriores
            for para_data in old_paragraphs:
                new_para = doc.add_paragraph(para_data['text'], style=para_data['style'])
                new_para.alignment = para_data['alignment']
        
        # Guardar documento
        doc.save(str(docx_path))
        print(f"Documento Word guardado en: {docx_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar el documento Word: {e}")
        return False


def generate_users_excel(conn, output_path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from datetime import datetime
    query = f"""
WITH assignment_stats AS (
    SELECT
        user_id,
        COUNT(DISTINCT annotation_id) AS premisas_asignadas,
        AVG(EXTRACT(EPOCH FROM (assigned_at{TIME_SUB_SQL})::time)) AS avg_assignment_seconds
    FROM annotation_assignments
    GROUP BY user_id
),
translation_stats AS (
    SELECT
        user_id,
        COUNT(*) AS traducciones_completadas,
        AVG(EXTRACT(EPOCH FROM (created_at{TIME_SUB_SQL})::time)) AS avg_translation_seconds
    FROM annotation_translations
    GROUP BY user_id
),
activity_stats AS (
    SELECT
        user_id,
        AVG(activity_seconds) AS avg_activity_seconds
    FROM (
        SELECT
            user_id,
            EXTRACT(EPOCH FROM (assigned_at{TIME_SUB_SQL})::time) AS activity_seconds
        FROM annotation_assignments

        UNION ALL

        SELECT
            user_id,
            EXTRACT(EPOCH FROM (created_at{TIME_SUB_SQL})::time) AS activity_seconds
        FROM annotation_translations
    ) activity
    GROUP BY user_id
)
SELECT
    u.id,
    u.nombre_completo,
    u.email,
    u.contacto,

    COALESCE(a.premisas_asignadas, 0) AS premisas_asignadas,
    COALESCE(t.traducciones_completadas, 0) AS traducciones_completadas,

    CASE
        WHEN COALESCE(a.premisas_asignadas, 0) = 0
         AND COALESCE(t.traducciones_completadas, 0) = 0
            THEN 'inactivo'

        WHEN COALESCE(a.premisas_asignadas, 0) > 0
         AND COALESCE(t.traducciones_completadas, 0) = 0
            THEN 'activo'

        WHEN COALESCE(t.traducciones_completadas, 0) > 0
            THEN 'muy activo'
    END AS estado,

    TO_CHAR(
        make_interval(secs => ROUND(a.avg_assignment_seconds)::int),
        'HH24:MI'
    ) AS hora_promedio_asignacion,

    TO_CHAR(
        make_interval(secs => ROUND(t.avg_translation_seconds)::int),
        'HH24:MI'
    ) AS hora_promedio_traduccion,

    TO_CHAR(
        make_interval(secs => ROUND(act.avg_activity_seconds)::int),
        'HH24:MI'
    ) AS hora_promedio_activo

        -- Determinar turno según la hora promedio de actividad (hora local ajustada)
        , CASE
                WHEN act.avg_activity_seconds IS NULL THEN 'Desconocido'
                WHEN FLOOR(act.avg_activity_seconds/3600)::int BETWEEN 5 AND 11 THEN 'Mañana'
                WHEN FLOOR(act.avg_activity_seconds/3600)::int BETWEEN 12 AND 13 THEN 'Siesta'
                WHEN FLOOR(act.avg_activity_seconds/3600)::int BETWEEN 14 AND 18 THEN 'Tarde'
                ELSE 'Noche'
            END AS turno

FROM users u
LEFT JOIN assignment_stats a
    ON a.user_id = u.id
LEFT JOIN translation_stats t
    ON t.user_id = u.id
LEFT JOIN activity_stats act
    ON act.user_id = u.id
ORDER BY
    CASE
        WHEN COALESCE(t.traducciones_completadas, 0) > 0 THEN 1
        WHEN COALESCE(a.premisas_asignadas, 0) > 0 THEN 2
        ELSE 3
    END,
    COALESCE(t.traducciones_completadas, 0) DESC,
    COALESCE(a.premisas_asignadas, 0) DESC;
    """

    result = execute_query(conn, query)

    if result is None:
        print("No se obtuvo resultado para la query de usuarios. Comprueba la query y la conexión.")
        return False

    wb = Workbook()
    ws = wb.active
    ws.title = "Usuarios"

    # Header info
    ws["A1"] = "Última actualización"
    ws["B1"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    ws["A3"] = "Listado de usuarios"
    ws["A3"].font = Font(size=14, bold=True)

    headers = [
        "Nombre completo",
        "Email",
        "Contacto",
        "Estado",
        "Traducciones realizadas",
        "Premisas asignadas",
        "Hora promedio asignación",
        "Hora promedio traducción",
        "Hora promedio activo",
        "Turno",
    ]

    ws.append([])
    ws.append(headers)

    # Estilo header
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=5, column=col)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", fill_type="solid")

    # Activar filtros en encabezados
    ws.auto_filter.ref = f"A5:{get_column_letter(len(headers))}5"
    # Freeze panes para mantener encabezados visibles
    ws.freeze_panes = "A6"

    # Datos: mapear con tolerancia a filas con menos columnas
    row_index = 6
    for row in result:
        # Mapear columnas según la query nueva
        full_name = row[1] if len(row) > 1 else ''
        email = row[2] if len(row) > 2 else ''
        contact = row[3] if len(row) > 3 else ''
        premises = row[4] if len(row) > 4 else 0
        translations = row[5] if len(row) > 5 else 0
        estado = row[6] if len(row) > 6 else ''

        hora_asign = row[7] if len(row) > 7 and row[7] is not None else '-'
        hora_trad = row[8] if len(row) > 8 and row[8] is not None else '-'
        hora_act = row[9] if len(row) > 9 and row[9] is not None else '-'
        turno = row[10] if len(row) > 10 and row[10] is not None else '-'

        ws.append([
            full_name,
            email,
            contact or '',
            estado,
            translations,
            premises,
            hora_asign,
            hora_trad,
            hora_act,
            turno,
        ])

        # Colorear estado (tolerante a mayúsculas/minúsculas)
        est_norm = (estado or '').lower()
        if est_norm == "muy activo":
            fill = PatternFill(start_color="C6EFCE", fill_type="solid")  # verde
        elif est_norm == "activo":
            fill = PatternFill(start_color="FFEB9C", fill_type="solid")  # amarillo
        else:
            fill = PatternFill(start_color="FFC7CE", fill_type="solid")  # rojo

        ws.cell(row=row_index, column=4).fill = fill
        row_index += 1

    # Auto width
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)

        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass

        ws.column_dimensions[col_letter].width = max_length + 2

    file_path = output_path / "Listado_Usuarios.xlsx"
    wb.save(file_path)

    print(f"Excel generado en: {file_path}")
    return True


def generate_user_translations_excel(conn, output_path):
    query = f"""
SELECT
    u.id AS user_id,
    u.nombre_completo,
    u.email,
    at.created_at{TIME_SUB_SQL} AS fecha_traduccion,
    a.id AS annotation_id,
    a.question_es,
    a.answer_es,
    at.question_gn,
    at.answer_gn,
    a.source,
    a.answer_number,
    a.equation_solution
FROM annotation_translations at
INNER JOIN users u
    ON u.id = at.user_id
INNER JOIN annotations a
    ON a.id = at.annotation_id
ORDER BY
    u.nombre_completo ASC,
    at.created_at ASC;
    """

    result = execute_query(conn, query)

    if result is None:
        print("No se obtuvo resultado para la query de traducciones por usuario. Comprueba la query y la conexión.")
        return False

    wb = Workbook()
    ws = wb.active
    ws.title = "Traducciones por usuario"

    ws["A1"] = "Última actualización"
    ws["B1"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    ws["A3"] = "Todas las traducciones por usuario"
    ws["A3"].font = Font(size=14, bold=True)

    headers = [
        "Nombre completo",
        "Email",
        "Fecha traducción",
        "ID annotation",
        "Pregunta original ES",
        "Respuesta original ES",
        "Pregunta traducida GN",
        "Respuesta traducida GN",
        "Fuente",
        "Número respuesta",
        "Solución ecuación",
    ]

    ws.append([])
    ws.append(headers)

    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=5, column=col)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", fill_type="solid")

    ws.freeze_panes = "A6"

    current_user_id = None
    row_index = 6

    for row in result:
        user_id = row[0]
        full_name = row[1] or ''
        email = row[2] or ''
        fecha_traduccion = row[3]

        if user_id != current_user_id:
            current_user_id = user_id
            ws.append([f"Usuario: {full_name} - {email}"])
            ws.merge_cells(start_row=row_index, start_column=1, end_row=row_index, end_column=len(headers))
            group_cell = ws.cell(row=row_index, column=1)
            group_cell.font = Font(bold=True)
            group_cell.fill = PatternFill(start_color="D9EAF7", fill_type="solid")
            row_index += 1

        ws.append([
            full_name,
            email,
            fecha_traduccion.strftime('%Y-%m-%d %H:%M:%S') if fecha_traduccion else '',
            row[4],
            row[5] or '',
            row[6] or '',
            row[7] or '',
            row[8] or '',
            row[9] or '',
            row[10] if row[10] is not None else '',
            row[11] or '',
        ])
        row_index += 1

    if row_index > 6:
        ws.auto_filter.ref = f"A5:{get_column_letter(len(headers))}{row_index - 1}"

    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)

        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass

        ws.column_dimensions[col_letter].width = min(max_length + 2, 80)

    file_path = output_path / "Traducciones_Por_Usuario.xlsx"
    wb.save(file_path)

    print(f"Excel de traducciones por usuario generado en: {file_path}")
    return True



def get_activity_by_weekday(conn, output_path):
    """
    Calcula la cantidad de premisas tomadas por día de la semana
    (basado en `annotation_assignments.assigned_at` ajustado por servidor)
    Genera un CSV y un PNG (histograma de barras) en `output_path`.

    Returns: Path al PNG generado o None si falla.
    """
    try:
        query = f"""
SELECT EXTRACT(DOW FROM (assigned_at{TIME_SUB_SQL}))::int AS dow,
       COUNT(*)::int AS total
FROM annotation_assignments
GROUP BY dow
ORDER BY dow;
"""
        rows = execute_query(conn, query)
        if rows is None:
            print("No se obtuvieron datos para actividad por día.")
            return None

        # Mapear dow (0=Sunday .. 6=Saturday) a nombres en español
        dow_names = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado']
        counts = {name: 0 for name in dow_names}

        for dow, total in rows:
            name = dow_names[int(dow) % 7]
            counts[name] = int(total)

        # Ordenar desde lunes a domingo
        ordered_days = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
        ordered_counts = [counts[d] for d in ordered_days]

        # Asegurar carpeta
        output_path.mkdir(parents=True, exist_ok=True)

        # Generar gráfico (matplotlib local import para evitar fallo si no instalado)
        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            print(f"matplotlib no disponible: {e}. No se generará el PNG.")
            return None

        fig, ax = plt.subplots(figsize=(8, 4.5))
        bars = ax.bar(ordered_days, ordered_counts, color='deepskyblue')
        ax.set_title('Premisas por día de la semana')
        ax.set_ylabel('Cantidad de premisas asiganadas')
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        # Etiquetas sobre barras
        for bar in bars:
            h = bar.get_height()
            ax.annotate(str(int(h)), xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')

        fig.tight_layout()
        png_path = output_path / 'premisas_por_dia.png'
        fig.savefig(png_path)
        plt.close(fig)

        print(f"PNG generado en: {png_path}")
        return png_path

    except Exception as e:
        print(f"Error generando actividad por día: {e}")
        return None


def get_translations_by_weekday(conn, output_path):
    """
    Genera un histograma PNG con la cantidad de traducciones por día de la semana
    (basado en `annotation_translations.created_at` ajustado por servidor).
    """
    try:
        query = f"""
SELECT EXTRACT(DOW FROM (created_at{TIME_SUB_SQL}))::int AS dow,
       COUNT(*)::int AS total
FROM annotation_translations
GROUP BY dow
ORDER BY dow;
"""
        rows = execute_query(conn, query)
        if rows is None:
            print("No se obtuvieron datos para traducciones por día.")
            return None

        dow_names = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado']
        counts = {name: 0 for name in dow_names}
        for dow, total in rows:
            counts[dow_names[int(dow) % 7]] = int(total)

        ordered_days = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
        ordered_counts = [counts[d] for d in ordered_days]

        output_path.mkdir(parents=True, exist_ok=True)
        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            print(f"matplotlib no disponible: {e}. No se generará el PNG de traducciones.")
            return None

        fig, ax = plt.subplots(figsize=(8, 4.5))
        bars = ax.bar(ordered_days, ordered_counts, color='mediumpurple')
        ax.set_title('Traducciones por día de la semana')
        ax.set_ylabel('Cantidad de traducciones')
        ax.set_xlabel('Día')
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        for bar in bars:
            h = bar.get_height()
            ax.annotate(str(int(h)), xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')
        fig.tight_layout()
        png_path = output_path / 'traducciones_por_dia.png'
        fig.savefig(png_path)
        plt.close(fig)
        print(f"PNG de traducciones generado en: {png_path}")
        return png_path
    except Exception as e:
        print(f"Error generando traducciones por día: {e}")
        return None


def get_global_activity_by_weekday(conn, output_path):
    """
    Genera un histograma PNG con la actividad global por día (asignaciones + traducciones).
    """
    try:
        query = f"""
SELECT dow, SUM(total) AS total FROM (
  SELECT EXTRACT(DOW FROM (assigned_at{TIME_SUB_SQL}))::int AS dow, COUNT(*)::int AS total
  FROM annotation_assignments
  GROUP BY dow
  UNION ALL
  SELECT EXTRACT(DOW FROM (created_at{TIME_SUB_SQL}))::int AS dow, COUNT(*)::int AS total
  FROM annotation_translations
  GROUP BY dow
) s
GROUP BY dow
ORDER BY dow;
"""
        rows = execute_query(conn, query)
        if rows is None:
            print("No se obtuvieron datos para actividad global por día.")
            return None

        dow_names = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado']
        counts = {name: 0 for name in dow_names}
        for dow, total in rows:
            counts[dow_names[int(dow) % 7]] = int(total)

        ordered_days = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
        ordered_counts = [counts[d] for d in ordered_days]

        output_path.mkdir(parents=True, exist_ok=True)
        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            print(f"matplotlib no disponible: {e}. No se generará el PNG de actividad global.")
            return None

        fig, ax = plt.subplots(figsize=(8, 4.5))
        bars = ax.bar(ordered_days, ordered_counts, color='seagreen')
        ax.set_title('Actividad (asignaciones + traducciones) por día')
        ax.set_ylabel('Cantidad total')
        ax.set_xlabel('Día')
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        for bar in bars:
            h = bar.get_height()
            ax.annotate(str(int(h)), xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')
        fig.tight_layout()
        png_path = output_path / 'actividad_global_por_dia.png'
        fig.savefig(png_path)
        plt.close(fig)
        print(f"PNG de actividad global generado en: {png_path}")
        return png_path
    except Exception as e:
        print(f"Error generando actividad global por día: {e}")
        return None

def get_global_activity_by_date(conn, output_path):
    """
    Genera un gráfico PNG con la actividad global por fecha real:
    premisas asignadas + traducciones realizadas por día.
    """
    try:
        query = f"""
WITH activity AS (
    SELECT
        DATE(assigned_at{TIME_SUB_SQL}) AS fecha,
        COUNT(*)::int AS premisas,
        0::int AS traducciones
    FROM annotation_assignments
    GROUP BY DATE(assigned_at{TIME_SUB_SQL})

    UNION ALL

    SELECT
        DATE(created_at{TIME_SUB_SQL}) AS fecha,
        0::int AS premisas,
        COUNT(*)::int AS traducciones
    FROM annotation_translations
    GROUP BY DATE(created_at{TIME_SUB_SQL})
),
daily_activity AS (
    SELECT
        fecha,
        SUM(premisas)::int AS premisas,
        SUM(traducciones)::int AS traducciones,
        SUM(premisas + traducciones)::int AS total
    FROM activity
    GROUP BY fecha
),
date_range AS (
    SELECT generate_series(
        (SELECT MIN(fecha) FROM daily_activity),
        (SELECT MAX(fecha) FROM daily_activity),
        INTERVAL '1 day'
    )::date AS fecha
)
SELECT
    dr.fecha,
    COALESCE(da.premisas, 0) AS premisas,
    COALESCE(da.traducciones, 0) AS traducciones,
    COALESCE(da.total, 0) AS total
FROM date_range dr
LEFT JOIN daily_activity da
    ON da.fecha = dr.fecha
ORDER BY dr.fecha;
"""

        rows = execute_query(conn, query)

        if rows is None or len(rows) == 0:
            print("No se obtuvieron datos para actividad global diaria.")
            return None

        fechas = [row[0].strftime("%d/%m") for row in rows]
        totales = [int(row[3]) for row in rows]

        output_path.mkdir(parents=True, exist_ok=True)

        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            print(f"matplotlib no disponible: {e}. No se generará el PNG de actividad global diaria.")
            return None

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.plot(fechas, totales, marker='o')
        ax.set_title("Actividad global diaria")
        ax.set_ylabel("Premisas + traducciones")
        ax.set_xlabel("Fecha")
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        plt.xticks(rotation=45, ha='right')

        fig.tight_layout()

        png_path = output_path / "actividad_global_diaria.png"
        fig.savefig(png_path)
        plt.close(fig)

        print(f"PNG de actividad global diaria generado en: {png_path}")
        return png_path

    except Exception as e:
        print(f"Error generando actividad global diaria: {e}")
        return None
    
def get_global_activity_heatmap(conn, output_path):
    """
    Genera un mapa de calor con actividad global por día de semana y hora:
    premisas asignadas + traducciones realizadas.
    """
    try:
        query = f"""
SELECT
    EXTRACT(DOW FROM fecha)::int AS dow,
    EXTRACT(HOUR FROM fecha)::int AS hour,
    COUNT(*)::int AS total
FROM (
    SELECT assigned_at{TIME_SUB_SQL} AS fecha
    FROM annotation_assignments

    UNION ALL

    SELECT created_at{TIME_SUB_SQL} AS fecha
    FROM annotation_translations
) activity
GROUP BY dow, hour
ORDER BY dow, hour;
"""

        rows = execute_query(conn, query)

        if rows is None:
            print("No se obtuvieron datos para el mapa de calor.")
            return None

        ordered_days = [
            "lunes",
            "martes",
            "miércoles",
            "jueves",
            "viernes",
            "sábado",
            "domingo"
        ]

        dow_to_index = {
            1: 0,  # lunes
            2: 1,
            3: 2,
            4: 3,
            5: 4,
            6: 5,
            0: 6,  # domingo
        }

        heatmap_data = [[0 for _ in range(24)] for _ in range(7)]

        for dow, hour, total in rows:
            day_index = dow_to_index[int(dow)]
            hour_index = int(hour)
            heatmap_data[day_index][hour_index] = int(total)

        output_path.mkdir(parents=True, exist_ok=True)

        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            print(f"matplotlib no disponible: {e}. No se generará el mapa de calor.")
            return None

        fig, ax = plt.subplots(figsize=(14, 5.5))

        image = ax.imshow(
            heatmap_data,
            aspect="auto",
            interpolation="nearest",
            cmap="Blues"
        )

        ax.set_title("Actividad global por día y hora")
        ax.set_xlabel("Hora del día")
        ax.set_ylabel("Día de la semana")

        ax.set_xticks(range(24))
        ax.set_xticklabels([f"{h:02d}" for h in range(24)])

        ax.set_yticks(range(7))
        ax.set_yticklabels(ordered_days)

        cbar = fig.colorbar(image, ax=ax)
        cbar.set_label("Premisas + traducciones")

        for day_index in range(7):
            for hour_index in range(24):
                value = heatmap_data[day_index][hour_index]
                if value > 0:
                    ax.text(
                        hour_index,
                        day_index,
                        str(value),
                        ha="center",
                        va="center",
                        fontsize=7
                    )

        fig.tight_layout()

        png_path = output_path / "actividad_global_por_dia_hora.png"
        fig.savefig(png_path)
        plt.close(fig)

        print(f"Mapa de calor generado en: {png_path}")
        return png_path

    except Exception as e:
        print(f"Error generando mapa de calor: {e}")
        return None
    

def main():
    """
    Función principal que ejecuta todas las métricas.
    """
    print("Iniciando generación de métricas...")
    
    # Conectar a la base de datos
    conn = get_connection()
    print(" Conectado a la base de datos")
    
    try:
        # Recopilar todas las métricas
        print("Recopilando métricas...")
        metrics_data = {
            'usuarios': get_user_metrics(conn),
            'anotaciones': get_annotation_metrics(conn),
            'asignaciones': get_assignment_metrics(conn),
            'traducciones': get_translation_metrics(conn),
            'user_breakdown': get_user_breakdown_metrics(conn),
        }
        
        # Generar y mostrar reporte en consola
        report = generate_report(metrics_data)
        
        # Generar/Actualizar documento Word y CSV de usuarios
        documents_folder = ensure_documents_folder()
        update_metrics_docx(metrics_data, documents_folder)
        #generate_users_csv(conn, documents_folder)
        generate_users_excel(conn, documents_folder)
        generate_user_translations_excel(conn, documents_folder)
        # Generar actividad por día (PNG)
        get_activity_by_weekday(conn, documents_folder)
        # Generar traducciones por día (PNG)
        get_translations_by_weekday(conn, documents_folder)
        # Generar actividad global (asignaciones + traducciones) por día (PNG)
        get_global_activity_by_weekday(conn, documents_folder)
        # Generar actividad global por fecha real (PNG)
        get_global_activity_by_date(conn, documents_folder)
        # Generar mapa de calor de actividad global por día y hora (PNG)
        get_global_activity_heatmap(conn, documents_folder)
        
        print(" Métricas generadas exitosamente")
        
    except Exception as e:
        print(f"Error durante la generación de métricas: {e}")
        sys.exit(1)
        
    finally:
        # Cerrar conexión
        if conn:
            conn.close()
            print("Conexión cerrada")


if __name__ == "__main__":
    main()
