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
    query_new_users = """
    SELECT DATE(created_at) AS fecha, COUNT(*) AS total
    FROM users
    WHERE created_at >= NOW() - INTERVAL '2 days'
    GROUP BY DATE(created_at)
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
    query_recent = """
    SELECT COUNT(*)
    FROM annotations
    WHERE translated = true
    AND updated_at >= NOW() - INTERVAL '2 days';
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
    
    # Asignaciones en los últimos 2 días
    query_recent = """
    SELECT COUNT(*)
    FROM annotation_assignments
    WHERE assigned_at >= NOW() - INTERVAL '2 days';
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
    doc.add_paragraph(f"Premisas tomadas por usuarios: {metrics_data['asignaciones']['annotations_tomadas_usuarios']}/720")
    
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
    
    query = """
   SELECT 
    u.id,
    u.nombre_completo,
    u.email,
    u.contacto,
    COUNT(DISTINCT aa.annotation_id) AS premisas_asignadas,
    COUNT(DISTINCT at.id) AS traducciones_completadas,
    CASE 
        WHEN COUNT(DISTINCT aa.annotation_id) = 0 
         AND COUNT(DISTINCT at.id) = 0 THEN 'inactivo'
        WHEN COUNT(DISTINCT aa.annotation_id) > 0 
         AND COUNT(DISTINCT at.id) = 0 THEN 'activo'
        WHEN COUNT(DISTINCT at.id) > 0 THEN 'muy activo'
    END AS estado
    FROM users u
    LEFT JOIN annotation_assignments aa
        ON aa.user_id = u.id
    LEFT JOIN annotation_translations at
        ON at.user_id = u.id
    GROUP BY u.id, u.nombre_completo, u.email, u.contacto
    ORDER BY 
        CASE 
            WHEN COUNT(DISTINCT at.id) > 0 THEN 1        -- muy activo
            WHEN COUNT(DISTINCT aa.annotation_id) > 0 THEN 2  -- activo
            ELSE 3                                       -- inactivo
        END,
        traducciones_completadas DESC,
        premisas_asignadas DESC;
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
        "Premisas asignadas"
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
    # Datos: mapear con tolerancia a filas con menos columnas
    row_index = 6
    for row in result:
        try:
            full_name = row[1] if len(row) > 1 else ''
            email = row[2] if len(row) > 2 else ''
            contact = row[3] if len(row) > 3 else ''
            premises = row[4] if len(row) > 4 else ''
            translations = row[5] if len(row) > 5 else ''
            estado = row[6] if len(row) > 6 else ''
        except Exception:
            full_name = email = contact = premises = translations = estado = ''

        ws.append([
            full_name,
            email,
            contact or '',
            estado,
            translations,
            premises
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
