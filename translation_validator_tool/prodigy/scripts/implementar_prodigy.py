"""
Script interactivo para implementar Prodigy como herramienta complementaria
Guía paso a paso para el flujo completo
"""

import os
import sys
import subprocess
from pathlib import Path

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_step(number, text):
    print(f"{Colors.BLUE}{Colors.BOLD}📍 Paso {number}: {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def wait_for_user():
    input(f"\n{Colors.YELLOW}Presiona Enter para continuar...{Colors.END}")

def run_command(cmd, description=None):
    """Ejecutar comando y mostrar resultado"""
    if description:
        print(f"\n{Colors.BOLD}Ejecutando: {description}{Colors.END}")
    print(f"{Colors.BLUE}$ {cmd}{Colors.END}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print_error(result.stderr)
    
    return result.returncode == 0

def main():
    print_header("🚀 Implementación de Prodigy - Herramienta Complementaria")
    
    print("""
Este script te guiará paso a paso para implementar Prodigy como herramienta
complementaria a tu sistema actual React + FastAPI + PostgreSQL.

Al final tendrás:
✅ Datos exportados de PostgreSQL
✅ Anotaciones realizadas en Prodigy
✅ Datos sincronizados de vuelta a PostgreSQL
✅ Flujo completo funcionando
    """)
    
    wait_for_user()
    
    # ============================================================
    # PASO 1: Verificar requisitos
    # ============================================================
    print_step(1, "Verificar requisitos previos")
    
    print_info("Verificando que Prodigy esté instalado...")
    if run_command("python -m prodigy stats", "Verificar Prodigy"):
        print_success("Prodigy instalado correctamente")
    else:
        print_error("Prodigy no está instalado")
        return
    
    print_info("Verificando estructura de archivos...")
    required_files = [
        "scripts/export_to_prodigy.py",
        "scripts/sync_prodigy_to_db.py",
        "recipes/guarani_pos_tagging.py",
        "data/export/original_translations.jsonl"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print_success(f"✓ {file}")
        else:
            print_warning(f"✗ {file} (se creará)")
            all_exist = False
    
    wait_for_user()
    
    # ============================================================
    # PASO 2: Exportar datos desde PostgreSQL
    # ============================================================
    print_step(2, "Exportar traducciones desde PostgreSQL")
    
    print_info("""
Vamos a exportar traducciones con is_original=true desde tu base de datos.
Esto NO afecta tu base de datos actual, solo crea un archivo de exportación.
    """)
    
    export_limit = input(f"\n{Colors.BOLD}¿Cuántas traducciones quieres exportar? (recomendado: 50): {Colors.END}") or "50"
    
    export_cmd = f"cd .. && cd api && python ../prodigy/scripts/export_to_prodigy.py --output ../prodigy/data/export/original_translations.jsonl --only-original --limit {export_limit}"
    
    if run_command(export_cmd, "Exportar traducciones"):
        print_success(f"Exportadas {export_limit} traducciones a data/export/original_translations.jsonl")
    else:
        print_error("Error al exportar. Verifica tu conexión a PostgreSQL")
        return
    
    wait_for_user()
    
    # ============================================================
    # PASO 3: Importar a Prodigy
    # ============================================================
    print_step(3, "Importar datos a Prodigy")
    
    dataset_name = input(f"\n{Colors.BOLD}Nombre del dataset (default: guarani_test): {Colors.END}") or "guarani_test"
    
    import_cmd = f"python -m prodigy db-in {dataset_name} data/export/original_translations.jsonl"
    
    if run_command(import_cmd, "Importar a Prodigy"):
        print_success(f"Datos importados al dataset '{dataset_name}'")
    else:
        print_error("Error al importar")
        return
    
    wait_for_user()
    
    # ============================================================
    # PASO 4: Iniciar Prodigy para anotar
    # ============================================================
    print_step(4, "Iniciar interfaz de anotación")
    
    print_info("""
Ahora vamos a iniciar Prodigy para que anotes algunas traducciones.

Se abrirá en: http://localhost:8081

INSTRUCCIONES:
1. Selecciona palabras en el texto Guaraní
2. Haz clic en la categoría gramatical (SUJETO, VERBO, OBJETO, etc.)
3. Presiona Enter para aceptar y siguiente
4. Anota al menos 5-10 oraciones
5. Cuando termines, presiona Ctrl+C en la terminal para detener

¿Estás listo?
    """)
    
    wait_for_user()
    
    print_info(f"Iniciando Prodigy en http://localhost:8081")
    print_warning("Anota algunas oraciones y luego presiona Ctrl+C para continuar...")
    
    prodigy_cmd = f"python -m prodigy guarani-pos {dataset_name}_pos data/export/original_translations.jsonl -F recipes/guarani_pos_tagging.py"
    
    try:
        subprocess.run(prodigy_cmd, shell=True)
    except KeyboardInterrupt:
        print_info("\nProdigy detenido")
    
    wait_for_user()
    
    # ============================================================
    # PASO 5: Ver estadísticas de anotación
    # ============================================================
    print_step(5, "Ver estadísticas de tus anotaciones")
    
    stats_cmd = f"python -m prodigy stats {dataset_name}_pos"
    
    if run_command(stats_cmd, "Ver estadísticas"):
        print_success("Estadísticas mostradas arriba")
    
    wait_for_user()
    
    # ============================================================
    # PASO 6: Exportar anotaciones
    # ============================================================
    print_step(6, "Exportar anotaciones a archivo")
    
    export_format = input(f"\n{Colors.BOLD}¿Formato de exportación? (jsonl/csv) [jsonl]: {Colors.END}") or "jsonl"
    
    if export_format == "csv":
        export_annotations_cmd = f"python -m prodigy db-out {dataset_name}_pos --format csv > data/annotations/pos_results.csv"
    else:
        export_annotations_cmd = f"python -m prodigy db-out {dataset_name}_pos > data/annotations/pos_results.jsonl"
    
    if run_command(export_annotations_cmd, "Exportar anotaciones"):
        print_success(f"Anotaciones exportadas a data/annotations/pos_results.{export_format}")
    
    wait_for_user()
    
    # ============================================================
    # PASO 7: Sincronizar a PostgreSQL (si aplicable)
    # ============================================================
    print_step(7, "Sincronizar validaciones a PostgreSQL (opcional)")
    
    sync = input(f"\n{Colors.BOLD}¿Quieres sincronizar validaciones a PostgreSQL? (s/n): {Colors.END}")
    
    if sync.lower() == 's':
        user_id = input(f"{Colors.BOLD}ID del usuario que anotó (default: 1): {Colors.END}") or "1"
        
        print_warning("Ejecutando en modo DRY RUN primero (sin guardar)...")
        dry_run_cmd = f"cd .. && cd api && python ../prodigy/scripts/sync_prodigy_to_db.py sync-validations {dataset_name} --user-id {user_id} --dry-run"
        
        if run_command(dry_run_cmd, "Simulación de sincronización"):
            confirm = input(f"\n{Colors.BOLD}¿Proceder con la sincronización real? (s/n): {Colors.END}")
            
            if confirm.lower() == 's':
                real_sync_cmd = f"cd .. && cd api && python ../prodigy/scripts/sync_prodigy_to_db.py sync-validations {dataset_name} --user-id {user_id}"
                
                if run_command(real_sync_cmd, "Sincronización real"):
                    print_success("¡Validaciones sincronizadas a PostgreSQL!")
                else:
                    print_error("Error en sincronización")
            else:
                print_info("Sincronización cancelada")
    else:
        print_info("Sincronización omitida")
    
    wait_for_user()
    
    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    print_header("🎉 ¡Implementación Completada!")
    
    print(f"""
{Colors.GREEN}{Colors.BOLD}¡Felicitaciones! Has completado el flujo completo de Prodigy.{Colors.END}

📊 RESUMEN:
✅ Exportaste traducciones desde PostgreSQL
✅ Importaste datos a Prodigy
✅ Anotaste oraciones en la interfaz web
✅ Exportaste los resultados
✅ (Opcional) Sincronizaste validaciones a PostgreSQL

📁 ARCHIVOS CREADOS:
• data/export/original_translations.jsonl - Datos exportados
• data/annotations/pos_results.{export_format} - Tus anotaciones

🔄 PRÓXIMOS PASOS:

1. REVISAR ANOTACIONES:
   python -m prodigy db-out {dataset_name}_pos --format csv

2. AGREGAR A TU REACT UI:
   - Agrega un botón que abra http://localhost:8081
   - Consulta INTEGRACION.md para código de ejemplo

3. USAR REGULARMENTE:
   - Exporta batch de traducciones semanalmente
   - Anota con tu equipo
   - Sincroniza resultados
   - Usa datos para entrenar modelos

📚 DOCUMENTACIÓN:
• README.md - Plan completo de implementación
• QUICKSTART.md - Comandos rápidos
• EXPLORACION_PRACTICA.md - Ejercicios prácticos
• INTEGRACION.md - Guía de integración con tu sistema

{Colors.YELLOW}💡 TIP: Guarda este workflow para usarlo regularmente con tu equipo{Colors.END}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Script interrumpido por el usuario{Colors.END}")
    except Exception as e:
        print_error(f"Error inesperado: {e}")
