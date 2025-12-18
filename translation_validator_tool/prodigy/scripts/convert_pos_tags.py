"""
Script para convertir anotaciones entre etiquetas amigables y Universal Dependencies

Convierte archivos JSONL/JSON entre etiquetas amigables (español) y 
Universal Dependencies (UD), manteniendo toda la metadata y estructura.

Usa ud_guarani_mapper.py como fuente única de verdad para el mapeo.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Importar el módulo de mapeo UD (fuente única de verdad)
from ud_guarani_mapper import (
    FRIENDLY_TO_UD,
    UD_TO_FRIENDLY,
    map_label,
    map_labels_batch,
    is_valid_ud,
    VALID_UPOS,
    VALID_FEATURES,
)


def convert_spans_to_ud(spans: list) -> list:
    """
    Convierte una lista de spans con etiquetas amigables a UD.
    
    Args:
        spans: Lista de dicts con keys 'start', 'end', 'label', 'text'
        
    Returns:
        Nueva lista de spans con etiquetas UD
    """
    converted = []
    for span in spans:
        new_span = span.copy()
        friendly_label = span.get("label", "")
        
        try:
            ud_label = map_label(friendly_label, direction="to_ud")
            new_span["ud_label"] = ud_label
            new_span["original_label"] = friendly_label
            new_span["label"] = ud_label
        except Exception:
            # Si la etiqueta ya está en formato UD, mantenerla
            if is_valid_ud(friendly_label):
                new_span["ud_label"] = friendly_label
                new_span["original_label"] = friendly_label
            else:
                new_span["ud_label"] = "X"
                new_span["original_label"] = friendly_label
                new_span["label"] = "X"
                new_span["conversion_error"] = f"Etiqueta no reconocida: {friendly_label}"
        
        converted.append(new_span)
    
    return converted


def convert_spans_to_friendly(spans: list) -> list:
    """
    Convierte una lista de spans con etiquetas UD a amigables (español).
    
    Args:
        spans: Lista de dicts con keys 'start', 'end', 'label', 'text'
        
    Returns:
        Nueva lista de spans con etiquetas amigables
    """
    converted = []
    for span in spans:
        new_span = span.copy()
        ud_label = span.get("label", "")
        
        try:
            friendly_label = map_label(ud_label, direction="to_friendly")
            new_span["friendly_label"] = friendly_label
            new_span["ud_label"] = ud_label
            new_span["label"] = friendly_label
        except Exception:
            # Mantener original si no se puede convertir
            new_span["friendly_label"] = ud_label
            new_span["ud_label"] = ud_label
            new_span["conversion_error"] = f"Sin mapeo amigable para: {ud_label}"
        
        converted.append(new_span)
    
    return converted


def convert_jsonl_to_ud(input_file: str, output_file: str, verbose: bool = False):
    """
    Convierte archivo JSONL con etiquetas amigables a UD.
    
    Args:
        input_file: Ruta al archivo JSONL de entrada
        output_file: Ruta al archivo JSONL de salida
        verbose: Mostrar detalles de conversión
    """
    converted_count = 0
    span_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        for line_num, line in enumerate(f_in, 1):
            try:
                example = json.loads(line)
                
                # Convertir spans si existen
                if 'spans' in example and example['spans']:
                    original_spans = example['spans']
                    converted_spans = convert_spans_to_ud(original_spans)
                    example['spans'] = converted_spans
                    
                    span_count += len(converted_spans)
                    converted_count += 1
                    
                    if verbose:
                        print(f"Línea {line_num}: {len(original_spans)} spans convertidos")
                        for span in converted_spans:
                            orig = span.get('original_label', '')
                            ud = span.get('ud_label', '')
                            text = span.get('text', '')
                            print(f"  • '{text}': {orig} → {ud}")
                
                # Agregar metadata de conversión
                if 'meta' not in example:
                    example['meta'] = {}
                example['meta']['converted_to_ud'] = True
                example['meta']['conversion_source'] = 'friendly_spanish'
                
                # Escribir línea convertida
                f_out.write(json.dumps(example, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError as e:
                print(f"Error en línea {line_num}: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"Error procesando línea {line_num}: {e}", file=sys.stderr)
                continue
    
    print(f"\n✓ Conversión completada:")
    print(f"  • Ejemplos convertidos: {converted_count}")
    print(f"  • Total spans: {span_count}")
    print(f"  • Archivo de salida: {output_file}")


def convert_jsonl_to_friendly(input_file: str, output_file: str, verbose: bool = False):
    """
    Convierte archivo JSONL con etiquetas UD a amigables (español).
    
    Args:
        input_file: Ruta al archivo JSONL de entrada
        output_file: Ruta al archivo JSONL de salida
        verbose: Mostrar detalles de conversión
    """
    converted_count = 0
    span_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        for line_num, line in enumerate(f_in, 1):
            try:
                example = json.loads(line)
                
                # Convertir spans si existen
                if 'spans' in example and example['spans']:
                    original_spans = example['spans']
                    converted_spans = convert_spans_to_friendly(original_spans)
                    example['spans'] = converted_spans
                    
                    span_count += len(converted_spans)
                    converted_count += 1
                    
                    if verbose:
                        print(f"Línea {line_num}: {len(original_spans)} spans convertidos")
                        for span in converted_spans:
                            ud = span.get('ud_label', '')
                            friendly = span.get('friendly_label', '')
                            text = span.get('text', '')
                            print(f"  • '{text}': {ud} → {friendly}")
                
                # Agregar metadata de conversión
                if 'meta' not in example:
                    example['meta'] = {}
                example['meta']['converted_to_friendly'] = True
                example['meta']['conversion_source'] = 'ud'
                
                # Escribir línea convertida
                f_out.write(json.dumps(example, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError as e:
                print(f"Error en línea {line_num}: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"Error procesando línea {line_num}: {e}", file=sys.stderr)
                continue
    
    print(f"\n✓ Conversión completada:")
    print(f"  • Ejemplos convertidos: {converted_count}")
    print(f"  • Total spans: {span_count}")
    print(f"  • Archivo de salida: {output_file}")


def convert_json_report(input_file: str, output_file: str, direction: str = "to_ud", verbose: bool = False):
    """
    Convierte archivo JSON (reporte con metadata) entre formatos.
    
    Args:
        input_file: Ruta al archivo JSON de entrada
        output_file: Ruta al archivo JSON de salida
        direction: 'to_ud' o 'to_friendly'
        verbose: Mostrar detalles de conversión
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    converted_count = 0
    span_count = 0
    
    # Convertir ejemplos
    if 'examples' in report:
        for example in report['examples']:
            if 'spans' in example and example['spans']:
                if direction == "to_ud":
                    example['spans'] = convert_spans_to_ud(example['spans'])
                else:
                    example['spans'] = convert_spans_to_friendly(example['spans'])
                
                span_count += len(example['spans'])
                converted_count += 1
    
    # Actualizar metadata
    if 'metadata' not in report:
        report['metadata'] = {}
    
    report['metadata']['label_format'] = 'ud' if direction == "to_ud" else 'friendly_spanish'
    report['metadata']['conversion_direction'] = direction
    
    # Guardar archivo convertido
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Conversión de reporte completada:")
    print(f"  • Ejemplos convertidos: {converted_count}")
    print(f"  • Total spans: {span_count}")
    print(f"  • Formato: {report['metadata']['label_format']}")
    print(f"  • Archivo de salida: {output_file}")


def show_statistics(file_path: str):
    """
    Muestra estadísticas de las etiquetas en un archivo.
    
    Args:
        file_path: Ruta al archivo JSONL o JSON
    """
    from collections import Counter
    
    label_counts = Counter()
    total_examples = 0
    total_spans = 0
    
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == '.jsonl':
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    example = json.loads(line)
                    total_examples += 1
                    if 'spans' in example:
                        for span in example['spans']:
                            label = span.get('label', 'UNKNOWN')
                            label_counts[label] += 1
                            total_spans += 1
        
        elif file_ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'examples' in data:
                    for example in data['examples']:
                        total_examples += 1
                        if 'spans' in example:
                            for span in example['spans']:
                                label = span.get('label', 'UNKNOWN')
                                label_counts[label] += 1
                                total_spans += 1
        
        print(f"\n{'='*60}")
        print(f"ESTADÍSTICAS: {Path(file_path).name}")
        print(f"{'='*60}")
        print(f"Total ejemplos: {total_examples}")
        print(f"Total spans: {total_spans}")
        print(f"\nDistribución de etiquetas:")
        print(f"{'-'*60}")
        print(f"{'ETIQUETA':<30} {'CANTIDAD':<15} {'%'}")
        print(f"{'-'*60}")
        
        for label, count in label_counts.most_common():
            percentage = (count / total_spans * 100) if total_spans > 0 else 0
            print(f"{label:<30} {count:<15} {percentage:>5.1f}%")
        
        print(f"{'='*60}\n")
        
        # Detectar formato
        sample_labels = set(label_counts.keys())
        # Etiquetas UD típicas
        ud_tags = VALID_UPOS | VALID_FEATURES
        is_ud = any(label in ud_tags for label in sample_labels)
        # Etiquetas amigables típicas
        friendly_tags = {'Verbo', 'Sustantivo', 'Pronombre', 'Adverbio', '1ra Persona', 'Singular'}
        is_friendly = any(label in friendly_tags for label in sample_labels)
        
        if is_ud and not is_friendly:
            print("✓ Formato detectado: UD (Universal Dependencies)")
        elif is_friendly:
            print("✓ Formato detectado: AMIGABLE (Español)")
        else:
            print("⚠ Formato no detectado claramente")
    
    except Exception as e:
        print(f"Error analizando archivo: {e}", file=sys.stderr)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convertir anotaciones entre etiquetas amigables (español) y UD"
    )
    
    parser.add_argument(
        "input",
        help="Archivo de entrada (.jsonl o .json)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Archivo de salida (por defecto: input_converted.ext)"
    )
    
    parser.add_argument(
        "--direction", "-d",
        choices=["to_ud", "to_friendly"],
        default="to_ud",
        help="Dirección de conversión (por defecto: to_ud)"
    )
    
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Mostrar estadísticas del archivo sin convertir"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostrar detalles de conversión"
    )
    
    args = parser.parse_args()
    
    # Determinar archivo de salida
    if not args.output:
        input_path = Path(args.input)
        suffix = "_ud" if args.direction == "to_ud" else "_friendly"
        args.output = str(input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}")
    
    # Mostrar estadísticas si se solicita
    if args.stats:
        show_statistics(args.input)
        if not args.output:
            sys.exit(0)
    
    # Convertir archivo
    file_ext = Path(args.input).suffix.lower()
    
    try:
        if file_ext == '.jsonl':
            if args.direction == "to_ud":
                convert_jsonl_to_ud(args.input, args.output, args.verbose)
            else:
                convert_jsonl_to_friendly(args.input, args.output, args.verbose)
        
        elif file_ext == '.json':
            convert_json_report(args.input, args.output, args.direction, args.verbose)
        
        else:
            print(f"Error: Formato de archivo no soportado: {file_ext}", file=sys.stderr)
            print("Formatos soportados: .jsonl, .json", file=sys.stderr)
            sys.exit(1)
        
        # Mostrar estadísticas del archivo convertido
        if not args.stats:
            print("\nEstadísticas del archivo convertido:")
            show_statistics(args.output)
    
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error durante la conversión: {e}", file=sys.stderr)
        sys.exit(1)
