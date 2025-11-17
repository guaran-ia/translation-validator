"""
Script para visualizar anotaciones POS en formato HTML
Genera una página web interactiva con todas las anotaciones
"""

import json
import sys
from pathlib import Path

# Colores para cada etiqueta POS
COLORS = {
    "SUJETO": "#ef4444",      # rojo
    "VERBO": "#3b82f6",       # azul
    "OBJETO": "#10b981",      # verde
    "SUSTANTIVO": "#f59e0b",  # naranja
    "ADJETIVO": "#8b5cf6",    # púrpura
    "ADVERBIO": "#ec4899",    # rosa
    "PRONOMBRE": "#06b6d4",   # cyan
    "PREPOSICIÓN": "#84cc16", # lima
    "ARTÍCULO": "#6366f1",    # índigo
    "CONJUNCIÓN": "#f97316"   # naranja oscuro
}

def create_html_visualization(jsonl_file, output_file):
    """Crea visualización HTML de las anotaciones"""
    
    annotations = []
    # Intentar diferentes encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(jsonl_file, 'r', encoding=encoding) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        annotations.append(json.loads(line))
            break  # Si funciona, salir del loop
        except (UnicodeDecodeError, json.JSONDecodeError):
            annotations = []  # Reset para siguiente intento
            continue
    
    html_parts = []
    html_parts.append("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Anotaciones POS - Guaraní</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header h1 {
                color: #667eea;
                font-size: 32px;
                margin-bottom: 10px;
            }
            .stats {
                display: flex;
                gap: 20px;
                margin-top: 20px;
            }
            .stat {
                background: #f3f4f6;
                padding: 15px 20px;
                border-radius: 8px;
                flex: 1;
            }
            .stat-number {
                font-size: 28px;
                font-weight: bold;
                color: #667eea;
            }
            .stat-label {
                color: #6b7280;
                font-size: 14px;
                margin-top: 5px;
            }
            .legend {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .legend h3 {
                margin-bottom: 15px;
                color: #374151;
            }
            .legend-items {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .legend-item {
                padding: 5px 12px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: 600;
                color: white;
            }
            .annotation {
                background: white;
                padding: 25px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .annotation:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            .annotation-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f3f4f6;
            }
            .annotation-number {
                font-size: 20px;
                font-weight: bold;
                color: #667eea;
            }
            .status {
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }
            .status-accept {
                background: #d1fae5;
                color: #065f46;
            }
            .status-reject {
                background: #fee2e2;
                color: #991b1b;
            }
            .spanish {
                background: #fef3c7;
                padding: 12px 15px;
                border-radius: 8px;
                margin-bottom: 15px;
                border-left: 4px solid #f59e0b;
            }
            .spanish-label {
                font-size: 11px;
                font-weight: 600;
                color: #92400e;
                text-transform: uppercase;
                margin-bottom: 5px;
            }
            .spanish-text {
                color: #78350f;
                font-size: 15px;
            }
            .guarani {
                font-size: 18px;
                line-height: 1.8;
                color: #1f2937;
            }
            .token {
                padding: 3px 0;
                position: relative;
                display: inline;
            }
            .token-labeled {
                padding: 4px 8px;
                border-radius: 4px;
                color: white;
                font-weight: 600;
                margin: 0 2px;
            }
            .token-labeled::after {
                content: attr(data-label);
                position: absolute;
                top: -20px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 10px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                white-space: nowrap;
                opacity: 0;
                transition: opacity 0.2s;
                pointer-events: none;
            }
            .token-labeled:hover::after {
                opacity: 1;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏷️ Anotaciones POS - Textos Guaraní</h1>
                <p style="color: #6b7280; margin-top: 10px;">Visualización de categorías gramaticales anotadas</p>
                <div class="stats">
    """)
    
    # Estadísticas
    total = len(annotations)
    accepted = sum(1 for a in annotations if a.get('answer') == 'accept')
    rejected = total - accepted
    
    html_parts.append(f"""
                    <div class="stat">
                        <div class="stat-number">{total}</div>
                        <div class="stat-label">Total anotaciones</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{accepted}</div>
                        <div class="stat-label">Aceptadas</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{rejected}</div>
                        <div class="stat-label">Rechazadas</div>
                    </div>
                </div>
            </div>
            
            <div class="legend">
                <h3>Leyenda de Etiquetas</h3>
                <div class="legend-items">
    """)
    
    for label, color in COLORS.items():
        html_parts.append(f'<div class="legend-item" style="background-color: {color}">{label}</div>')
    
    html_parts.append("""
                </div>
            </div>
    """)
    
    # Generar visualización para cada anotación
    for idx, ann in enumerate(annotations, 1):
        text = ann.get('text', '')
        spanish = ann.get('meta', {}).get('spanish_text', '')
        spans = ann.get('spans', [])
        tokens = ann.get('tokens', [])
        answer = ann.get('answer', 'unknown')
        
        status_class = 'status-accept' if answer == 'accept' else 'status-reject'
        status_text = '✓ Aceptada' if answer == 'accept' else '✗ Rechazada'
        
        html_parts.append(f"""
            <div class="annotation">
                <div class="annotation-header">
                    <div class="annotation-number">#{idx}</div>
                    <div class="status {status_class}">{status_text}</div>
                </div>
                
                <div class="spanish">
                    <div class="spanish-label">🇪🇸 Traducción al español</div>
                    <div class="spanish-text">{spanish}</div>
                </div>
                
                <div class="guarani">
        """)
        
        # Crear mapa de spans
        span_map = {}
        for span in spans:
            start = span['start']
            end = span['end']
            label = span['label']
            span_map[(start, end)] = label
        
        # Generar texto con etiquetas
        current_pos = 0
        sorted_spans = sorted(spans, key=lambda x: x['start'])
        
        for span in sorted_spans:
            start = span['start']
            end = span['end']
            label = span['label']
            color = COLORS.get(label, '#6b7280')
            
            # Texto antes del span
            if current_pos < start:
                html_parts.append(text[current_pos:start])
            
            # Span etiquetado
            span_text = text[start:end]
            html_parts.append(f'<span class="token-labeled" style="background-color: {color}" data-label="{label}">{span_text}</span>')
            
            current_pos = end
        
        # Texto restante
        if current_pos < len(text):
            html_parts.append(text[current_pos:])
        
        html_parts.append("""
                </div>
            </div>
        """)
    
    html_parts.append("""
        </div>
    </body>
    </html>
    """)
    
    # Escribir archivo HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(html_parts))
    
    print(f"[OK] Visualización creada: {output_file}")
    print(f"[OK] Total de anotaciones: {total}")
    print(f"[OK] Aceptadas: {accepted} | Rechazadas: {rejected}")
    print(f"\n[NEXT] Abre el archivo en tu navegador:")
    print(f"    {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python visualize_annotations.py <archivo.jsonl> [salida.html]")
        print("\nEjemplo:")
        print("    python scripts/visualize_annotations.py data/annotations/verificacion.jsonl")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.jsonl', '.html')
    
    if not Path(input_file).exists():
        print(f"[ERROR] Archivo no encontrado: {input_file}")
        sys.exit(1)
    
    create_html_visualization(input_file, output_file)
