"""
Genera visualización HTML interactiva de anotaciones exportadas.

Características:
- Visualización de spans con colores por familia
- Resaltado de texto con overlapping
- Estadísticas IAA
- Filtrado por etiqueta

Uso:
    python scripts/visualize_annotations.py resultados/export_test_ud.json --output resultados/visualization.html
"""

import argparse
import json
from pathlib import Path
from collections import Counter, defaultdict

# Importar mapper centralizado
try:
    from ud_guarani_mapper import LABEL_FAMILIES, LABEL_COLORS, UD_TO_FRIENDLY
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from ud_guarani_mapper import LABEL_FAMILIES, LABEL_COLORS, UD_TO_FRIENDLY


def get_label_color(label: str) -> str:
    """Obtiene el color de una etiqueta."""
    return LABEL_COLORS.get(label, "#6b7280")


def generate_span_html(text: str, spans: list) -> str:
    """
    Genera HTML con spans resaltados que soporta overlapping.
    """
    if not spans:
        return f'<span class="text-content">{text}</span>'
    
    # Ordenar spans por posición
    sorted_spans = sorted(spans, key=lambda x: (x['start'], -x['end']))
    
    # Crear marcadores de inicio/fin
    markers = []
    for i, span in enumerate(sorted_spans):
        label = span.get('label', 'Unknown')
        color = get_label_color(label)
        ud_label = span.get('ud_label', label)
        markers.append((span['start'], 'open', i, label, color, ud_label))
        markers.append((span['end'], 'close', i, label, color, ud_label))
    
    # Ordenar por posición (close antes de open en la misma posición)
    markers.sort(key=lambda x: (x[0], x[1] == 'open'))
    
    # Generar HTML
    html_parts = []
    last_pos = 0
    open_spans = []
    
    for pos, action, idx, label, color, ud_label in markers:
        # Agregar texto antes del marcador
        if pos > last_pos:
            html_parts.append(text[last_pos:pos])
        
        if action == 'open':
            html_parts.append(
                f'<span class="span-highlight" style="background:{color}22;border-bottom:2px solid {color};" '
                f'data-label="{label}" data-ud="{ud_label}" title="{label} → {ud_label}">'
            )
            open_spans.append(idx)
        else:
            html_parts.append('</span>')
            if idx in open_spans:
                open_spans.remove(idx)
        
        last_pos = pos
    
    # Agregar texto restante
    if last_pos < len(text):
        html_parts.append(text[last_pos:])
    
    return ''.join(html_parts)


def generate_legend_html() -> str:
    """Genera leyenda de colores por familia."""
    html_parts = ['<div class="legend">']
    html_parts.append('<h3>📋 Familias de Etiquetas</h3>')
    html_parts.append('<div class="legend-grid">')
    
    for family_name, family_data in LABEL_FAMILIES.items():
        color = family_data['color']
        labels = family_data['labels']
        
        html_parts.append(f'''
            <div class="legend-family">
                <div class="family-header" style="color:{color};">
                    {family_name}
                </div>
                <div class="family-labels">
        ''')
        
        for label in labels:
            html_parts.append(
                f'<span class="label-badge" style="background:{color};">{label}</span>'
            )
        
        html_parts.append('</div></div>')
    
    html_parts.append('</div></div>')
    return '\n'.join(html_parts)


def generate_stats_html(data: dict) -> str:
    """Genera estadísticas del dataset."""
    metadata = data.get('metadata', {})
    examples = data.get('examples', [])
    
    # Contar etiquetas
    label_counts = Counter()
    ud_label_counts = Counter()
    for ex in examples:
        for span in ex.get('spans', []):
            label_counts[span.get('label', 'Unknown')] += 1
            ud_label_counts[span.get('ud_label', span.get('label', 'Unknown'))] += 1
    
    total_spans = sum(label_counts.values())
    
    return f'''
    <div class="stats-panel">
        <h3>📊 Estadísticas</h3>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">{metadata.get('total_examples', 0)}</div>
                <div class="stat-label">Ejemplos</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_spans}</div>
                <div class="stat-label">Spans totales</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{metadata.get('average_agreement', 1.0):.1%}</div>
                <div class="stat-label">Acuerdo IAA</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{metadata.get('total_conflicts', 0)}</div>
                <div class="stat-label">Conflictos</div>
            </div>
        </div>
        <div class="label-stats">
            <h4>Top Etiquetas (Amigables)</h4>
            <div class="label-bars">
                {''.join([
                    f'<div class="label-bar"><span class="label-name">{label}</span>'
                    f'<div class="bar" style="width:{count/total_spans*100:.0f}%;background:{get_label_color(label)};"></div>'
                    f'<span class="label-count">{count}</span></div>'
                    for label, count in label_counts.most_common(10)
                ])}
            </div>
        </div>
    </div>
    '''


def generate_examples_html(examples: list) -> str:
    """
    Genera HTML para todos los ejemplos, AGRUPADOS por oración.
    Muestra las anotaciones de cada anotador y los conflictos específicos.
    """
    # Agrupar ejemplos por texto (o _task_hash si existe)
    grouped = defaultdict(list)
    for ex in examples:
        # Usar el texto como key de agrupación
        key = ex.get('text', '')
        grouped[key].append(ex)
    
    html_parts = ['<div class="examples-container">']
    
    for i, (text, group) in enumerate(grouped.items(), 1):
        if not text:
            continue
        
        # Tomar metadata del primer ejemplo del grupo
        first_ex = group[0]
        meta = first_ex.get('meta', {})
        spanish_text = meta.get('spanish_text', 'N/A')
        
        # Recopilar todos los anotadores y sus spans
        all_annotators = {}
        all_spans_merged = []
        all_conflicts = []
        
        for ex in group:
            # Obtener anotadores de este ejemplo
            annotators = ex.get('annotators', [])
            for ann in annotators:
                ann_session = ann.get('session', 'unknown')
                ann_spans = ann.get('num_spans', 0)
                if ann_session not in all_annotators:
                    all_annotators[ann_session] = {
                        'spans': [],
                        'num_spans': ann_spans
                    }
            
            # Agregar spans (evitar duplicados)
            for span in ex.get('spans', []):
                span_key = (span.get('start'), span.get('end'), span.get('label'))
                if not any(
                    s.get('start') == span.get('start') and 
                    s.get('end') == span.get('end') and 
                    s.get('label') == span.get('label') 
                    for s in all_spans_merged
                ):
                    all_spans_merged.append(span)
            
            # Recopilar conflictos
            iaa = ex.get('iaa_metrics', {})
            conflicts = iaa.get('conflicts', [])
            for conflict in conflicts:
                if conflict not in all_conflicts:
                    all_conflicts.append(conflict)
        
        # Calcular métricas agregadas
        num_annotators = len(all_annotators)
        num_conflicts = len(all_conflicts)
        
        # Calcular agreement promedio del grupo
        agreements = [ex.get('iaa_metrics', {}).get('agreement_score', 1.0) for ex in group]
        avg_agreement = sum(agreements) / len(agreements) if agreements else 1.0
        
        # Color de acuerdo
        if avg_agreement >= 0.9:
            agreement_class = 'agreement-high'
        elif avg_agreement >= 0.7:
            agreement_class = 'agreement-medium'
        else:
            agreement_class = 'agreement-low'
        
        # Generar HTML de spans fusionados
        span_text_html = generate_span_html(text, all_spans_merged)
        
        # Lista de spans fusionados
        span_list_html = ''
        if all_spans_merged:
            span_items = []
            for span in sorted(all_spans_merged, key=lambda x: x.get('start', 0)):
                label = span.get('label', 'Unknown')
                ud_label = span.get('ud_label', label)
                span_text_content = span.get('text', text[span.get('start', 0):span.get('end', 0)])
                color = get_label_color(label)
                span_items.append(
                    f'<span class="span-item" style="border-left:3px solid {color};">'
                    f'<span class="span-text">"{span_text_content}"</span> → '
                    f'<span class="span-label" style="background:{color};">{label}</span> '
                    f'<span class="span-ud">({ud_label})</span>'
                    f'</span>'
                )
            span_list_html = '<div class="span-list"><h4>📌 Spans consensuados:</h4>' + ''.join(span_items) + '</div>'
        
        # Generar HTML de anotadores
        annotators_html = ''
        if num_annotators > 0:
            ann_items = []
            for session, data in sorted(all_annotators.items()):
                ann_items.append(
                    f'<span class="annotator-badge">👤 {session} ({data["num_spans"]} spans)</span>'
                )
            annotators_html = '<div class="annotators-list">' + ' '.join(ann_items) + '</div>'
        
        # Generar HTML de conflictos DETALLADOS
        conflicts_html = ''
        if all_conflicts:
            conflict_items = []
            
            # Agrupar conflictos por posición (start, end) para mostrar las diferentes etiquetas
            conflicts_by_pos = defaultdict(list)
            for conflict in all_conflicts:
                start = conflict.get('start', 0)
                end = conflict.get('end', 0)
                pos_key = (start, end)
                conflicts_by_pos[pos_key].append(conflict)
            
            for (start, end), pos_conflicts in conflicts_by_pos.items():
                # Obtener el texto del conflicto
                conflict_text = text[start:end] if start < end <= len(text) else '???'
                
                # Si hay múltiples etiquetas para la misma posición = desacuerdo de etiqueta
                if len(pos_conflicts) > 1:
                    labels_html = []
                    for c in pos_conflicts:
                        label = c.get('label', 'Unknown')
                        agree_ratio = c.get('agreement_ratio', 0)
                        annotators_agree = c.get('annotators_agree', 0)
                        total_ann = c.get('total_annotators', 1)
                        color = get_label_color(label)
                        labels_html.append(
                            f'<span style="background:{color};color:white;padding:2px 8px;border-radius:4px;margin:2px;">'
                            f'{label} ({annotators_agree}/{total_ann})</span>'
                        )
                    
                    conflict_items.append(
                        f'<div class="conflict-item conflict-label">'
                        f'<span class="conflict-type">🏷️ Etiquetas diferentes</span> '
                        f'<span class="conflict-text">"{conflict_text}"</span> [{start}:{end}]<br/>'
                        f'<span class="conflict-details">Anotadores eligieron: {" vs ".join(labels_html)}</span>'
                        f'</div>'
                    )
                else:
                    # Solo un conflicto en esta posición = span parcial (algunos lo marcaron, otros no)
                    c = pos_conflicts[0]
                    label = c.get('label', 'Unknown')
                    agree_ratio = c.get('agreement_ratio', 0)
                    annotators_agree = c.get('annotators_agree', 0)
                    total_ann = c.get('total_annotators', 1)
                    color = get_label_color(label)
                    
                    if agree_ratio < 1.0:
                        missing_count = total_ann - annotators_agree
                        conflict_items.append(
                            f'<div class="conflict-item conflict-missing">'
                            f'<span class="conflict-type">❓ Span parcial</span> '
                            f'<span class="conflict-text">"{conflict_text}"</span> '
                            f'<span class="span-label" style="background:{color};">{label}</span><br/>'
                            f'<span class="conflict-details">'
                            f'Solo {annotators_agree} de {total_ann} anotadores marcaron este span ({agree_ratio:.0%} acuerdo)'
                            f'</span>'
                            f'</div>'
                        )
            
            if conflict_items:
                conflicts_html = f'''
                <div class="conflicts-section">
                    <h4>⚠️ Conflictos ({len(conflict_items)}):</h4>
                    <div class="conflicts-list">
                        {''.join(conflict_items)}
                    </div>
                </div>
                '''
        
        html_parts.append(f'''
        <div class="example-card" data-index="{i}">
            <div class="example-header">
                <span class="example-number">#{i}</span>
                <span class="example-stats">
                    <span class="stat">{len(all_spans_merged)} spans</span>
                    <span class="stat {agreement_class}">{avg_agreement:.0%} acuerdo</span>
                    <span class="stat">{num_annotators} anotador(es)</span>
                    {f'<span class="stat conflict">{num_conflicts} conflictos</span>' if num_conflicts > 0 else ''}
                </span>
            </div>
            <div class="example-content">
                <div class="spanish-text">
                    <span class="lang-label">🇪🇸 Español:</span>
                    {spanish_text}
                </div>
                <div class="guarani-text">
                    <span class="lang-label">🇵🇾 Guaraní:</span>
                    <div class="annotated-text">{span_text_html}</div>
                </div>
                {annotators_html}
                {span_list_html}
                {conflicts_html}
            </div>
        </div>
        ''')
    
    html_parts.append('</div>')
    return '\n'.join(html_parts)


def generate_html(data: dict, output_path: str):
    """Genera el archivo HTML completo."""
    
    metadata = data.get('metadata', {})
    examples = data.get('examples', [])
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualización de Anotaciones - {metadata.get('dataset_name', 'Dataset')}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            color: #1f2937;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        header .subtitle {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .main-grid {{
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
        }}
        
        @media (max-width: 1024px) {{
            .main-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .panel {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .panel h3 {{
            font-size: 16px;
            margin-bottom: 15px;
            color: #374151;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 12px;
            background: #f9fafb;
            border-radius: 8px;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #8b5cf6;
        }}
        
        .stat-label {{
            font-size: 11px;
            color: #6b7280;
            text-transform: uppercase;
        }}
        
        .label-stats {{
            margin-top: 20px;
        }}
        
        .label-stats h4 {{
            font-size: 13px;
            color: #6b7280;
            margin-bottom: 10px;
        }}
        
        .label-bars {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .label-bar {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
        }}
        
        .label-name {{
            width: 80px;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
        }}
        
        .bar {{
            height: 16px;
            border-radius: 4px;
            min-width: 4px;
        }}
        
        .label-count {{
            color: #6b7280;
            font-size: 11px;
        }}
        
        .legend {{
            background: white;
            border-radius: 12px;
            padding: 20px;
        }}
        
        .legend-grid {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .legend-family {{
            border-bottom: 1px solid #f3f4f6;
            padding-bottom: 10px;
        }}
        
        .legend-family:last-child {{
            border-bottom: none;
        }}
        
        .family-header {{
            font-weight: 600;
            font-size: 12px;
            margin-bottom: 6px;
        }}
        
        .family-labels {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }}
        
        .label-badge {{
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            color: white;
        }}
        
        .examples-container {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        
        .example-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .example-header {{
            background: #f9fafb;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #f3f4f6;
        }}
        
        .example-number {{
            font-weight: bold;
            color: #8b5cf6;
        }}
        
        .example-stats {{
            display: flex;
            gap: 12px;
            font-size: 12px;
        }}
        
        .example-stats .stat {{
            padding: 2px 8px;
            background: #f3f4f6;
            border-radius: 4px;
            color: #6b7280;
        }}
        
        .agreement-high {{
            background: #d1fae5 !important;
            color: #065f46 !important;
        }}
        
        .agreement-medium {{
            background: #fef3c7 !important;
            color: #92400e !important;
        }}
        
        .agreement-low {{
            background: #fee2e2 !important;
            color: #991b1b !important;
        }}
        
        .conflict {{
            background: #fee2e2 !important;
            color: #991b1b !important;
        }}
        
        .example-content {{
            padding: 16px;
        }}
        
        .spanish-text, .guarani-text {{
            margin-bottom: 12px;
        }}
        
        .lang-label {{
            font-weight: 600;
            font-size: 13px;
            margin-right: 8px;
        }}
        
        .annotated-text {{
            display: inline;
            font-size: 16px;
            line-height: 2;
        }}
        
        .span-highlight {{
            padding: 2px 0;
            cursor: help;
        }}
        
        .span-list {{
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #f3f4f6;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .span-item {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 8px;
            background: #f9fafb;
            border-radius: 6px;
            font-size: 12px;
        }}
        
        .span-text {{
            color: #374151;
            font-style: italic;
        }}
        
        .span-label {{
            color: white;
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 11px;
        }}
        
        .span-ud {{
            color: #9ca3af;
            font-size: 10px;
        }}
        
        .annotators-list {{
            margin: 12px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .annotator-badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            background: #e0e7ff;
            color: #3730a3;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .conflicts-section {{
            margin-top: 16px;
            padding: 16px;
            background: #fef2f2;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
        }}
        
        .conflicts-section h4 {{
            color: #991b1b;
            margin-bottom: 12px;
            font-size: 14px;
        }}
        
        .conflicts-list {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .conflict-item {{
            padding: 10px 12px;
            background: white;
            border-radius: 6px;
            font-size: 13px;
            border: 1px solid #fecaca;
        }}
        
        .conflict-type {{
            font-weight: 600;
            margin-right: 8px;
        }}
        
        .conflict-text {{
            font-style: italic;
            color: #374151;
            background: #fef3c7;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .conflict-details {{
            display: block;
            margin-top: 6px;
            font-size: 12px;
            color: #6b7280;
        }}
        
        .conflict-label {{
            border-left: 3px solid #f59e0b;
        }}
        
        .conflict-missing {{
            border-left: 3px solid #ef4444;
        }}
        
        .span-list h4 {{
            width: 100%;
            font-size: 13px;
            color: #6b7280;
            margin-bottom: 8px;
        }}
        
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #9ca3af;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔬 Visualización de Anotaciones Morfológicas</h1>
            <div class="subtitle">
                Dataset: <strong>{metadata.get('dataset_name', 'Unknown')}</strong> | 
                Exportado: {metadata.get('export_date', 'N/A')[:10]}
            </div>
        </header>
        
        <div class="main-grid">
            <div class="sidebar">
                {generate_stats_html(data)}
                {generate_legend_html()}
            </div>
            
            <div class="content">
                {generate_examples_html(examples)}
            </div>
        </div>
        
        <div class="footer">
            <p>Generado con UD Guaraní Mapper | Universal Dependencies para Old Guaraní</p>
            <p>Referencia: <a href="https://universaldependencies.org/treebanks/gn_oldtudet/index.html">UD Guarani OldTuDeT</a></p>
        </div>
    </div>
</body>
</html>
'''
    
    # Guardar archivo
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding='utf-8')
    print(f"✅ Visualización generada: {output_path}")
    print(f"   - {len(examples)} ejemplos")
    print(f"   - Abrir en navegador para ver")


def main():
    parser = argparse.ArgumentParser(
        description="Genera visualización HTML de anotaciones exportadas"
    )
    parser.add_argument(
        "input",
        help="Archivo JSON exportado (ej: resultados/export_test_ud.json)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Archivo HTML de salida (default: mismo nombre con .html)"
    )
    
    args = parser.parse_args()
    
    # Cargar datos
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Archivo no encontrado: {input_path}")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Determinar salida
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.with_suffix('.html'))
    
    # Generar HTML
    generate_html(data, output_path)


if __name__ == "__main__":
    main()
